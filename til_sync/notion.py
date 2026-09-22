"""Read-only Notion API access, including pagination and transient failures."""

from __future__ import annotations

import logging
import math
import random
import time
from collections.abc import Iterator
from http import HTTPStatus
from typing import Self
from urllib.parse import quote, unquote

import requests

from .constants import DEFAULT_DATE_PROPERTY, REQUEST_TIMEOUT

API_BASE = "https://api.notion.com/v1"
API_VERSION = "2026-03-11"
PAGE_SIZE = 100
TITLE_PROPERTY_INLINE_LIMIT = 25
REQUEST_INTERVAL = 0.34  # Stay below the basic plan's 180 requests/minute.
MAX_ATTEMPTS = 5
MAX_RETRY_DELAY = 300.0
MAX_BACKOFF_DELAY = 30.0
MAX_RETRY_JITTER = 0.25
NOTION_SERVICE_OVERLOAD = 529  # Notion-specific status, absent from HTTPStatus.
RETRYABLE_STATUSES = {
    HTTPStatus.TOO_MANY_REQUESTS,
    HTTPStatus.INTERNAL_SERVER_ERROR,
    HTTPStatus.BAD_GATEWAY,
    HTTPStatus.SERVICE_UNAVAILABLE,
    HTTPStatus.GATEWAY_TIMEOUT,
    NOTION_SERVICE_OVERLOAD,
}

LOGGER = logging.getLogger(__name__)

ERROR_HINTS = {
    HTTPStatus.BAD_REQUEST: "Check the configured property names, property types, and IDs.",
    HTTPStatus.UNAUTHORIZED: "Check NOTION_TOKEN and whether the Notion connection is still active.",
    HTTPStatus.FORBIDDEN: "Give the Notion connection permission to read this content.",
    HTTPStatus.NOT_FOUND: "Check the ID and share the database/page with the Notion connection.",
    HTTPStatus.TOO_MANY_REQUESTS: "Notion's request limit was reached; try again later.",
}
KNOWN_ERROR_CODES = {
    "invalid_json",
    "invalid_request_url",
    "invalid_request",
    "validation_error",
    "missing_version",
    "unauthorized",
    "restricted_resource",
    "object_not_found",
    "row_limit_exceeded",
    "conflict_error",
    "rate_limited",
    "internal_server_error",
    "bad_gateway",
    "service_unavailable",
    "database_connection_unavailable",
    "gateway_timeout",
    "service_overload",
}


class NotionAPIError(RuntimeError):
    """An actionable error that never includes API tokens or response bodies."""

    def __init__(
        self, message: str, *, status: int | None = None, code: str = ""
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code


class NotionClient:
    """One sync run's HTTP session and cache; use as a context manager."""

    def __init__(self, token: str) -> None:
        if not token.strip():
            raise ValueError("NOTION_TOKEN is required.")
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {token.strip()}",
                "Notion-Version": API_VERSION,
                "Content-Type": "application/json",
            }
        )
        self._next_request_at = 0.0
        self._children_cache: dict[str, list[dict]] = {}
        self._block_cache: dict[str, dict] = {}

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def close(self) -> None:
        self._session.close()

    def resolve_data_source(self, database_id: str, data_source_id: str = "") -> str:
        """Keep old database IDs working without choosing an unrelated source."""
        if data_source_id.strip():
            return data_source_id.strip()
        database = self._request("GET", f"/databases/{_path_id(database_id)}")
        sources = database.get("data_sources")
        if not isinstance(sources, list) or any(
            not isinstance(source, dict)
            or not isinstance(source.get("id"), str)
            or not source["id"].strip()
            for source in sources
        ):
            raise NotionAPIError(
                "Notion returned an invalid database data_sources list."
            )
        source_ids = list(dict.fromkeys(source["id"].strip() for source in sources))
        if not source_ids:
            raise NotionAPIError(
                "The database has no accessible data source. Check the database ID "
                "and the Notion connection's access."
            )
        if len(source_ids) != 1:
            raise NotionAPIError(
                "The database contains multiple data sources. Set "
                "NOTION_DATA_SOURCE_ID to the data source containing your TIL notes."
            )
        return source_ids[0]

    def query_pages(
        self,
        data_source_id: str,
        date_property: str = DEFAULT_DATE_PROPERTY,
        target_date: str | None = None,
    ) -> Iterator[dict]:
        """Yield every matching page, preserving the API's returned order."""
        payload: dict = {"page_size": PAGE_SIZE}
        if target_date is not None:
            payload["filter"] = {
                "property": date_property,
                "date": {"equals": target_date},
            }
        yield from self._paginate(
            "POST", f"/data_sources/{_path_id(data_source_id)}/query", payload
        )

    def get_block_children(self, block_id: str) -> list[dict]:
        """Retrieve all children once; callers should treat cached blocks as read-only."""
        block_id = block_id.strip()
        if block_id not in self._children_cache:
            children = list(
                self._paginate("GET", f"/blocks/{_path_id(block_id)}/children")
            )
            # Populate caches only after all pages have been retrieved successfully.
            self._children_cache[block_id] = children
            for block in children:
                if isinstance(block.get("id"), str):
                    self._block_cache[block["id"]] = block
        return self._children_cache[block_id]

    def retrieve_block(self, block_id: str) -> dict:
        block_id = block_id.strip()
        if block_id not in self._block_cache:
            self._block_cache[block_id] = self._request(
                "GET", f"/blocks/{_path_id(block_id)}"
            )
        return self._block_cache[block_id]

    def iter_page_property_items(
        self, page_id: str, property_id: str
    ) -> Iterator[dict]:
        """Paginate list-valued properties, including long titles and rich text."""
        # Notion may already percent-encode short property IDs in responses.
        property_path = quote(unquote(property_id), safe="")
        if not property_path:
            raise ValueError("A Notion property ID is required.")
        yield from self._paginate(
            "GET", f"/pages/{_path_id(page_id)}/properties/{property_path}"
        )

    def _paginate(
        self, method: str, path: str, payload: dict | None = None
    ) -> Iterator[dict]:
        cursor: str | None = None
        seen_cursors: set[str] = set()
        while True:
            parameters = dict(payload or {"page_size": PAGE_SIZE})
            if cursor is not None:
                parameters["start_cursor"] = cursor
            response = self._request(method, path, parameters)
            results = response.get("results")
            if not isinstance(results, list) or any(
                not isinstance(result, dict) for result in results
            ):
                raise NotionAPIError(
                    "Notion returned an invalid paginated results list."
                )
            has_more = response.get("has_more")
            if not isinstance(has_more, bool):
                raise NotionAPIError(
                    "Notion returned an invalid pagination has_more flag."
                )
            next_cursor = response.get("next_cursor")
            if has_more:
                if not isinstance(next_cursor, str) or not next_cursor.strip():
                    raise NotionAPIError(
                        "Notion reports more results without a valid pagination cursor."
                    )
                if next_cursor in seen_cursors:
                    raise NotionAPIError(
                        "Notion repeated a pagination cursor; refusing an incomplete export."
                    )
                seen_cursors.add(next_cursor)
            yield from results
            if not has_more:
                return
            cursor = next_cursor

    def _request(self, method: str, path: str, parameters: dict | None = None) -> dict:
        # The sole POST operation is a read-only query, so every operation here
        # is safe to repeat after a transient transport/server failure.
        for attempt in range(MAX_ATTEMPTS):
            wait = self._next_request_at - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            self._next_request_at = time.monotonic() + REQUEST_INTERVAL
            try:
                response = self._session.request(
                    method,
                    API_BASE + path,
                    params=parameters if method == "GET" else None,
                    json=parameters if method == "POST" else None,
                    timeout=REQUEST_TIMEOUT,
                    allow_redirects=False,
                )
            except (
                requests.ConnectionError,
                requests.Timeout,
                requests.exceptions.ChunkedEncodingError,
            ):
                if attempt == MAX_ATTEMPTS - 1:
                    raise NotionAPIError(
                        "Notion could not be reached after repeated attempts. "
                        "Check the network connection and try again."
                    ) from None
                delay = _backoff(attempt)
                LOGGER.warning(
                    "Notion network failure; retrying in %.1f seconds (%d/%d).",
                    delay,
                    attempt + 1,
                    MAX_ATTEMPTS - 1,
                )
                time.sleep(delay)
                continue
            except requests.RequestException:
                raise NotionAPIError(
                    "The Notion HTTP request failed. Check the network and HTTP configuration."
                ) from None

            try:
                if HTTPStatus.OK <= response.status_code < HTTPStatus.MULTIPLE_CHOICES:
                    try:
                        data = response.json()
                    except ValueError:
                        raise NotionAPIError("Notion returned invalid JSON.") from None
                    if not isinstance(data, dict):
                        raise NotionAPIError("Notion returned an invalid JSON object.")
                    return data

                error = _response_error(response)
                if (
                    response.status_code not in RETRYABLE_STATUSES
                    or attempt == MAX_ATTEMPTS - 1
                ):
                    raise error
                delay = _backoff(attempt)
                try:
                    retry_after = float(response.headers.get("Retry-After", ""))
                except (TypeError, ValueError):
                    retry_after = 0.0
                if math.isfinite(retry_after) and retry_after > 0:
                    delay = max(delay, retry_after)
                if delay > MAX_RETRY_DELAY:
                    # Never shorten Retry-After and issue another request too soon.
                    raise NotionAPIError(
                        f"Notion requested a retry delay longer than {MAX_RETRY_DELAY:g} seconds. "
                        "Run the sync again later.",
                        status=error.status,
                        code=error.code,
                    )
                LOGGER.warning(
                    "Notion HTTP %d; retrying in %.1f seconds (%d/%d).",
                    response.status_code,
                    delay,
                    attempt + 1,
                    MAX_ATTEMPTS - 1,
                )
            finally:
                response.close()
            time.sleep(delay)
        raise AssertionError("Unreachable retry state")


def _path_id(value: str) -> str:
    if not value.strip():
        raise ValueError("A Notion object ID is required.")
    return quote(value.strip(), safe="")


def _backoff(attempt: int) -> float:
    return min(2**attempt, MAX_BACKOFF_DELAY) + random.uniform(0, MAX_RETRY_JITTER)


def _response_error(response: requests.Response) -> NotionAPIError:
    code = "unknown_error"
    try:
        data = response.json()
        if isinstance(data, dict) and data.get("code") in KNOWN_ERROR_CODES:
            code = data["code"]
    except (TypeError, ValueError):
        pass
    hint = ERROR_HINTS.get(
        response.status_code,
        "Notion could not complete the request. Try again later or check its service status.",
    )
    return NotionAPIError(
        f"Notion API failed (HTTP {response.status_code}, {code}). {hint}",
        status=response.status_code,
        code=code,
    )

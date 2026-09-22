"""Notion의 만료되는 첨부파일 URL을 저장소의 상대경로로 바꿉니다."""

import hashlib
import mimetypes
import re
import tempfile
from http import HTTPStatus
from pathlib import Path
from types import TracebackType
from typing import Self
from urllib.parse import parse_qs, quote, unquote, urlsplit
from uuid import UUID

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .constants import (
    ASSETS_DIRECTORY,
    BYTES_PER_MIB,
    RELATIVE_URL_SAFE,
    REQUEST_TIMEOUT,
)

MAX_ASSET_BYTES = 50 * BYTES_PER_MIB
DOWNLOAD_CHUNK_BYTES = 64 * 1024
DOWNLOAD_RETRY_COUNT = 3
DOWNLOAD_BACKOFF_FACTOR = 1
MAX_ASSET_ID_LENGTH = 48
ASSET_HASH_LENGTH = 16
HOSTED_DOMAIN_SUFFIXES = (".amazonaws.com", ".notion.so", ".notion-static.com")
SIGNED_URL_PARAMETERS = frozenset({"x-amz-signature", "signature", "x-amz-credential"})
RETRYABLE_STATUSES = (
    HTTPStatus.TOO_MANY_REQUESTS,
    HTTPStatus.INTERNAL_SERVER_ERROR,
    HTTPStatus.BAD_GATEWAY,
    HTTPStatus.SERVICE_UNAVAILABLE,
    HTTPStatus.GATEWAY_TIMEOUT,
)


class AssetError(RuntimeError):
    """첨부파일을 안전하게 저장할 수 없어 해당 페이지의 내보내기를 중단합니다."""


def is_hosted_embed(url: str) -> bool:
    parsed = urlsplit(url)
    host = (parsed.hostname or "").lower()
    signed = {key.lower() for key in parse_qs(parsed.query)}
    return host.endswith(HOSTED_DOMAIN_SUFFIXES) and bool(
        signed & SIGNED_URL_PARAMETERS
    )


class AssetStore:
    def __init__(
        self,
        markdown_path: Path,
        page_id: str,
        *,
        session: requests.Session | None = None,
    ) -> None:
        self.markdown_path = markdown_path
        self.directory = markdown_path.parent / ASSETS_DIRECTORY / UUID(page_id).hex
        # Notion API Session을 재사용하지 않아 외부 호스트에 토큰을 보내지 않습니다.
        self.session = session or requests.Session()
        if session is None:
            retry = Retry(
                total=DOWNLOAD_RETRY_COUNT,
                backoff_factor=DOWNLOAD_BACKOFF_FACTOR,
                status_forcelist=RETRYABLE_STATUSES,
                allowed_methods={"GET"},
                respect_retry_after_header=True,
            )
            self.session.mount("https://", HTTPAdapter(max_retries=retry))
        self._urls: dict[tuple[str, str], str] = {}

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.session.close()

    def media_url(self, block: dict, payload: dict) -> str:
        url = (
            payload.get("file", {}).get("url")
            or payload.get("external", {}).get("url")
            or payload.get("url", "")
        )
        if not url:
            raise AssetError(
                f"첨부파일 URL을 가져올 수 없습니다 (블록 {block.get('id', '?')})."
            )
        if not payload.get("file") and not is_hosted_embed(url):
            return url
        parsed = urlsplit(url)
        if parsed.scheme != "https" or not parsed.hostname:
            raise AssetError("Notion 첨부파일은 유효한 HTTPS URL이어야 합니다.")
        block_key = (
            re.sub(r"[^a-zA-Z0-9_-]", "", block.get("id", "asset"))[
                :MAX_ASSET_ID_LENGTH
            ]
            or "asset"
        )
        source = f"{parsed.netloc}{parsed.path}"
        cache_key = (block_key, source)
        if cache_key in self._urls:
            return self._urls[cache_key]
        digest = hashlib.sha256(source.encode()).hexdigest()[:ASSET_HASH_LENGTH]
        extension = Path(unquote(parsed.path)).suffix.lower()
        if not re.fullmatch(r"\.[a-z0-9]{1,10}", extension):
            extension = ""
        self.directory.mkdir(parents=True, exist_ok=True)
        temporary: Path | None = None
        size_error = (
            f"첨부파일이 {MAX_ASSET_BYTES / BYTES_PER_MIB:g} MiB를 넘습니다. "
            "외부 링크로 첨부하거나 파일을 줄여 주세요."
        )
        try:
            with self.session.get(
                url, timeout=REQUEST_TIMEOUT, stream=True
            ) as response:
                response.raise_for_status()
                size_header = response.headers.get("Content-Length", "")
                if size_header.isdecimal() and int(size_header) > MAX_ASSET_BYTES:
                    raise AssetError(size_error)
                if not extension:
                    content_type = response.headers.get("Content-Type", "").split(";")[
                        0
                    ]
                    extension = mimetypes.guess_extension(content_type) or ".bin"
                destination = self.directory / f"{block_key}-{digest}{extension}"
                with tempfile.NamedTemporaryFile(
                    dir=self.directory, delete=False
                ) as handle:
                    temporary = Path(handle.name)
                    total = 0
                    downloaded_hash = hashlib.sha256()
                    for chunk in response.iter_content(chunk_size=DOWNLOAD_CHUNK_BYTES):
                        total += len(chunk)
                        if total > MAX_ASSET_BYTES:
                            raise AssetError(size_error)
                        downloaded_hash.update(chunk)
                        handle.write(chunk)
            identical = False
            if destination.exists():
                with destination.open("rb") as current:
                    identical = (
                        hashlib.file_digest(current, "sha256").digest()
                        == downloaded_hash.digest()
                    )
            if not identical:
                temporary.replace(destination)
            link = quote(
                destination.relative_to(self.markdown_path.parent).as_posix(),
                safe=RELATIVE_URL_SAFE,
            )
            self._urls[cache_key] = link
            return link
        except requests.RequestException as exc:
            raise AssetError(
                f"첨부파일 다운로드 실패 (블록 {block_key}, {type(exc).__name__})."
            ) from None
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

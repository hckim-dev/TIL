"""Notion의 만료되는 첨부파일 URL을 저장소의 상대경로로 바꿉니다."""

import hashlib
import mimetypes
import os
import re
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlsplit
from uuid import UUID

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

MAX_ASSET_BYTES = 50 * 1024 * 1024


class AssetError(RuntimeError):
    pass


def is_hosted_embed(url: str) -> bool:
    parsed = urlsplit(url)
    host = (parsed.hostname or "").lower()
    signed = {key.lower() for key in parse_qs(parsed.query)}
    return (
        host.endswith(".amazonaws.com")
        or host.endswith(".notion.so")
        or host.endswith(".notion-static.com")
    ) and bool(signed & {"x-amz-signature", "signature", "x-amz-credential"})


class AssetStore:
    def __init__(self, markdown_path: Path, page_id: str, *, session=None):
        self.markdown_path = markdown_path
        self.directory = markdown_path.parent / "assets" / UUID(page_id).hex
        # Notion API Session을 재사용하지 않아 외부 호스트에 토큰을 보내지 않습니다.
        self.session = session or requests.Session()
        if session is None:
            retry = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods={"GET"},
                respect_retry_after_header=True,
            )
            self.session.mount("https://", HTTPAdapter(max_retries=retry))
        self._urls: dict[tuple[str, str], str] = {}

    def __enter__(self):
        return self

    def __exit__(self, *args):
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
            re.sub(r"[^a-zA-Z0-9_-]", "", block.get("id", "asset"))[:48] or "asset"
        )
        source = f"{parsed.netloc}{parsed.path}"
        cache_key = (block_key, source)
        if cache_key in self._urls:
            return self._urls[cache_key]
        digest = hashlib.sha256(source.encode()).hexdigest()[:16]
        extension = Path(unquote(parsed.path)).suffix.lower()
        if not re.fullmatch(r"\.[a-z0-9]{1,10}", extension):
            extension = ""
        self.directory.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with self.session.get(url, timeout=(10, 60), stream=True) as response:
                response.raise_for_status()
                size_header = response.headers.get("Content-Length", "")
                if size_header.isdecimal() and int(size_header) > MAX_ASSET_BYTES:
                    raise AssetError(
                        "첨부파일이 50 MiB를 넘습니다. 외부 링크로 첨부하거나 파일을 줄여 주세요."
                    )
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
                    for chunk in response.iter_content(chunk_size=64 * 1024):
                        total += len(chunk)
                        if total > MAX_ASSET_BYTES:
                            raise AssetError(
                                "첨부파일이 50 MiB를 넘습니다. 외부 링크로 첨부하거나 파일을 줄여 주세요."
                            )
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
                os.replace(temporary, destination)
            link = quote(
                destination.relative_to(self.markdown_path.parent).as_posix(),
                safe="/-._~",
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

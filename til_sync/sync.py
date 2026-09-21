"""조회 → Markdown 변환 → 파일 저장 → README 갱신을 조율합니다."""

import logging
from datetime import date

from .assets import AssetStore
from .config import Config
from .markdown import MarkdownRenderer, notion_url, plain_text
from .notion import NotionClient
from .storage import PageStore, update_readme

LOGGER = logging.getLogger(__name__)


def page_title(page: dict, property_name: str, client: NotionClient) -> str:
    properties = page.get("properties", {})
    prop = properties.get(property_name)
    if not prop or prop.get("type") != "title":
        prop = next(
            (value for value in properties.values() if value.get("type") == "title"), {}
        )
    rich_text = prop.get("title", [])
    if len(rich_text) >= 25 and prop.get("id"):
        rich_text = [
            item["title"]
            for item in client.iter_page_property_items(page["id"], prop["id"])
            if item.get("type") == "title"
        ]
    return plain_text(rich_text).strip() or "제목없음"


def sync(config: Config, client: NotionClient) -> int:
    source_id = client.resolve_data_source(config.database_id, config.data_source_id)
    store = PageStore(config.root)
    saved = skipped = failed = 0
    LOGGER.info(
        "동기화 모드: %s%s",
        config.fetch_mode,
        f" (날짜: {config.target_date}, KST)" if config.target_date else "",
    )
    for page in client.query_pages(source_id, config.date_property, config.target_date):
        if page.get("in_trash") or page.get("archived"):
            continue
        page_id = page["id"]
        try:
            properties = page.get("properties", {})
            if config.date_property not in properties:
                raise ValueError(
                    f"'{config.date_property}' 날짜 속성을 찾을 수 없습니다."
                )
            date_property = properties[config.date_property]
            if date_property.get("type") != "date":
                raise ValueError(
                    f"'{config.date_property}' 속성은 date 타입이어야 합니다."
                )
            date_value = date_property.get("date")
            if not date_value or not date_value.get("start"):
                skipped += 1
                LOGGER.warning("날짜가 비어 있어 건너뜁니다 (페이지 %s).", page_id)
                continue
            date_str = date.fromisoformat(date_value["start"][:10]).isoformat()
            title = page_title(page, config.title_property, client)
            path = store.path_for(page_id, title, date_str)
            page_url = page.get("url") or notion_url(page_id)
            with AssetStore(path, page_id) as assets:
                renderer = MarkdownRenderer(
                    client.get_block_children,
                    media_url=assets.media_url,
                    page_url=page_url,
                )
                body = renderer.render(client.get_block_children(page_id))
                changed = store.save(page_id, title, date_str, page_url, body, path)
            saved += 1
            LOGGER.info(
                "%s: %s",
                "저장" if changed else "변경 없음",
                path.relative_to(config.root),
            )
        except Exception as exc:
            failed += 1
            LOGGER.error("페이지 %s 처리 실패: %s", page_id, exc)
    if failed:
        raise RuntimeError(
            f"{failed}개 페이지 동기화 실패. README를 갱신하지 않았습니다."
        )
    update_readme(config.root, reset=config.reset_readme)
    LOGGER.info("동기화 완료: 처리 %d개, 날짜 없음 %d개", saved, skipped)
    return saved


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        config = Config.from_env()
        with NotionClient(config.token) as client:
            sync(config, client)
    except Exception as exc:
        LOGGER.error("동기화 중단: %s", exc)
        return 1
    return 0

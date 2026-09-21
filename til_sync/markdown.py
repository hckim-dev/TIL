"""Render Notion's block tree as portable GitHub Markdown.

Layout-only features (columns, colors and interactive embeds) have readable
fallbacks. Content the Notion API cannot expose gets a visible source link.
"""

import html
import logging
import re
from collections.abc import Callable
from urllib.parse import quote

LOGGER = logging.getLogger(__name__)
LIST_TYPES = {"bulleted_list_item", "numbered_list_item", "to_do"}
MEDIA_TYPES = {"image", "audio", "video", "pdf", "file"}
LANGUAGE_ALIASES = {
    "plain text": "text",
    "c++": "cpp",
    "c#": "csharp",
    "f#": "fsharp",
    "shell": "bash",
    "docker": "dockerfile",
    "markup": "html",
    "objective-c": "objectivec",
    "vb.net": "vbnet",
    "visual basic": "vbnet",
    "java/c/c++/c#": "text",
    "webassembly": "wasm",
}


def notion_url(identifier: str) -> str:
    return "https://www.notion.so/" + identifier.replace("-", "")


def escape_markdown(text: str) -> str:
    """Escape literal prose, while keeping source text reasonably readable."""
    text = html.escape(text, quote=False)
    text = re.sub(r"([\\`*_{}\[\]#!~$])", r"\\\1", text)
    text = re.sub(r"(?m)^(\s*)([-+])(?=\s|$)", r"\1\\\2", text)
    text = re.sub(r"(?m)^( {0,3})(-)(?=-{2,}\s*$)", r"\1\\\2", text)
    return re.sub(r"(?m)^(\s*\d+)([.)])(?=\s)", r"\1\\\2", text)


def _mention_text(mention: dict) -> str:
    kind = mention.get("type", "")
    value = mention.get(kind, {})
    if kind == "date":
        return " → ".join(str(value[key]) for key in ("start", "end") if value.get(key))
    if kind == "user":
        return "@" + (value.get("name") or "Anonymous")
    if kind == "template_mention":
        return "@" + value.get(value.get("type", ""), "template")
    if kind in {"page", "database"}:
        return value.get("title") or kind
    if kind == "custom_emoji":
        return ":" + value.get("name", "emoji") + ":"
    return value.get("url") or value.get("name") or "@" + (kind or "mention")


def _text_value(item: dict) -> str:
    if "plain_text" in item:
        return item["plain_text"] or ""
    kind = item.get("type", "text")
    if kind == "text":
        return item.get("text", {}).get("content", "")
    if kind == "equation":
        return item.get("equation", {}).get("expression", "")
    if kind == "mention":
        return _mention_text(item.get("mention", {}))
    return item.get(kind, {}).get("name", "[" + kind + "]")


def plain_text(rich_text: list[dict]) -> str:
    """Extract unformatted text; in particular, never add markup to code."""
    return "".join(_text_value(item) for item in rich_text)


def _url(value: str) -> str:
    return quote(value, safe="/:#?&=@!$'+,;%~-._")


def _link(label: str, url: str) -> str:
    return f"[{label}]({_url(url)})" if url else label


def _inline_code(text: str) -> str:
    fence = "`" * (max((len(run) for run in re.findall(r"`+", text)), default=0) + 1)
    padding = (
        " "
        if text.startswith("`")
        or text.endswith("`")
        or (text.startswith(" ") and text.endswith(" ") and text.strip())
        else ""
    )
    return fence + padding + text.replace("\n", " ") + padding + fence


def _rich_text(rich_text: list[dict], html_mode: bool = False) -> str:
    # The API may split a styled run into multiple objects (for example, at
    # its text length limit). Adjacent **runs****like this** break emphasis.
    runs = []
    for item in rich_text:
        if (
            runs
            and item.get("type", "text") == runs[-1].get("type", "text") == "text"
            and (
                item.get("annotations", {}) == runs[-1].get("annotations", {})
                and item.get("href") == runs[-1].get("href")
                and item.get("text", {}).get("link")
                == runs[-1].get("text", {}).get("link")
            )
        ):
            runs[-1]["plain_text"] = _text_value(runs[-1]) + _text_value(item)
        else:
            runs.append(dict(item))
    result = []
    for index, item in enumerate(runs):
        raw = _text_value(item).replace("\r\n", "\n").replace("\r", "\n")
        annotations = item.get("annotations", {})
        if item.get("type") == "equation":
            expression = item.get("equation", {}).get("expression", raw)
            content = "$" + expression + "$"
            if html_mode:
                content = html.escape(content)
        elif annotations.get("code"):
            content = (
                "<code>" + html.escape(raw) + "</code>"
                if html_mode
                else _inline_code(raw)
            )
        else:
            content = html.escape(raw) if html_mode else escape_markdown(raw)
            content = content.replace("\n", "<br>")

        # A styled punctuation span inside a word, e.g. x**(y)**z, is not
        # emphasis in CommonMark. Inline HTML preserves these boundaries.
        previous = _text_value(runs[index - 1]) if index else ""
        following = _text_value(runs[index + 1]) if index + 1 < len(runs) else ""
        boundary_html = bool(
            content
            and (
                (previous and not previous[-1].isspace() and not content[0].isalnum())
                or (
                    following
                    and not following[0].isspace()
                    and not content[-1].isalnum()
                )
            )
        )

        for annotation, markdown_tag, html_tag in (
            ("bold", "**", "strong"),
            ("italic", "*", "em"),
            ("strikethrough", "~~", "del"),
            ("underline", "", "ins"),
        ):
            if annotations.get(annotation) and content.strip():
                # Markdown emphasis must not start/end with whitespace.
                leading = content[: len(content) - len(content.lstrip())]
                trailing = content[len(content.rstrip()) :]
                core = content.strip()
                if html_mode or boundary_html or annotation == "underline":
                    core = f"<{html_tag}>{core}</{html_tag}>"
                else:
                    core = markdown_tag + core + markdown_tag
                content = leading + core + trailing

        href = item.get("href") or (item.get("text", {}).get("link") or {}).get("url")
        mention = item.get("mention", {})
        kind = mention.get("type")
        if kind == "custom_emoji" and mention[kind].get("url"):
            emoji = mention[kind]
            if html_mode:
                content = f'<img alt="{html.escape(raw, quote=True)}" src="{html.escape(_url(emoji["url"]), quote=True)}">'
            else:
                content = "!" + _link(escape_markdown(raw), emoji["url"])
        if not href and kind in {"page", "database"}:
            identifier = mention[kind].get("id")
            href = notion_url(identifier) if identifier else None
        if not href and kind == "link_preview":
            href = mention[kind].get("url")
        if href:
            if html_mode:
                content = (
                    f'<a href="{html.escape(_url(href), quote=True)}">{content}</a>'
                )
            else:
                content = _link(content, href)
        result.append(content)
    return "".join(result)


def render_rich_text(rich_text: list[dict]) -> str:
    return _rich_text(rich_text)


class MarkdownRenderer:
    def __init__(
        self,
        fetch_children: Callable[[str], list[dict]],
        media_url: Callable[[dict, dict], str] | None = None,
        page_url: str = "",
    ):
        self.fetch_children = fetch_children
        self.media_url = media_url
        self.page_url = page_url
        self._active_ids: set[str] = set()
        self._headings: list[tuple[int, str, str]] = []
        self._anchors: dict[str, int] = {}

    def render(self, blocks: list[dict]) -> str:
        """Render a whole page. Network/content errors intentionally propagate."""
        self._active_ids.clear()
        self._headings.clear()
        self._anchors.clear()
        content = self._render_blocks(blocks)
        # Delayed TOC insertion includes headings nested in columns/toggles.
        toc = self._table_of_contents()
        content = re.sub(
            r"(?m)^([ >]*)\x00NOTION_TOC\x00$",
            lambda match: "\n".join(match[1] + line for line in toc.split("\n")),
            content,
        )
        return content.rstrip() + "\n" if content else ""

    def _children(self, block: dict) -> list[dict]:
        payload = block.get(block.get("type"), {})
        children = payload.get("children")
        if isinstance(children, list):
            return children
        if block.get("has_children"):
            return self.fetch_children(block["id"])
        return []

    def _render_blocks(self, blocks: list[dict]) -> str:
        parts = []
        previous_kind = None
        number = 0
        for block in blocks:
            if block.get("archived") or block.get("in_trash"):
                continue
            kind = block.get("type", "unsupported")
            number = number + 1 if kind == previous_kind == "numbered_list_item" else 1
            content = self._render_block(block, number)
            if not content:
                continue
            if parts:
                if kind in LIST_TYPES and kind == previous_kind:
                    separator = "\n"
                elif kind in LIST_TYPES and previous_kind in LIST_TYPES:
                    # Bullet and checkbox items otherwise merge into one list.
                    separator = "\n\n<!-- list break -->\n\n"
                else:
                    separator = "\n\n"
                parts.append(separator)
            parts.append(content)
            previous_kind = kind
        return "".join(parts)

    def _render_block(self, block: dict, number: int) -> str:
        identifier = block.get("id")
        if identifier and identifier in self._active_ids:
            return self._fallback(block, "순환 참조")
        if identifier:
            self._active_ids.add(identifier)
        try:
            return self._render_content(block, number)
        finally:
            if identifier:
                self._active_ids.remove(identifier)

    def _with_children(self, content: str, block: dict) -> str:
        children = self._render_blocks(self._children(block))
        return "\n\n".join(part for part in (content, children) if part)

    def _render_content(self, block: dict, number: int) -> str:
        kind = block.get("type", "unsupported")
        payload = block.get(kind, {})
        rich_text = payload.get("rich_text", [])
        text = render_rich_text(rich_text)

        if kind == "paragraph":
            icon = self._icon(block, payload.get("icon"))
            return self._with_children(
                " ".join(filter(None, (icon, text))) or "<br>", block
            )
        if kind in LIST_TYPES:
            marker = f"{number}. " if kind == "numbered_list_item" else "- "
            checkbox = (
                ("[x] " if payload.get("checked") else "[ ] ")
                if kind == "to_do"
                else ""
            )
            content = marker + checkbox + text
            children = self._render_blocks(self._children(block))
            if children:
                content += "\n\n" + self._indent(children, len(marker))
            return content
        if kind in {"heading_1", "heading_2", "heading_3", "heading_4"}:
            level = int(kind[-1])
            anchor = self._heading_anchor(block, level, plain_text(rich_text))
            if payload.get("is_toggleable"):
                summary = f"<strong>{_rich_text(rich_text, html_mode=True)}</strong>"
                return (
                    anchor
                    + "\n\n"
                    + self._details(summary, self._render_blocks(self._children(block)))
                )
            return (
                anchor + "\n\n" + self._with_children("#" * level + " " + text, block)
            )
        if kind in {"toggle", "template"}:
            return self._details(
                _rich_text(rich_text, html_mode=True) or "내용",
                self._render_blocks(self._children(block)),
            )
        if kind in {"quote", "callout"}:
            if kind == "callout":
                text = " ".join(
                    filter(None, (self._icon(block, payload.get("icon")), text))
                )
            return "\n".join(
                "> " + line if line else ">"
                for line in self._with_children(text, block).split("\n")
            )
        if kind == "code":
            code = plain_text(rich_text)
            fence = "`" * max(
                3, max((len(run) + 1 for run in re.findall(r"`+", code)), default=0)
            )
            language = payload.get("language", "text")
            language = LANGUAGE_ALIASES.get(language, language)
            if not re.fullmatch(r"[\w+#.-]+", language):
                language = "text"
            content = (
                f"{fence}{language}\n{code}"
                + ("" if code.endswith("\n") else "\n")
                + fence
            )
            return self._with_caption(content, payload)
        if kind == "equation":
            return "$$\n" + payload.get("expression", "") + "\n$$"
        if kind == "divider":
            return "---"
        if kind in MEDIA_TYPES:
            url = self._media_url(block, payload)
            if not url:
                return self._fallback(block, kind + " 파일 URL 없음")
            label = (
                plain_text(payload.get("caption", []))
                if kind == "image"
                else payload.get("name")
            )
            label = escape_markdown(label or kind).replace("\n", " ")
            content = ("!" if kind == "image" else "") + _link(label, url)
            return self._with_caption(content, payload)
        if kind in {"bookmark", "embed", "link_preview"}:
            url = payload.get("url", "")
            if kind == "embed" and url and self.media_url:
                url = self.media_url(
                    block, {"type": "external", "external": {"url": url}}
                )
            content = _link(escape_markdown(payload.get("title") or url or kind), url)
            return self._with_caption(content, payload)
        if kind == "link_to_page":
            target_type = payload.get("type", "page_id")
            identifier = payload.get(target_type)
            return (
                _link(
                    "Notion " + target_type.removesuffix("_id"), notion_url(identifier)
                )
                if identifier
                else self._fallback(block, kind)
            )
        if kind in {"child_page", "child_database"}:
            content = _link(
                escape_markdown(payload.get("title") or kind), notion_url(block["id"])
            )
            # A database is queried through the database/data-source API, not
            # through the block-children endpoint. Keep its source link here.
            return (
                self._with_children(content, block) if kind == "child_page" else content
            )
        if kind == "table":
            return self._table(block)
        if kind == "table_row":
            return " | ".join(
                render_rich_text(cell) for cell in payload.get("cells", [])
            )
        if kind in {"column_list", "column", "tab"}:
            return self._render_blocks(self._children(block))
        if kind == "synced_block":
            source = (payload.get("synced_from") or {}).get("block_id")
            return (
                self._referenced_children(source, block)
                if source
                else self._render_blocks(self._children(block))
            )
        if kind in {"meeting_notes", "transcription"}:
            return self._meeting_notes(block)
        if kind == "table_of_contents":
            return "\x00NOTION_TOC\x00"
        if kind == "breadcrumb":
            return _link("Notion 페이지 경로", self._block_url(block))
        # Future types may still include readable text/children. Preserve both.
        fallback = self._fallback(block, payload.get("block_type") or kind)
        return self._with_children("\n\n".join(filter(None, (text, fallback))), block)

    @staticmethod
    def _indent(content: str, count: int) -> str:
        return "\n".join(
            " " * count + line if line else "" for line in content.split("\n")
        )

    @staticmethod
    def _details(summary: str, content: str) -> str:
        return f"<details>\n<summary>{summary}</summary>\n\n{content}\n\n</details>"

    @staticmethod
    def _with_caption(content: str, payload: dict) -> str:
        caption = render_rich_text(payload.get("caption", []))
        return content + ("\n\n" + caption if caption else "")

    def _media_url(self, block: dict, payload: dict) -> str:
        if self.media_url:
            return self.media_url(block, payload)
        return (payload.get("file") or payload.get("external") or {}).get("url", "")

    def _icon(self, block: dict, icon: dict | None) -> str:
        if not icon:
            return ""
        if icon.get("emoji"):
            return icon["emoji"]
        if "custom_emoji" in icon:
            emoji = icon["custom_emoji"]
            label = ":" + emoji.get("name", "emoji") + ":"
            if emoji.get("url"):
                icon_block = dict(block, id=block.get("id", "") + "-icon")
                url = self._media_url(
                    icon_block, {"type": "external", "external": {"url": emoji["url"]}}
                )
                return "!" + _link(escape_markdown(label), url)
            return label
        if icon.get("type") in {"file", "external"}:
            icon_block = dict(block, id=block.get("id", "") + "-icon")
            url = self._media_url(icon_block, icon)
            return "!" + _link("icon", url) if url else ""
        native = icon.get("icon") or {}
        return escape_markdown(native.get("name", ""))

    def _referenced_children(self, identifier: str, block: dict) -> str:
        if identifier in self._active_ids:
            return self._fallback(block, "순환 참조")
        self._active_ids.add(identifier)
        try:
            return self._render_blocks(self.fetch_children(identifier))
        finally:
            self._active_ids.remove(identifier)

    def _meeting_notes(self, block: dict) -> str:
        payload = block[block["type"]]
        title = payload.get("title", [])
        parts = (
            [
                "### "
                + (
                    render_rich_text(title)
                    if isinstance(title, list)
                    else escape_markdown(title)
                )
            ]
            if title
            else []
        )
        if payload.get("status"):
            parts.append("상태: " + escape_markdown(payload["status"]))
        event = payload.get("calendar_event") or payload.get("recording") or {}
        times = [event[key] for key in ("start_time", "end_time") if event.get(key)]
        if times:
            parts.append(" → ".join(times))
        sections = payload.get("children", {})
        if isinstance(sections, dict) and any(sections.values()):
            seen = set()
            for key, label in (
                ("summary_block_id", "요약"),
                ("notes_block_id", "메모"),
                ("transcript_block_id", "대화 기록"),
            ):
                identifier = sections.get(key)
                if identifier and identifier not in seen:
                    seen.add(identifier)
                    parts.append(
                        "#### "
                        + label
                        + "\n\n"
                        + self._referenced_children(identifier, block)
                    )
        else:
            parts.append(self._render_blocks(self._children(block)))
        return "\n\n".join(filter(None, parts)) or self._fallback(block, block["type"])

    def _table(self, block: dict) -> str:
        payload = block["table"]
        rows = []
        other_blocks = []
        for child in self._children(block):
            if child.get("archived") or child.get("in_trash"):
                continue
            if child.get("type") == "table_row":
                rows.append(
                    [
                        render_rich_text(cell).replace("|", "\\|").replace("\n", "<br>")
                        for cell in child["table_row"].get("cells", [])
                    ]
                )
            else:
                other_blocks.append(child)
        width = max([payload.get("table_width", 0)] + [len(row) for row in rows])
        if not width:
            return self._render_blocks(other_blocks)
        for row in rows:
            row.extend([""] * (width - len(row)))
            if payload.get("has_row_header") and row[0]:
                row[0] = "**" + row[0] + "**"
        header = (
            rows.pop(0) if rows and payload.get("has_column_header") else [""] * width
        )
        lines = [
            "| " + " | ".join(row) + " |" for row in [header, ["---"] * width, *rows]
        ]
        content = "\n".join(lines)
        other = self._render_blocks(other_blocks)
        return content + ("\n\n" + other if other else "")

    def _heading_anchor(self, block: dict, level: int, title: str) -> str:
        identifier = re.sub(r"[^a-zA-Z0-9_-]", "", block.get("id", "").replace("-", ""))
        base = "notion-" + (identifier or f"heading-{len(self._headings) + 1}")
        occurrence = self._anchors.get(base, 0) + 1
        self._anchors[base] = occurrence
        anchor = base if occurrence == 1 else f"{base}-{occurrence}"
        self._headings.append((level, title, anchor))
        return f'<a id="{anchor}"></a>'

    def _table_of_contents(self) -> str:
        minimum = min((level for level, _, _ in self._headings), default=1)
        return (
            "\n".join(
                "  " * (level - minimum)
                + "- "
                + _link(escape_markdown(title).replace("\n", " "), "#" + anchor)
                for level, title, anchor in self._headings
            )
            or "목차에 표시할 제목이 없습니다."
        )

    def _block_url(self, block: dict) -> str:
        identifier = block.get("id", "").replace("-", "")
        if self.page_url:
            return self.page_url.split("#", 1)[0] + (
                "#" + identifier if identifier else ""
            )
        return notion_url(identifier) if identifier else "https://www.notion.so"

    def _fallback(self, block: dict, reason: str) -> str:
        LOGGER.warning(
            "Notion block %s (%s) requires a source link",
            block.get("id", "unknown"),
            reason,
        )
        return "> " + _link(
            "Notion에서 확인: " + escape_markdown(reason), self._block_url(block)
        )

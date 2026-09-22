import unittest

from til_sync.markdown import (
    MarkdownRenderer,
    escape_markdown,
    plain_text,
    render_rich_text,
)


def rich(value, **annotations):
    return [{"type": "text", "text": {"content": value}, "annotations": annotations}]


def block(kind, text="", identifier=None, children=None, **payload):
    value = {"rich_text": rich(text), **payload}
    if children is not None:
        value["children"] = children
    result = {"type": kind, kind: value, "has_children": children is not None}
    if identifier:
        result["id"] = identifier
    return result


class RichTextTests(unittest.TestCase):
    def test_literal_text_code_links_annotations_and_mentions(self):
        content = rich(" 배열[0] * 2 ", bold=True, italic=True, underline=True)
        content += rich(" a`b ", code=True)
        content += [
            {
                "type": "mention",
                "mention": {"type": "page", "page": {"id": "ab-cd"}},
                "plain_text": "참고[문서]",
            }
        ]
        content += [
            {
                "type": "mention",
                "mention": {
                    "type": "date",
                    "date": {"start": "2026-09-20", "end": "2026-09-22"},
                },
            }
        ]
        content += [
            {"type": "mention", "mention": {"type": "user", "user": {"name": "홍길동"}}}
        ]
        content += [{"type": "equation", "equation": {"expression": r"a_1 + \alpha"}}]
        rendered = render_rich_text(content)
        self.assertIn(r" <ins>***배열\[0\] \* 2***</ins> ", rendered)
        self.assertIn("``  a`b  ``", rendered)
        self.assertIn(r"[참고\[문서\]](https://www.notion.so/abcd)", rendered)
        self.assertIn("2026-09-20 → 2026-09-22@홍길동", rendered)
        self.assertIn(r"$a_1 + \alpha$", rendered)
        self.assertEqual(plain_text(rich('ptr[0] = "**hi**";')), 'ptr[0] = "**hi**";')

    def test_literal_html_newlines_and_difficult_links(self):
        content = rich("<script> x & y\n1. item")
        content[0]["text"]["link"] = {"url": "https://example.org/a(b)?q=one two"}
        self.assertEqual(
            render_rich_text(content),
            r"[&lt;script&gt; x &amp; y<br>1\. item](https://example.org/a%28b%29?q=one%20two)",
        )
        self.assertEqual(
            escape_markdown("- literal\n# literal"), "\\- literal\n\\# literal"
        )
        self.assertEqual(escape_markdown("---"), "\\---")

    def test_split_styled_runs_do_not_create_ambiguous_delimiters(self):
        content = rich("Hel", bold=True) + rich("lo", bold=True)
        self.assertEqual(render_rich_text(content), "**Hello**")
        self.assertEqual(
            render_rich_text(rich("x") + rich("(y)", bold=True) + rich("z")),
            "x<strong>(y)</strong>z",
        )
        self.assertEqual(render_rich_text(rich("$5")), r"\$5")
        self.assertNotIn(
            "plain_text", content[0]
        )  # Rendering does not mutate API objects.

    def test_inline_custom_emoji_uses_the_returned_url(self):
        emoji = {
            "type": "mention",
            "mention": {
                "type": "custom_emoji",
                "custom_emoji": {"name": "bufo", "url": "https://example.org/bufo.png"},
            },
        }
        self.assertEqual(
            render_rich_text([emoji]), "![:bufo:](https://example.org/bufo.png)"
        )


class MarkdownRendererTests(unittest.TestCase):
    def renderer(self, children=None, media_url=None):
        mapping = children or {}
        self.fetches = []

        def fetch(identifier):
            self.fetches.append(identifier)
            return mapping[identifier]

        return MarkdownRenderer(fetch, media_url, page_url="https://www.notion.so/page")

    def test_nested_lists_preserve_numbering_and_list_boundaries(self):
        blocks = [
            block(
                "numbered_list_item",
                "첫째",
                children=[
                    block("paragraph", "설명"),
                    block(
                        "bulleted_list_item",
                        "자식",
                        children=[block("to_do", "완료", checked=True)],
                    ),
                ],
            ),
            block("numbered_list_item", "둘째"),
            block("bulleted_list_item", "독립 목록"),
            block("to_do", "할 일", checked=False),
            block("paragraph", "구분"),
            block("numbered_list_item", "다시 시작"),
        ]
        result = self.renderer().render(blocks)
        self.assertEqual(
            result,
            """1. 첫째

   설명

   - 자식

     - [x] 완료
2. 둘째

<!-- list break -->

- 독립 목록

<!-- list break -->

- [ ] 할 일

구분

1. 다시 시작
""",
        )

    def test_code_is_raw_and_fence_cannot_be_closed_by_its_contents(self):
        source = 'char *ptr = "a_b";\n```\n[link](bad)\n'
        code = block(
            "code", source, language="c++", caption=rich("포인터 예제", italic=True)
        )
        code["code"]["rich_text"][0]["annotations"] = {"bold": True}
        code["code"]["rich_text"][0]["href"] = "https://example.org"
        self.assertEqual(
            self.renderer().render([code]),
            "````cpp\n" + source + "````\n\n*포인터 예제*\n",
        )

    def test_code_languages_preserve_tags_indentation_and_literal_source(self):
        cpp_source = (
            "#include <vector>\n"
            "void append(std::vector<int>& values) {\n"
            "    values.push_back(1);\n"
            "}\n"
        )
        plain_source = "  *not emphasis* [label](url)\n\t<raw> & $value\n"
        cases = [
            (
                "c",
                "c",
                "#include <stdint.h>\n"
                "uint8_t read_value(const uint8_t *buffer) {\n"
                "    return buffer[0] & 0x0F;\n"
                "}\n",
            ),
            ("c++", "cpp", cpp_source),
            ("cpp", "cpp", cpp_source),
            (
                "python",
                "python",
                'def describe(values):\n    return f"value={values[0]}_ready"\n',
            ),
            (
                "bash",
                "bash",
                'if [ "$status" -eq 0 ]; then\n\tprintf "%s\\n" "$value" # log\nfi\n',
            ),
            ("plaintext", "text", plain_source),
            ("plain text", "text", plain_source),
            (
                "verilog",
                "verilog",
                "`define WIDTH 8\n"
                "module counter(input wire clk, output reg [`WIDTH-1:0] count);\n"
                "    always @(posedge clk) begin\n"
                "        count <= count + 1'b1;\n"
                "    end\n"
                "endmodule\n",
            ),
        ]
        renderer = self.renderer()
        for language, expected_tag, source in cases:
            with self.subTest(language=language):
                result = renderer.render([block("code", source, language=language)])
                self.assertEqual(result, f"```{expected_tag}\n{source}```\n")

    def test_recursive_api_children_columns_toggles_quotes_and_toc(self):
        children = {
            "columns": [block("column", identifier="column", children=[])],
            "nested": [
                block(
                    "heading_4",
                    "레지스터",
                    identifier="heading",
                    is_toggleable=True,
                    children=[
                        block(
                            "quote", "주의", children=[block("paragraph", "중첩 내용")]
                        ),
                    ],
                )
            ],
        }
        # API responses omit embedded children; use the has_children flag.
        children["columns"][0]["column"].pop("children")
        children["column"] = [
            block(
                "toggle",
                identifier="nested",
                children=[],
                rich_text=rich("토글 <내용>", bold=True),
            )
        ]
        children["column"][0]["toggle"].pop("children")
        columns = block("column_list", identifier="columns", children=[])
        columns["column_list"].pop("children")
        result = self.renderer(children).render([block("table_of_contents"), columns])
        self.assertIn("- [레지스터](#notion-heading)", result)
        self.assertIn('<a id="notion-heading"></a>', result)
        self.assertIn("<summary><strong>토글 &lt;내용&gt;</strong></summary>", result)
        self.assertIn("<summary><strong>레지스터</strong></summary>", result)
        self.assertIn("> 주의\n>\n> 중첩 내용", result)
        self.assertEqual(self.fetches, ["columns", "column", "nested"])

    def test_toc_handles_leading_deep_headings_and_skipped_levels(self):
        blocks = [block("table_of_contents")]
        blocks.extend(
            [
                block("heading_4", "먼저 나온 상세 내용", identifier="first"),
                block("heading_1", "주제", identifier="topic"),
                block("heading_4", "상세 내용", identifier="detail"),
                block("heading_2", "다음 내용", identifier="next"),
            ]
        )
        result = self.renderer().render(blocks)
        self.assertEqual(
            result.split("\n\n", 1)[0],
            "- [먼저 나온 상세 내용](#notion-first)\n"
            "- [주제](#notion-topic)\n"
            "  - [상세 내용](#notion-detail)\n"
            "  - [다음 내용](#notion-next)",
        )

    def test_tables_keep_first_data_row_when_there_is_no_column_header(self):
        table = block(
            "table",
            table_width=2,
            has_column_header=False,
            has_row_header=True,
            children=[
                block("table_row", cells=[rich("키"), rich("a | b\n둘째 줄")]),
                block("table_row", cells=[rich("값"), rich("x | y", code=True)]),
            ],
        )
        self.assertEqual(
            self.renderer().render([table]),
            r"""|  |  |
| --- | --- |
| **키** | a \| b<br>둘째 줄 |
| **값** | `x \| y` |
""",
        )
        table["table"]["has_column_header"] = True
        result = self.renderer().render([table])
        self.assertTrue(
            result.startswith("| **키** | a \\| b<br>둘째 줄 |\n| --- | --- |")
        )
        self.assertEqual(result.count("**키**"), 1)

    def test_media_callbacks_captions_links_and_database_boundary(self):
        seen = []

        def media_url(item, payload):
            seen.append((item["id"], payload))
            return "assets/" + item["id"] + ".png"

        blocks = [
            block(
                "image",
                identifier="image",
                type="file",
                file={"url": "https://signed-url"},
                caption=rich("회로[도]"),
            )
        ]
        blocks += [
            block(
                "callout",
                "메모",
                identifier="callout",
                icon={"type": "file", "file": {"url": "https://icon"}},
            )
        ]
        blocks += [block("embed", identifier="embed", url="https://notion-file")]
        blocks += [
            block("child_database", identifier="database", title="표", children=[])
        ]
        renderer = self.renderer(media_url=media_url)
        result = renderer.render(blocks)
        self.assertIn(r"![회로\[도\]](assets/image.png)", result)
        self.assertIn(r"회로\[도\]", result)
        self.assertIn("> ![icon](assets/callout-icon.png) 메모", result)
        self.assertIn("(assets/embed.png)", result)
        self.assertIn("[표](https://www.notion.so/database)", result)
        self.assertEqual(
            [identifier for identifier, _ in seen], ["image", "callout-icon", "embed"]
        )
        self.assertEqual(self.fetches, [])

    def test_custom_and_native_callout_icons_have_readable_fallbacks(self):
        seen = []

        def media_url(item, payload):
            seen.append((item["id"], payload["external"]["url"]))
            return "assets/emoji.png"

        items = [
            block(
                "callout",
                "회의",
                identifier="custom",
                icon={
                    "type": "custom_emoji",
                    "custom_emoji": {
                        "name": "bufo",
                        "url": "https://example.org/bufo.png",
                    },
                },
            ),
            block(
                "callout",
                "식사",
                icon={"type": "icon", "icon": {"name": "pizza", "color": "blue"}},
            ),
        ]
        result = self.renderer(media_url=media_url).render(items)
        self.assertIn("> ![:bufo:](assets/emoji.png) 회의", result)
        self.assertIn("> pizza 식사", result)
        self.assertEqual(seen, [("custom-icon", "https://example.org/bufo.png")])

    def test_synced_blocks_repeat_content_but_stop_cyclic_references(self):
        copy = block(
            "synced_block", identifier="copy", synced_from={"block_id": "source"}
        )
        renderer = self.renderer({"source": [block("paragraph", "공통 내용")]})
        self.assertEqual(renderer.render([copy, copy]), "공통 내용\n\n공통 내용\n")
        cyclic = block(
            "synced_block", identifier="cycle", synced_from={"block_id": "source"}
        )
        renderer = self.renderer({"source": [cyclic]})
        with self.assertLogs("til_sync.markdown", level="WARNING"):
            result = renderer.render([copy])
        self.assertIn("순환 참조", result)
        self.assertEqual(self.fetches, ["source"])

    def test_unknown_blocks_preserve_text_children_and_source_link(self):
        unknown = block(
            "future_widget",
            "위젯 텍스트",
            identifier="unknown",
            children=[block("paragraph", "자식")],
        )
        renderer = self.renderer()
        with self.assertLogs("til_sync.markdown", level="WARNING"):
            result = renderer.render(
                [
                    unknown,
                    {
                        "type": "unsupported",
                        "id": "button",
                        "unsupported": {"block_type": "button"},
                    },
                ]
            )
        self.assertIn("위젯 텍스트", result)
        self.assertIn("자식", result)
        self.assertIn(
            r"[Notion에서 확인: future\_widget](https://www.notion.so/page#unknown)",
            result,
        )
        self.assertIn(
            "[Notion에서 확인: button](https://www.notion.so/page#button)", result
        )

    def test_meeting_notes_render_section_content_and_legacy_name(self):
        renderer = self.renderer(
            {
                "summary": [block("paragraph", "학습 요약")],
                "notes": [block("paragraph", "상세 기록")],
            }
        )
        for kind in ("meeting_notes", "transcription"):
            note = block(kind, title=rich("학습 회의"), status="notes_ready")
            note[kind]["children"] = {
                "summary_block_id": "summary",
                "notes_block_id": "notes",
            }
            result = renderer.render([note])
            self.assertIn("### 학습 회의", result)
            self.assertIn("#### 요약\n\n학습 요약", result)
            self.assertIn("#### 메모\n\n상세 기록", result)

    def test_fetch_failures_are_not_converted_to_empty_content(self):
        def fail(_):
            raise RuntimeError("permission denied")

        item = block("paragraph", "부모", identifier="parent", children=[])
        item["paragraph"].pop("children")
        with self.assertRaisesRegex(RuntimeError, "permission denied"):
            MarkdownRenderer(fail).render([item])


if __name__ == "__main__":
    unittest.main()

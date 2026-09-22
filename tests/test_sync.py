import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock, patch

from til_sync.config import Config, FetchMode
from til_sync.notion import NotionAPIError
from til_sync.storage import PageStore, sanitize_filename, scan_entries, update_readme
from til_sync.sync import SyncError, main, sync

PAGE_ID = "11111111-1111-1111-1111-111111111111"
OTHER_ID = "22222222-2222-2222-2222-222222222222"


def make_page(page_id=PAGE_ID, title="학습_기록 [C]", day="2026-09-21"):
    return {
        "id": page_id,
        "url": f"https://www.notion.so/{page_id.replace('-', '')}",
        "properties": {
            "제목": {
                "type": "title",
                "title": [
                    {"type": "text", "text": {"content": title[:3]}},
                    {"type": "text", "text": {"content": title[3:]}},
                ],
            },
            "날짜": {"type": "date", "date": {"start": day} if day else None},
        },
    }


class ConfigTests(unittest.TestCase):
    def test_kst_previous_day_across_utc_midnight(self):
        env = {"NOTION_TOKEN": "private", "NOTION_DATABASE_ID": "db"}
        now = datetime(2026, 9, 21, 15, 5, tzinfo=UTC)
        config = Config.from_env(env, now=now)
        self.assertEqual(config.target_date, "2026-09-21")
        self.assertIs(config.fetch_mode, FetchMode.DAILY)
        self.assertNotIn("private", repr(config))
        self.assertEqual(Config.from_env(dict(env, FETCH_MODE="ALL")).target_date, None)
        self.assertEqual(
            Config.from_env(dict(env, TARGET_DATE="2026-08-01")).target_date,
            "2026-08-01",
        )

    def test_bad_configuration_fails_before_network(self):
        base = {"NOTION_TOKEN": "t", "NOTION_DATABASE_ID": "d"}
        for overrides in (
            {"NOTION_TOKEN": ""},
            {"FETCH_MODE": "typo"},
            {"TARGET_DATE": "2026-02-30"},
            {"TARGET_DATE": "20260921"},
            {"RESET_MODE": "yes"},
            {"FETCH_MODE": "ALL", "TARGET_DATE": "2026-09-21"},
        ):
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                Config.from_env(dict(base, **overrides))

    def test_environment_mode_is_normalized_to_enum(self):
        config = Config.from_env(
            {
                "NOTION_TOKEN": "token",
                "NOTION_DATA_SOURCE_ID": "source",
                "FETCH_MODE": " all ",
                "NOTION_PROPERTY_TITLE": "Name",
                "NOTION_PROPERTY_DATE": "Date",
            }
        )
        self.assertIs(config.fetch_mode, FetchMode.ALL)
        self.assertEqual(str(config.fetch_mode), "ALL")
        self.assertIsNone(config.target_date)
        self.assertEqual(
            (config.title_property, config.date_property), ("Name", "Date")
        )


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.config = Config(
            token="t", database_id="db", fetch_mode=FetchMode.ALL, root=self.root
        )
        self.client = Mock()
        self.client.resolve_data_source.return_value = "source"
        self.client.query_pages.return_value = [make_page()]
        self.client.get_block_children.return_value = [
            {
                "id": "paragraph",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "text": {"content": "코드와 포인터"},
                            "annotations": {"bold": True},
                        }
                    ]
                },
            }
        ]

    def test_export_index_and_idempotent_rerun(self):
        self.assertEqual(sync(self.config, self.client), 1)
        entries = scan_entries(self.root / "TIL")
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].title, "학습_기록 [C]")
        self.assertIn("**코드와 포인터**", entries[0].path.read_text(encoding="utf-8"))
        index = (self.root / "README.md").read_text(encoding="utf-8")
        self.assertIn(r"학습\_기록 \[C\]", index)
        before = {
            p: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.root.rglob("*.md")
        }
        sync(self.config, self.client)
        self.assertEqual(
            before,
            {
                p: (p.read_bytes(), p.stat().st_mtime_ns)
                for p in self.root.rglob("*.md")
            },
        )

    def test_failure_keeps_old_page_and_readme_and_fails_run(self):
        sync(self.config, self.client)
        before = {p: p.read_bytes() for p in self.root.rglob("*.md")}
        self.client.get_block_children.side_effect = NotionAPIError("fetch failed")
        with self.assertRaisesRegex(SyncError, "1개 페이지"):
            sync(self.config, self.client)
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob("*.md")})

    def test_unexpected_programming_error_is_not_hidden_as_page_failure(self):
        sync(self.config, self.client)
        before = {p: p.read_bytes() for p in self.root.rglob("*.md")}
        self.client.get_block_children.side_effect = TypeError("unexpected bug")
        with self.assertRaisesRegex(TypeError, "unexpected bug"):
            sync(self.config, self.client)
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob("*.md")})

    def test_expected_page_failure_continues_other_pages_but_fails_run(self):
        self.client.query_pages.return_value = [make_page(), make_page(OTHER_ID)]
        self.client.get_block_children.side_effect = [NotionAPIError("offline"), []]
        with self.assertRaisesRegex(SyncError, "1개 페이지"):
            sync(self.config, self.client)
        entries = scan_entries(self.root / "TIL")
        self.assertEqual(
            [entry.page_id for entry in entries], [OTHER_ID.replace("-", "")]
        )
        self.assertFalse((self.root / "README.md").exists())

    def test_empty_date_skipped_but_missing_column_fails(self):
        self.client.query_pages.return_value = [make_page(day=None)]
        self.assertEqual(sync(self.config, self.client), 0)
        self.client.get_block_children.assert_not_called()
        page = make_page()
        del page["properties"]["날짜"]
        self.client.query_pages.return_value = [page]
        with self.assertRaises(RuntimeError):
            sync(self.config, self.client)

    def test_wrong_property_types_do_not_silently_skip_content(self):
        page = make_page()
        page["properties"]["날짜"] = {"type": "rich_text", "rich_text": []}
        self.client.query_pages.return_value = [page]
        with self.assertRaises(RuntimeError):
            sync(self.config, self.client)
        page = make_page()
        page["properties"]["Actual title"] = page["properties"]["제목"]
        page["properties"]["제목"] = {"type": "rich_text", "rich_text": []}
        self.client.query_pages.return_value = [page]
        sync(self.config, self.client)
        self.assertEqual(scan_entries(self.root / "TIL")[0].title, "학습_기록 [C]")

    def test_case_only_title_change_keeps_page_on_case_insensitive_filesystems(self):
        self.client.query_pages.return_value = [make_page(title="lower")]
        sync(self.config, self.client)
        self.client.query_pages.return_value = [make_page(title="LOWER")]
        sync(self.config, self.client)
        entries = scan_entries(self.root / "TIL")
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].title, "LOWER")

    def test_title_and_date_change_move_only_the_same_notion_page(self):
        sync(self.config, self.client)
        old = scan_entries(self.root / "TIL")[0].path
        self.client.query_pages.return_value = [
            make_page(title="새 제목", day="2026-10-01")
        ]
        sync(self.config, self.client)
        self.assertFalse(old.exists())
        entries = scan_entries(self.root / "TIL")
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].title, "새 제목")
        self.assertEqual(entries[0].path.parent.name, "10")

    def test_sanitized_title_collision_does_not_overwrite_other_page(self):
        self.client.query_pages.return_value = [
            make_page(title="A/B"),
            make_page(OTHER_ID, "AB"),
        ]
        sync(self.config, self.client)
        entries = scan_entries(self.root / "TIL")
        self.assertEqual({entry.title for entry in entries}, {"A/B", "AB"})
        self.assertEqual(len(entries), 2)

    def test_legacy_page_is_recognized_from_its_source_link(self):
        path = self.root / "TIL/2026/09/2026-09-21_old.md"
        path.parent.mkdir(parents=True)
        path.write_text(
            f"# Old\n\n> 날짜: 2026-09-21\n> 원본 노션: [링크](https://app.notion.com/p/Old-{PAGE_ID.replace('-', '')})\n",
            encoding="utf-8",
        )
        sync(self.config, self.client)
        self.assertFalse(path.exists())
        self.assertEqual(len(scan_entries(self.root / "TIL")), 1)

    def test_paginated_title_and_title_property_rename(self):
        page = make_page()
        page["properties"]["Name"] = page["properties"].pop("제목")
        prop = page["properties"]["Name"]
        prop.update(id="title", title=[{"plain_text": "x"}] * 25)
        self.client.iter_page_property_items.return_value = [
            {"type": "title", "title": {"plain_text": str(i)}} for i in range(30)
        ]
        self.client.query_pages.return_value = [page]
        sync(self.config, self.client)
        self.assertEqual(
            scan_entries(self.root / "TIL")[0].title, "".join(map(str, range(30)))
        )

    def test_entrypoint_returns_failure_on_config_error(self):
        with (
            patch.dict("os.environ", {}, clear=True),
            patch("til_sync.sync.NotionClient") as client,
        ):
            self.assertEqual(main(), 1)
            client.assert_not_called()


class StorageTests(unittest.TestCase):
    def test_readme_preserves_custom_text_and_rejects_broken_markers(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            readme = root / "README.md"
            readme.write_text("# My intro\n", encoding="utf-8")
            update_readme(root)
            self.assertTrue(
                readme.read_text(encoding="utf-8").startswith("# My intro\n")
            )
            readme.write_text("Intro\n<!-- TIL_LIST_START -->\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                update_readme(root)
            self.assertEqual(
                readme.read_text(encoding="utf-8"), "Intro\n<!-- TIL_LIST_START -->\n"
            )
            update_readme(root, reset=True)
            self.assertIn("<!-- TIL_LIST_END -->", readme.read_text(encoding="utf-8"))

    def test_empty_and_long_titles_have_portable_names(self):
        self.assertEqual(sanitize_filename('/:*?"<>|'), "제목없음")
        self.assertLessEqual(len(sanitize_filename("한" * 300).encode()), 180)
        self.assertNotIn("\n", sanitize_filename("hello\nworld"))

    def test_unknown_existing_file_is_preserved_on_collision(self):
        with tempfile.TemporaryDirectory() as directory:
            store = PageStore(Path(directory))
            path = store.path_for(PAGE_ID, "name", "2026-09-21")
            path.parent.mkdir(parents=True)
            path.write_text("manually maintained", encoding="utf-8")
            second = store.path_for(PAGE_ID, "name", "2026-09-21")
            self.assertNotEqual(path, second)
            self.assertEqual(path.read_text(), "manually maintained")

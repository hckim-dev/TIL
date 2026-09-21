"""Notion API regressions, using fake HTTP responses without network or sleeps."""

import unittest
from unittest.mock import Mock, patch

import requests

from til_sync.notion import API_VERSION, MAX_ATTEMPTS, NotionAPIError, NotionClient


def response(data, status=200, headers=None):
    result = Mock(status_code=status, headers=headers or {})
    if isinstance(data, Exception):
        result.json.side_effect = data
    else:
        result.json.return_value = data
    return result


def page(results, *, has_more=False, cursor=None):
    return {"results": results, "has_more": has_more, "next_cursor": cursor}


class NotionClientTests(unittest.TestCase):
    def setUp(self):
        self.session = Mock(headers={})
        session_patch = patch(
            "til_sync.notion.requests.Session", return_value=self.session
        )
        session_patch.start()
        self.addCleanup(session_patch.stop)
        sleep_patch = patch("til_sync.notion.time.sleep")
        self.sleep = sleep_patch.start()
        self.addCleanup(sleep_patch.stop)
        # An advancing clock makes pacing independent of fake HTTP call speed.
        monotonic_patch = patch(
            "til_sync.notion.time.monotonic", side_effect=range(1000)
        )
        monotonic_patch.start()
        self.addCleanup(monotonic_patch.stop)
        jitter_patch = patch("til_sync.notion.random.uniform", return_value=0.0)
        jitter_patch.start()
        self.addCleanup(jitter_patch.stop)
        self.client = NotionClient("secret-token")
        self.addCleanup(self.client.close)

    def test_context_manager_configures_version_and_closes_session(self):
        with self.client as client:
            self.assertIs(client, self.client)
            self.assertEqual(self.session.headers["Notion-Version"], API_VERSION)
            self.assertEqual(
                self.session.headers["Authorization"], "Bearer secret-token"
            )
        self.session.close.assert_called_once()

    def test_empty_token_rejected(self):
        with self.assertRaisesRegex(ValueError, "NOTION_TOKEN"):
            NotionClient(" ")

    def test_database_id_resolves_to_unique_data_source(self):
        self.session.request.return_value = response(
            {"data_sources": [{"id": "source"}]}
        )
        self.assertEqual(self.client.resolve_data_source("database"), "source")
        args, kwargs = self.session.request.call_args
        self.assertEqual(args, ("GET", "https://api.notion.com/v1/databases/database"))
        self.assertEqual(kwargs["timeout"], (10, 60))
        self.assertFalse(kwargs["allow_redirects"])

    def test_explicit_data_source_does_not_discover_or_query_other_sources(self):
        self.assertEqual(
            self.client.resolve_data_source("database", " chosen "), "chosen"
        )
        self.session.request.assert_not_called()

    def test_ambiguous_data_source_requires_configuration(self):
        self.session.request.return_value = response(
            {"data_sources": [{"id": "one"}, {"id": "two"}]}
        )
        with self.assertRaisesRegex(NotionAPIError, "NOTION_DATA_SOURCE_ID"):
            self.client.resolve_data_source("database")
        self.session.request.assert_called_once()

    def test_empty_and_malformed_data_sources_fail(self):
        for sources in ([], None, {}, [{"id": ""}], ["bad"], [{"id": None}]):
            with self.subTest(sources=sources):
                self.session.request.return_value = response({"data_sources": sources})
                with self.assertRaises(NotionAPIError):
                    self.client.resolve_data_source("database")

    def test_queries_follow_cursors_and_preserve_date_filter(self):
        self.session.request.side_effect = [
            response(page([{"id": "first"}], has_more=True, cursor="cursor-2")),
            response(page([{"id": "second"}])),
        ]
        self.assertEqual(
            list(self.client.query_pages("source", "수업 날짜", "2026-09-21")),
            [{"id": "first"}, {"id": "second"}],
        )
        first, second = self.session.request.call_args_list
        self.assertEqual(first.args[0], "POST")
        self.assertTrue(first.args[1].endswith("/data_sources/source/query"))
        self.assertEqual(first.kwargs["json"]["page_size"], 100)
        self.assertNotIn("start_cursor", first.kwargs["json"])
        self.assertEqual(second.kwargs["json"]["start_cursor"], "cursor-2")
        self.assertEqual(
            second.kwargs["json"]["filter"],
            {"property": "수업 날짜", "date": {"equals": "2026-09-21"}},
        )

    def test_all_mode_does_not_apply_date_filter(self):
        self.session.request.return_value = response(page([]))
        self.assertEqual(list(self.client.query_pages("source")), [])
        self.assertNotIn("filter", self.session.request.call_args.kwargs["json"])

    def test_children_paginate_and_cache_complete_results(self):
        self.session.request.side_effect = [
            response(page([{"id": "one"}], has_more=True, cursor="next")),
            response(page([{"id": "two"}])),
        ]
        children = self.client.get_block_children("parent")
        self.assertEqual(children, [{"id": "one"}, {"id": "two"}])
        self.assertEqual(self.client.get_block_children("parent"), children)
        self.assertEqual(self.client.retrieve_block("one"), {"id": "one"})
        self.assertEqual(self.session.request.call_count, 2)
        self.assertEqual(
            self.session.request.call_args.kwargs["params"],
            {"page_size": 100, "start_cursor": "next"},
        )

    def test_failed_child_pagination_is_not_cached_as_success(self):
        self.session.request.side_effect = [
            response(page([{"id": "one"}], has_more=True, cursor="next")),
            response({"code": "object_not_found"}, 404),
            response(page([{"id": "one"}, {"id": "two"}])),
        ]
        with self.assertRaises(NotionAPIError):
            self.client.get_block_children("parent")
        self.assertEqual(
            self.client.get_block_children("parent"), [{"id": "one"}, {"id": "two"}]
        )
        self.assertEqual(self.session.request.call_count, 3)

    def test_missing_repeated_or_invalid_cursor_fails(self):
        for cursor in (None, "", " ", 42, []):
            with self.subTest(cursor=cursor):
                self.session.request.return_value = response(
                    page([{"id": "one"}], has_more=True, cursor=cursor)
                )
                with self.assertRaisesRegex(NotionAPIError, "cursor"):
                    list(self.client.query_pages("source"))
        self.session.request.side_effect = [
            response(page([{"id": "one"}], has_more=True, cursor="repeated")),
            response(page([{"id": "two"}], has_more=True, cursor="repeated")),
        ]
        with self.assertRaisesRegex(NotionAPIError, "repeated"):
            list(self.client.query_pages("source"))

    def test_invalid_pagination_shape_is_not_treated_as_an_empty_export(self):
        for data in ({}, {"results": [], "has_more": "false"}, page({}), page([42])):
            with self.subTest(data=data):
                self.session.request.return_value = response(data)
                with self.assertRaises(NotionAPIError):
                    list(self.client.query_pages("source"))

    def test_empty_page_with_more_results_is_still_paginated(self):
        self.session.request.side_effect = [
            response(page([], has_more=True, cursor="next")),
            response(page([{"id": "one"}])),
        ]
        self.assertEqual(list(self.client.query_pages("source")), [{"id": "one"}])

    def test_title_property_items_paginate_without_double_encoding_property_id(self):
        self.session.request.side_effect = [
            response(
                page([{"title": {"plain_text": "A"}}], has_more=True, cursor="next")
            ),
            response(page([{"title": {"plain_text": "B"}}])),
        ]
        items = list(self.client.iter_page_property_items("page", "a%3Ab"))
        self.assertEqual([item["title"]["plain_text"] for item in items], ["A", "B"])
        self.assertTrue(
            self.session.request.call_args.args[1].endswith("/properties/a%3Ab")
        )

    def test_retry_after_is_honored_for_rate_limit_and_overload(self):
        for status in (429, 529):
            with self.subTest(status=status):
                failed = response(
                    {"code": "rate_limited"}, status, {"Retry-After": "12"}
                )
                succeeded = response({"id": "block"})
                self.session.request.side_effect = [failed, succeeded]
                self.client.retrieve_block(str(status))
                self.sleep.assert_called_with(12.0)
                failed.close.assert_called_once()
                succeeded.close.assert_called_once()

    def test_server_errors_and_network_timeouts_retry_read_only_query(self):
        self.session.request.side_effect = [
            requests.Timeout("sensitive transport detail"),
            response({"code": "service_unavailable"}, 503),
            response(page([{"id": "one"}])),
        ]
        self.assertEqual(list(self.client.query_pages("source")), [{"id": "one"}])
        self.assertEqual(
            [call.args[0] for call in self.sleep.call_args_list], [1.0, 2.0]
        )

    def test_interrupted_response_stream_retries(self):
        self.session.request.side_effect = [
            requests.exceptions.ChunkedEncodingError("interrupted connection"),
            response({"id": "block"}),
        ]
        self.assertEqual(self.client.retrieve_block("block"), {"id": "block"})
        self.assertEqual(self.session.request.call_count, 2)
        self.sleep.assert_called_once_with(1.0)

    def test_retries_stop_and_error_does_not_disclose_response_body(self):
        self.session.request.return_value = response(
            {"code": "service_unavailable", "message": "secret-token private note"}, 503
        )
        with self.assertRaises(NotionAPIError) as caught:
            self.client.retrieve_block("block")
        self.assertEqual(self.session.request.call_count, MAX_ATTEMPTS)
        self.assertEqual(caught.exception.status, 503)
        self.assertEqual(caught.exception.code, "service_unavailable")
        self.assertNotIn("secret-token", str(caught.exception))
        self.assertNotIn("private note", str(caught.exception))

    def test_network_retry_exhaustion_does_not_disclose_exception(self):
        self.session.request.side_effect = requests.ConnectionError("secret-token")
        with self.assertRaises(NotionAPIError) as caught:
            self.client.retrieve_block("block")
        self.assertEqual(self.session.request.call_count, MAX_ATTEMPTS)
        self.assertNotIn("secret-token", str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)

    def test_configuration_errors_fail_without_retry_or_sensitive_error_code(self):
        self.session.request.return_value = response(
            {"code": "secret-token", "message": "private content"}, 401
        )
        with self.assertRaisesRegex(NotionAPIError, "NOTION_TOKEN") as caught:
            self.client.retrieve_block("block")
        self.assertEqual(self.session.request.call_count, 1)
        self.sleep.assert_not_called()
        self.assertNotIn("secret-token", str(caught.exception))

    def test_retry_after_longer_than_budget_stops_instead_of_retrying_early(self):
        self.session.request.return_value = response(
            {"code": "rate_limited"}, 429, {"Retry-After": "600"}
        )
        with self.assertRaisesRegex(NotionAPIError, "later"):
            self.client.retrieve_block("block")
        self.assertEqual(self.session.request.call_count, 1)
        self.sleep.assert_not_called()

    def test_invalid_retry_after_values_fall_back_to_finite_backoff(self):
        for value in ("broken", "nan", "inf", "-1", None):
            with self.subTest(value=value):
                self.session.request.side_effect = [
                    response({"code": "rate_limited"}, 429, {"Retry-After": value}),
                    response({"id": "block"}),
                ]
                self.client.retrieve_block(str(value))
                self.sleep.assert_called_with(1.0)

    def test_invalid_success_json_is_a_failure_and_response_is_closed(self):
        for data in (ValueError("private body"), [], None):
            with self.subTest(data=data):
                result = response(data)
                self.session.request.return_value = result
                with self.assertRaisesRegex(NotionAPIError, "JSON"):
                    self.client.retrieve_block("block")
                result.close.assert_called_once()

    def test_request_pacing(self):
        self.session.request.return_value = response({"id": "block"})
        with patch("til_sync.notion.time.monotonic", return_value=10.0):
            self.client.retrieve_block("one")
            self.client.retrieve_block("two")
        self.assertAlmostEqual(self.sleep.call_args.args[0], 0.34)


if __name__ == "__main__":
    unittest.main()

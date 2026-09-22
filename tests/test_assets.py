import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests

from til_sync.assets import AssetError, AssetStore

PAGE_ID = "11111111-1111-1111-1111-111111111111"


class AssetTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name) / "page.md"
        self.response = Mock()
        self.response.__enter__ = Mock(return_value=self.response)
        self.response.__exit__ = Mock(return_value=False)
        self.response.headers = {"Content-Type": "image/png"}
        self.response.iter_content.return_value = [b"image bytes"]
        self.session = Mock()
        self.session.get.return_value = self.response
        self.payload = {
            "type": "file",
            "file": {"url": "https://example.com/image.png?signature=first"},
        }

    def test_borrowed_session_is_not_closed_after_success_or_failure(self):
        with AssetStore(self.path, PAGE_ID, session=self.session) as store:
            store.media_url({"id": "block"}, self.payload)
        self.session.close.assert_not_called()

        self.session.get.side_effect = requests.ConnectionError("network failure")
        with (
            self.assertRaises(AssetError),
            AssetStore(self.path, PAGE_ID, session=self.session) as store,
        ):
            store.media_url({"id": "block"}, self.payload)
        self.session.close.assert_not_called()

    def test_owned_session_is_closed_after_success_or_failure(self):
        with patch("til_sync.assets.requests.Session", return_value=self.session):
            with AssetStore(self.path, PAGE_ID) as store:
                store.media_url({"id": "block"}, self.payload)
            self.session.close.assert_called_once()

            self.session.reset_mock()
            self.session.get.side_effect = requests.ConnectionError("network failure")
            with self.assertRaises(AssetError), AssetStore(self.path, PAGE_ID) as store:
                store.media_url({"id": "block"}, self.payload)
            self.session.close.assert_called_once()

    def test_signed_url_becomes_stable_relative_asset_and_repeated_reference_cached(
        self,
    ):
        with AssetStore(self.path, PAGE_ID, session=self.session) as store:
            first = store.media_url({"id": "block"}, self.payload)
            changed_signature = {
                "file": {"url": "https://example.com/image.png?signature=second"}
            }
            self.assertEqual(first, store.media_url({"id": "block"}, changed_signature))
        self.session.get.assert_called_once()
        self.assertEqual((self.path.parent / first).read_bytes(), b"image bytes")
        self.assertNotIn("signature", first)
        self.assertNotIn("headers", self.session.get.call_args.kwargs)

    def test_external_url_is_preserved_without_download(self):
        with AssetStore(self.path, PAGE_ID, session=self.session) as store:
            self.assertEqual(
                store.media_url({}, {"external": {"url": "https://example.com/x"}}),
                "https://example.com/x",
            )
        self.session.get.assert_not_called()

    def test_signed_embed_is_downloaded(self):
        with AssetStore(self.path, PAGE_ID, session=self.session) as store:
            result = store.media_url(
                {"id": "embed"},
                {
                    "external": {
                        "url": "https://s3.us-west-2.amazonaws.com/f.html?X-Amz-Signature=signed"
                    }
                },
            )
        self.assertTrue(result.endswith(".html"))
        self.session.get.assert_called_once()

    def test_stream_failure_does_not_replace_existing_asset_or_leak_signed_url(self):
        with AssetStore(self.path, PAGE_ID, session=self.session) as store:
            link = store.media_url({"id": "block"}, self.payload)
        before = (self.path.parent / link).read_bytes()
        self.response.iter_content.side_effect = requests.ConnectionError(
            "PRIVATE_SIGNED_URL"
        )
        with (
            AssetStore(self.path, PAGE_ID, session=self.session) as store,
            self.assertRaises(AssetError) as raised,
        ):
            store.media_url({"id": "block"}, self.payload)
        self.assertNotIn("PRIVATE_SIGNED_URL", str(raised.exception))
        self.assertEqual((self.path.parent / link).read_bytes(), before)
        self.assertEqual(len(list((self.path.parent / "assets").rglob("*.*"))), 1)

    def test_oversize_stream_leaves_no_partial_file(self):
        with (
            patch("til_sync.assets.MAX_ASSET_BYTES", 3),
            AssetStore(self.path, PAGE_ID, session=self.session) as store,
            self.assertRaises(AssetError),
        ):
            store.media_url({"id": "block"}, self.payload)
        self.assertFalse(any(p.is_file() for p in self.path.parent.rglob("*")))

    def test_size_limit_error_uses_the_configured_limit(self):
        self.response.headers["Content-Length"] = str(3 * 1024 * 1024)
        with (
            patch("til_sync.assets.MAX_ASSET_BYTES", 2 * 1024 * 1024),
            AssetStore(self.path, PAGE_ID, session=self.session) as store,
            self.assertRaisesRegex(AssetError, "2 MiB"),
        ):
            store.media_url({"id": "block"}, self.payload)
        self.assertFalse(any(p.is_file() for p in self.path.parent.rglob("*")))

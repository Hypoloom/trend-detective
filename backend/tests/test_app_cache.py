import tempfile
import unittest
from unittest import mock

import app


class MissingCache(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.patch = mock.patch.object(app, "CACHE_DIR", self.tmp.name)
        self.patch.start()
        self.c = app.app.test_client()

    def tearDown(self):
        self.patch.stop()
        self.tmp.cleanup()

    def test_series_missing_is_clean_404(self):
        r = self.c.get("/api/series?dataset=T2M&region=kerala")
        self.assertEqual(r.status_code, 404)
        self.assertIn("error", r.get_json())

    def test_ask_missing_is_clean_404(self):
        r = self.c.post("/api/ask", json={"question": "My pond turned green"})
        self.assertEqual(r.status_code, 404)
        self.assertIn("cached data missing", r.get_json()["error"])

    def test_datasets_not_ready(self):
        d = self.c.get("/api/datasets").get_json()["datasets"]
        self.assertTrue(all(x["ready"] is False for x in d))


if __name__ == "__main__":
    unittest.main()
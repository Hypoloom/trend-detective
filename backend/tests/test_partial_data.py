import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import answer
import app as appmod

BOX = (72, 16, 80, 21)


class TestPartialData(unittest.TestCase):
    def test_build_marks_uncached_axis(self):
        out = answer.build("pond", "Maharashtra", BOX, 1980, 2025, is_cached=lambda k: k != "sunlight")
        st = {a["name"]: a["status"] for a in out["axes"]}
        self.assertEqual(st["sunlight"], "data_unavailable")
        self.assertEqual(st["air_temp"], "analyzed")
        self.assertEqual(out["tested_count"], 2)

    def test_route_survives_one_missing_file(self):
        real = appmod.cache_file
        fake = lambda key, box: None if key == "sunlight" else real(key, box)
        with mock.patch.object(appmod, "cache_file", fake):
            c = appmod.app.test_client()
            for level in ("plain", "detailed", "pro"):
                with self.subTest(level=level):
                    r = c.post("/api/ask", json={"question": "My pond turned green", "level": level})
                    j = r.get_json()
                    self.assertEqual(r.status_code, 200)
                    self.assertFalse(j["fallback"])
                    print(level, "| note:", j.get("phrase_note"))
                    self.assertNotIn("guard rejected", j.get("phrase_note") or "")

    def test_all_missing_still_404(self):
        with mock.patch.object(appmod, "cache_file", lambda key, box: None):
            r = appmod.app.test_client().post("/api/ask", json={"question": "My pond turned green"})
            self.assertEqual(r.status_code, 404)


if __name__ == "__main__":
    unittest.main()
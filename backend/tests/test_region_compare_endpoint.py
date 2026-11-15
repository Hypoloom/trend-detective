import unittest
import app


class RegionCompareEndpoint(unittest.TestCase):
    def test_compare_question(self):
        c = app.app.test_client()
        for lv in ("plain", "detailed", "pro"):
            j = c.post("/api/ask", json={"question": "Which region is warming fastest?", "level": lv}).get_json()
            self.assertFalse(j["fallback"])
            self.assertEqual(j["domain"], "region_compare")

    def test_others_unchanged(self):
        c = app.app.test_client()
        self.assertEqual(c.post("/api/ask", json={"question": "Is it getting hotter where I live?"}).get_json()["domain"], "heat")
        self.assertEqual(c.post("/api/ask", json={"question": "Was this year hotter than usual?"}).get_json()["domain"], "year_vs_record")
        self.assertEqual(c.post("/api/ask", json={"question": "My pond turned green"}).get_json()["domain"], "pond")


if __name__ == "__main__":
    unittest.main()
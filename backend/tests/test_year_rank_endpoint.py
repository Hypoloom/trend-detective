import unittest
import app


class YearRankEndpoint(unittest.TestCase):
    def test_year_question(self):
        c = app.app.test_client()
        for lv in ("plain", "detailed", "pro"):
            j = c.post("/api/ask", json={"question": "Was this year hotter than usual?", "level": lv}).get_json()
            self.assertFalse(j["fallback"])
            self.assertEqual(j["domain"], "year_vs_record")
            self.assertIn("2025", j["text"])

    def test_other_routes_unchanged(self):
        c = app.app.test_client()
        j = c.post("/api/ask", json={"question": "Is it getting hotter where I live?"}).get_json()
        self.assertEqual(j["domain"], "heat")
        j = c.post("/api/ask", json={"question": "My pond turned green"}).get_json()
        self.assertEqual(j["domain"], "pond")


if __name__ == "__main__":
    unittest.main()
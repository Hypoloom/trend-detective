import unittest
import app


class SeasonEndpoint(unittest.TestCase):
    def test_season_question(self):
        c = app.app.test_client()
        for lv in ("plain", "detailed", "pro"):
            j = c.post("/api/ask", json={"question": "Are the monsoon months getting wetter?", "level": lv}).get_json()
            self.assertFalse(j["fallback"])
            self.assertEqual(j["domain"], "season")
            self.assertIn("June", j["text"])

    def test_others_unchanged(self):
        c = app.app.test_client()
        for q, d in (("Is the monsoon getting wetter or drier?", "monsoon"), ("Are summers getting sunnier or cloudier?", "sunshine"),
                     ("Was this year hotter than usual?", "year_vs_record"), ("Which region is warming fastest?", "region_compare"),
                     ("My pond turned green", "pond")):
            self.assertEqual(c.post("/api/ask", json={"question": q}).get_json()["domain"], d, q)


if __name__ == "__main__":
    unittest.main()
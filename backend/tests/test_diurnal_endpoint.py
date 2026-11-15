import unittest
import app


class DiurnalEndpoint(unittest.TestCase):
    def test_question(self):
        c = app.app.test_client()
        for lv in ("plain", "detailed", "pro"):
            j = c.post("/api/ask", json={"question": "Are days heating faster than nights?", "level": lv}).get_json()
            self.assertFalse(j["fallback"])
            self.assertEqual(j["domain"], "diurnal")

    def test_others_unchanged(self):
        c = app.app.test_client()
        for q, d in (("Is it getting hotter where I live?", "heat"), ("Are the monsoon months getting wetter?", "season"),
                     ("Was this year hotter than usual?", "year_vs_record"), ("Which region is warming fastest?", "region_compare"),
                     ("My pond turned green", "pond")):
            self.assertEqual(c.post("/api/ask", json={"question": q}).get_json()["domain"], d, q)


if __name__ == "__main__":
    unittest.main()
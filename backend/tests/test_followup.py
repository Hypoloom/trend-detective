import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import answer
import followup
import router
import app as appmod

REGIONS = ("maharashtra", "rajasthan", "kerala", "gujarat")
ROUTES = [
    ("Is it getting hotter where I live?", "heat"),
    ("Is Rajasthan getting hotter?", "heat"),
    ("Is the monsoon getting wetter or drier?", "monsoon"),
    ("Are summers getting sunnier or cloudier?", "sunshine"),
    ("My pond turned green", "pond"),
    ("Why are my oranges so small this year?", "citrus"),
    ("tell me a joke", None),
]
CTX = {"domain": "pond", "region": "maharashtra"}


class TestRouting(unittest.TestCase):
    def test_routes(self):
        for q, dom in ROUTES:
            with self.subTest(q=q):
                self.assertEqual(router.route(q).domain, dom)


class TestPlan(unittest.TestCase):
    def test_axes_match_domains_json(self):
        for d, axes in followup.DOMAIN_AXES.items():
            with self.subTest(domain=d):
                dom = answer.load_domain(d)
                self.assertEqual({a["name"] for a in dom["axes"] if a["source"] == "nasa_data"}, axes)

    def test_intents(self):
        cases = [
            ("Why is the temperature so high?", "causal", "air_temp"),
            ("Why is it not significant?", "why_no_trend", None),
            ("How sure are you?", "how_sure", None),
            ("What about rainfall?", "variable", "rainfall"),
            ("What about Kerala?", "region", None),
            ("And the nights?", "variable", "night_temp"),
        ]
        for q, intent, focus in cases:
            with self.subTest(q=q):
                p = followup.plan(q, CTX, "maharashtra")
                self.assertEqual(p["intent"], intent)
                self.assertEqual(p["focus"], focus)

    def test_region_and_none(self):
        self.assertEqual(followup.plan("What about Kerala?", CTX, "maharashtra")["region"], "kerala")
        self.assertIsNone(followup.plan("tell me a joke", CTX, "maharashtra"))
        self.assertIsNone(followup.plan("Why is the temperature so high?", None, "maharashtra"))

    def test_rainfall_from_heat_context_switches_domain(self):
        p = followup.plan("What about rainfall?", {"domain": "heat", "region": "kerala"}, "maharashtra")
        self.assertEqual((p["domain"], p["region"]), ("monsoon", "kerala"))


class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        self.c = appmod.app.test_client()

    def ask(self, q, region="maharashtra", level="plain", context=None):
        r = self.c.post("/api/ask", json={"question": q, "region": region, "level": level, "context": context})
        return r.status_code, r.get_json()

    def test_new_domains_all_regions_levels(self):
        for q in ("Is it getting hotter where I live?", "Is the monsoon getting wetter or drier?",
                  "Are summers getting sunnier or cloudier?"):
            for region in REGIONS:
                for level in ("plain", "detailed", "pro"):
                    with self.subTest(q=q, region=region, level=level):
                        code, j = self.ask(q, region, level)
                        self.assertEqual(code, 200)
                        self.assertFalse(j["fallback"])
                        self.assertNotIn("guard rejected", j.get("phrase_note") or "")

    def test_followups(self):
        for q in ("Why is the temperature so high?", "Why is it not significant?", "How sure are you?",
                  "What about rainfall?", "What about Kerala?"):
            for level in ("plain", "detailed", "pro"):
                with self.subTest(q=q, level=level):
                    code, j = self.ask(q, level=level, context=CTX)
                    self.assertEqual(code, 200)
                    self.assertTrue(j.get("followup"))
                    self.assertNotIn("guard rejected", j.get("phrase_note") or "")

    def test_causal_lead_and_region(self):
        code, j = self.ask("Why is the temperature so high?", context=CTX)
        self.assertIn("do not show the reason", j["text"])
        self.assertEqual(len(j["result"]["axes"]), 1)
        code, j = self.ask("What about Kerala?", context=CTX)
        self.assertEqual(j["result"]["region"], "Kerala")

    def test_forecast_note(self):
        code, j = self.ask("Will next year be hotter?")
        self.assertTrue(j["text"].startswith("A trend in past records is not a forecast"))

    def test_no_context_still_falls_back(self):
        code, j = self.ask("Why is the temperature so high?")
        self.assertTrue(j["fallback"])


if __name__ == "__main__":
    unittest.main()
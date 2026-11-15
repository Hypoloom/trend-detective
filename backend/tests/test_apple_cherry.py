import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import router
import app as appmod

REGIONS = ("maharashtra", "rajasthan", "kerala", "gujarat")
ROUTES = [
    ("Why are apples so sweet this year?", "apple"),
    ("Why are my apples so sweet?", "apple"),
    ("why is my cherry blossom blooming so late", "cherry_blossom"),
    ("My cherry blossoms are late", "cherry_blossom"),
    ("Why are my oranges so small this year?", "citrus"),
    ("My pond turned green", "pond"),
    ("Is my pond going to get an algae bloom?", "pond"),
    ("Is it getting hotter where I live?", "heat"),
    ("tell me a joke", None),
]


class TestAppleCherryRouting(unittest.TestCase):
    def test_routes(self):
        for q, dom in ROUTES:
            with self.subTest(q=q):
                self.assertEqual(router.route(q).domain, dom)

    def test_single_word_still_falls_back(self):
        for q in ("apple", "cherry", "sweet"):
            with self.subTest(q=q):
                self.assertTrue(router.route(q).is_fallback)


class TestAppleCherryEndToEnd(unittest.TestCase):
    def setUp(self):
        self.c = appmod.app.test_client()

    def test_all_regions_levels(self):
        for q, dom in (("Why are apples so sweet this year?", "apple"),
                       ("why is my cherry blossom blooming so late", "cherry_blossom")):
            for region in REGIONS:
                for level in ("plain", "detailed", "pro"):
                    with self.subTest(q=q, region=region, level=level):
                        r = self.c.post("/api/ask", json={"question": q, "region": region, "level": level})
                        j = r.get_json()
                        self.assertEqual(r.status_code, 200)
                        self.assertFalse(j["fallback"])
                        self.assertEqual(j["domain"], dom)
                        self.assertTrue(j["result"]["abstained"])
                        self.assertNotIn("guard rejected", j.get("phrase_note") or "")

    def test_followup_after_apple(self):
        r = self.c.post("/api/ask", json={"question": "What about Kerala?", "level": "plain",
                                          "context": {"domain": "apple", "region": "maharashtra"}})
        j = r.get_json()
        self.assertEqual(r.status_code, 200)
        self.assertTrue(j.get("followup"))


if __name__ == "__main__":
    unittest.main()
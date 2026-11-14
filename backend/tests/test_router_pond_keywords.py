"""Router rules for the pond domain keywords 'green' and 'murky' (uses the real domains.json)."""
import unittest

from router import route, load_domains


class PondKeywordTests(unittest.TestCase):
    def test_keywords_are_in_domains_json(self):
        pond = next(d for d in load_domains() if d["id"] == "pond")
        self.assertIn("green", pond["keywords"])
        self.assertIn("murky", pond["keywords"])

    def test_green_pond_routes_to_pond(self):
        r = route("My pond turned green")
        self.assertEqual((r.domain, r.source, r.confidence), ("pond", "rules", 0.667), f"{r}")

    def test_murky_pond_routes_to_pond(self):
        r = route("My pond water is murky")
        self.assertEqual((r.domain, r.source, r.confidence), ("pond", "rules", 0.667), f"{r}")

    def test_green_or_murky_alone_is_still_too_weak(self):
        for q in ("green", "murky", "Is green tea healthy?"):
            with self.subTest(q=q):
                r = route(q)
                self.assertTrue(r.is_fallback, f"{r}")

    def test_existing_routes_are_unchanged(self):
        r = route("tell me a joke")
        self.assertTrue(r.is_fallback)
        self.assertEqual(r.reason, "no keyword matched")
        r = route("Why are my oranges so small this year?")
        self.assertEqual((r.domain, r.confidence), ("citrus", 0.667), f"{r}")
        r = route("Is my fish pond going to get algae this summer?")
        self.assertEqual((r.domain, r.confidence), ("pond", 0.667), f"{r}")

    def test_green_does_not_steal_a_citrus_question(self):
        r = route("Why are my green oranges small?")
        self.assertEqual(r.domain, "citrus", f"{r}")

    def test_mixed_pond_and_orange_is_still_ambiguous(self):
        r = route("My pond has orange fish")
        self.assertTrue(r.is_fallback)
        self.assertIn("ambiguous", r.reason)


if __name__ == "__main__":
    unittest.main()
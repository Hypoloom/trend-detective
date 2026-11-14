import unittest

from router import route, load_domains, STUB_DOMAINS

CASES = [
    ("Is my fish pond going to get algae this summer?", "pond"),
    ("When will green scum show up on my pond?", "pond"),
    ("Will there be an algae bloom in the pond?", "pond"),
    ("Why are my oranges so small this year?", "citrus"),
    ("Citrus orchard fruit size is dropping", "citrus"),
    ("Why are my lemons small?", "citrus"),
    ("ORANGES!! small??", "citrus"),
    ("Small pond algae", "pond"),
    ("What is the weather in Paris tomorrow?", None),   # off-topic
    ("Best pizza recipe", None),                        # off-topic
    ("Is the temperature rising in Maharashtra?", None),  # no vetted domain
    ("My pond has orange fish", None),                  # ambiguous
    ("algae", None),                                    # too weak on its own
    ("", None),                                         # empty
]


class RouterTests(unittest.TestCase):
    def test_question_table(self):
        for q, expected in CASES:
            with self.subTest(q=q):
                r = route(q, domains=STUB_DOMAINS)
                self.assertEqual(r.domain, expected, f"{r}")
                self.assertEqual(r.is_fallback, expected is None)

    def test_tie_goes_to_fallback(self):
        r = route("pond orange", domains=STUB_DOMAINS)
        self.assertTrue(r.is_fallback)
        self.assertIn("ambiguous", r.reason)      # was "weak" before the label fix

    def test_llm_cannot_invent_domain(self):
        for bad in ({"domain": "lake"}, {"domain": "none"}, "pond", None, {}):
            with self.subTest(bad=bad):
                r = route("pond orange", domains=STUB_DOMAINS, llm_choose=lambda q, m, b=bad: b)
                self.assertTrue(r.is_fallback)

    def test_llm_valid_choice_and_menu(self):
        seen = {}

        def fake(q, menu):
            seen["menu"] = menu
            return {"domain": "pond"}

        r = route("pond orange", domains=STUB_DOMAINS, llm_choose=fake)
        self.assertEqual((r.domain, r.source), ("pond", "llm"))
        for item in seen["menu"]:
            self.assertEqual(set(item), {"id", "description", "example_questions"})

    def test_llm_not_called_when_rules_confident(self):
        calls = []
        r = route("Why are my oranges small?", domains=STUB_DOMAINS,
                  llm_choose=lambda q, m: calls.append(1) or {"domain": "pond"})
        self.assertEqual((r.domain, r.source, calls), ("citrus", "rules", []))

    def test_llm_exception_falls_back(self):
        def boom(q, m):
            raise RuntimeError("down")
        self.assertTrue(route("pond orange", domains=STUB_DOMAINS, llm_choose=boom).is_fallback)

    def test_fallback_has_form(self):
        r = route("Best pizza recipe", domains=STUB_DOMAINS)
        ids = [o["id"] for o in r.form["step1_pick_topic"]["options"]]
        self.assertEqual(ids, ["pond", "citrus", "none"])
        self.assertEqual(r.form["step2_followups"]["pond"][0]["name"], "pond_size")

    def test_load_domains_stub_when_missing(self):
        ids = [d["id"] for d in load_domains("/nonexistent/domains.json")]
        self.assertEqual(ids, ["pond", "citrus"])


if __name__ == "__main__":
    unittest.main()

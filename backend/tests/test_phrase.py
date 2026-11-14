import copy
import unittest

from phrase import (CallableAdapter, LEVELS, allowed_numbers, check_text, must_abstain,
                    numbers_in_text, phrase, phrase_with_report, template_phrase)
from tests import mocks

ALL = mocks.all_mocks()
GOOD_POND = ("This tool cannot give a definite answer here. Nutrient load and existing algae are "
             "not knowable from this data, so no number of days can be given.")


class GuardTests(unittest.TestCase):
    def test_guard_accepts_template_all_mocks(self):
        for name, r in ALL.items():
            for lvl in LEVELS:
                with self.subTest(mock=name, level=lvl):
                    g = check_text(template_phrase(r, lvl), r)
                    self.assertTrue(g.ok, g.reasons)

    def test_guard_rejects_invented_number(self):
        g = check_text("No trend was found. The slope is 0.07 K per year.", mocks.no_trend())
        self.assertFalse(g.ok)
        self.assertTrue(any("0.07" in x for x in g.reasons), g.reasons)

    def test_guard_accepts_number_from_result(self):
        g = check_text("No trend was found; the slope is 0.0045 K per year with p = 0.237.", mocks.no_trend())
        self.assertTrue(g.ok, g.reasons)

    def test_guard_rejects_causal_words(self):
        for bad in ("This is caused by warming.", "Rain causes algae.", "It happened because of heat.",
                    "Due to heat, it changed.", "The trend is driven by sun.", "Warming leads to small fruit."):
            with self.subTest(bad=bad):
                g = check_text("No trend was found. " + bad, mocks.no_trend())
                self.assertFalse(g.ok)
                self.assertTrue(any("causal" in x for x in g.reasons), g.reasons)

    def test_guard_rejects_missing_abstention(self):
        g = check_text("Algae risk is moderate this summer.", mocks.pond_abstained())
        self.assertFalse(g.ok)
        self.assertTrue(any("abstention" in x for x in g.reasons), g.reasons)

    def test_guard_rejects_softened_abstention(self):
        g = check_text("This tool cannot give a definite answer here, but it is probably fine.",
                       mocks.pond_abstained())
        self.assertFalse(g.ok)
        self.assertTrue(any("softened" in x for x in g.reasons), g.reasons)

    def test_guard_rejects_no_trend_exists(self):
        g = check_text("No trend was found, and no trend exists here.", mocks.no_trend())
        self.assertFalse(g.ok)
        self.assertTrue(any("overclaim" in x for x in g.reasons), g.reasons)

    def test_guard_accepts_good_llm_text(self):
        g = check_text(GOOD_POND, mocks.pond_abstained())
        self.assertTrue(g.ok, g.reasons)


class PhraseTests(unittest.TestCase):
    def test_phrase_uses_llm_when_ok(self):
        out, rep = phrase_with_report(mocks.pond_abstained(), "plain", CallableAdapter(lambda s, u: GOOD_POND))
        self.assertEqual((out, rep.source), (GOOD_POND, "llm"))

    def test_phrase_falls_back_on_bad_llm(self):
        r = mocks.pond_abstained()
        out, rep = phrase_with_report(r, "plain", CallableAdapter(lambda s, u: "Algae will bloom in 12 days."))
        self.assertEqual(out, template_phrase(r, "plain"))
        self.assertEqual(rep.source, "template")
        self.assertIn("guard rejected", rep.note)

    def test_phrase_falls_back_on_adapter_error(self):
        def boom(s, u):
            raise RuntimeError("provider down")
        r = mocks.no_trend()
        self.assertEqual(phrase(r, "detailed", CallableAdapter(boom)), template_phrase(r, "detailed"))

    def test_phrase_without_adapter_is_template(self):
        r = mocks.detected()
        self.assertEqual(phrase(r, "pro"), template_phrase(r, "pro"))

    def test_must_abstain_critical_not_knowable(self):
        r = mocks.hidden_critical()
        self.assertFalse(r["abstained"])
        self.assertTrue(must_abstain(r))
        for lvl in LEVELS:
            self.assertIn("cannot give a definite answer", template_phrase(r, lvl))
        self.assertFalse(check_text("All good, algae risk is low.", r).ok)

    def test_noncritical_not_knowable_does_not_force(self):
        r = mocks.no_trend()
        r["axes"] = [{"name": "x", "source": "not_knowable", "critical": False, "status": "not_knowable"}]
        self.assertFalse(must_abstain(r))

    def test_template_reads_from_result(self):
        r = mocks.no_trend()
        r["trend"]["slope_per_year"] = 0.5
        txt = template_phrase(r, "pro")
        self.assertIn("0.5", txt)
        self.assertNotIn("0.0045", txt)

    def test_bad_level(self):
        with self.assertRaises(ValueError):
            template_phrase(mocks.no_trend(), "loud")


if __name__ == "__main__":
    unittest.main()

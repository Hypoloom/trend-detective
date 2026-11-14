"""Tests built from the shape of REAL engine output (answer.build / contract), not the old mocks.

tests/real_pond.json must be replaced by real output once available:
    python answer.py pond > tests/real_pond.json
"""
import copy
import json
import os
import unittest

from phrase import (CallableAdapter, LEVELS, _fmt, _risk_window_text, allowed_numbers,
                    check_text, phrase, phrase_with_report, template_phrase)
from router import STUB_DOMAINS, route

HERE = os.path.dirname(os.path.abspath(__file__))


def load_pond():
    with open(os.path.join(HERE, "real_pond.json"), encoding="utf-8") as f:
        return json.load(f)


def axis_result(name):
    """A single-axis contract result (what answer.build(...)['axes'][i]['result'] holds)."""
    for a in load_pond()["axes"]:
        if a["name"] == name:
            return copy.deepcopy(a["result"])
    raise KeyError(name)


class RealPondTemplateTests(unittest.TestCase):
    def test_template_passes_guard_all_levels(self):
        r = load_pond()
        for lvl in LEVELS:
            with self.subTest(level=lvl):
                g = check_text(phrase(r, lvl), r)
                self.assertTrue(g.ok, g.reasons)

    def test_mentions_both_axis_results_no_brackets(self):
        r = load_pond()
        for lvl in LEVELS:
            with self.subTest(level=lvl):
                text = phrase(r, lvl)
                low = text.lower()
                self.assertIn("air temperature", low)
                self.assertIn("no trend found", low)
                self.assertIn("rainfall", low)
                self.assertIn("detected", low)
                self.assertNotIn("[", text)
                self.assertNotIn("{", text)
                self.assertNotIn("months:", text)       # no raw dict keys
                self.assertNotIn("base_rate", text)

    def test_no_invented_inconclusive_sentence(self):
        r = load_pond()
        self.assertIsNone(r.get("verdict"))
        for lvl in LEVELS:
            with self.subTest(level=lvl):
                self.assertNotIn("inconclusive", phrase(r, lvl).lower())

    def test_risk_window_sentence(self):
        text = phrase(load_pond(), "plain")
        self.assertIn("April, May and June", text)
        self.assertIn("12 of 20 years", text)

    def test_skips_not_analyzed_axes_in_axis_report(self):
        text = phrase(load_pond(), "plain")
        self.assertNotIn("Pond size:", text)
        self.assertNotIn("Nutrient load:", text)

    def test_abstention_always_present(self):
        r = load_pond()
        for lvl in LEVELS:
            self.assertIn("cannot give a definite answer", phrase(r, lvl))


class RiskWindowTextTests(unittest.TestCase):
    RW = {"months": [4, 5, 6], "month_names": ["April", "May", "June"],
          "base_rate": {"years_met": 12, "years_total": 20, "statement": ""},
          "caveat": "This is a window, not a forecast"}      # note: no full stop

    def test_full_stop_after_risk_window_text(self):
        for rw in (self.RW, {**self.RW, "caveat": ""}, {**self.RW, "base_rate": {}}, "warm weeks", ["a", "b"]):
            with self.subTest(rw=rw):
                out = _risk_window_text(rw, "pond", "detailed")
                self.assertTrue(out.endswith("."), repr(out))

    def test_full_stop_in_final_text(self):
        r = load_pond()
        r["risk_window"]["caveat"] = "A caveat with no full stop"
        text = phrase(r, "plain")
        self.assertIn("A caveat with no full stop.", text)

    def test_never_prints_keys_or_lists(self):
        out = _risk_window_text(self.RW, "pond", "pro")
        for bad in ("[", "]", "{", "}", "months:", "base_rate", "years_met"):
            self.assertNotIn(bad, out)
        self.assertIn("12 of the 20 years", out)

    def test_engine_caveat_used_as_is(self):
        self.assertIn("This is a window, not a forecast.", _risk_window_text(self.RW, "pond"))


class GuardOnEngineTextTests(unittest.TestCase):
    def test_engine_words_do_not_trip_guard(self):
        r = load_pond()
        text = ("This tool cannot give a definite answer here. No trend found (not proof of absence). "
                "Trends found here do not show cause.")
        self.assertTrue(check_text(text, r).ok, check_text(text, r).reasons)

    def test_llms_own_causal_word_still_rejected(self):
        r = load_pond()
        for bad in ("It rains because the season changes.", "Heat caused the change.", "This is proof."):
            with self.subTest(bad=bad):
                text = "This tool cannot give a definite answer here. Trends found here do not show cause. " + bad
                g = check_text(text, r)
                self.assertFalse(g.ok)
                self.assertTrue(any(("causal" in x or "overclaim" in x) for x in g.reasons), g.reasons)

    def test_still_rejects_invented_number_missing_and_softened_abstention_no_trend_exists(self):
        r = load_pond()
        self.assertFalse(check_text("This tool cannot give a definite answer here. Risk is 77 days.", r).ok)
        self.assertFalse(check_text("The pond looks fine this summer.", r).ok)
        soft = check_text("This tool cannot give a definite answer here, but it is probably fine.", r)
        self.assertTrue(any("softened" in x for x in soft.reasons), soft.reasons)
        ov = check_text("This tool cannot give a definite answer here. No trend exists.", r)
        self.assertTrue(any("overclaim" in x for x in ov.reasons), ov.reasons)

    def test_unrelated_guard_fallback_on_bad_llm_with_real_result(self):
        r = load_pond()
        out, rep = phrase_with_report(r, "plain", CallableAdapter(lambda s, u: "Algae will bloom in 5 days."))
        self.assertEqual(rep.source, "template")
        self.assertEqual(out, template_phrase(r, "plain"))


class LongDecimalTests(unittest.TestCase):
    LONG = 0.004480123456789

    def test_formatter_output_is_accepted(self):
        r = axis_result("air_temperature")
        self.assertEqual(r["trend"]["slope_per_year"], self.LONG)
        shown = _fmt(self.LONG)
        self.assertNotEqual(float(shown), self.LONG)         # the rounding really changes the value
        g = check_text(f"No trend was found; slope {shown} K per year.", r)
        self.assertTrue(g.ok, g.reasons)
        self.assertIn(float(shown), allowed_numbers(r))

    def test_close_but_different_number_still_rejected(self):
        r = axis_result("air_temperature")
        g = check_text("No trend was found; slope 0.0045 K per year.", r)
        self.assertFalse(g.ok)
        self.assertTrue(any("invented number" in x for x in g.reasons), g.reasons)

    def test_single_axis_verdict_paths_llm_off(self):
        # detected / no_trend / data_limited, each with long decimals, at all levels
        base = axis_result("air_temperature")
        cases = {}
        d = copy.deepcopy(base)
        d["verdict"].update(code="detected", label="Trend detected")
        d["trend"]["slope_per_year"] = 0.031234567891234
        cases["detected"] = (d, "A trend was found")
        cases["no_trend"] = (copy.deepcopy(base), "No trend was found")
        dl = copy.deepcopy(base)
        dl["verdict"].update(code="data_limited", label="Data limited")
        dl["years"]["have"] = 12
        cases["data_limited"] = (dl, "not enough data")
        for name, (r, needle) in cases.items():
            for lvl in LEVELS:
                with self.subTest(case=name, level=lvl):
                    text = phrase(r, lvl)
                    self.assertIn(needle, text)
                    g = check_text(text, r)
                    self.assertTrue(g.ok, g.reasons)

    def test_detected_path_prints_rounded_slope(self):
        r = axis_result("rainfall")
        self.assertIn(_fmt(r["trend"]["slope_per_year"]), phrase(r, "plain"))


class RouterLabelTests(unittest.TestCase):
    def test_tie_between_domains_says_ambiguous(self):
        r = route("My pond has orange fish", domains=STUB_DOMAINS)
        self.assertTrue(r.is_fallback)
        self.assertIn("ambiguous", r.reason)
        self.assertNotIn("too weak", r.reason)

    def test_single_weak_keyword_still_says_weak(self):
        r = route("algae", domains=STUB_DOMAINS)
        self.assertIn("too weak", r.reason)

    def test_no_match_label(self):
        self.assertIn("no keyword", route("Best pizza recipe", domains=STUB_DOMAINS).reason)


if __name__ == "__main__":
    unittest.main()

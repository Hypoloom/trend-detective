"""Tests built from the shape of REAL engine output (answer.build / contract), not the old mocks.

tests/real_pond.json must be replaced by real output once available:
    python answer.py pond > tests/real_pond.json
"""
import copy
import json
import os
import unittest

from phrase import (CallableAdapter, LEVELS, _fmt, _fmt_sig, _risk_window_text, allowed_numbers,
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
        self.assertIn("In the last 20 years of the record these months averaged", text)

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
          "base_rate": {"years_met": 12, "years_total": 20, "statement": ""},   # no statement text
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
        self.assertIn("12 of the last 20 years", out)

    def test_engine_caveat_used_as_is(self):
        self.assertIn("This is a window, not a forecast.", _risk_window_text(self.RW, "pond"))


class GuardOnEngineTextTests(unittest.TestCase):
    def test_engine_words_do_not_trip_guard(self):
        r = load_pond()
        engine = [c if isinstance(c, str) else str(c.get("text", "")) for c in r["caveats"]]
        text = " ".join(["This tool cannot give a definite answer here."] + engine)
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
    LONG = 0.00448129

    def test_formatter_output_is_accepted(self):
        r = copy.deepcopy(axis_result("air_temp"))
        long_val = 0.004480123456789          # test's own long decimal, independent of the fixture
        r["trend"]["slope_per_year"] = long_val
        shown = _fmt(long_val)
        self.assertNotEqual(float(shown), long_val)          # the rounding really changes the value
        g = check_text(f"No trend was found; slope {shown} K per year.", r)
        self.assertTrue(g.ok, g.reasons)
        self.assertIn(float(shown), allowed_numbers(r))

    def test_close_but_different_number_still_rejected(self):
        r = axis_result("air_temp")
        g = check_text("No trend was found; slope 0.0045 K per year.", r)
        self.assertFalse(g.ok)
        self.assertTrue(any("invented number" in x for x in g.reasons), g.reasons)

    def test_single_axis_verdict_paths_llm_off(self):
        # detected / no_trend / data_limited, each with long decimals, at all levels
        base = axis_result("air_temp")
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
        self.assertIn(_fmt_sig(r["trend"]["slope_per_year"]), phrase(r, "plain"))
        self.assertIn(_fmt(r["trend"]["slope_per_year"]), phrase(r, "pro"))


class BaseRateSentenceTests(unittest.TestCase):
    def rw(self, statement, met=12, total=20):
        return {"month_names": ["April"], "base_rate": {"years_met": met, "years_total": total,
                                                        "statement": statement}}

    def test_fragment_becomes_one_sentence(self):
        out = _risk_window_text(self.rw("years in which these months averaged above the record's own average."),
                                "pond", "detailed")
        self.assertIn("In 12 of the last 20 years, these months averaged above the record's own average.", out)
        self.assertNotIn("fit the window definition", out)
        self.assertNotIn("years in which", out)
        self.assertNotIn(". years", out)             # no lowercase fragment after a full stop

    def test_fragment_without_final_stop(self):
        out = _risk_window_text(self.rw("years in which these months averaged above the record's own average"),
                                "pond")
        self.assertIn("own average.", out)

    def test_statement_that_already_has_the_numbers(self):
        out = _risk_window_text(self.rw("these months met it in 12 of 20 years."), "pond")
        self.assertIn("These months met it in 12 of 20 years.", out)
        self.assertNotIn("In 12 of the last 20", out)

    def test_no_statement(self):
        self.assertIn("The window was met in 12 of the last 20 years.", _risk_window_text(self.rw(""), "pond"))

    def test_full_text_has_no_garbled_pieces(self):
        for lvl in LEVELS:
            with self.subTest(level=lvl):
                text = phrase(load_pond(), lvl)
                self.assertNotIn("fit the window definition", text)
                self.assertNotIn(". years in which", text)

class MeaningfulSentenceTests(unittest.TestCase):
    SENTENCE = "That is smaller than the 0.471 W m-2 per year chosen as meaningful for this variable."

    def test_sunlight_in_pond_gets_engine_sentence(self):
        r = load_pond()
        for lvl in LEVELS:
            with self.subTest(level=lvl):
                text = phrase(r, lvl)
                self.assertIn(self.SENTENCE, text)
                self.assertTrue(check_text(text, r).ok, check_text(text, r).reasons)

    def test_sentence_sits_with_the_sunlight_line_only(self):
        text = phrase(load_pond(), "plain")
        self.assertEqual(text.count(self.SENTENCE), 1)
        self.assertGreater(text.index(self.SENTENCE), text.index("Sunlight:"))

    def test_rainfall_slope_now_above_threshold_has_no_sentence(self):
        self.assertNotIn("0.0147", phrase(load_pond(), "plain"))

    def test_not_added_when_no_trend(self):
        # a no_trend axis never gets the sentence, even if its summary happened to contain it
        pond = load_pond()
        pond["axes"][0]["result"]["verdict"]["summary"] = self.SENTENCE
        text = phrase(pond, "plain")
        self.assertEqual(text.count(self.SENTENCE), 1)                 # only the sunlight one
        self.assertGreater(text.index(self.SENTENCE), text.index("Sunlight:"))

    def test_not_added_when_slope_is_meaningful(self):
        pond = load_pond()
        pond["axes"][2]["result"]["trend"]["slope_per_year"] = 0.6
        self.assertNotIn(self.SENTENCE, phrase(pond, "plain"))

    def test_not_added_without_meaningful_value_or_sentence(self):
        pond = load_pond()
        del pond["axes"][2]["result"]["meaningful"]
        self.assertNotIn(self.SENTENCE, phrase(pond, "plain"))
        pond = load_pond()
        pond["axes"][2]["result"]["verdict"]["summary"] = "A trend was detected in sunlight."
        text = phrase(pond, "plain")
        self.assertNotIn("smaller than", text)           # nothing is invented


class SignificantFigureTests(unittest.TestCase):
    def test_fmt_sig(self):
        self.assertEqual(_fmt_sig(0.00448129), "0.00448")
        self.assertEqual(_fmt_sig(-0.000312345), "-0.000312")
        self.assertEqual(_fmt_sig(0.0125), "0.0125")
        self.assertEqual(_fmt_sig(0.009996), "0.01")
        self.assertEqual(_fmt_sig(123.456), "123")
        self.assertEqual(_fmt_sig(0.0), "0")
        self.assertEqual(_fmt_sig(5), "5")

    def test_plain_and_detailed_use_three_figures_pro_keeps_full(self):
        r = load_pond()
        for lvl in ("plain", "detailed"):
            with self.subTest(level=lvl):
                text = phrase(r, lvl)
                self.assertIn("slope 0.0036 K per year", text)
                self.assertNotIn("0.00359828", text)
        self.assertIn("slope 0.00359828 K per year", phrase(r, "pro"))

    def test_guard_accepts_three_figure_form_and_still_rejects_wrong_numbers(self):
        r = axis_result("air_temp")
        self.assertTrue(check_text("No trend was found; slope 0.0036 K per year.", r).ok)
        self.assertTrue(check_text("No trend was found; slope 0.00359828 K per year.", r).ok)
        self.assertFalse(check_text("No trend was found; slope 0.0045 K per year.", r).ok)

    def test_detected_headline_three_figures(self):
        r = axis_result("air_temp")
        r["verdict"].update(code="detected", label="Trend detected")
        r["trend"]["slope_per_year"] = 0.031234567891234
        self.assertIn("changes by 0.0312 K per year", phrase(r, "plain"))
        self.assertIn("changes by 0.0312345679 K per year", phrase(r, "pro"))
        for lvl in LEVELS:
            self.assertTrue(check_text(phrase(r, lvl), r).ok)


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

class YearsNeededNoneTests(unittest.TestCase):
    def test_summary_with_unbounded_high(self):
        from contract import _summary
        text = _summary("data_limited", 0.01, "K", 46, 66.5, None)
        self.assertIn("at least 66.5 years long", text)
        self.assertNotIn("roughly", text)
        
if __name__ == "__main__":
    unittest.main()



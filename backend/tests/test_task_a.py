import json
import os
import unittest

from phrase import check_text, phrase

HERE = os.path.dirname(__file__)


def pond():
    with open(os.path.join(HERE, "real_pond.json"), encoding="utf-8") as f:
        return json.load(f)


def limited_pond(code="data_limited", label="Data-limited"):
    r = pond()
    ax = next(a for a in r["axes"] if a["name"] == "rainfall")
    ax["result"]["verdict"]["code"] = code
    ax["result"]["verdict"]["label"] = label
    ax["result"]["trend"]["fragile"] = False
    return r


class NoTrendWording(unittest.TestCase):
    def reasons(self, text):
        return check_text(text, pond()).reasons

    def test_no_change_wording_flagged(self):
        self.assertTrue(any("no-change wording" in x for x in self.reasons("Air temperature is stable.")))

    def test_hedge_exempts(self):
        text = "Air temperature is stable. That is not proof that nothing is happening."
        self.assertFalse(any("no-change wording" in x for x in self.reasons(text)))

    def test_not_found_wording_allowed(self):
        self.assertFalse(any("no-change wording" in x
                             for x in self.reasons("No trend was found for air temperature.")))


class LimitedAxes(unittest.TestCase):
    def test_found_wording_flagged(self):
        r = limited_pond()
        reasons = check_text("Rainfall shows a significant trend.", r).reasons
        self.assertTrue(any("found-trend wording" in x for x in reasons))

    def test_marker_missing_flagged(self):
        r = limited_pond()
        reasons = check_text("Rainfall: Data-limited.", r).reasons
        self.assertTrue(any("limited-evidence marker" in x for x in reasons))

    def test_template_carries_marker_and_passes_guard(self):
        for code, label in (("data_limited", "Data-limited"), ("masked", "Masked by aggregation"),
                            ("inconclusive", "Inconclusive")):
            r = limited_pond(code, label)
            for lvl in ("plain", "detailed", "pro"):
                with self.subTest(code=code, level=lvl):
                    text = phrase(r, lvl)
                    self.assertIn("Evidence is limited", text)
                    g = check_text(text, r)
                    self.assertTrue(g.ok, g.reasons)


if __name__ == "__main__":
    unittest.main()
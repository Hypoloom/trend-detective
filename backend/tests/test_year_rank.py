import unittest
import numpy as np
import pandas as pd
import yearrank


def synth():
    idx = pd.date_range("1980-01-01", "2026-03-01", freq="MS")
    rng = np.random.default_rng(1)
    return pd.Series(300 + 3 * np.sin(2 * np.pi * (idx.month - 1) / 12) + rng.normal(0, 0.3, len(idx)), index=idx)


class YearRank(unittest.TestCase):
    def test_detect(self):
        self.assertIsNotNone(yearrank.detect("Was this year hotter than usual?"))
        self.assertIsNone(yearrank.detect("Why are my oranges so small this year?"))
        self.assertIsNone(yearrank.detect("Was last summer hotter than usual?"))
        self.assertIsNone(yearrank.detect("Is it getting hotter where I live?"))

    def test_levels_pass_guard(self):
        for q in ("Was this year hotter than usual?", "Was this year wetter than normal in Kerala?",
                  "Was this year sunnier than average?"):
            for lv in ("plain", "detailed", "pro"):
                r = yearrank.answer(q, "maharashtra", lambda k, reg: synth(), lv, today_year=2026)
                self.assertIsNotNone(r, (q, lv))
                self.assertIn("2025", r["text"])
                self.assertIn("not a forecast", r["text"])

    def test_missing_data(self):
        self.assertIsNone(yearrank.answer("Was this year hotter than usual?", "kerala", lambda k, r: None))


if __name__ == "__main__":
    unittest.main()
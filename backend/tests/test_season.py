import unittest
import numpy as np
import pandas as pd
import season


def synth():
    idx = pd.date_range("1980-01-01", "2025-12-01", freq="MS")
    rng = np.random.default_rng(5)
    return pd.Series(2 + 3 * np.sin(2 * np.pi * (idx.month - 3) / 12) + rng.normal(0, 0.4, len(idx)), index=idx)


class Season(unittest.TestCase):
    def test_detect(self):
        self.assertIsNotNone(season.detect("Are the monsoon months getting wetter?"))
        self.assertIsNotNone(season.detect("Is the pre-monsoon getting hotter?"))
        self.assertIsNone(season.detect("Is the monsoon getting wetter or drier?"))
        self.assertIsNone(season.detect("Are summers getting sunnier or cloudier?"))
        self.assertIsNone(season.detect("Which region has the wettest monsoon months?"))

    def test_levels_pass_guard(self):
        s = synth()
        for q in ("Are the monsoon months getting wetter?", "Is the pre-monsoon season getting hotter in Kerala?"):
            for lv in ("plain", "detailed", "pro"):
                r = season.answer(q, "maharashtra", lambda k, reg: s, lv)
                self.assertIsNotNone(r, (q, lv))
                self.assertIn("project choice", r["text"])

    def test_missing(self):
        self.assertIsNone(season.answer("Are the monsoon months getting wetter?", "kerala", lambda k, r: None))


if __name__ == "__main__":
    unittest.main()
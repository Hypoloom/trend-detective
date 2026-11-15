import unittest
import numpy as np
import pandas as pd
import diurnal


def synth(slope, seed):
    idx = pd.date_range("1980-01-01", "2025-12-01", freq="MS")
    rng = np.random.default_rng(seed)
    return pd.Series(300 + 3 * np.sin(2 * np.pi * (idx.month - 1) / 12)
                     + slope * np.arange(len(idx)) / 12 + rng.normal(0, 0.3, len(idx)), index=idx)


class Diurnal(unittest.TestCase):
    def test_detect(self):
        self.assertTrue(diurnal.detect("Are days heating faster than nights?"))
        self.assertTrue(diurnal.detect("Is the gap between day and night temperature changing in Kerala?"))
        self.assertFalse(diurnal.detect("Is it getting hotter where I live?"))
        self.assertFalse(diurnal.detect("Which region has the hottest days and nights?"))

    def test_levels_pass_guard(self):
        data = {"t2m_max": synth(0.0, 1), "t2m_min": synth(0.05, 2)}
        for lv in ("plain", "detailed", "pro"):
            r = diurnal.answer("Are days heating faster than nights?", "maharashtra", lambda k, reg: data[k], lv)
            self.assertIsNotNone(r, lv)
            self.assertIn("Day-night temperature gap", r["text"])
            self.assertIn("project choice", r["text"])

    def test_missing(self):
        self.assertIsNone(diurnal.answer("Are days heating faster than nights?", "kerala", lambda k, r: None))


if __name__ == "__main__":
    unittest.main()
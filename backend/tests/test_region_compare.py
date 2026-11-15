import unittest
import numpy as np
import pandas as pd
import regioncompare


def synth(slope, seed):
    idx = pd.date_range("1980-01-01", "2025-12-01", freq="MS")
    rng = np.random.default_rng(seed)
    return pd.Series(300 + 3 * np.sin(2 * np.pi * (idx.month - 1) / 12)
                     + slope * np.arange(len(idx)) / 12 + rng.normal(0, 0.3, len(idx)), index=idx)


SEP = {"maharashtra": synth(0.0, 1), "rajasthan": synth(0.0, 2), "kerala": synth(0.05, 3), "gujarat": synth(0.0, 4)}
SAME = {k: synth(0.01, i) for i, k in enumerate(SEP)}


class RegionCompare(unittest.TestCase):
    def test_detect(self):
        self.assertIsNotNone(regioncompare.detect("Which region is warming fastest?"))
        self.assertIsNotNone(regioncompare.detect("Which state is getting wetter?"))
        self.assertIsNone(regioncompare.detect("Is it getting hotter where I live?"))
        self.assertIsNone(regioncompare.detect("Was this year hotter than usual?"))
        self.assertIsNone(regioncompare.detect("Why are most of my oranges small?"))

    def test_levels_pass_guard(self):
        for data, sep in ((SEP, True), (SAME, False)):
            for lv in ("plain", "detailed", "pro"):
                r = regioncompare.answer("Which region is warming fastest?", lambda k, reg: data[reg], lv)
                self.assertIsNotNone(r, (sep, lv))
                self.assertEqual(r["result"]["separated"], sep)
                if sep:
                    self.assertEqual(r["result"]["top_region"], "Kerala")
                else:
                    self.assertIn("cannot separate", r["text"])

    def test_missing_data(self):
        self.assertIsNone(regioncompare.answer("Which region is warming fastest?", lambda k, r: None))


if __name__ == "__main__":
    unittest.main()
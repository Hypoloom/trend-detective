import os
import unittest

import contract
import meaningful as m
import stream

BOX = (72, 16, 80, 21)


def _run(name):
    s = stream.get_series(name, BOX, 1980, 2025, verbose=False)
    return contract.run_analysis(s, "MERRA-2", name, "K", "Maharashtra",
                                 meaningful=m.resolve(name, s)["value"])


class WhyNoTrend(unittest.TestCase):
    def test_air_and_day_temperature(self):
        for name in ("t2m", "t2m_max"):
            with self.subTest(name=name):
                try:
                    r = _run(name)
                except FileNotFoundError:
                    self.skipTest("cache CSV missing")
                self.assertEqual(r["verdict"]["code"], "no_trend")
                t = r["verdict"]["summary"]
                for piece in ("not proof", "95% range", "chosen as meaningful",
                              "too short to tell"):
                    self.assertIn(piece, t)
                self.assertNotIn("even with a long record", t)
                lo, hi = r["trend"]["slope_ci"]
                self.assertLess(max(abs(lo), abs(hi)), r["years"]["meaningful_slope"])


if __name__ == "__main__":
    unittest.main()
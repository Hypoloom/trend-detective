from collections import Counter

import numpy as np
import pandas as pd

from engine import analyze


def synth(n_years, seed, slope, sigma=0.5, phi=0.5):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2000-01-01", periods=n_years * 12, freq="MS")
    e = np.zeros(len(idx))
    for i in range(1, len(idx)):
        e[i] = phi * e[i - 1] + rng.normal(0, sigma * np.sqrt(1 - phi**2))
    season = 5 * np.sin(2 * np.pi * (idx.month - 1) / 12)
    return pd.Series(season + slope * np.arange(len(idx)) / 12 + e, index=idx)


def run(slope, n_list=(10, 20, 30, 45), seeds=200, meaningful=None):
    print(f"\ntrue slope = {slope} per year (noise 0.5, AR1 0.5), {seeds} seeds each")
    for n in n_list:
        c = Counter(analyze(synth(n, sd, slope), meaningful=meaningful)["verdict"].split(" (")[0]
                    for sd in range(seeds))
        row = ", ".join(f"{k} {100 * v / seeds:.0f}%" for k, v in sorted(c.items()))
        print(f"  {n:>2} yrs: {row}")


if __name__ == "__main__":
    run(0.02, meaningful=0.02)
    run(0.0, meaningful=0.02)
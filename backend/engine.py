import numpy as np
import pandas as pd
from scipy import stats

INF = float("inf")


def deseasonalize(s: pd.Series) -> pd.Series:
    return s - s.groupby(s.index.month).transform("mean")


def _lag1(x):
    x = x - x.mean()
    return float(np.dot(x[:-1], x[1:]) / np.dot(x, x))


def _need(sigma, phi, w):
    # Weatherhead-style years-to-detect (formula still on our "to verify" list)
    if w <= 0:
        return INF
    return float((3.3 * sigma / w * np.sqrt((1 + phi) / (1 - phi))) ** (2 / 3))


def _fit(s: pd.Series, deseason=True):
    s = s.dropna()
    a = deseasonalize(s) if deseason else s
    t = (a.index.year + (a.index.month - 0.5) / 12).to_numpy(float)
    y = a.to_numpy(float)
    ols = stats.linregress(t, y)
    annual = a.groupby(a.index.year).mean()
    av, ay = annual.to_numpy(float), annual.index.to_numpy(float)
    ts_slope, _, ts_lo, ts_hi = stats.theilslopes(av, ay, 0.95)   # on annual means, like the test
    mk = stats.kendalltau(ay, av)
    keep = np.argsort(np.abs(av - np.median(av)))[:-3]
    p_drop3 = float(stats.kendalltau(ay[keep], av[keep]).pvalue) if len(av) >= 10 else None
    resid = y - (ols.intercept + ols.slope * t)
    phi = min(max(_lag1(resid), 0.0), 0.9)
    sigma = float(resid.std(ddof=2))
    return dict(
        years=float(t[-1] - t[0]), ols=float(ols.slope), ts=float(ts_slope),
        ts_ci=(float(ts_lo), float(ts_hi)), p_mk=float(mk.pvalue),
        sigma=sigma, phi=phi, se=float(ols.stderr), ts_se=float((ts_hi - ts_lo) / 3.92), p_drop3=p_drop3
    )


def analyze(s: pd.Series, regions: dict | None = None, alpha=0.05, deseason=True,
            meaningful=None):
    f = _fit(s, deseason)
    w = abs(f["ts"])
    n_mid = _need(f["sigma"], f["phi"], w)
    n_low = _need(f["sigma"], f["phi"], w + f["ts_se"])
    n_high = _need(f["sigma"], f["phi"], w - f["ts_se"])

    masked = False
    if regions:
        signs = set()
        for r in regions.values():
            rf = _fit(r, deseason)
            if rf["p_mk"] < alpha:
                signs.add(np.sign(rf["ts"]))
        masked = len(signs) > 1

    infl = np.sqrt((1 + f["phi"]) / (1 - f["phi"]))
    min_det = 3.3 * f["sigma"] * infl / f["years"] ** 1.5
    n_need = _need(f["sigma"], f["phi"], meaningful) if meaningful else None

    if f["p_mk"] < alpha:
        verdict = "Detected"
    elif masked:
        verdict = "Masked by aggregation"
    elif meaningful:
        verdict = ("Data-limited" if f["years"] < n_need
                   else "No trend found (not proof of absence)")
    elif f["years"] < n_low:
        verdict = "Data-limited"
    elif np.isfinite(n_high) and f["years"] >= n_high:
        verdict = "No trend found (not proof of absence)"
    else:
        verdict = "Inconclusive"

    return dict(verdict=verdict, years_have=round(f["years"], 1),
                min_detectable=float(min_det),
                years_needed_meaningful=(round(float(n_need), 1)
                                         if n_need is not None and np.isfinite(n_need) else None),
                years_needed=(round(n_low, 1), round(n_mid, 1),
                              round(n_high, 1) if np.isfinite(n_high) else None),
                **{k: f[k] for k in ("ols", "ts", "ts_ci", "p_mk", "sigma", "phi", "p_drop3")})


if __name__ == "__main__":
    # Synthetic test with a known answer: trend 0.02/yr, noise 0.5, AR(1)=0.5, plus seasonal cycle
    def synth(n_years, seed=0, slope=0.02, sigma=0.5, phi=0.5):
        rng = np.random.default_rng(seed)
        idx = pd.date_range("2000-01-01", periods=n_years * 12, freq="MS")
        e = np.zeros(len(idx))
        for i in range(1, len(idx)):
            e[i] = phi * e[i - 1] + rng.normal(0, sigma * np.sqrt(1 - phi**2))
        season = 5 * np.sin(2 * np.pi * (idx.month - 1) / 12)
        return pd.Series(season + slope * np.arange(len(idx)) / 12 + e, index=idx)

    for n in (10, 30):
        r = analyze(synth(n))
        print(n, "yrs ->", r["verdict"], "| needed (low, mid, high):", r["years_needed"],
              "| p_MK:", round(r["p_mk"], 4), "| slope:", round(r["ts"], 4))
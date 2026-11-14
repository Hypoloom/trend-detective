# scratch_endpoints.py  (read-only use of stream/contract; run from backend/)
import math, json
import numpy as np
import pandas as pd
import stream, contract
# runtime-only entries, stream.py on disk is not changed
stream.VARIABLES["t2m_max"] = dict(short_name="M2SMNXSLV", var="T2MMAX", units="K", scale=1.0)
stream.VARIABLES["t2m_min"] = dict(short_name="M2SMNXSLV", var="T2MMIN", units="K", scale=1.0)

BOX = (72, 16, 80, 21)

def theil_sen(x, y):
    n = len(x)
    sl = [(y[j] - y[i]) / (x[j] - x[i]) for i in range(n) for j in range(i + 1, n)]
    return float(np.median(sl))

def mann_kendall_p(y):
    n = len(y)
    s = sum(np.sign(y[j] - y[i]) for i in range(n) for j in range(i + 1, n))
    var = n * (n - 1) * (2 * n + 5) / 18
    z = 0.0 if s == 0 else (s - np.sign(s)) / math.sqrt(var)
    return math.erfc(abs(z) / math.sqrt(2))

def annual_trend(s, start, end):
    a = s[(s.index.year >= start) & (s.index.year <= end)]
    ann = a.groupby(a.index.year).mean()
    x, y = ann.index.values.astype(float), ann.values
    return len(ann), theil_sen(x, y), mann_kendall_p(y)

series = {k: stream.get_series(k, BOX, 1980, 2025, workers=32) for k in ("t2m", "t2m_max", "t2m_min")}

print("=== LAST 12 MONTHS ===")
print(pd.DataFrame({k: v.tail(12).round(2) for k, v in series.items()}))

print("\n=== FIRST 12 MONTHS (t2m_max) ===")
print(series["t2m_max"].head(12).round(2))

print("\n=== ANNUAL MEANS, t2m_min and t2m_max ===")
ann = pd.DataFrame({k: series[k].groupby(series[k].index.year).mean().round(2) for k in ("t2m_min", "t2m_max")})
print(ann.to_string())

print("\n=== OWN ANNUAL-MEAN TREND (Theil-Sen K/yr, Mann-Kendall p, no tie correction) ===")
for k in ("t2m_min", "t2m_max"):
    for (a, b) in [(1980, 2025), (1980, 2024), (1985, 2025), (1985, 2024)]:
        n, sl, p = annual_trend(series[k], a, b)
        print(f"{k:8s} {a}-{b}  n={n}  slope={sl:+.5f}  p={p:.4f}")

print("\n=== ENGINE RUNS (meaningful=0.02; chart removed) ===")
for k, (a, b) in [("t2m_min", (1980, 2024)), ("t2m_max", (1985, 2025))]:
    s = series[k]
    s = s[(s.index.year >= a) & (s.index.year <= b)]
    res = contract.run_analysis(s, "MERRA-2 M2SMNXSLV", k, "K", f"Maharashtra box {a}-{b}", meaningful=0.02)
    res["chart"]["points"] = f"<{len(res['chart']['points'])} points>"
    print(f"--- {k} {a}-{b} ---")
    print(json.dumps(res, indent=2, default=str))
# task2_monthly_fetch.py  (run from backend/; does NOT edit stream.py)
import time
import numpy as np
import earthaccess
import stream

BOX = (72, 16, 80, 21)

# Add the two variables in memory only
stream.VARIABLES["t2m_max"] = dict(short_name="M2SMNXSLV", var="T2MMAX", units="K", scale=1.0)
stream.VARIABLES["t2m_min"] = dict(short_name="M2SMNXSLV", var="T2MMIN", units="K", scale=1.0)

# 1) Read what the variables mean, from the file itself
earthaccess.login(persist=True)
sess = earthaccess.get_requests_https_session()
gr = earthaccess.search_data(short_name="M2SMNXSLV", temporal=("2020-01-01", "2020-01-31"), count=1)
url = next(u["URL"] for u in gr[0]["umm"]["RelatedUrls"]
           if "opendap" in u["URL"].lower()
           and not u["URL"].endswith((".html", ".dmr", ".dds", ".das")))
dmr = sess.get(url + ".dmr", timeout=60).text
for v in ["T2MMAX", "T2MMIN"]:
    i = dmr.find(f'name="{v}"')
    print(f"\n--- {v} description from the file ---")
    print(dmr[i - 20:i + 900] if i >= 0 else "not found in DMR")

# 2) Fetch the series
out = {}
for name in ["t2m_max", "t2m_min", "t2m"]:
    t0 = time.time()
    s = stream.get_series(name, BOX, 1980, 2025, workers=32, verbose=False)
    out[name] = s
    print(f"\n{name}: {len(s)} months, NaN={int(s.isna().sum())}, {time.time()-t0:.1f}s")
    print(f"  mean {s.mean():.2f} K | min {s.min():.2f} K ({s.idxmin():%Y-%m}) | max {s.max():.2f} K ({s.idxmax():%Y-%m})")

# 3) Checks
gap = out["t2m_max"] - out["t2m_min"]
print(f"\nDay-night gap (max minus min): mean {gap.mean():.2f} K | min {gap.min():.2f} | max {gap.max():.2f}")
print("Mean gap by calendar month:")
print(gap.groupby(gap.index.month).mean().round(2).to_string())
ok = (out["t2m_min"] < out["t2m"]) & (out["t2m"] < out["t2m_max"])
print(f"\nMonths where T2MMIN < T2M < T2MMAX: {int(ok.sum())} of {len(ok)}")
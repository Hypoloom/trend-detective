# task2_trends.py  (run from backend/; does NOT edit stream.py)
# Usage: python task2_trends.py 0.02
import sys
import stream, contract

BOX = (72, 16, 80, 21)
meaningful = float(sys.argv[1]) if len(sys.argv) > 1 else 0.02   # TEST VALUE, K per year

stream.VARIABLES["t2m_max"] = dict(short_name="M2SMNXSLV", var="T2MMAX", units="K", scale=1.0)
stream.VARIABLES["t2m_min"] = dict(short_name="M2SMNXSLV", var="T2MMIN", units="K", scale=1.0)

mx = stream.get_series("t2m_max", BOX, 1980, 2025, workers=32, verbose=False)   # from cache
mn = stream.get_series("t2m_min", BOX, 1980, 2025, workers=32, verbose=False)   # from cache
series = {
    "T2MMAX (day-time)": mx,
    "T2MMIN (night-time)": mn,
    "Gap (max minus min)": mx - mn,
}

print(f"meaningful (test value): {meaningful} K per year\n")
for name, s in series.items():
    r = contract.run_analysis(s, "MERRA-2 M2SMNXSLV", name, "K",
                              "Maharashtra box (72,16,80,21)", meaningful=meaningful)
    t, y = r["trend"], r["years"]
    print(f"=== {name}")
    print(f"  verdict: {r['verdict']['code']}")
    print(f"  slope (Theil-Sen): {t['slope_per_year']} K/yr | OLS: {t['ols_slope_per_year']}")
    print(f"  slope 95% range: {t['slope_ci']}")
    print(f"  p-value: {t['p_value']} | min detectable slope: {t['min_detectable_slope']}")
    print(f"  years have: {y['have']} | needed for meaningful: {y['needed_for_meaningful']}")
    print(f"  noise sigma: {r['noise']['sigma']} | lag-1 autocorr: {r['noise']['lag1_autocorr']}\n")
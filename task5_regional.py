# task5_regional.py  (run from backend/ or with PYTHONPATH pointing to backend/)
import sys, time, json
import numpy as np
import stream, contract

BOX = (72, 16, 80, 21)

t0 = time.time()
s = stream.get_series("t2m", BOX, 1980, 2025, workers=32)
print("seconds:", round(time.time() - t0, 1), "| months:", len(s), "| NaN:", int(s.isna().sum()))
print("mean K:", round(float(s.mean()), 2), "| min:", round(float(s.min()), 2), "| max:", round(float(s.max()), 2))
print("coldest:", s.idxmin(), "| warmest:", s.idxmax())

# simple check on yearly averages (not the engine)
ann = s.groupby(s.index.year).mean()
print("simple slope on yearly means, K/yr:", round(float(np.polyfit(ann.index, ann.values, 1)[0]), 4))

# same check after removing the seasonal cycle
anom = s - s.groupby(s.index.month).transform("mean")
x = anom.index.year + (anom.index.month - 1) / 12
print("simple slope on seasonal-free monthly values, K/yr:", round(float(np.polyfit(x, anom.values, 1)[0]), 4))

# `meaningful` = smallest trend (K per year) we call meaningful. TEST VALUE, not a scientific choice.
# Usage: python task5_regional.py 0.02
meaningful = float(sys.argv[1]) if len(sys.argv) > 1 else 0.02
print("\nmeaningful (test value), K/yr:", meaningful)

res = contract.run_analysis(s, "MERRA-2 M2TMNXSLV", "t2m", "K",
                            "Maharashtra box (72,16,80,21)", meaningful=meaningful)

full = json.dumps(res, indent=2, default=str)
with open(f"out_task5_result_{meaningful}.json", "w") as f:
    f.write(full)                                  # full JSON, local only, do not commit

res["chart"]["points"] = f"<{len(res['chart']['points'])} points>"   # shorter print
print(json.dumps(res, indent=2, default=str))
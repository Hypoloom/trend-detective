# scratch_swgdn_stats.py  (run from backend/; stream.py on disk is not edited)
import numpy as np
import stream

stream.VARIABLES["swgdn"] = {"short_name": "M2TMNXRAD", "var": "SWGDN", "units": "W m-2", "scale": 1.0}

BOX = (72, 16, 80, 21)
s = stream.get_series("swgdn", BOX, 1980, 2025, workers=32)

print("months:", len(s), "| NaN:", int(s.isna().sum()))
print("mean:", round(float(s.mean()), 1), "| min:", round(float(s.min()), 1), "| max:", round(float(s.max()), 1))
print("lowest month:", s.idxmin(), "| highest month:", s.idxmax())
print("values above 1e6 (possible fill values):", int((s > 1e6).sum()))

print("\nMean by calendar month (W m-2):")
print(s.groupby(s.index.month).mean().round(1).to_string())

anom = s - s.groupby(s.index.month).transform("mean")
x = anom.index.year + (anom.index.month - 1) / 12
print("\nsimple slope, seasonal-free monthly, W m-2 per year:", round(float(np.polyfit(x, anom.values, 1)[0]), 4))
# scratch_swgdn_engine.py  (run from backend/; stream.py and contract.py on disk are not edited)
import json
import stream, contract

stream.VARIABLES["swgdn"] = {"short_name": "M2TMNXRAD", "var": "SWGDN", "units": "W m-2", "scale": 1.0}

s = stream.get_series("swgdn", (72, 16, 80, 21), 1980, 2025, workers=32)

# 2% of the mean per decade, converted to W m-2 per year (placeholder, unsourced)
meaningful = 0.02 * float(s.mean()) / 10
print("meaningful, W m-2/yr:", round(meaningful, 4))

res = contract.run_analysis(s, "MERRA-2 M2TMNXRAD", "swgdn", "W m-2",
                            "Maharashtra box (72,16,80,21)", meaningful=meaningful)
res["chart"]["points"] = f"<{len(res['chart']['points'])} points>"
print(json.dumps(res, indent=2, default=str))
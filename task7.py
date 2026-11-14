import json
import stream, contract

s = stream.get_series("t2m", (-180, -90, 180, 90), 1980, 2025)
print(len(s), "months")

out = contract.run_analysis(
    s, "MERRA-2 M2TMNXSLV", "T2M", "K",
    "Global (-180,-90,180,90)", meaningful=0.02,
)
out["chart"]["points"] = f"<{len(out['chart']['points'])} points>"
print(json.dumps(out, indent=2))
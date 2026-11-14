# task1_swgdn.py  (run from backend/)
import time
import earthaccess
import stream

earthaccess.login(persist=True)

# Step 1: does the monthly radiation collection exist?
for sn in ["M2TMNXRAD", "M2T1NXRAD"]:
    res = earthaccess.search_datasets(short_name=sn)
    print(f"{sn}: {len(res)} collection(s)")
    for c in res[:1]:
        print("  title:", c["umm"]["EntryTitle"], "| version:", c["umm"].get("Version"))

# Step 2: add the variable in memory only (stream.py is not edited)
stream.VARIABLES["swgdn"] = {
    "short_name": "M2TMNXRAD",
    "var": "SWGDN",
    "units": "W m-2",
    "scale": 1.0,
}

# Step 3: fetch and summarise
BOX = (72, 16, 80, 21)
t0 = time.time()
s = stream.get_series("swgdn", BOX, 1980, 2025, workers=32)
print("seconds:", round(time.time() - t0, 1))
print("type:", type(s).__name__, "| months:", len(s))
print("first:", s.index[0], "| last:", s.index[-1])
print("NaN count:", int(s.isna().sum()))
print(s.describe().round(2).to_string())
print("min:", s.idxmin(), round(s.min(), 1), "| max:", s.idxmax(), round(s.max(), 1))
print("\nMean by calendar month:")
print(s.groupby(s.index.month).mean().round(1).to_string())
s.to_csv("swgdn_72_16_80_21.csv")   # local only, do not commit
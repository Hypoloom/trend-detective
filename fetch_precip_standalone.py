import os
import shutil
import sys
import time

import earthaccess
import h5py
import numpy as np
import pandas as pd

SHORT = "M2TMNXFLX"
VAR = "PRECTOTCORR"
BOX = (72, 16, 80, 21)  # west, south, east, north
TEST = len(sys.argv) > 1 and sys.argv[1] == "test"
START, END = ("1990-01-01", "1990-12-31") if TEST else ("1980-01-01", "2025-12-31")
OUT = "precip_test_mmday.csv" if TEST else "precip_mmday.csv"


def read_one(path):
    """Cos-lat weighted box mean of PRECTOTCORR for one monthly file, in mm/day."""
    w, s, e, n = BOX
    with h5py.File(path, "r") as h:
        lat, lon = h["lat"][:], h["lon"][:]
        i = np.where((lat >= s) & (lat <= n))[0]
        j = np.where((lon >= w) & (lon <= e))[0]
        a = h[VAR][0, i[0]:i[-1] + 1, j[0]:j[-1] + 1].astype("float64")
    a[a > 1e14] = np.nan  # MERRA-2 fill value is 1e15
    wts = np.cos(np.deg2rad(lat[i]))
    val = float(np.nansum(np.nanmean(a, axis=1) * wts) / wts.sum()) * 86400  # -> mm/day
    ym = os.path.basename(str(path))[-10:-4]  # ...YYYYMM.nc4
    return pd.Timestamp(year=int(ym[:4]), month=int(ym[4:]), day=1), val


def main():
    t0 = time.time()
    earthaccess.login(persist=True)
    os.makedirs("year_cache", exist_ok=True)
    tag = "_".join(str(b) for b in BOX)
    rows = []
    for year in range(int(START[:4]), int(END[:4]) + 1):
        part = f"year_cache/{SHORT}_{VAR}_mmday_{tag}_{year}.csv"
        if os.path.exists(part):
            p = pd.read_csv(part, index_col=0, parse_dates=True).iloc[:, 0]
            rows += list(zip(p.index, p.values))
            print(year, "loaded from year_cache", flush=True)
            continue
        res = earthaccess.search_data(short_name=SHORT,
                                      temporal=(f"{year}-01-01", f"{year}-12-31"),
                                      bounding_box=BOX)
        folder = f"data_cache/{SHORT}_{year}"
        files = earthaccess.download(res, local_path=folder, threads=8)
        year_rows = [read_one(f) for f in files]
        shutil.rmtree(folder, ignore_errors=True)
        pd.Series(dict(year_rows)).to_csv(part)
        rows += year_rows
        print(year, "done", round(time.time() - t0, 1), "s", flush=True)

    times, vals = zip(*rows)
    s = pd.Series(vals, index=pd.DatetimeIndex(times), name="PRECTOTCORR_mm_per_day").sort_index()
    s = s[~s.index.duplicated()]
    s.index.freq = "MS"
    s.to_csv(OUT, index_label="time")

    print("\n", len(s), "months;", "min", round(s.min(), 3), "max", round(s.max(), 3),
          "mean", round(s.mean(), 3), "mm/day; nan:", int(s.isna().sum()))
    print("monthly climatology (mm/day):")
    print(s.groupby(s.index.month).mean().round(2).to_string())
    print(round(time.time() - t0, 1), "seconds; wrote", OUT)


if __name__ == "__main__":
    main()
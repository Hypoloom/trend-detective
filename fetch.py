import os
import shutil
import time

import earthaccess
import numpy as np
import pandas as pd
import h5py


def _one(f, var, box):
    w, s_, e, n = box
    with h5py.File(f, "r") as h:
        lat, lon = h["lat"][:], h["lon"][:]
        i = np.where((lat >= s_) & (lat <= n))[0]
        j = np.where((lon >= w) & (lon <= e))[0]
        a = h[var][0, i[0]:i[-1] + 1, j[0]:j[-1] + 1].astype("float64")
    a[a > 1e14] = np.nan  # MERRA-2 fill value is 1e15
    wts = np.cos(np.deg2rad(lat[i]))
    val = float(np.nansum(np.nanmean(a, axis=1) * wts) / wts.sum())
    ym = os.path.basename(str(f))[-10:-4]
    return pd.Timestamp(year=int(ym[:4]), month=int(ym[4:]), day=1), val

def fetch_series(short_name, var, box, start, end, cache=None):
    """Box-averaged (cos-lat weighted) monthly series from a MERRA-2 monthly product.
    box = (west, south, east, north). One year at a time; finished years are saved
    in year_cache/ so a rerun resumes. Raw files are deleted after reading."""
    if cache and os.path.exists(cache):
        s = pd.read_csv(cache, index_col=0, parse_dates=True).iloc[:, 0]
        s.index.freq = "MS"
        return s
    t0 = time.time()
    earthaccess.login(persist=True)
    os.makedirs("year_cache", exist_ok=True)
    boxtag = "_".join(str(b) for b in box)
    rows = []
    for year in range(int(start[:4]), int(end[:4]) + 1):
        part = f"year_cache/{short_name}_{var}_{boxtag}_{year}.csv"
        if os.path.exists(part):
            p = pd.read_csv(part, index_col=0, parse_dates=True).iloc[:, 0]
            rows += list(zip(p.index, p.values))
            print(year, "loaded from year_cache", flush=True)
            continue
        y0 = max(start, f"{year}-01-01")
        y1 = min(end, f"{year}-12-31")
        res = earthaccess.search_data(short_name=short_name, temporal=(y0, y1),
                                      bounding_box=box)
        folder = f"data_cache/{short_name}_{year}"
        files = earthaccess.download(res, local_path=folder, threads=8)
        year_rows = [_one(f, var, box) for f in files]
        shutil.rmtree(folder, ignore_errors=True)
        pd.Series(dict(year_rows)).to_csv(part)
        rows += year_rows
        print(year, "done", round(time.time() - t0, 1), "s", flush=True)
    times, vals = zip(*rows)
    out = pd.Series(vals, index=pd.DatetimeIndex(times), name=var).sort_index()
    out = out[~out.index.duplicated()]
    out.index.freq = "MS"
    if cache:
        out.to_csv(cache)
    return out


if __name__ == "__main__":
    t0 = time.time()
    s = fetch_series("M2TMNXSLV", "T2M", (72, 16, 80, 21), "1980-01-01", "2025-12-31",
                     cache="t2m_fetched.csv")
    print(s.head(3), "\n", len(s), "months")
    print(round(time.time() - t0, 1), "seconds")
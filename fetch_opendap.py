"""
fetch_opendap.py -- drop-in replacement for fetch.py (same fetch_series signature).

Old way: download each whole global file (~52 MB), read the box, delete the file.
New way: ask the NASA server (OPeNDAP) for ONLY the grid cells inside the box.
         Each month then transfers a few KB instead of 52 MB.

Besides the box-average series (same CSV as before), it also saves the small
grid "cube" (month x lat x lon) of the box. With the cube saved you can later
average ANY smaller box inside it locally, with no NASA call.

Needs: earthaccess, numpy, pandas, xarray, and (pydap OR netCDF4).
First run:  python fetch_opendap.py test     (one month, prints time + value)
Then:       python fetch_opendap.py          (everything, resumes if stopped)
"""
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import earthaccess
import numpy as np
import pandas as pd

CACHE_ROOT = "cube_cache"   # one tiny .npz per month, so a rerun resumes
WORKERS = 8                 # parallel requests; lower this if NASA throttles you


def _opendap_url(g):
    """OPeNDAP address of one granule. Prefer the link NASA lists in the
    granule metadata; fall back to rewriting the normal download link."""
    for u in g["umm"].get("RelatedUrls", []):
        url = u.get("URL", "")
        if u.get("Subtype") == "OPENDAP DATA" or "/opendap/" in url:
            return url[:-5] if url.endswith(".html") else url
    return g.data_links()[0].replace("/data/", "/opendap/", 1)


def _open(url, session):
    import xarray as xr
    errs = []
    for engine, kw in (("pydap", {"session": session}), ("netcdf4", {})):
        try:
            return xr.open_dataset(url, engine=engine, **kw)
        except Exception as e:  # try the next engine
            errs.append(f"{engine}: {e}")
    raise RuntimeError(" | ".join(errs))


def _box_slices(lat, lon, box):
    """Index range of the grid cells inside box = (west, south, east, north).
    Same rule as the old fetch.py (cell centres inside the box, edges included)."""
    w, s, e, n = box
    i = np.where((lat >= s) & (lat <= n))[0]
    j = np.where((lon >= w) & (lon <= e))[0]
    return slice(int(i[0]), int(i[-1]) + 1), slice(int(j[0]), int(j[-1]) + 1)


def _box_mean(a, lat_sub):
    """cos(latitude)-weighted mean of one month's box (same maths as old fetch.py)."""
    a = np.where(a > 1e14, np.nan, a)   # MERRA-2 fill value is 1e15
    w = np.cos(np.deg2rad(lat_sub))
    return float(np.nansum(np.nanmean(a, axis=1) * w) / w.sum())


def _month_id(url):
    return os.path.basename(url.split("?")[0])[-10:-4]   # e.g. "198001"


def _one_month(g, var, box, session, folder):
    url = _opendap_url(g)
    ym = _month_id(url)
    path = os.path.join(folder, f"{ym}.npz")
    if os.path.exists(path):
        d = np.load(path)
        return ym, d["a"], d["lat"], d["lon"]
    last = None
    for attempt in range(3):
        try:
            ds = _open(url, session)
            lat, lon = ds["lat"].values, ds["lon"].values
            si, sj = _box_slices(lat, lon, box)
            # only this slice crosses the network
            a = ds[var].isel(time=0, lat=si, lon=sj).values.astype("float64")
            ds.close()
            np.savez_compressed(path, a=a, lat=lat[si], lon=lon[sj])
            return ym, a, lat[si], lon[sj]
        except Exception as e:
            last = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"{ym} failed after 3 tries: {last}")


def fetch_series(short_name, var, box, start, end, cache=None, cube_out=True):
    """Box-averaged (cos-lat weighted) monthly series, fetched with OPeNDAP.
    box = (west, south, east, north). Returns a pandas Series like fetch.py did."""
    if cache and os.path.exists(cache):
        s = pd.read_csv(cache, index_col=0, parse_dates=True).iloc[:, 0]
        s.index.freq = "MS"
        return s

    t0 = time.time()
    earthaccess.login(persist=True)
    session = earthaccess.get_requests_https_session()
    boxtag = "_".join(str(b) for b in box)
    folder = os.path.join(CACHE_ROOT, f"{short_name}_{var}_{boxtag}")
    os.makedirs(folder, exist_ok=True)

    res = earthaccess.search_data(short_name=short_name, temporal=(start, end),
                                  bounding_box=box)
    print(len(res), "monthly files found", flush=True)

    done = {}
    with ThreadPoolExecutor(WORKERS) as ex:
        futs = [ex.submit(_one_month, g, var, box, session, folder) for g in res]
        for k, f in enumerate(as_completed(futs), 1):
            ym, a, lat, lon = f.result()
            done[ym] = (a, lat, lon)
            if k % 24 == 0 or k == len(futs):
                print(f"{k}/{len(futs)} months", round(time.time() - t0, 1), "s",
                      flush=True)

    yms = sorted(done)
    times = [pd.Timestamp(year=int(m[:4]), month=int(m[4:]), day=1) for m in yms]
    lat, lon = done[yms[0]][1], done[yms[0]][2]
    cube = np.stack([done[m][0] for m in yms])          # (months, lat, lon)

    if cube_out:
        np.savez_compressed(f"{short_name}_{var}_{boxtag}_cube.npz", cube=cube,
                            lat=lat, lon=lon,
                            months=np.array([t.strftime("%Y-%m") for t in times]))

    vals = [_box_mean(cube[k], lat) for k in range(len(yms))]
    out = pd.Series(vals, index=pd.DatetimeIndex(times), name=var).sort_index()
    out = out[~out.index.duplicated()]
    out.index.freq = "MS"
    if cache:
        out.to_csv(cache)
    return out


if __name__ == "__main__":
    t0 = time.time()
    maha = (72, 16, 80, 21)
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # one month only: check it works, how fast, and compare with Giovanni
        s = fetch_series("M2TMNXSLV", "T2M", maha, "1980-01-01", "1980-01-31")
        print(s)
        print("seconds for ONE month:", round(time.time() - t0, 1))
    else:
        s = fetch_series("M2TMNXSLV", "T2M", maha, "1980-01-01", "2025-12-31",
                         cache="t2m_fetched.csv")
        print(s.head(3), "\n", len(s), "months")
        print(round(time.time() - t0, 1), "seconds")

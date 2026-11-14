"""stream.py - live, server-side-subset MERRA-2 monthly series via OPeNDAP (DAP4).
Usage:  python stream.py probe
        python stream.py <name> <west> <south> <east> <north> <start_year> <end_year>
"""
import os, sys, time
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
import earthaccess
from pydap.client import open_url
from pydap.net import create_session

# One entry per variable the engine can use. Add radiation etc. here later.
VARIABLES = {
    "t2m":    dict(short_name="M2TMNXSLV", var="T2M",         units="K",      scale=1.0),
    "precip": dict(short_name="M2TMNXFLX", var="PRECTOTCORR", units="mm/day", scale=86400.0),
    "sunlight": dict(short_name="M2TMNXRAD", var="SWGDN",     units="W m-2",  scale=1.0),
    "t2m_min": dict(short_name="M2SMNXSLV", var="T2MMIN",     units="K",      scale=1.0),
    "t2m_max": dict(short_name="M2SMNXSLV", var="T2MMAX",     units="K",      scale=1.0),
}

LAT = -90.0 + 0.5 * np.arange(361)
LON = -180.0 + 0.625 * np.arange(576)
FILL = 1e14          # anything above this is fill (fill value is 1e15)
_session = None
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stream_cache")

def _get_session():
    global _session
    if _session is None:
        auth = earthaccess.login(persist=True)
        _session = create_session(session=auth.get_session())
    return _session


def _index_box(box):
    w, s, e, n = box
    if w > e:
        raise NotImplementedError("box crossing the antimeridian")
    i = np.where((LAT >= s) & (LAT <= n))[0]
    j = np.where((LON >= w) & (LON <= e))[0]
    if len(i) == 0 or len(j) == 0:
        raise ValueError("box contains no grid cells")
    return int(i[0]), int(i[-1]), int(j[0]), int(j[-1])


def _list_months(short_name, start, end):
    res = earthaccess.search_data(short_name=short_name,
                                  temporal=(f"{start}-01-01", f"{end}-12-31"), count=-1)
    out = []
    for g in res:
        t = g["umm"]["TemporalExtent"]["RangeDateTime"]["BeginningDateTime"]
        month = pd.Timestamp(t).tz_localize(None).replace(day=1).normalize()
        url = None
        for u in g["umm"].get("RelatedUrls", []):
            link = u.get("URL", "")
            if "opendap" in link.lower() and not link.endswith((".html", ".dmr", ".dds", ".das")):
                url = link
                break
        if url is None:
            raise RuntimeError("no OPeNDAP link in granule: "
                               + str([u.get("URL") for u in g["umm"].get("RelatedUrls", [])]))
        out.append((month, url))
    return sorted(out)


def _one_month(url, var, ib, scale):
    i0, i1, j0, j1 = ib
    ce = f"?dap4.ce=/{var}[0][{i0}:1:{i1}][{j0}:1:{j1}]"
    ds = open_url(url + ce, protocol="dap4", session=_get_session())
    x = ds[var][:]
    a = np.asarray(getattr(x, "data", x), dtype=float).reshape(i1 - i0 + 1, j1 - j0 + 1)
    a[a >= FILL] = np.nan
    w = np.cos(np.radians(LAT[i0:i1 + 1]))[:, None] * np.ones_like(a)
    ok = ~np.isnan(a)
    if not ok.any():
        return np.nan
    return float((a[ok] * w[ok]).sum() / w[ok].sum()) * scale


def get_series(name, box, start, end, workers=32, cache_dir=CACHE_DIR, verbose=True):
    """Monthly area-mean series (pd.Series, month-start index) for VARIABLES[name] over box."""
    cfg = VARIABLES[name]
    ib = _index_box(box)
    os.makedirs(cache_dir, exist_ok=True)
    key = f"{name}_{'_'.join(f'{float(b):g}' for b in box)}.csv"
    path = os.path.join(cache_dir, key)
    have = pd.Series(dtype=float)
    if os.path.exists(path):
        d = pd.read_csv(path, parse_dates=["time"])
        have = pd.Series(d["value"].values, index=pd.DatetimeIndex(d["time"]))
    todo = [(m, u) for m, u in _list_months(cfg["short_name"], start, end) if m not in have.index]
    t0 = time.time()
    if todo:
        def work(mu):
            return mu[0], _one_month(mu[1], cfg["var"], ib, cfg["scale"])
        new = {}
        with ThreadPoolExecutor(max_workers=workers) as ex:
            for k, (m, v) in enumerate(ex.map(work, todo), 1):
                new[m] = v
                if verbose and (k % 12 == 0 or k == len(todo)):
                    print(f"  {name}: {k}/{len(todo)} months, {time.time()-t0:.0f}s", flush=True)
        have = pd.concat([have, pd.Series(new)]).sort_index()
        pd.DataFrame({"time": have.index, "value": have.values}).to_csv(path, index=False)
    have = have[(have.index >= f"{start}-01-01") & (have.index <= f"{end}-12-31")]
    have.index.name = "time"
    return have


def _probe():
    box = (72, 16, 80, 21)
    cdir = "stream_cache_probe"
    t = time.time()
    s = get_series("t2m", box, 1980, 1980, workers=1, cache_dir=cdir)
    print(f"1980, workers=1: {len(s)} months in {time.time()-t:.1f}s, NaN={int(s.isna().sum())}")
    print(s.round(3).to_string())
    from loaders import load_giovanni_csv
    g = load_giovanni_csv(os.path.join("sample", "t2m.csv"))
    d = (s.iloc[:3] - g.iloc[:3]).abs()
    print("max |stream - Giovanni| Jan-Mar 1980 (K):", float(d.max()))
    t = time.time()
    s2 = get_series("t2m", box, 1981, 1981, workers=4, cache_dir=cdir)
    print(f"1981, workers=4: {len(s2)} months in {time.time()-t:.1f}s")


def _bench():
    box = (72, 16, 80, 21)
    ib = _index_box(box)
    cfg = VARIABLES["t2m"]
    t = time.time()
    months = _list_months(cfg["short_name"], 1982, 1982)
    print(f"search (12 granules): {time.time()-t:.1f}s")
    _get_session()
    i0, i1, j0, j1 = ib
    url = months[0][1] + f"?dap4.ce=/{cfg['var']}[0][{i0}:1:{i1}][{j0}:1:{j1}]"
    t = time.time()
    ds = open_url(url, protocol="dap4", session=_get_session())
    print(f"open_url (metadata): {time.time()-t:.1f}s")
    t = time.time()
    _ = ds[cfg["var"]][:]
    print(f"data read: {time.time()-t:.1f}s")
    for w, yr in ((8, 1983), (16, 1984)):
        t = time.time()
        s = get_series("t2m", box, yr, yr, workers=w, cache_dir="stream_cache_probe", verbose=False)
        print(f"{yr}, workers={w}: {len(s)} months in {time.time()-t:.1f}s")

def _bench2():
    box = (72, 16, 80, 21)
    for w, (y0, y1) in ((16, (1985, 1988)), (32, (1989, 1992)), (64, (1993, 1996))):
        t = time.time()
        try:
            s = get_series("t2m", box, y0, y1, workers=w, cache_dir="stream_cache_probe", verbose=False)
            print(f"workers={w}: {len(s)} months, NaN={int(s.isna().sum())}, {time.time()-t:.1f}s", flush=True)
        except Exception as e:
            print(f"workers={w}: FAILED after {time.time()-t:.1f}s: {type(e).__name__}: {e}", flush=True)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "bench2":
        _bench2()
    elif len(sys.argv) > 1 and sys.argv[1] == "bench":
        _bench()
    elif len(sys.argv) > 1 and sys.argv[1] == "probe":
        _probe()
    else:
        nm = sys.argv[1]
        w, s_, e, n = map(float, sys.argv[2:6])
        y0, y1 = int(sys.argv[6]), int(sys.argv[7])
        ser = get_series(nm, (w, s_, e, n), y0, y1)
        print(ser.describe())

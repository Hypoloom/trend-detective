# task2_timing.py  (uses stream.py read-only)
# Run:  python task2_timing.py M2SDNXSLV T2MMAX 1 2020
#       python task2_timing.py M2T1NXSLV T2M 24 2020
import sys, time
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import earthaccess
from pydap.client import open_url
import stream

SHORT, VAR, NT = sys.argv[1], sys.argv[2], int(sys.argv[3])
YEAR = int(sys.argv[4]) if len(sys.argv) > 4 else 2020
WORKERS = 32
BOX = (72, 16, 80, 21)
IB = stream._index_box(BOX)


def list_files(short, year):
    res = earthaccess.search_data(short_name=short,
                                  temporal=(f"{year}-01-01", f"{year}-12-31"), count=-1)
    out = []
    for g in res:
        t = g["umm"]["TemporalExtent"]["RangeDateTime"]["BeginningDateTime"]
        url = next((u["URL"] for u in g["umm"].get("RelatedUrls", [])
                    if "opendap" in u["URL"].lower()
                    and not u["URL"].endswith((".html", ".dmr", ".dds", ".das"))), None)
        if url is None:
            raise RuntimeError("no OPeNDAP link for granule at " + t)
        out.append((t, url))
    return sorted(out)


def fetch(url):
    i0, i1, j0, j1 = IB
    ce = f"?dap4.ce=/{VAR}[0:1:{NT-1}][{i0}:1:{i1}][{j0}:1:{j1}]"
    ds = open_url(url + ce, protocol="dap4", session=stream._get_session())
    x = ds[VAR][:]
    a = np.asarray(getattr(x, "data", x), dtype=float).reshape(NT, i1 - i0 + 1, j1 - j0 + 1)
    a[a >= stream.FILL] = np.nan
    w = np.cos(np.radians(stream.LAT[i0:i1 + 1]))[None, :, None] * np.ones_like(a)
    ok = ~np.isnan(a)
    num = (np.where(ok, a, 0.0) * w).sum(axis=(1, 2))
    den = np.where(ok, w, 0.0).sum(axis=(1, 2))
    return num / np.where(den == 0, np.nan, den)


stream._get_session()                      # log in first so it is not timed

t0 = time.time()
files = list_files(SHORT, YEAR)
t_list = time.time() - t0
print(f"{SHORT} {VAR} {YEAR}: {len(files)} files, listing took {t_list:.1f}s")

t0 = time.time()
first = fetch(files[0][1])
print(f"one file, one at a time: {time.time()-t0:.2f}s | values per file: {len(first)}")

t0 = time.time()
with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    res = list(ex.map(fetch, [u for _, u in files]))
total = time.time() - t0
vals = np.concatenate(res)

per_file = total / len(files)
print(f"all {len(files)} files, {WORKERS} workers: {total:.1f}s ({per_file:.3f}s per file)")
print(f"NaN: {int(np.isnan(vals).sum())} of {len(vals)}")
print(f"values (K): mean {np.nanmean(vals):.2f}, min {np.nanmin(vals):.2f}, max {np.nanmax(vals):.2f}")
est = per_file * len(files) * 46 / 60
print(f"ESTIMATE for 46 years: about {len(files)*46} files, {est:.0f} minutes")
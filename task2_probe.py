# task2_probe.py  (login required; does not use stream.py)
import earthaccess

earthaccess.login(persist=True)
sess = earthaccess.get_requests_https_session()

for sn in ["M2T1NXSLV", "M2SDNXSLV"]:
    cols = earthaccess.search_datasets(short_name=sn)
    print(f"\n=== {sn}: {len(cols)} collection(s)")
    if not cols:
        continue
    print("title:", cols[0]["umm"]["EntryTitle"], "| version:", cols[0]["umm"].get("Version"))

    gr = earthaccess.search_data(short_name=sn, temporal=("2020-07-01", "2020-07-03"), count=3)
    print("granules found:", len(gr))
    if not gr:
        continue
    sz = gr[0].size
    sz = sz() if callable(sz) else sz   # property in newer earthaccess, method in older
    print("size MB (first):", sz)

    urls = [u["URL"] for u in gr[0]["umm"].get("RelatedUrls", []) if "opendap" in u["URL"].lower()]
    print("opendap urls:", urls[:2])
    if urls:
        dds = urls[0].replace(".html", "") + ".dds"
        try:
            txt = sess.get(dds, timeout=60).text
            for v in ["T2M", "T2MMAX", "T2MMIN", "T2MMEAN"]:
                print(f"  {v} in DDS:", v in txt)
        except Exception as e:
            print("  DDS fetch failed:", repr(e))
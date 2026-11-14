# task2_monthly_probe.py  (login required; does not use stream.py)
# Checks whether a MONTHLY min/max temperature product exists.
import earthaccess

earthaccess.login(persist=True)
sess = earthaccess.get_requests_https_session()

SHORT = "M2SMNXSLV"
cols = earthaccess.search_datasets(short_name=SHORT)
print(f"=== {SHORT}: {len(cols)} collection(s)")
if cols:
    print("title:", cols[0]["umm"]["EntryTitle"], "| version:", cols[0]["umm"].get("Version"))

    gr = earthaccess.search_data(short_name=SHORT, temporal=("2020-01-01", "2020-12-31"), count=-1)
    print("granules found for 2020:", len(gr), "(expect 12)")
    if gr:
        sz = gr[0].size
        sz = sz() if callable(sz) else sz
        print("size MB (first):", sz)
        urls = [u["URL"] for u in gr[0]["umm"].get("RelatedUrls", [])
                if "opendap" in u["URL"].lower()
                and not u["URL"].endswith((".html", ".dmr", ".dds", ".das"))]
        print("opendap url:", urls[:1])
        if urls:
            try:
                txt = sess.get(urls[0] + ".dds", timeout=60).text
                for v in ["T2M", "T2MMAX", "T2MMIN", "T2MMEAN"]:
                    print(f"  {v} in DDS:", v in txt)
            except Exception as e:
                print("  DDS fetch failed:", repr(e))
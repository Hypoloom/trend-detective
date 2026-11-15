"""regioncompare.py - 'Which region is warming fastest?': rank the four regions by estimated yearly change.
A leader is named only if its 95% range does not overlap the others. Text is checked by phrase.check_text."""
import re

import contract
import meaningful
import phrase

REGIONS = {"maharashtra": "Maharashtra", "rajasthan": "Rajasthan", "kerala": "Kerala", "gujarat": "Gujarat"}
# (stream key, label, units, words, descending) - checked in this order
VARS = [
    ("t2m_min", "night-time air temperature", "K", ("night", "nights", "overnight", "minimum"), True),
    ("t2m_max", "day-time air temperature", "K", ("daytime", "maximum", "afternoon"), True),
    ("precip", "rainfall", "mm/day", ("wetter", "wettest", "rain", "rainy", "rainfall", "precipitation"), True),
    ("precip", "rainfall", "mm/day", ("drier", "driest", "drying", "dry"), False),
    ("sunlight", "sunlight", "W m-2", ("sunnier", "sunniest", "brighter", "sunlight", "sunshine", "sunny"), True),
    ("sunlight", "sunlight", "W m-2", ("dimming", "dimmer", "cloudier", "cloudy"), False),
    ("t2m", "air temperature", "K", ("hotter", "hottest", "warming", "warmer", "warmest", "heating", "heat",
                                     "temperature", "hot", "warm"), True),
]
COMPARE = re.compile(r"\b(?:which|what) (?:region|regions|state|states|place|places|area|areas)\b|"
                     r"\bfastest\b|\bcompare[sd]?\b|\bcomparison\b|\bmost\b|\bwhere is it\b", re.I)
SKIP = ("pond", "algae", "orange", "oranges", "citrus", "lemon", "fruit", "apple", "apples", "cherry",
        "blossom", "flower", "flowers", "usual", "normal")


def _words(q):
    return re.findall(r"[a-z]+", q.lower())


def detect(question):
    w = _words(question)
    if not COMPARE.search(question) or any(x in SKIP for x in w):
        return None
    for key, label, units, words, desc in VARS:
        if any(x in words for x in w):
            return key, label, units, desc
    return None


def answer(question, get, level="plain"):
    """get(stream_key, region_key) -> monthly pd.Series or None. Returns dict or None (caller falls through)."""
    d = detect(question)
    if d is None:
        return None
    key, label, units, desc = d
    rows = []
    for rk, rname in REGIONS.items():
        s = get(key, rk)
        if s is None:
            continue
        r = contract.run_analysis(s, "MERRA-2", key, units, rname,
                                  meaningful=meaningful.resolve(key, s)["value"])
        t = r["trend"]
        ci = t.get("slope_ci")
        if t.get("slope_per_year") is None or not ci or ci[0] is None or ci[1] is None:
            continue
        rows.append({"region": rname, "slope": t["slope_per_year"], "lo": ci[0], "hi": ci[1]})
    if len(rows) < 2:
        return None
    rows.sort(key=lambda x: x["slope"], reverse=desc)
    top = rows[0]
    others = rows[1:]
    overlap = [o["region"] for o in others if max(top["lo"], o["lo"]) <= min(top["hi"], o["hi"])]
    separated = not overlap
    caveats = ["All regions come from the same MERRA-2 reanalysis (a model product), so they are not independent checks.",
               "The region boxes are rough rectangles, and comparing several regions makes chance differences more likely."]
    result = {"domain": "region_compare", "variable": label, "units": units, "regions": rows,
              "top_region": top["region"], "n_regions": len(rows), "interval_percent": 95,
              "separated": separated, "tested_count": len(rows), "caveats": caveats}
    f, g = phrase._fmt, phrase._fmt_sig
    order = "highest" if desc else "lowest"
    s1 = (f"Among the {len(rows)} regions, {top['region']} has the {order} estimated yearly change in {label} "
          f"(slope {g(top['slope'])} {units} per year).")
    if separated:
        s2 = f"Its 95% range does not overlap the others, so {top['region']} stands out in this record."
    else:
        s2 = (f"The 95% ranges of {phrase._join_names([top['region']] + overlap)} overlap, "
              "so these records cannot separate them.")
    s3 = "A high slope is not the same as a detected trend, and this ranks the regions only."
    per = [f"{x['region']}: slope {g(x['slope'])} {units} per year (95% range {g(x['lo'])} to {g(x['hi'])})."
           for x in rows]
    if level == "plain":
        text = " ".join([s1, s2, s3, caveats[1]])
    elif level == "detailed":
        text = "\n".join([s1, s2, s3] + per + caveats)
    else:
        text = "\n".join([s1, s2, s3] + [
            f"{x['region']}: slope {f(x['slope'])} {units} per year (95% range {f(x['lo'])} to {f(x['hi'])})."
            for x in rows] + [f"Number of regions compared: {len(rows)}."] + caveats)
    if not phrase.check_text(text, result).ok:
        return None
    return {"text": text, "result": result, "level": level, "guard_ok": True}
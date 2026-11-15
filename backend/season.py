"""season.py - 'Are the monsoon months getting wetter?': the normal trend analysis on a subset of months.
Triggers only on explicit season phrases. The month sets are project choices and are named in the answer."""
import re

import contract
import meaningful
import phrase

REGIONS = {"maharashtra": "Maharashtra", "rajasthan": "Rajasthan", "kerala": "Kerala", "gujarat": "Gujarat"}
SEASONS = [
    ("pre-monsoon", re.compile(r"\bpre[- ]?monsoon\b|\bapril (?:to|-) june\b", re.I), "pre-monsoon months", (4, 5, 6),
     ["April", "May", "June"]),
    ("monsoon", re.compile(r"\bmonsoon (?:months|season)\b|\bduring the monsoon\b|\bjune (?:to|-) september\b", re.I),
     "monsoon months", (6, 7, 8, 9), ["June", "July", "August", "September"]),
]
# (stream key, label, units, words) - checked in this order
VARS = [
    ("t2m_min", "night-time air temperature", "K", ("night", "nights", "overnight", "minimum")),
    ("t2m_max", "day-time air temperature", "K", ("daytime", "maximum", "afternoon")),
    ("precip", "rainfall", "mm/day", ("wetter", "drier", "rain", "rainy", "rainfall", "dry", "precipitation")),
    ("sunlight", "sunlight", "W m-2", ("sunnier", "cloudier", "sunny", "cloudy", "sunlight", "sunshine")),
    ("t2m", "air temperature", "K", ("hotter", "warmer", "hot", "warm", "temperature", "heat", "warming")),
]
SKIP = ("which", "fastest", "compare", "usual", "normal", "pond", "algae", "orange", "oranges", "apple",
        "apples", "cherry", "blossom", "flower", "flowers")


def detect(question):
    """(season tuple, var tuple) or None."""
    w = re.findall(r"[a-z]+", question.lower())
    if any(x in SKIP for x in w):
        return None
    sea = next((s for s in SEASONS if s[1].search(question)), None)
    if sea is None:
        return None
    var = next((v for v in VARS if any(x in v[3] for x in w)), None)
    return (sea, var) if var else None


def answer(question, default_region, get, level="plain"):
    d = detect(question)
    if d is None:
        return None
    (sid, _rx, sname, months, mnames), (key, vlabel, units, _w) = d
    region = next((x for x in re.findall(r"[a-z]+", question.lower()) if x in REGIONS), default_region)
    s = get(key, region)
    if s is None:
        return None
    sub = s.dropna()
    sub = sub[sub.index.month.isin(months)]
    if len(sub) < 10 * len(months):
        return None
    r = contract.run_analysis(sub, "MERRA-2", key, units, REGIONS[region],
                              meaningful=meaningful.resolve(key, sub)["value"])
    label = f"{sname.capitalize()} {vlabel}"
    caveats = ["Only the chosen months are used, so this says nothing about the other months of the year.",
               "Values come from the MERRA-2 reanalysis (a model product) for a region box, not from a station at your location."]
    result = {"domain": "season", "region": REGIONS[region], "abstained": False, "abstain_reason": "",
              "risk_window": None, "tested_count": 1, "llm_allowed_phrases": [], "caveats": caveats,
              "axes": [{"name": f"{sid}_{key}", "label": label, "source": "nasa_data", "critical": False,
                        "status": "analyzed", "result": r}]}
    text, rep = phrase.phrase_with_report(result, level)
    lead = (f"This uses only the {phrase._join_names(mnames)} data of each year. Which months count as the "
            f"{sname.replace(' months', '')} is a project choice.")
    full = lead + "\n\n" + text
    if not phrase.check_text(full, result).ok:
        return None
    return {"text": full, "result": result, "level": level, "phrase_note": rep.note}
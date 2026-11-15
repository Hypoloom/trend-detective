"""yearrank.py - 'Was this year hotter than usual?': rank the latest full year within the record.
Not a trend and not a forecast. Text is checked by phrase.check_text; if it fails, answer() returns None."""
import datetime
import re

import phrase

REGIONS = {"maharashtra": "Maharashtra", "rajasthan": "Rajasthan", "kerala": "Kerala", "gujarat": "Gujarat"}
# (stream key, label, units, words) - checked in this order
VARS = [
    ("precip", "rainfall", "mm/day", ("wetter", "drier", "rain", "rainy", "rainfall", "dry", "wettest",
                                      "driest", "precipitation")),
    ("sunlight", "sunlight", "W m-2", ("sunnier", "cloudier", "sunny", "cloudy", "sunlight", "sunshine",
                                       "brighter", "dimmer")),
    ("t2m", "air temperature", "K", ("hotter", "hottest", "hot", "warmer", "warmest", "cooler", "colder",
                                     "coldest", "temperature", "heat", "warm")),
]
COMPARE = re.compile(
    r"\b(?:than (?:usual|normal|average|other years|most years|last year|before|typical)|"
    r"(?:hottest|warmest|coldest|wettest|driest) year|on record|record[- ]breaking|unusual(?:ly)?|"
    r"compared (?:to|with) other years)\b", re.I)
SKIP = ("pond", "algae", "orange", "oranges", "citrus", "lemon", "fruit", "apple", "apples", "cherry",
        "blossom", "flower", "flowers")
SEASONS = ("summer", "winter", "monsoon", "spring", "autumn", "season", "month", "january", "february",
           "march", "april", "may", "june", "july", "august", "september", "october", "november", "december")


def _words(q):
    return re.findall(r"[a-z]+", q.lower())


def detect(question):
    """(key, label, units) if this is a 'was this year unusual' question, else None."""
    w = _words(question)
    if not COMPARE.search(question) or any(x in SKIP or x in SEASONS for x in w):
        return None
    for key, label, units, words in VARS:
        if any(x in words for x in w):
            return key, label, units
    return None


def region_in(question, default):
    for x in _words(question):
        if x in REGIONS:
            return x
    return default


def _ord(n):
    if 10 <= n % 100 <= 20:
        return f"{n}th"
    return f"{n}" + {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def answer(question, default_region, get, level="plain", today_year=None):
    """get(stream_key, region_key) -> monthly pd.Series or None. Returns dict or None (caller falls through)."""
    d = detect(question)
    if d is None:
        return None
    key, label, units = d
    region = region_in(question, default_region)
    s = get(key, region)
    if s is None:
        return None
    s = s.dropna()
    full = s.groupby(s.index.year).count()
    annual = s.groupby(s.index.year).mean()
    annual = annual[full[full == 12].index]
    if len(annual) < 10:
        return None
    n, last, first = len(annual), int(annual.index[-1]), int(annual.index[0])
    v = float(annual.iloc[-1])
    earlier = annual.iloc[:-1]
    em, sd = float(earlier.mean()), float(earlier.std(ddof=1))
    rank = int((annual > v).sum()) + 1
    gap = round(v - em, 3)
    today = today_year or datetime.date.today().year
    caveats = ["This compares one year with the other years in the same record. It is not a trend and not a forecast.",
               "Values come from the MERRA-2 reanalysis (a model product) for a region box, not from a station at your location."]
    result = {"domain": "year_vs_record", "region": REGIONS[region], "variable": label, "year": last,
              "first_year": first, "years_in_record": n, "earlier_years": n - 1, "top_rank": 1, "rank": rank,
              "value": round(v, 3), "earlier_mean": round(em, 3), "earlier_sd": round(sd, 3),
              "gap": abs(gap), "current_year": today, "units": units, "tested_count": 1, "caveats": caveats}
    f = phrase._fmt
    s1 = (f"In {result['region']}, {last} had the {_ord(rank)} highest annual average {label} of the {n} years "
          f"from {first} to {last} (1 is the highest).")
    s2 = f"It was {f(abs(gap))} {units} {'above' if gap >= 0 else 'below'} the average of the {n - 1} earlier years."
    note = (f"The records end with {last}, so that is the latest full year available; "
            f"the current year ({today}) is not in the data.")
    s3 = f"The {last} average was {f(result['value'])} {units}; the earlier years averaged {f(result['earlier_mean'])} {units}."
    s4 = f"The spread of the earlier yearly averages (standard deviation) was {f(result['earlier_sd'])} {units}."
    if level == "plain":
        text = " ".join([s1, s2, note, caveats[0]])
    elif level == "detailed":
        text = "\n".join([s1, s2, s3, note] + caveats)
    else:
        text = "\n".join([s1, s2, s3, s4, note] + caveats)
    g = phrase.check_text(text, result)
    if not g.ok:
        return None
    return {"text": text, "result": result, "level": level, "guard_ok": True}
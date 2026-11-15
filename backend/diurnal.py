"""diurnal.py - 'Are days heating faster than nights?': trend analysis on the day-night gap
(monthly daily-maximum minus monthly daily-minimum air temperature). Tests the difference directly."""
import re

import contract
import meaningful
import phrase

REGIONS = {"maharashtra": "Maharashtra", "rajasthan": "Rajasthan", "kerala": "Kerala", "gujarat": "Gujarat"}
SKIP = ("which", "fastest", "usual", "normal", "pond", "algae", "orange", "oranges", "apple", "apples",
        "cherry", "blossom", "flower", "flowers", "monsoon", "summer", "winter")
DAY = ("day", "days", "daytime")
NIGHT = ("night", "nights", "nighttime", "overnight")


def detect(question):
    w = re.findall(r"[a-z]+", question.lower())
    if any(x in SKIP for x in w):
        return False
    return any(x in DAY for x in w) and any(x in NIGHT for x in w)


def answer(question, default_region, get, level="plain"):
    if not detect(question):
        return None
    region = next((x for x in re.findall(r"[a-z]+", question.lower()) if x in REGIONS), default_region)
    hi, lo = get("t2m_max", region), get("t2m_min", region)
    if hi is None or lo is None:
        return None
    gap = (hi - lo).dropna()
    if len(gap) < 240:
        return None
    r = contract.run_analysis(gap, "MERRA-2", "diurnal_range", "K", REGIONS[region],
                              meaningful=meaningful.resolve("t2m", gap)["value"])
    caveats = ["This is the gap between the monthly averages of the daily highest and lowest air temperature.",
               "Values come from the MERRA-2 reanalysis (a model product) for a region box, not from a station at your location."]
    result = {"domain": "diurnal", "region": REGIONS[region], "abstained": False, "abstain_reason": "",
              "risk_window": None, "tested_count": 1, "llm_allowed_phrases": [], "caveats": caveats,
              "axes": [{"name": "diurnal_range", "label": "Day-night temperature gap", "source": "nasa_data",
                        "critical": False, "status": "analyzed", "result": r}]}
    text, rep = phrase.phrase_with_report(result, level)
    lead = ("This analyzes the day-night gap: the daily highest minus the daily lowest air temperature. "
            "A positive slope means the gap is widening; a negative slope means it is narrowing. "
            "The size counted as meaningful is a project choice.")
    full = lead + "\n\n" + text
    if not phrase.check_text(full, result).ok:
        return None
    return {"text": full, "result": result, "level": level, "phrase_note": rep.note}
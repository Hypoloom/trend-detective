"""followup.py - rules for follow-up questions. No data and no LLM: it only decides what the backend should do."""
import re

REGION_KEYS = ("maharashtra", "rajasthan", "kerala", "gujarat")

# Which analysed axes each domain has. tests/test_followup.py checks this against domains.json.
DOMAIN_AXES = {
    "pond": {"air_temp", "rainfall", "sunlight"},
    "citrus": {"air_temp", "rainfall", "sunlight"},
    "heat": {"air_temp", "night_temp", "day_temp"},
    "monsoon": {"rainfall"},
    "sunshine": {"sunlight"},
}
AXIS_DOMAIN = {"air_temp": "heat", "night_temp": "heat", "day_temp": "heat",
               "rainfall": "monsoon", "sunlight": "sunshine"}

_VAR_WORDS = [
    ("night_temp", ["night", "nights", "overnight", "minimum"]),
    ("day_temp", ["daytime", "day time", "maximum", "afternoon"]),
    ("air_temp", ["temperature", "temperatures", "hot", "hotter", "hottest", "warm", "warmer", "warming", "heat"]),
    ("rainfall", ["rain", "rainfall", "rainy", "monsoon", "precipitation", "wetter", "drier", "dry"]),
    ("sunlight", ["sun", "sunny", "sunnier", "sunlight", "sunshine", "cloud", "cloudy", "cloudier", "dimming"]),
]

WHY_NO_TREND = ["not significant", "no trend", "can't tell", "cant tell", "cannot tell", "can't find",
                "cant find", "cannot find", "couldn't find", "couldn't tell", "not found", "why not",
                "not enough", "too short", "inconclusive", "why no", "why is there no"]
CAUSAL_WORDS = ["why", "cause", "causing", "caused", "because", "reason", "due to", "how come"]
SURE = ["how sure", "how certain", "how confident", "how reliable", "how accurate", "how good",
        "can i trust", "trust", "reliable", "accurate", "confidence", "meaningful"]
FORECAST = ["next year", "next summer", "next monsoon", "next decade", "future", "forecast",
            "predict", "prediction", "years from now"]

CAUSAL_LEAD = ("The records show whether something changed and by how much. They do not show the reason, "
               "and no sourced explanation is on file here. Anything found below co-occurs with the "
               "question; it is not an explanation.")
SURE_LEAD = ("These results come from MERRA-2, a NASA reanalysis (a model product), not from direct "
             "measurements at your location. Not finding a trend is not proof that nothing changed. "
             "A trend in past records is not a forecast. The size treated as meaningful is a project "
             "choice, not a standard.")
FORECAST_LEAD = ("A trend in past records is not a forecast, so these records cannot say what next year "
                 "will be like. Here is what the past records show.")


def _text(q):
    return " " + " ".join(re.findall(r"[a-z0-9']+", (q or "").lower())) + " "


def _any(t, phrases):
    return any(" " + p + " " in t for p in phrases)


def region_in_text(question):
    t = _text(question)
    for k in REGION_KEYS:
        if " " + k + " " in t:
            return k
    return None


def axis_in_text(t):
    for axis, words in _VAR_WORDS:
        if _any(t, words):
            return axis
    return None


def forecast_note(question):
    return FORECAST_LEAD if _any(_text(question), FORECAST) else None


def plan(question, context, default_region):
    """Return a plan dict for the backend, or None if this is not a follow-up we handle."""
    if not context or context.get("domain") not in DOMAIN_AXES:
        return None
    t = _text(question)
    ctx_dom = context["domain"]
    named = region_in_text(question)
    region = named or context.get("region") or default_region
    axis = axis_in_text(t)
    domain = ctx_dom if (not axis or axis in DOMAIN_AXES[ctx_dom]) else AXIS_DOMAIN[axis]
    p = {"intent": None, "domain": domain, "region": region, "focus": axis, "pick": None, "lead": ""}
    if _any(t, WHY_NO_TREND):
        p.update(intent="why_no_trend", pick=None if axis else "not_detected")
    elif _any(t, CAUSAL_WORDS):
        p.update(intent="causal", lead=CAUSAL_LEAD, pick=None if axis else "first")
    elif _any(t, SURE):
        p.update(intent="how_sure", lead=SURE_LEAD)
    elif axis:
        p.update(intent="variable")
    elif named:
        p.update(intent="region")
    else:
        return None
    return p
"""phrase.py - turns an engine result into Plain / Detailed / Pro text.

phrase(result, level, adapter=None) -> str
  - adapter=None  -> deterministic template (LLM off). Always works.
  - adapter given -> LLM text is used ONLY if it passes check_text(); otherwise the template.
The LLM never sees or picks variables, and never makes numbers.
"""
import json
import math
import re
from dataclasses import dataclass

LEVELS = ("plain", "detailed", "pro")


# ---------------- adapter layer (no provider chosen yet) ----------------
class LLMAdapter:
    def complete(self, system: str, user: str) -> str:
        raise NotImplementedError


class CallableAdapter(LLMAdapter):
    """Wrap any function fn(system, user) -> str (any provider can be plugged in here)."""

    def __init__(self, fn):
        self.fn = fn

    def complete(self, system, user):
        return self.fn(system, user)


SYSTEM_PROMPT = (
    "You rewrite a finished analysis in plain language. Rules: use ONLY numbers that appear in the "
    "JSON. Never add a number. Never explain causes. Never use the words cause, caused, because, due "
    "to. Say 'co-occurs with', not 'caused by'. Say 'not found', never 'no trend exists'. If the JSON "
    "says abstained, or the evidence is limited, say so clearly and do not soften it. Do not pick or "
    "name climate variables that are not in the JSON. Level: plain = 2-3 short sentences, detailed = a "
    "short paragraph, pro = include the statistics."
)


# ---------------- the guard ----------------
_NUM = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?")
CAUSAL = re.compile(
    r"\b(caus(?:e|es|ed|ing)|because|due to|driven by|leads? to|led to|responsible for|"
    r"results? from|resulting from)\b", re.I)
OVERCLAIM = re.compile(
    r"\b(no trend exists|there is no trend|there's no trend|no trend at all|proves?|proof)\b", re.I)
SOFTEN = re.compile(
    r"\b(probably|most likely|almost certainly|no need to worry|should be fine|nothing to worry|"
    r"safe to assume)\b", re.I)
ABSTAIN_MARKERS = (
    "cannot give", "cannot say", "cannot tell", "cannot be determined", "not able to",
    "not knowable", "abstain", "insufficient evidence", "not enough evidence",
    "not enough data", "unable to")
NO_TREND_MARKERS = ("not found", "no trend found", "no trend was found", "did not find", "not detected")


def numbers_in_text(text):
    text = re.sub(r"(?m)^\s*\d+[.)]\s+", "", text)  # ignore "1. " list numbering
    return [float(m.replace(",", "")) for m in _NUM.findall(text)]


def allowed_numbers(obj):
    out = []

    def walk(x):
        if x is None or isinstance(x, bool):
            return
        if isinstance(x, (int, float)):
            if not (isinstance(x, float) and math.isnan(x)):
                out.append(abs(float(x)))
        elif isinstance(x, str):
            out.extend(numbers_in_text(x))
        elif isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, (list, tuple)):
            for v in x:
                walk(v)

    walk(obj)
    return out


def must_abstain(result):
    if result.get("abstained") is True:
        return True
    for ax in result.get("axes") or []:
        if ax.get("critical") and (ax.get("status") == "not_knowable" or ax.get("source") == "not_knowable"):
            return True
    return False


def _verdict_code(result):
    return (result.get("verdict") or {}).get("code")


def needs_evidence_notice(result):
    return _verdict_code(result) in ("data_limited", "masked", "inconclusive")


@dataclass
class GuardResult:
    ok: bool
    reasons: list


def check_text(text, result):
    reasons = []
    if not text or not text.strip():
        return GuardResult(False, ["empty text"])
    low = text.lower().replace("\u2019", "'")
    allowed = allowed_numbers(result)
    for n in numbers_in_text(text):
        if not any(math.isclose(n, a, rel_tol=1e-9, abs_tol=1e-12) for a in allowed):
            reasons.append(f"invented number: {n:g}")
    m = CAUSAL.search(text)
    if m:
        reasons.append(f"causal wording: {m.group(0)!r}")
    m = OVERCLAIM.search(text)
    if m:
        reasons.append(f"overclaim wording: {m.group(0)!r}")
    if must_abstain(result) or needs_evidence_notice(result):
        if not any(k in low for k in ABSTAIN_MARKERS):
            reasons.append("abstention / limited evidence is missing")
        if SOFTEN.search(text):
            reasons.append("abstention softened")
    if _verdict_code(result) == "no_trend" and not any(k in low for k in NO_TREND_MARKERS):
        reasons.append("'not found' wording missing for no_trend")
    return GuardResult(not reasons, reasons)


# ---------------- deterministic template (LLM off) ----------------
def _fmt(v):
    if v is None or isinstance(v, bool):
        return str(v)
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        if v == int(v) and abs(v) < 1e15:
            return str(int(v))
        return f"{v:.10f}".rstrip("0").rstrip(".")
    return str(v)


def _risk_window_text(rw):
    if isinstance(rw, dict):
        return "; ".join(f"{k}: {_fmt(v)}" for k, v in rw.items())
    if isinstance(rw, (list, tuple)):
        return ", ".join(_fmt(v) for v in rw)
    return str(rw)


def _check_level(level):
    if level not in LEVELS:
        raise ValueError(f"level must be one of {LEVELS}, got {level!r}")


def template_phrase(result, level="plain"):
    _check_level(level)
    code = _verdict_code(result) or "inconclusive"
    t = result.get("trend") or {}
    y = result.get("years") or {}
    nz = result.get("noise") or {}
    pv = result.get("provenance") or {}
    units = t.get("units") or ""
    where = "the data"
    if pv.get("variable"):
        where = f"the {pv['variable']} data for {pv.get('region', 'this region')}"
    abstain = must_abstain(result)

    # headline about the trend
    head = []
    if code == "detected":
        if t.get("slope_per_year") is not None:
            head.append(f"A trend was found in {where}: it changes by {_fmt(t['slope_per_year'])} "
                        f"{units} per year.".replace("  ", " "))
        else:
            head.append(f"A trend was found in {where}.")
    elif code == "no_trend":
        head.append(f"No trend was found in {where}. That means the data did not show one clearly; "
                    "it does not mean one is absent.")
    elif code == "data_limited":
        s = f"There is not enough data yet to say anything firm about {where}."
        if y.get("have") is not None and y.get("needed_for_meaningful") is not None:
            s += (f" The record has {_fmt(y['have'])} years; about {_fmt(y['needed_for_meaningful'])} "
                  "are needed to see a meaningful change.")
        head.append(s)
    elif code == "masked":
        head.append(f"A trend in {where} may be hidden by noise, so this tool cannot say either way.")
    else:
        head.append(f"The result for {where} is inconclusive: there is not enough evidence to say.")

    # abstention block
    ab = []
    if abstain:
        ab.append("This tool cannot give a definite answer here.")
        if result.get("abstain_reason"):
            ab.append(str(result["abstain_reason"]))
        if result.get("risk_window"):
            rw = _risk_window_text(result["risk_window"]).strip()
            ab.append("What the data can show instead is a risk window: "
                      + rw + ("" if rw.endswith((".", "!", "?")) else "."))
        names = [str(a.get("name", "?")).replace("_", " ") for a in result.get("axes") or []
                 if a.get("status") == "not_knowable" or a.get("source") == "not_knowable"]
        if names:
            ab.append("Not knowable from this data: " + ", ".join(names) + ".")

    lines = ab[:] if (abstain and level == "plain") else ab + head
    if level == "plain":
        return " ".join(lines)

    ci = t.get("slope_ci")
    if isinstance(ci, (list, tuple)) and len(ci) == 2:
        lines.append(f"The range for the yearly change runs from {_fmt(ci[0])} to {_fmt(ci[1])} {units}.")
    if t.get("min_detectable_slope") is not None:
        lines.append(f"The smallest yearly change this record could reliably pick up is "
                     f"{_fmt(t['min_detectable_slope'])} {units}.")
    for c in result.get("caveats") or []:
        lines.append(str(c))
    if result.get("axes"):
        lines.append("Any trend reported here co-occurs with the question you asked about; "
                     "it is not an explanation.")
        lines.append("Checks: " + ", ".join(
            f"{str(a.get('name', '?')).replace('_', ' ')} ({a.get('status', a.get('source', '?'))})"
            for a in result["axes"]) + ".")

    if level == "pro":
        if t.get("slope_per_year") is not None:
            lines.append(f"Slope {_fmt(t['slope_per_year'])} {units}/yr, p-value {_fmt(t.get('p_value'))}.")
        if nz:
            lines.append(f"Noise: sigma {_fmt(nz.get('sigma'))}, first-lag autocorrelation "
                         f"{_fmt(nz.get('lag1_autocorr'))}.")
        if result.get("tested_count") is not None:
            lines.append(f"Number of tests run: {_fmt(result['tested_count'])}.")
        if pv:
            s = (f"Source: {pv.get('dataset')}, variable {pv.get('variable')}, {pv.get('region')}, "
                 f"{_fmt(pv.get('start'))} to {_fmt(pv.get('end'))}.")
            if pv.get("simulated"):
                s += " These values are simulated."
            lines.append(s)
    return "\n".join(lines)


# ---------------- public interface ----------------
@dataclass
class PhraseReport:
    source: str   # "template" | "llm"
    note: str


def phrase_with_report(result, level="plain", adapter=None):
    tmpl = template_phrase(result, level)
    if adapter is None:
        return tmpl, PhraseReport("template", "LLM off")
    user = json.dumps({"level": level, "result": result,
                       "llm_allowed_phrases": result.get("llm_allowed_phrases", [])},
                      ensure_ascii=False, default=str)
    try:
        raw = adapter.complete(SYSTEM_PROMPT, user)
    except Exception as e:  # any provider failure -> template
        return tmpl, PhraseReport("template", f"adapter error: {type(e).__name__}")
    g = check_text(raw if isinstance(raw, str) else "", result)
    if g.ok:
        return raw.strip(), PhraseReport("llm", "passed guard")
    return tmpl, PhraseReport("template", "guard rejected: " + "; ".join(g.reasons))


def phrase(result, level="plain", adapter=None):
    return phrase_with_report(result, level, adapter)[0]
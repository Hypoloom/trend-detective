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

# Keys whose string values are the ENGINE's own wording. The guard does not scan text that is copied
# verbatim from these fields for banned words (the engine may say "not proof there isn't one").
ENGINE_TEXT_KEYS = {"caveat", "caveats", "summary", "label", "definition", "statement", "text",
                    "abstain_reason", "llm_allowed_phrases"}


def numbers_in_text(text):
    text = re.sub(r"(?m)^\s*\d+[.)]\s+", "", text)  # ignore "1. " list numbering
    return [float(m.replace(",", "")) for m in _NUM.findall(text)]


def allowed_numbers(obj):
    """Every number in the result, plus the rounded form the template prints (see _fmt)."""
    out = []

    def walk(x):
        if x is None or isinstance(x, bool):
            return
        if isinstance(x, (int, float)):
            if isinstance(x, float) and not math.isfinite(x):
                return
            v = abs(float(x))
            out.append(v)
            if isinstance(x, float):
                out.append(abs(float(_fmt(v))))       # rounded form, same rounding as the formatter
                out.append(abs(float(_fmt_sig(v))))   # 3 significant figures, as shown in plain / detailed
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


def engine_strings(result):
    """Strings the engine wrote itself (caveats, labels, summaries, reasons...), longest first."""
    found = set()

    def walk(x, key=None):
        if isinstance(x, dict):
            for k, v in x.items():
                walk(v, k)
        elif isinstance(x, (list, tuple)):
            for v in x:
                walk(v, key)      # list items inherit the key of their list
        elif isinstance(x, str) and key in ENGINE_TEXT_KEYS and len(x.strip()) >= 3:
            found.add(x.strip())

    walk(result)
    return sorted(found, key=len, reverse=True)


def own_wording(text, result):
    """The text with everything copied verbatim from the engine removed: only the writer's own words stay."""
    t = text.replace("’", "'")
    for s in engine_strings(result):
        t = re.sub(re.escape(s.replace("’", "'")), " ", t, flags=re.I)
    return t


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
    low = text.lower().replace("’", "'")
    allowed = allowed_numbers(result)
    for n in numbers_in_text(text):
        if not any(math.isclose(n, a, rel_tol=1e-9, abs_tol=1e-12) for a in allowed):
            reasons.append(f"invented number: {n:g}")
    own = own_wording(text, result)       # banned-word checks look at the writer's own words only
    m = CAUSAL.search(own)
    if m:
        reasons.append(f"causal wording: {m.group(0)!r}")
    m = OVERCLAIM.search(own)
    if m:
        reasons.append(f"overclaim wording: {m.group(0)!r}")
    if must_abstain(result) or needs_evidence_notice(result):
        if not any(k in low for k in ABSTAIN_MARKERS):
            reasons.append("abstention / limited evidence is missing")
        if SOFTEN.search(own):
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
        if not math.isfinite(v):
            return str(v)
        if v == int(v) and abs(v) < 1e15:
            return str(int(v))
        return f"{v:.10f}".rstrip("0").rstrip(".")
    return str(v)


def _fmt_sig(v, sig=3):
    """Round a float to `sig` significant figures (0.00448129 -> 0.00448). Other types go through _fmt."""
    if not isinstance(v, float) or not math.isfinite(v) or v == 0 or v == int(v):
        return _fmt(v)
    digits = sig - 1 - math.floor(math.log10(abs(v)))
    r = round(v, digits)
    if digits <= 0:
        return str(int(r))
    return f"{r:.{digits}f}".rstrip("0").rstrip(".")


def _slope(v, level):
    """Slopes: 3 significant figures in plain and detailed, the full value in pro."""
    return _fmt(v) if level == "pro" else _fmt_sig(v)


def _sentence(s):
    """Make sure a piece of text ends with a full stop (or ! or ?)."""
    s = str(s).strip()
    return s if (not s or s.endswith((".", "!", "?"))) else s + "."


def _join_names(names):
    names = [str(n) for n in names]
    if len(names) <= 1:
        return "".join(names)
    return ", ".join(names[:-1]) + " and " + names[-1]


_WINDOW_TOPIC = {"pond": "the highest average air temperature"}


def _risk_window_text(rw, domain=None, level="plain"):
    """Turn the engine's risk_window into plain sentences. Never prints dict keys or Python lists."""
    if isinstance(rw, (list, tuple)):
        return _sentence(", ".join(_fmt(v) for v in rw))
    if not isinstance(rw, dict):
        return _sentence(rw) if rw else ""
    parts = []
    names = rw.get("month_names") or rw.get("months") or []
    if names:
        topic = _WINDOW_TOPIC.get(domain)
        lead = f"The months in the risk window with {topic} are " if topic else "The months in the risk window are "
        parts.append(f"{lead}{_join_names(_fmt(n) for n in names)}.")
    if level != "plain" and rw.get("definition"):
        parts.append("Window definition: " + _sentence(rw["definition"]))
    br = rw.get("base_rate")
    if isinstance(br, dict):
        s = _base_rate_sentence(br)
        if s:
            parts.append(s)
    rv = rw.get("recent_vs_earlier")
    if isinstance(rv, dict) and rv.get("difference") is not None:
        parts.append(_sentence(
            f"In the last {_fmt(rv['recent_years'])} years of the record these months averaged "
            f"{_fmt_sig(rv['difference'])} {rv.get('units', '')} {rv['direction']} than in the "
            f"{_fmt(rv['earlier_years'])} years before"))
    if rw.get("caveat"):
        parts.append(_sentence(rw["caveat"]))
    return " ".join(parts)


_FRAGMENT_LEAD = re.compile(r"^years?\s+(?:in\s+which|when|where|that)\s+", re.I)


def _base_rate_sentence(br):
    """One sentence from years_met / years_total / statement.

    The engine's statement is a fragment like "years in which these months averaged above the
    record's own average." It is joined into: "In 12 of the last 20 years, these months averaged ...".
    """
    met, total = br.get("years_met"), br.get("years_total")
    stmt = str(br.get("statement") or "").strip().rstrip(".!? ").strip()
    have_counts = met is not None and total is not None
    if stmt and have_counts:
        m = _FRAGMENT_LEAD.match(stmt)
        if m:
            body = stmt[m.end():]
        elif {_fmt(met), _fmt(total)} <= numbers_str(stmt):
            return _sentence(_cap(stmt))          # the statement already carries both numbers
        else:
            body = stmt[:1].lower() + stmt[1:]
        return _sentence(f"In {_fmt(met)} of the last {_fmt(total)} years, {body}")
    if stmt:
        return _sentence(_cap(stmt))
    if have_counts:
        return f"The window was met in {_fmt(met)} of the last {_fmt(total)} years."
    return ""


def numbers_str(text):
    """Numbers found in a text, as the strings _fmt would print."""
    return {_fmt(n) for n in numbers_in_text(str(text))}


def _check_level(level):
    if level not in LEVELS:
        raise ValueError(f"level must be one of {LEVELS}, got {level!r}")


def _cap(s):
    s = str(s)
    return s[:1].upper() + s[1:]


def _meaningful_note(r):
    """For a 'detected' axis whose |slope| is below meaningful.value: the engine's own
    'That is smaller than the X ... chosen as meaningful ...' sentence, copied from verdict.summary."""
    v = r.get("verdict") or {}
    if v.get("code") != "detected":
        return ""
    mean = r.get("meaningful")
    mv = mean.get("value") if isinstance(mean, dict) else None
    slope = (r.get("trend") or {}).get("slope_per_year")
    nums = (int, float)
    if isinstance(mv, bool) or isinstance(slope, bool) or not isinstance(mv, nums) or not isinstance(slope, nums):
        return ""
    if abs(slope) >= abs(mv):
        return ""
    for s in re.split(r"(?<=[.!?])\s+", str(v.get("summary") or "")):
        if "smaller than" in s.lower() and "meaningful" in s.lower():
            return _sentence(s)
    return ""


def _axis_lines(result, level):
    """One short report per analyzed axis: label, verdict label, slope + units (more at detailed / pro)."""
    out = []
    for a in result.get("axes") or []:
        r = a.get("result")
        if a.get("status") != "analyzed" or not isinstance(r, dict):
            continue                      # others are already in the "Checks:" line
        v = r.get("verdict") or {}
        t = r.get("trend") or {}
        units = t.get("units") or ""
        label = _cap(a.get("label") or str(a.get("name", "?")).replace("_", " "))
        s = f"{label}: {v.get('label') or v.get('code') or 'no verdict'}"
        if t.get("slope_per_year") is not None:
            s += f"; slope {_slope(t['slope_per_year'], level)} {units} per year".replace("  ", " ")
        line = _sentence(s)
        ci = t.get("slope_ci")
        if level != "plain" and isinstance(ci, (list, tuple)) and len(ci) == 2:
            line += (f" The range for the yearly change runs from {_slope(ci[0], level)} to "
                     f"{_slope(ci[1], level)} {units}.").replace("  ", " ")
        if level == "pro" and t.get("p_value") is not None:
            line += f" p-value {_fmt(t['p_value'])}."
        note = _meaningful_note(r)
        if note:
            line += " " + note
        out.append(line)
    return out


def _caveat_text(c):
    if isinstance(c, dict):
        return str(c.get("text") or c.get("caveat") or "")
    return str(c)


def template_phrase(result, level="plain"):
    _check_level(level)
    code = _verdict_code(result)
    t = result.get("trend") or {}
    y = result.get("years") or {}
    nz = result.get("noise") or {}
    pv = result.get("provenance") or {}
    units = t.get("units") or ""
    where = "the data"
    if pv.get("variable"):
        where = f"the {pv['variable']} data for {pv.get('region', 'this region')}"
    abstain = must_abstain(result)

    # headline about the trend - only when the engine gave a top-level verdict
    head = []
    if code == "detected":
        if t.get("slope_per_year") is not None:
            head.append(f"A trend was found in {where}: it changes by {_slope(t['slope_per_year'], level)} "
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
    elif code:
        head.append(f"The result for {where} is inconclusive: there is not enough evidence to say.")
    # no top-level verdict: say nothing invented; the per-axis lines below carry the facts

    # abstention block + risk window
    ab = []
    if abstain:
        ab.append("This tool cannot give a definite answer here.")
        if result.get("abstain_reason"):
            ab.append(_sentence(result["abstain_reason"]))
    if result.get("risk_window"):
        rw = _risk_window_text(result["risk_window"], result.get("domain"), level).strip()
        if rw:
            if abstain:
                sep = ". " if isinstance(result["risk_window"], dict) else ": "
                ab.append("What the data can show instead is a risk window" + sep + rw)
            else:
                ab.append("Risk window. " + rw)
    if abstain:
        names = [str(a.get("name", "?")).replace("_", " ") for a in result.get("axes") or []
                 if a.get("status") == "not_knowable" or a.get("source") == "not_knowable"]
        if names:
            ab.append("Not knowable from this data: " + ", ".join(names) + ".")

    axis_lines = _axis_lines(result, level)
    if abstain and level == "plain":
        lines = ab + axis_lines
    else:
        lines = ab + head + axis_lines
    if not lines:
        lines = ["This result has no overall verdict."]
    if level == "plain":
        return " ".join(lines)

    ci = t.get("slope_ci")
    if isinstance(ci, (list, tuple)) and len(ci) == 2:
        lines.append(f"The range for the yearly change runs from {_slope(ci[0], level)} to "
                     f"{_slope(ci[1], level)} {units}.")
    if t.get("min_detectable_slope") is not None:
        lines.append(f"The smallest yearly change this record could reliably pick up is "
                     f"{_slope(t['min_detectable_slope'], level)} {units}.")
    for c in result.get("caveats") or []:
        lines.append(_caveat_text(c))
    if result.get("axes"):
        lines.append("Any trend reported here co-occurs with the question you asked about; "
                     "it is not an explanation.")
        lines.append("Checks: " + ", ".join(
            f"{str(a.get('name', '?')).replace('_', ' ')} ({a.get('status', a.get('source', '?'))})"
            for a in result["axes"]) + ".")

    if level == "pro":
        if t.get("slope_per_year") is not None:
            p = f", p-value {_fmt(t['p_value'])}" if t.get("p_value") is not None else ""
            lines.append(f"Slope {_fmt(t['slope_per_year'])} {units}/yr{p}.")
        if nz.get("sigma") is not None or nz.get("lag1_autocorr") is not None:
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

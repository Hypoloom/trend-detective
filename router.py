"""router.py - rules-first question router for Hypoloom (works with the LLM off).

route(question) -> RouteResult. If the rules are not confident the result is a
fallback (domain=None) carrying a guided form. An optional LLM may only choose
among vetted domain ids; anything else it says is thrown away.
Run:  python router.py "Why are my oranges small?"
"""
import json
import os
import re
import sys
from dataclasses import dataclass
from typing import Optional

from fallback_form import build_fallback_form

THRESHOLD = 0.6   # confidence needed to accept a rule match
MARGIN = 1.0      # best score must beat the runner-up by at least this much


def _ax(name, source, critical=False, variable=None, prompt="", why="", evidence=""):
    return {"name": name, "source": source, "critical": critical, "variable": variable,
            "prompt": prompt, "why_it_matters": why, "evidence": evidence}


# Stub used until the teammate's domains.json lands. Same schema.
STUB_DOMAINS = [
    {
        "id": "pond",
        "description": "Algae risk in a pond",
        "example_questions": ["Will my pond get algae this summer?",
                              "When will green scum appear on my fish pond?"],
        "keywords": ["pond", "algae", "algal", "bloom", "scum", "green water",
                     "fish pond", "eutrophication", "stagnant"],
        "axes": [
            _ax("air_temperature", "nasa_data", variable="t2m", why="Warm spells speed up algae growth"),
            _ax("rainfall", "nasa_data", variable="precip", why="Rain can wash nutrients into a pond"),
            _ax("pond_size", "ask_user", prompt="About how big is the pond?", why="Small ponds warm up faster"),
            _ax("nutrient_load", "not_knowable", critical=True, why="Nutrients feed algae", evidence="no data"),
            _ax("existing_algae", "not_knowable", critical=True, why="Algae already there", evidence="no data"),
        ],
        "abstain_policy": "abstain_if_critical_not_knowable",
        "risk_window_template": "Higher-risk window: {window}",
    },
    {
        "id": "citrus",
        "description": "Why oranges (citrus fruit) are small",
        "example_questions": ["Why are my oranges small this year?",
                              "Why is my lemon fruit size dropping?"],
        "keywords": ["citrus", "orange", "lemon", "mandarin", "fruit", "orchard",
                     "grove", "fruit size", "small"],
        "axes": [
            _ax("air_temperature", "nasa_data", variable="t2m", why="Heat stress affects fruit"),
            _ax("rainfall", "nasa_data", variable="precip", why="Water supply affects fruit"),
            _ax("sunlight", "nasa_data", variable="sunlight", why="UNVERIFIED: teammate checking"),
            _ax("tree_age", "ask_user", prompt="How old are the trees?", why="Young trees fruit differently"),
            _ax("fruit_size", "not_knowable", critical=True, why="No fruit-size data", evidence="no data"),
        ],
        "abstain_policy": "abstain_if_critical_not_knowable",
        "risk_window_template": "",
    },
]

_STOP = {"the", "a", "an", "is", "are", "my", "of", "in", "on", "to", "this", "that",
         "will", "why", "when", "what", "how", "and", "for", "get", "does", "do", "it"}


def _norm(word):
    w = word.lower()
    if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
        w = w[:-1]
    return w


def tokens(text):
    return [_norm(w) for w in re.findall(r"[a-z0-9']+", (text or "").lower())]


def _has(seq, phrase):
    n = len(phrase)
    return any(seq[i:i + n] == phrase for i in range(len(seq) - n + 1))


def _derive_keywords(domain):
    text = domain.get("description", "") + " " + " ".join(domain.get("example_questions", []))
    return [t for t in set(tokens(text)) if t not in _STOP and len(t) > 3]


def load_domains(path=None):
    path = path or os.path.join(os.path.dirname(os.path.abspath(__file__)), "domains.json")
    if not os.path.exists(path):
        return STUB_DOMAINS
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    domains = data.get("domains") if isinstance(data, dict) else None
    if not isinstance(domains, list) or not all(isinstance(d, dict) and d.get("id") for d in domains):
        raise ValueError("domains.json: expected {'domains': [{'id': ...}, ...]}")
    return domains


def score_domains(question, domains):
    seq = tokens(question)
    scores = {}
    for d in domains:
        kws = d.get("keywords") or _derive_keywords(d)
        seen = set()
        s = 0.0
        for kw in kws:
            p = tuple(tokens(kw))
            if not p or p in seen:
                continue
            seen.add(p)
            if _has(seq, list(p)):
                s += 1.5 if len(p) > 1 else 1.0
        scores[d["id"]] = s
    return scores


@dataclass
class RouteResult:
    domain: Optional[str]
    confidence: float
    source: str          # "rules" | "llm" | "fallback"
    scores: dict
    reason: str
    form: Optional[dict] = None

    @property
    def is_fallback(self):
        return self.domain is None


def _ask_llm(question, domains, llm_choose):
    """The LLM sees only id/description/example_questions and may only return a vetted id."""
    menu = [{"id": d["id"], "description": d.get("description", ""),
             "example_questions": d.get("example_questions", [])} for d in domains]
    try:
        out = llm_choose(question, menu)
    except Exception:
        return None
    pick = out.get("domain") if isinstance(out, dict) else None
    return pick if pick in {d["id"] for d in domains} else None


def route(question, domains=None, threshold=THRESHOLD, margin=MARGIN, llm_choose=None):
    domains = load_domains() if domains is None else domains
    scores = score_domains(question, domains)
    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    best_id, best = ranked[0] if ranked else (None, 0.0)
    runner = ranked[1][1] if len(ranked) > 1 else 0.0
    conf = best / (best + 1.0) if best > 0 else 0.0
    if best_id and conf >= threshold and (best - runner) >= margin:
        return RouteResult(best_id, round(conf, 3), "rules", scores, "keyword match")
    if best == 0:
        why = "no keyword matched"
    elif conf < threshold:
        why = "match too weak"
    else:
        why = "ambiguous between domains"
    if llm_choose is not None:
        picked = _ask_llm(question, domains, llm_choose)
        if picked:
            return RouteResult(picked, round(conf, 3), "llm", scores,
                               f"rules unsure ({why}); LLM picked a vetted id")
        why += "; LLM gave no valid id"
    return RouteResult(None, round(conf, 3), "fallback", scores, why,
                       build_fallback_form(domains, question or ""))


if __name__ == "__main__":
    q = " ".join(sys.argv[1:])
    r = route(q)
    print(f"domain={r.domain} confidence={r.confidence} source={r.source} scores={r.scores} reason={r.reason}")
"""answer.py - run a domain's axes through the engine; abstain when a critical axis can't be known.
Usage: python answer.py pond"""
import json, sys
import numpy as np
import stream
from contract import run_analysis
from meaningful import resolve, RULES
import calendar

BLOCKING = {"needs_user", "not_knowable", "data_unavailable"}


def load_domain(domain_id, path="domains.json"):
    with open(path, encoding="utf-8") as f:
        for d in json.load(f)["domains"]:
            if d["id"] == domain_id:
                return d
    raise KeyError(domain_id)


def _risk_window(series_by_axis, rule, last_n=20):
    s = series_by_axis.get(rule["axis"]) if rule else None
    if s is None:
        return None
    clim = s.groupby(s.index.month).mean()
    n = int(rule["n_months"])
    pick = clim.nlargest(n) if rule.get("direction", "highest") == "highest" else clim.nsmallest(n)
    months = sorted(int(m) for m in pick.index)
    sub = s[s.index.month.isin(months)]
    yearly = sub.groupby(sub.index.year).mean()
    recent = yearly.iloc[-last_n:]
    met = int((recent > float(yearly.mean())).sum())
    return {"months": months, "month_names": [calendar.month_name[m] for m in months],
            "definition": rule["definition"],
            "base_rate": {"years_met": met, "years_total": int(len(recent)),
                          "statement": "years in which these months averaged above the record's own average"},
            "caveat": "A window of months where conditions co-occur, not a prediction and not a number of days."}


def build(domain_id, region_label, box, start, end, user_inputs=None,
          domains_path="domains.json", workers=32):
    dom = load_domain(domain_id, domains_path)
    user_inputs = user_inputs or {}
    axes, series, phrases, tested = [], {}, [], 0
    for ax in dom["axes"]:
        row = {"name": ax["name"], "label": ax.get("label", ax["name"]),
               "source": ax["source"], "critical": bool(ax["critical"]),
               "status": None, "result": None}
        if ax["source"] == "nasa_data":
            key = ax["variable"]
            if key not in stream.VARIABLES:
                row["status"] = "data_unavailable"
                phrases.append({"id": f"axis:{ax['name']}",
                                "text": f"{row['label']}: no data is available for this factor yet."})
            else:
                cfg = stream.VARIABLES[key]
                s = stream.get_series(key, box, start, end, workers=workers)
                series[ax["name"]] = s
                m = resolve(key, s) if key in RULES else None
                res = run_analysis(s, f"MERRA-2 {cfg['short_name']}", cfg["var"], cfg["units"],
                                   region_label,
                                   meaningful=m["value"] if m else None,
                                   meaningful_rule={"rule": m["rule"], "basis": m["basis"]} if m else None)
                row["status"], row["result"] = "analyzed", res
                tested += 1
                phrases.append({"id": f"axis:{ax['name']}",
                                "text": f"{row['label']}: {res['verdict']['summary']}"})
        elif ax["source"] == "ask_user":
            if ax["name"] in user_inputs:
                row["status"], row["result"] = "provided", {"value": user_inputs[ax["name"]]}
            else:
                row["status"] = "needs_user"
                row["prompt"] = ax.get("prompt")
        else:
            row["status"] = "not_knowable"
        axes.append(row)

    blockers = [a["label"] for a in axes if a["critical"] and a["status"] in BLOCKING]
    abstained = bool(blockers)
    reason = ("Cannot give a number. These critical factors are unknown here: "
              + ", ".join(blockers) + ".") if abstained else None
    rw = _risk_window(series, dom.get("risk_window_rule")) if abstained else None

    if abstained:
        phrases.append({"id": "abstain", "text": reason})
    if rw:
        phrases.append({"id": "risk_window",
                        "text": f"Risk window: {', '.join(rw['month_names'])}. In "
                                f"{rw['base_rate']['years_met']} of the last {rw['base_rate']['years_total']} "
                                f"years these months averaged above the record's own average. {rw['caveat']}"})
    phrases.append({"id": "tested", "text": f"{tested} data series were tested; results co-occur with each other "
                                            "and do not show cause."})
    caveats = ["Not finding a trend is not proof there isn't one.",
               "A trend is not a forecast."]

    if abstained and rw is None:
        phrases.append({"id": "no_risk_window",
                        "text": "No risk window could be computed for this question yet, so no timing can be given."})
    if tested > 1:
        caveats.append(f"{tested} series were tested; some significant results can arise by chance.")
    return {"domain": dom["id"], "region": region_label, "axes": axes,
            "abstained": abstained, "abstain_reason": reason, "risk_window": rw,
            "tested_count": tested, "llm_allowed_phrases": phrases,
            "caveats": caveats}

if __name__ == "__main__":
    out = build(sys.argv[1] if len(sys.argv) > 1 else "pond", "Maharashtra box (72,16,80,21)",
                (72, 16, 80, 21), 1980, 2025)
    text = json.dumps(out, allow_nan=False)
    for a in out["axes"]:
        if a["result"] and "chart" in a["result"]:
            a["result"]["chart"]["points"] = "<points>"
    print(json.dumps(out, indent=1))
    print("json bytes:", len(text))
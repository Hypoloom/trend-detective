import json
import sys

import numpy as np

from engine import analyze, deseasonalize

VERDICTS = {
    "Detected": ("detected", "Trend detected"),
    "Data-limited": ("data_limited", "Data-limited"),
    "Masked by aggregation": ("masked", "Masked by aggregation"),
    "No trend found (not proof of absence)": ("no_trend", "No trend found"),
    "Inconclusive": ("inconclusive", "Inconclusive"),
}


def _f(x, nd=6):
    """JSON-safe float: None for missing/inf/nan."""
    if x is None or not np.isfinite(x):
        return None
    return round(float(x), nd)


def _summary(code, slope, units, years, lo, hi, nm=None, meaningful=None, md=None):
    direction = "upward" if slope > 0 else "downward"
    if code == "detected":
        text = (f"A statistically significant {direction} trend of {slope:.3g} {units} "
                f"per year was found over {years} years of data.")
        if meaningful and abs(slope) < meaningful:
            text += (f" That is smaller than the {meaningful:g} {units} per year "
                     "chosen as meaningful for this variable.")
        return text
    if code == "data_limited":
        if nm is not None:
            lead = "To judge whether a meaningful trend exists, the record would need to be"
            need = f"about {nm} years long, to catch a trend of {meaningful:g} {units} per year"
        else:
            lead = "If the current slope continues, the record would need to be"
            need = (f"at least {lo} years long" if hi is None
                    else f"roughly {lo} to {hi} years long")
        return " ".join([
            "A trend may exist, but",
            f"{years} years of data is too short or too noisy to show it.",
            lead,
            need + ".",
        ])
    if code == "masked":
        return ("Different regions show opposite significant trends, so the combined "
                "series hides them.")
    if code == "no_trend":
        text = ("No trend was found even with a long record. "
                "That is not proof that nothing is happening.")
        if md is not None:
            text += (f" A trend larger than about {md:.2g} {units} per year "
                     "would probably have been detected.")
        return text
    return ("The evidence is mixed: the trend is not significant, and the record "
            "is not clearly too short.")


def run_analysis(s, dataset, variable, units, region, regions=None,
                 deseason=True, simulated=False, meaningful=None, meaningful_rule=None):
    """s: monthly pd.Series (DatetimeIndex). regions: optional {name: monthly Series}.
    meaningful: smallest trend (units per year) that matters for this variable.
    Returns a JSON-safe dict. This is the only shape the frontend should depend on."""
    s = s.dropna()
    r = analyze(s, regions=regions, deseason=deseason, meaningful=meaningful)
    code, label = VERDICTS[r["verdict"]]
    lo, mid, hi = r["years_needed"]
    lo, mid, hi = _f(lo, 1), _f(mid, 1), _f(hi, 1)
    nm = _f(r["years_needed_meaningful"], 1)
    md = _f(r["min_detectable"], 6)

    a = deseasonalize(s) if deseason else s
    annual = a.groupby(a.index.year).mean()
    yrs = annual.index.to_numpy(float) + 0.5
    vals = annual.to_numpy(float)
    ts_lo, ts_hi = r["ts_ci"]
    x0 = float(yrs.mean())
    y0 = float(np.median(vals - r["ts"] * (yrs - x0)))
    pts = [{"year": float(x), "value": _f(v)} for x, v in zip(yrs, vals)]
    trend = []
    for x in (yrs[0], yrs[-1]):
        band = (y0 + ts_lo * (x - x0), y0 + ts_hi * (x - x0))
        trend.append({"year": float(x), "trend": _f(y0 + r["ts"] * (x - x0)),
                      "low": _f(min(band)), "high": _f(max(band))})

    n_tested = 1 + (len(regions) if regions else 0)
    caveats = [
        "Not finding a trend is not proof there isn't one.",
        "Years-needed assumes the observed trend continues and the noise stays simple; read it as a range.",
        "A trend is not a forecast.",
    ]
    if meaningful:
        caveats.append(f"'Meaningful' was set to {meaningful:g} {units} per year; "
                       "the verdict depends on that choice.")
    
    if n_tested > 1:
        caveats.append(f"{n_tested} series were tested; some significant results can arise by chance.")
        meaningful_block = None
    if meaningful:
        sens = []
        if code != "detected":
            for f in (0.5, 1.0, 2.0):
                rr = analyze(s, regions=regions, deseason=deseason, meaningful=meaningful * f)
                c, _ = VERDICTS[rr["verdict"]]
                sens.append({"factor": f, "value": _f(meaningful * f, 6), "verdict_code": c,
                             "needed_years": _f(rr["years_needed_meaningful"], 1)})
        meaningful_block = {**(meaningful_rule or {}), "value": _f(meaningful, 6),
                            "sensitivity": sens}
    return {
        "verdict": {"code": code, "label": label,
                    "summary": _summary(code, r["ts"], units, r["years_have"], lo, hi,
                                        nm=nm, meaningful=meaningful, md=md)},
        "years": {"have": r["years_have"], "needed_low": lo, "needed_mid": mid,
                  "needed_high": hi, "needed_for_meaningful": nm,
                  "meaningful_slope": meaningful},
        "trend": {"slope_per_year": _f(r["ts"], 8), "slope_ci": [_f(ts_lo, 8), _f(ts_hi, 8)],
                  "ols_slope_per_year": _f(r["ols"], 8), "p_value": _f(r["p_mk"], 4),
                  "p_value_method": "Mann-Kendall (Kendall tau) on annual means",
                  "min_detectable_slope": md, "units": units},
        "noise": {"sigma": _f(r["sigma"], 4), "lag1_autocorr": _f(r["phi"], 3)},
        "chart": {"points": pts, "trend_line": trend, "seasonality_removed": deseason},
        "provenance": {"dataset": dataset, "variable": variable, "region": region,
                       "start": f"{s.index[0]:%Y-%m}", "end": f"{s.index[-1]:%Y-%m}",
                       "simulated": simulated},
        "caveats": caveats,
        "tested_count": n_tested,
        "meaningful": meaningful_block,
    }


if __name__ == "__main__":
    from loaders import load_giovanni_csv
    path = sys.argv[1] if len(sys.argv) > 1 else "t2m.csv"
    meaningful = float(sys.argv[2]) if len(sys.argv) > 2 else None
    out = run_analysis(load_giovanni_csv(path), "MERRA-2 M2TMNXSLV", "T2M", "K",
                       "Maharashtra box (72,16,80,21)", meaningful=meaningful)
    text = json.dumps(out, allow_nan=False)  # raises if any NaN/inf slipped through
    out["chart"]["points"] = f"<{len(out['chart']['points'])} points>"
    print(json.dumps(out, indent=2))
    print("json bytes:", len(text))
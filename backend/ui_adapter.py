"""ui_adapter.py - maps the contract JSON to the shape the React mock (mockData.getSeries) uses.
Endpoint: GET /api/ui/analysis?dataset=T2M&region=maharashtra  (same query params as /api/analysis)."""
from flask import Blueprint, current_app, jsonify, request

bp = Blueprint("ui", __name__)

VERDICT_UI = {
    "detected": "significant",
    "data_limited": "not_enough_data",
    "no_trend": "not_significant",
    "inconclusive": "not_significant",
    "masked": "not_significant",
}
GAP_REASON = {
    "data_limited": "Not enough data yet",
    "inconclusive": "Not enough data yet",
    "masked": "Method limit",
    "no_trend": "No trend found (not proof of absence)",
}


def _f(x):
    return "n/a" if x is None else format(x, ".3g")


def _interp(tl):
    """Return at(key, year) that interpolates the 2-point trend_line, or None."""
    if not tl or len(tl) < 2:
        return None
    a, b = tl[0], tl[-1]
    ya, yb = a.get("year"), b.get("year")
    if ya is None or yb is None or yb == ya:
        return None

    def at(key, y):
        va, vb = a.get(key), b.get(key)
        if va is None or vb is None:
            return None
        return va + (vb - va) * (y - ya) / (yb - ya)
    return at


def to_ui(c, dataset_id, region_id):
    v = c.get("verdict") or {}
    yrs = c.get("years") or {}
    tr = c.get("trend") or {}
    nz = c.get("noise") or {}
    pv = c.get("provenance") or {}
    ch = c.get("chart") or {}
    code = v.get("code")
    units = tr.get("units") or ""
    ci = tr.get("slope_ci")

    at = _interp(ch.get("trend_line"))
    series = []
    for p in ch.get("points") or []:
        y = p.get("year")
        if y is None:
            continue
        series.append({
            "year": int(y),
            "value": p.get("value"),
            "trend": at("trend", y) if at else None,
            "low": at("low", y) if at else None,
            "high": at("high", y) if at else None,
        })

    have = yrs.get("have")
    need = yrs.get("needed_for_meaningful") or yrs.get("needed_mid") or yrs.get("needed_low") or have
    gap = None
    if code != "detected":
        md = tr.get("min_detectable_slope")
        if code == "no_trend":
            tip = ("The size chosen as meaningful is a project choice, not a standard. "
                   "Changing it can change this verdict.")
        elif code == "data_limited" and yrs.get("needed_for_meaningful") is not None:
            tip = (f"About {_f(yrs['needed_for_meaningful'])} years of data are needed to see a change "
                   f"of {_f(yrs.get('meaningful_slope'))} {units} per year.")
        else:
            tip = "More years of data, or a different region or period, could settle this."
        gap = {"reason": GAP_REASON.get(code, "Not enough data yet"), "status": code,
               "yearsHave": round(have) if have is not None else None, "yearsNeed": need, "tip": tip}

    plain = v.get("summary") or v.get("label") or ""
    detailed = plain
    if tr.get("slope_per_year") is not None:
        rng = ""
        if isinstance(ci, (list, tuple)) and len(ci) == 2:
            rng = f" (95% range {_f(ci[0])} to {_f(ci[1])})"
        detailed += (f" Estimated change: {_f(tr['slope_per_year'])} {units} per year{rng}; "
                     f"p = {_f(tr.get('p_value'))}.")
    pro = detailed
    if tr.get("ols_slope_per_year") is not None:
        pro += f" Ordinary least squares slope: {_f(tr['ols_slope_per_year'])} {units} per year."
    if nz:
        pro += (f" Noise sigma {_f(nz.get('sigma'))}, lag-1 autocorrelation "
                f"{_f(nz.get('lag1_autocorr'))}.")
    if tr.get("min_detectable_slope") is not None:
        pro += (f" Smallest change this record can reliably detect: "
                f"{_f(tr['min_detectable_slope'])} {units} per year.")
    pro += (f" Source: {pv.get('dataset')}, {pv.get('variable')}, {pv.get('region')}, "
            f"{pv.get('start')} to {pv.get('end')}.")

    return {
        "regionId": region_id,
        "variableId": dataset_id,
        "title": f"{pv.get('variable')} in {pv.get('region')}",
        "subtitle": f"{pv.get('dataset')}, {pv.get('start')} to {pv.get('end')}",
        "verdict": VERDICT_UI.get(code, "not_significant"),
        "verdict_code": code,
        "slopePerYear": tr.get("slope_per_year"),
        "pValue": tr.get("p_value"),
        "ci95": ci,
        "yearsUsed": round(have) if have is not None else None,
        "dataset": pv.get("dataset"),
        "series": series,
        "summary": {"plain": plain, "detailed": detailed, "pro": pro},
        "gap": gap,
        "followUps": [],
        "simulated": bool(pv.get("simulated")),
        "caption": f"Values are yearly averages with the seasonal cycle removed (anomalies), not raw {units}.",
        "contract": c,
        "fragile": bool(tr.get("fragile")),
        "fragileNote": ("This result depends on a few extreme years: it is not significant when the most "
                        "extreme years are left out.") if tr.get("fragile") else None,
    }


@bp.route("/api/ui/analysis")
def ui_analysis():
    dataset = request.args.get("dataset", "T2M")
    region = request.args.get("region", "maharashtra")
    resp = current_app.test_client().get("/api/analysis", query_string=request.args)
    data = resp.get_json(silent=True)
    if resp.status_code != 200 or not isinstance(data, dict):
        return jsonify(data or {"error": "analysis failed"}), resp.status_code
    out = to_ui(data, dataset, region)
    return jsonify(out)
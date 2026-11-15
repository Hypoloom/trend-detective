"""
app.py -- a small web server for the backend. Run it with:   python app.py

It does NOT call NASA while a user clicks. It reads series that were fetched
earlier from CSV files in stream_cache/, then runs the analysis. If a CSV is
missing, the endpoint returns a clean JSON error (404) instead of fetching.

Endpoints (the frontend calls these):
  GET /api/health
  GET /api/datasets                                   what is available (per region too)
  GET /api/series?dataset=T2M&region=maharashtra      monthly numbers (for a chart)
  GET /api/analysis?dataset=T2M&region=maharashtra&slope=0.02
                                                      the JSON from contract.run_analysis
  GET /api/answer, GET|POST /api/ask                  see API.md

Needs only:  pip install flask pandas numpy
"""
import math
import os

import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

from ui_adapter import bp as ui_bp

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(HERE, "stream_cache")

# ---------------------------------------------------------------------------
# 1. What data exists. To add a variable: fetch it, then add one entry here.
#    "file" is the Maharashtra cache file (kept for reference; readiness is
#    checked for every region through cache_file()).
#    "slope" is the "meaningful trend per year" override (None = use meaningful.py).
# ---------------------------------------------------------------------------
DATASETS = {
    "T2M": {"label": "Air temperature at 2 m", "units": "K", "stream_key": "t2m",
            "file": "stream_cache/t2m_72_16_80_21.csv", "slope": None},
    "PRECIP": {"label": "Rainfall", "units": "mm/day", "stream_key": "precip",
               "file": "stream_cache/precip_72_16_80_21.csv", "slope": None},
    "SUNLIGHT": {"label": "Sunlight reaching the surface", "units": "W m-2", "stream_key": "sunlight",
                 "file": "stream_cache/sunlight_72_16_80_21.csv", "slope": None},
    "T2M_MIN": {"label": "Night-time air temperature (daily minimum)", "units": "K", "stream_key": "t2m_min",
                "file": "stream_cache/t2m_min_72_16_80_21.csv", "slope": None},
    "T2M_MAX": {"label": "Day-time air temperature (daily maximum)", "units": "K", "stream_key": "t2m_max",
                "file": "stream_cache/t2m_max_72_16_80_21.csv", "slope": None},
}

REGIONS = {
    "maharashtra": {"label": "Maharashtra", "box": [72, 16, 80, 21]},
    "rajasthan": {"label": "Rajasthan", "box": [69.5, 23.0, 78.0, 30.0]},
    "kerala": {"label": "Kerala", "box": [74.8, 8.2, 77.5, 12.8]},
    "gujarat": {"label": "Gujarat", "box": [68.0, 20.0, 74.5, 24.7]},
}

app = Flask(__name__)
app.register_blueprint(ui_bp)


class CacheMissing(FileNotFoundError):
    """The cached CSV for this variable and region is not on this machine."""


# ---------------------------------------------------------------------------
# 2. Small helpers
# ---------------------------------------------------------------------------
@app.after_request
def allow_frontend(resp):
    """Lets a frontend on another port (like localhost:3000) call this server."""
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp


def clean(x):
    """Turn numpy/pandas values into plain JSON. NaN becomes null."""
    if isinstance(x, dict):
        return {str(k): clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [clean(v) for v in x]
    if isinstance(x, np.ndarray):
        return clean(x.tolist())
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (float, np.floating)):
        return None if math.isnan(x) or math.isinf(x) else float(x)
    if isinstance(x, (pd.Timestamp,)):
        return x.strftime("%Y-%m-%d")
    if isinstance(x, (np.bool_,)):
        return bool(x)
    return x


def error(message, code):
    return jsonify({"error": message}), code


@app.errorhandler(Exception)
def unexpected(e):
    """Any unexpected failure becomes JSON, not an HTML page. HTTP errors pass through."""
    if isinstance(e, HTTPException):
        return e
    return error(f"server error: {type(e).__name__}", 500)


def cache_file(key, box):
    """Name of the cached CSV for this stream key and box, or None.
    Parses the numbers in each file name, so it does not depend on how they are formatted."""
    if not os.path.isdir(CACHE_DIR):
        return None
    prefix = key + "_"
    for name in sorted(os.listdir(CACHE_DIR)):
        if not (name.startswith(prefix) and name.endswith(".csv")):
            continue
        try:
            nums = [float(p) for p in name[len(prefix):-4].split("_")]
        except ValueError:
            continue                      # e.g. t2m_min_... when looking for t2m
        if len(nums) == 4 and all(math.isclose(a, b, abs_tol=1e-9) for a, b in zip(nums, box)):
            return name
    return None


def missing_cache(region, stream_keys):
    """Stream keys that have no cached CSV for this region."""
    box = tuple(REGIONS[region]["box"])
    return [k for k in stream_keys if cache_file(k, box) is None]


def cache_error(region, missing):
    return error(f"cached data missing for {REGIONS[region]['label']}: {', '.join(missing)}. "
                 f"Copy the CSV files into backend/stream_cache/ (the server does not fetch "
                 f"from NASA while serving).", 404)


def get_series(dataset, region):
    """Monthly Series from the cache. Raises CacheMissing if the CSV is not there."""
    import stream
    key = DATASETS[dataset]["stream_key"]
    box = tuple(REGIONS[region]["box"])
    if cache_file(key, box) is None:
        raise CacheMissing(f"no cached data for {key} in {REGIONS[region]['label']}")
    return stream.get_series(key, box, 1980, 2025, verbose=False)


def pick(args):
    """Read and check ?dataset= and ?region= from the URL."""
    dataset = args.get("dataset", "T2M")
    region = args.get("region", "maharashtra")
    if dataset not in DATASETS:
        return None, None, error(f"unknown dataset '{dataset}'. "
                                 f"Choose one of {list(DATASETS)}", 400)
    if region not in REGIONS:
        return None, None, error(f"unknown region '{region}'. "
                                 f"Choose one of {list(REGIONS)}", 400)
    return dataset, region, None


def call_run_analysis(series, dataset, region, slope):
    import stream
    from contract import run_analysis
    from meaningful import resolve
    key = DATASETS[dataset]["stream_key"]
    cfg = stream.VARIABLES[key]
    rule = None
    if slope is None:
        m = resolve(key, series)
        slope, rule = m["value"], {"rule": m["rule"], "basis": m["basis"]}
    r = REGIONS[region]
    return run_analysis(series, f"MERRA-2 {cfg['short_name']}", cfg["var"], cfg["units"],
                        f"{r['label']} box {tuple(r['box'])}",
                        meaningful=slope, meaningful_rule=rule)


def nasa_keys(dom):
    """Stream keys a domain needs from NASA data (only keys stream.py knows)."""
    import stream
    return [a["variable"] for a in dom.get("axes", [])
            if a.get("source") == "nasa_data" and a.get("variable") in stream.VARIABLES]


# ---------------------------------------------------------------------------
# 3. The endpoints
# ---------------------------------------------------------------------------
@app.get("/api/health")
def health():
    return jsonify({"ok": True})


@app.get("/api/datasets")
def datasets():
    out = []
    for key, info in DATASETS.items():
        ready_regions = {rid: cache_file(info["stream_key"], tuple(r["box"])) is not None
                         for rid, r in REGIONS.items()}
        out.append({
            "id": key,
            "label": info["label"],
            "units": info["units"],
            "default_slope": info["slope"],
            "ready": all(ready_regions.values()),
            "ready_regions": ready_regions,
        })
    regions = [{"id": k, "label": v["label"], "box": v["box"]}
               for k, v in REGIONS.items()]
    return jsonify({"datasets": out, "regions": regions})


@app.get("/api/series")
def series():
    dataset, region, err = pick(request.args)
    if err:
        return err
    try:
        s = get_series(dataset, region)
    except FileNotFoundError as e:
        return error(str(e), 404)
    return jsonify(clean({
        "dataset": dataset,
        "region": region,
        "units": DATASETS[dataset]["units"],
        "dates": [d.strftime("%Y-%m") for d in s.index],
        "values": s.values,
    }))


@app.get("/api/analysis")
def analysis():
    dataset, region, err = pick(request.args)
    if err:
        return err
    slope = request.args.get("slope", type=float)
    try:
        s = get_series(dataset, region)
    except FileNotFoundError as e:
        return error(str(e), 404)
    try:
        result = call_run_analysis(s, dataset, region, slope)
    except ImportError as e:
        return error(f"could not import contract.py: {e}. "
                     f"Keep app.py in the same folder as contract.py.", 500)
    except TypeError as e:
        return error(f"run_analysis was called the wrong way: {e}. "
                     f"Edit call_run_analysis() in app.py.", 500)
    return jsonify(clean(result))


@app.get("/api/answer")
def answer_endpoint():
    import answer
    region = request.args.get("region", "maharashtra")
    if region not in REGIONS:
        return error(f"unknown region '{region}'. Choose one of {list(REGIONS)}", 400)
    domain = request.args.get("domain", "pond")
    try:
        dom = answer.load_domain(domain)
    except (KeyError, ValueError):
        return error(f"unknown domain '{domain}'", 400)
    missing = missing_cache(region, nasa_keys(dom))
    if missing:
        return cache_error(region, missing)
    box = tuple(REGIONS[region]["box"])
    try:
        out = answer.build(domain, f"{REGIONS[region]['label']} box {box}", box, 1980, 2025)
    except FileNotFoundError as e:
        return error(str(e), 404)
    return jsonify(clean(out))


@app.route("/api/ask", methods=["GET", "POST"])
def ask_endpoint():
    """Question in, phrased answer out. LLM off: router -> answer.build -> template phrase."""
    import answer
    import phrase
    import router
    from fallback_form import form_to_text

    body = request.get_json(silent=True) or {}

    def arg(name, default=None):
        return body.get(name, request.args.get(name, default))

    question = str(arg("question", "") or "").strip()
    if not question:
        return error("missing 'question'", 400)
    region = arg("region", "maharashtra")
    if region not in REGIONS:
        return error(f"unknown region '{region}'. Choose one of {list(REGIONS)}", 400)
    level = arg("level", "plain")
    if level not in ("plain", "detailed", "pro"):
        return error("level must be plain, detailed or pro", 400)
    user_inputs = arg("user_inputs", {}) or {}
    if not isinstance(user_inputs, dict):
        return error("user_inputs must be an object", 400)

    r = router.route(question)
    if r.is_fallback:
        return jsonify(clean({"fallback": True, "reason": r.reason, "form": r.form,
                              "form_text": form_to_text(r.form), "used_llm": False}))

    label = REGIONS[region]["label"]
    box = tuple(REGIONS[region]["box"])
    dom = answer.load_domain(r.domain)
    allowed = {a["name"] for a in dom["axes"] if a["source"] == "ask_user"}
    unknown = sorted(set(user_inputs) - allowed)
    if unknown:
        return error(f"unknown user_inputs {unknown}. Allowed for {r.domain}: {sorted(allowed)}", 400)
    inputs = dict(user_inputs)
    if "region" in allowed:
        inputs.setdefault("region", label)

    missing = missing_cache(region, nasa_keys(dom))
    if missing:
        return cache_error(region, missing)
    try:
        out = answer.build(r.domain, label, box, 1980, 2025, user_inputs=inputs)
    except FileNotFoundError as e:
        return error(str(e), 404)
    text, rep = phrase.phrase_with_report(out, level)
    return jsonify(clean({"fallback": False, "domain": r.domain, "confidence": r.confidence,
                          "route_source": r.source, "level": level, "text": text,
                          "used_llm": rep.source == "llm", "phrase_note": rep.note,
                          "abstained": out["abstained"], "result": out}))


if __name__ == "__main__":
    # debug=True restarts the server when you edit a file. Turn it off for the demo.
    app.run(host="127.0.0.1", port=8000, debug=False)
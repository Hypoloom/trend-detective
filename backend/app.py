"""
app.py -- a small web server for the backend. Run it with:   python app.py

It does NOT call NASA while a user clicks. It reads series that were fetched
earlier (by fetch_opendap.py) from CSV files, then runs your friend's analysis.

Endpoints (the frontend calls these):
  GET /api/health
  GET /api/datasets                                   what is available
  GET /api/series?dataset=T2M&region=maharashtra      monthly numbers (for a chart)
  GET /api/analysis?dataset=T2M&region=maharashtra&slope=0.02
                                                      the JSON from contract.run_analysis

Needs only:  pip install flask pandas numpy
"""
import inspect
import math
import os

import numpy as np
import pandas as pd
from flask import Flask, jsonify, request

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# 1. What data exists. To add a variable: fetch it, then add one line here.
#    "file" is the CSV that fetch_opendap.py saved (cache=... argument).
#    "slope" is the "meaningful trend per year". PLACEHOLDER values: the team
#    still has to decide them (0.02 K/yr for T2M is only a placeholder).
# ---------------------------------------------------------------------------
DATASETS = {
    "T2M": {
        "label": "Air temperature at 2 m",
        "units": "K",
        "file": "t2m_fetched.csv",
        "slope": 0.02,
    },
    # Add rainfall after you have fetched it, for example:
    # "PRECTOTCORR": {"label": "Precipitation", "units": "kg m-2 s-1",
    #                 "file": "prectotcorr_fetched.csv", "slope": None},
}

REGIONS = {
    "maharashtra": {"label": "Maharashtra", "box": [72, 16, 80, 21]},
}

app = Flask(__name__)


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


def get_series(dataset, region):
    """Monthly pandas Series for (dataset, region), read from a saved CSV."""
    info = DATASETS[dataset]
    path = os.path.join(HERE, info["file"])
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"{info['file']} not found. Run fetch_opendap.py first "
            f"(it saves this file)."
        )
    s = pd.read_csv(path, index_col=0, parse_dates=True).iloc[:, 0]
    s.index.freq = "MS"
    return s


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


def call_run_analysis(series, slope):
    """
    The ONE place that talks to your friend's contract.py.
    I have not seen contract.py, so this adapts to what run_analysis accepts:
    it passes the series first, and the slope by whatever its parameter is called.
    If your friend's function looks different, edit only this function.
    """
    from contract import run_analysis

    params = inspect.signature(run_analysis).parameters
    kwargs = {}
    if slope is not None:
        for name in params:
            if "slope" in name.lower() or "meaningful" in name.lower():
                kwargs[name] = slope
                break
    return run_analysis(series, **kwargs)


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
        out.append({
            "id": key,
            "label": info["label"],
            "units": info["units"],
            "default_slope": info["slope"],
            "ready": os.path.exists(os.path.join(HERE, info["file"])),
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
    if slope is None:
        slope = DATASETS[dataset]["slope"]
    try:
        s = get_series(dataset, region)
    except FileNotFoundError as e:
        return error(str(e), 404)
    try:
        result = call_run_analysis(s, slope)
    except ImportError as e:
        return error(f"could not import contract.py: {e}. "
                     f"Keep app.py in the same folder as contract.py.", 500)
    except TypeError as e:
        return error(f"run_analysis was called the wrong way: {e}. "
                     f"Edit call_run_analysis() in app.py.", 500)
    return jsonify(clean(result))


if __name__ == "__main__":
    # debug=True restarts the server when you edit a file. Turn it off for the demo.
    app.run(host="127.0.0.1", port=8000, debug=True)

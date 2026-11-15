"""API smoke tests (LLM off, no network).

Checks the shapes of /api/health, /api/datasets, /api/ui/analysis, /api/ask and
the 400 errors. Tests that need a cache CSV are skipped when the CSV is missing
or does not cover 1980-01 to 2025-12, because stream.get_series would otherwise
try to fetch from NASA (and earthaccess may ask for a login).
"""
import copy
import json
import os
import sys

import pandas as pd
import pytest

TESTS = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.dirname(TESTS)
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)

from ui_adapter import to_ui  # noqa: E402

BOX_TAG = "72_16_80_21"
STREAM_KEYS = {"T2M": "t2m", "PRECIP": "precip", "SUNLIGHT": "sunlight",
               "T2M_MIN": "t2m_min", "T2M_MAX": "t2m_max"}


def _cache_ok(stream_key):
    """True only if the Maharashtra CSV exists and covers every month 1980-01..2025-12."""
    path = os.path.join(BACKEND, "stream_cache", f"{stream_key}_{BOX_TAG}.csv")
    if not os.path.exists(path):
        return False
    try:
        d = pd.read_csv(path, parse_dates=["time"])
    except Exception:
        return False
    want = pd.date_range("1980-01-01", "2025-12-01", freq="MS")
    return bool(want.isin(pd.DatetimeIndex(d["time"])).all())


def _skip_unless_cache(stream_key):
    return pytest.mark.skipif(
        not _cache_ok(stream_key),
        reason=f"cache {stream_key}_{BOX_TAG}.csv missing or incomplete (skipped to avoid NASA)")


DATASET_PARAMS = [pytest.param(d, marks=_skip_unless_cache(k)) for d, k in STREAM_KEYS.items()]
needs_pond_caches = pytest.mark.skipif(
    not all(_cache_ok(k) for k in ("t2m", "precip", "sunlight")),
    reason="pond needs t2m, precip and sunlight caches (skipped to avoid NASA)")

UI_KEYS = {"regionId", "variableId", "title", "subtitle", "verdict", "verdict_code",
           "slopePerYear", "pValue", "ci95", "yearsUsed", "dataset", "series", "summary",
           "gap", "followUps", "simulated", "caption", "contract", "fragile", "fragileNote"}
UI_VERDICTS = {"significant", "not_enough_data", "not_significant"}
VERDICT_CODES = {"detected", "data_limited", "no_trend", "inconclusive", "masked"}
ASK_OK_KEYS = {"fallback", "domain", "confidence", "route_source", "level", "text",
               "used_llm", "phrase_note", "abstained", "result"}
ASK_FALLBACK_KEYS = {"fallback", "form", "form_text", "reason", "used_llm"}
RESULT_KEYS = {"domain", "region", "axes", "abstained", "abstain_reason", "risk_window",
               "tested_count", "llm_allowed_phrases", "caveats"}


@pytest.fixture(scope="module")
def client():
    # answer.load_domain() opens domains.json relative to the current folder
    with pytest.MonkeyPatch.context() as mp:
        mp.chdir(BACKEND)
        from app import app
        app.config["TESTING"] = True
        yield app.test_client()


def ask(client, **body):
    return client.post("/api/ask", json=body)


# ---- no caches needed -------------------------------------------------------

def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"ok": True}


def test_datasets_shape(client):
    resp = client.get("/api/datasets")
    assert resp.status_code == 200
    data = resp.get_json()
    assert set(data) == {"datasets", "regions"}
    assert [d["id"] for d in data["datasets"]] == list(STREAM_KEYS)
    for d in data["datasets"]:
        assert set(d) == {"id", "label", "units", "default_slope", "ready", "ready_regions"}
        assert isinstance(d["ready"], bool)
    assert [r["id"] for r in data["regions"]] == ["maharashtra", "rajasthan", "kerala", "gujarat"]
    for r in data["regions"]:
        assert set(r) == {"id", "label", "box"}
        assert len(r["box"]) == 4


BAD_GETS = [
    ("/api/ui/analysis", {"dataset": "NOPE"}, "unknown dataset"),
    ("/api/ui/analysis", {"region": "atlantis"}, "unknown region"),
    ("/api/series", {"dataset": "NOPE"}, "unknown dataset"),
    ("/api/analysis", {"region": "atlantis"}, "unknown region"),
    ("/api/answer", {"region": "atlantis"}, "unknown region"),
]


@pytest.mark.parametrize("url,params,fragment", BAD_GETS)
def test_bad_query_is_400_json_error(client, url, params, fragment):
    resp = client.get(url, query_string=params)
    assert resp.status_code == 400
    data = resp.get_json()
    assert set(data) == {"error"}
    assert fragment in data["error"]


def test_ask_fallback_post_shape(client):
    resp = ask(client, question="tell me a joke")
    assert resp.status_code == 200
    data = resp.get_json()
    assert set(data) == ASK_FALLBACK_KEYS
    assert data["fallback"] is True and data["used_llm"] is False
    form = data["form"]
    assert form["type"] == "guided_form"
    assert form["step1_pick_topic"]["options"][-1]["id"] == "none"
    assert isinstance(data["form_text"], str) and form["message"] in data["form_text"]
    assert "text" not in data and "result" not in data and "domain" not in data


def test_ask_fallback_get_shape(client):
    resp = client.get("/api/ask", query_string={"question": "tell me a joke"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert set(data) == ASK_FALLBACK_KEYS
    assert data["fallback"] is True


ASK_BAD = [
    ({"question": ""}, "missing"),
    ({"question": "tell me a joke", "region": "atlantis"}, "unknown region"),
    ({"question": "tell me a joke", "level": "expert"}, "level"),
    ({"question": "tell me a joke", "user_inputs": [1]}, "user_inputs"),
]


@pytest.mark.parametrize("body,fragment", ASK_BAD)
def test_ask_validation_runs_before_routing(client, body, fragment):
    """Bad region, level or user_inputs give 400 even for a question that would fall back."""
    resp = ask(client, **body)
    assert resp.status_code == 400
    data = resp.get_json()
    assert set(data) == {"error"}
    assert fragment in data["error"]


# ---- to_ui with years.needed_high = None (no caches, no server) -------------

def _pond_axis_results():
    with open(os.path.join(TESTS, "real_pond.json"), encoding="utf-8") as f:
        pond = json.load(f)
    return {a["name"]: a["result"] for a in pond["axes"]
            if isinstance(a.get("result"), dict) and "verdict" in a["result"]}


AXIS_NAMES = list(_pond_axis_results())


@pytest.mark.parametrize("name", AXIS_NAMES)
def test_to_ui_with_needed_high_none(name):
    contract = copy.deepcopy(_pond_axis_results()[name])
    contract["years"]["needed_high"] = None
    out = to_ui(contract, "T2M", "maharashtra")
    json.dumps(out, allow_nan=False)
    assert set(out) == UI_KEYS
    assert out["contract"]["years"]["needed_high"] is None
    for text in out["summary"].values():
        assert "None" not in text and "needed_high" not in text
    assert out["fragile"] == bool(contract["trend"].get("fragile"))
    assert (out["fragileNote"] is None) == (not out["fragile"])
    if out["verdict_code"] == "detected":
        assert out["gap"] is None
    else:
        assert "None" not in out["gap"]["tip"]


def test_to_ui_data_limited_with_every_years_field_missing():
    contract = copy.deepcopy(_pond_axis_results()[AXIS_NAMES[0]])
    contract["verdict"]["code"] = "data_limited"
    for key in ("needed_low", "needed_mid", "needed_high", "needed_for_meaningful"):
        contract["years"][key] = None
    out = to_ui(contract, "T2M", "maharashtra")
    json.dumps(out, allow_nan=False)
    assert out["verdict"] == "not_enough_data"
    assert out["gap"]["status"] == "data_limited"
    assert out["gap"]["yearsNeed"] == contract["years"]["have"]
    assert "None" not in out["gap"]["tip"]


# ---- need the caches --------------------------------------------------------

@pytest.mark.parametrize("dataset", DATASET_PARAMS)
def test_ui_analysis_shape(client, dataset):
    resp = client.get("/api/ui/analysis", query_string={"dataset": dataset, "region": "maharashtra"})
    assert resp.status_code == 200
    assert "NaN" not in resp.get_data(as_text=True)
    data = resp.get_json()
    assert set(data) == UI_KEYS
    assert data["variableId"] == dataset and data["regionId"] == "maharashtra"
    assert data["verdict"] in UI_VERDICTS
    assert data["verdict_code"] in VERDICT_CODES
    assert set(data["summary"]) == {"plain", "detailed", "pro"}
    assert data["followUps"] == [] and data["simulated"] is False
    assert isinstance(data["fragile"], bool)
    assert (data["fragileNote"] is None) == (not data["fragile"])
    assert data["series"], "series should not be empty"
    assert set(data["series"][0]) == {"year", "value", "trend", "low", "high"}
    if data["verdict_code"] == "detected":
        assert data["gap"] is None
    else:
        assert set(data["gap"]) == {"reason", "status", "yearsHave", "yearsNeed", "tip"}
    years = data["contract"]["years"]
    assert "needed_high" in years          # key is always there; value may be null
    assert "p_value_without_extreme_years" in data["contract"]["trend"]


@_skip_unless_cache("t2m")
def test_t2m_needed_high_is_null(client):
    """The owner says the engine now returns null here (same series as real_pond air_temp)."""
    data = client.get("/api/ui/analysis", query_string={"dataset": "T2M"}).get_json()
    assert data["contract"]["years"]["needed_high"] is None


@needs_pond_caches
@pytest.mark.parametrize("level", ["plain", "detailed", "pro"])
def test_ask_pond_shape(client, level):
    resp = ask(client, question="How long before a pond turns green with algae?", level=level)
    assert resp.status_code == 200
    data = resp.get_json()
    assert set(data) == ASK_OK_KEYS
    assert data["fallback"] is False and data["domain"] == "pond"
    assert data["level"] == level and data["used_llm"] is False
    assert isinstance(data["text"], str) and data["text"].strip()
    assert "needed_high" not in data["text"]
    assert data["abstained"] is True
    assert set(data["result"]) == RESULT_KEYS
    assert data["result"]["region"] == "Maharashtra"


@needs_pond_caches
def test_ask_my_pond_turned_green_routes_to_pond(client):
    data = ask(client, question="My pond turned green").get_json()
    assert data["fallback"] is False and data["domain"] == "pond"
    assert data["confidence"] == pytest.approx(0.667, abs=0.01)


@needs_pond_caches
def test_ask_citrus_shape(client):
    resp = ask(client, question="Why are my oranges so small this year?")
    assert resp.status_code == 200
    data = resp.get_json()
    assert set(data) == ASK_OK_KEYS
    assert data["fallback"] is False and data["domain"] == "citrus"
    assert data["abstained"] is True
    assert set(data["result"]) == RESULT_KEYS

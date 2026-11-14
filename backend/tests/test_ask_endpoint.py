"""Tests for POST /api/ask (LLM off). Skips when the Maharashtra caches are missing."""
import os
import sys

import pytest

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(BACKEND)
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)

BOX_TAG = "72_16_80_21"


REQUIRED_CACHES = ("t2m", "precip", "sunlight")


def _missing_caches():
    """Names of the cache CSVs these tests need that are not present (empty list = all present)."""
    missing = []
    for key in REQUIRED_CACHES:
        path = os.path.join(BACKEND, "stream_cache", f"{key}_{BOX_TAG}.csv")
        if not os.path.exists(path):
            missing.append(os.path.relpath(path, ROOT))
    return missing


needs_caches = pytest.mark.skipif(
    bool(_missing_caches()),
    reason="Maharashtra caches missing, run fetch_opendap.py first. Missing: "
           + ", ".join(_missing_caches()),
)

@pytest.fixture(scope="module")
def client():
    # answer.build() and load_domain() open domains.json relative to the current folder
    with pytest.MonkeyPatch.context() as mp:
        mp.chdir(BACKEND)
        from app import app
        app.config["TESTING"] = True
        yield app.test_client()


def ask(client, **body):
    return client.post("/api/ask", json=body)


# ---- no caches needed: routing fallback and input validation ---------------

def test_joke_returns_fallback(client):
    resp = ask(client, question="tell me a joke")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["fallback"] is True
    assert set(data) == {"fallback", "form", "form_text", "reason", "used_llm"}
    assert data["used_llm"] is False


def test_unknown_region_is_400(client):
    resp = ask(client, question="how long before my pond turns green?", region="atlantis")
    assert resp.status_code == 400
    assert "unknown region" in resp.get_json()["error"]


def test_unknown_user_inputs_key_is_400(client):
    resp = ask(client, question="How long can I leave my pond unattended before algae?",
               user_inputs={"definitely_not_an_axis": 1})
    assert resp.status_code == 400
    assert "unknown user_inputs" in resp.get_json()["error"]


def test_empty_body_is_400(client):
    resp = client.post("/api/ask")
    assert resp.status_code == 400


def test_bad_level_is_400(client):
    resp = ask(client, question="how long before my pond turns green?", level="expert")
    assert resp.status_code == 400


# ---- need the caches: full answer path -------------------------------------

@needs_caches
@pytest.mark.parametrize("question", [
    "How long before a pond turns green with algae?",
    "How long can I leave my pond unattended before algae?",
])
def test_pond_routes_and_abstains(client, question):
    resp = ask(client, question=question)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["fallback"] is False
    assert data["domain"] == "pond"
    assert data["abstained"] is True
    assert data["used_llm"] is False
    for key in ("text", "phrase_note", "result"):
        assert key in data
    # 4b: abstention should be one clean statement, not two stacked refusals
    assert data["text"].lower().count("cannot give") <= 1


@needs_caches
def test_oranges_route_to_citrus_and_abstain(client):
    resp = ask(client, question="Why are my oranges so small this year?")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["fallback"] is False
    assert data["domain"] == "citrus"
    assert data["abstained"] is True
    assert data["used_llm"] is False
    assert data["text"]
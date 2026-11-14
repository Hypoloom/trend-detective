"""The deterministic template must pass its own guard at every level (synthetic results only)."""
import os
import sys

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)

import pytest  # noqa: E402

import phrase  # noqa: E402

FRAGILE_SENTENCE = ("This result depends on a few extreme years: it is not significant "
                    "when the most extreme years are left out.")


def _ax(name, label, code, slope, fragile=False, summary=None, p=0.0166, pwo=0.0842):
    verdict = {"code": code, "label": "Trend detected" if code == "detected" else "No trend found"}
    if summary:
        verdict["summary"] = summary
    trend = {"slope_per_year": slope, "units": "mm/day", "p_value": p, "fragile": fragile,
             "p_value_without_extreme_years": pwo, "slope_ci": [slope - 0.01, slope + 0.01]}
    return {"name": name, "label": label, "status": "analyzed", "critical": False,
            "result": {"verdict": verdict, "trend": trend}}


_SUMMARY = "A statistically significant upward trend of 0.016 mm/day per year was found over 45.9 years of data."
_NOT_KNOWABLE = {"name": "nutrient_load", "label": "Nutrient load", "status": "not_knowable", "critical": True}

CASES = {
    "abstained": {"domain": "pond", "abstained": True,
                  "abstain_reason": "Cannot give a number. These critical factors are unknown here: Nutrient load.",
                  "axes": [_ax("rainfall", "Rainfall", "no_trend", 0.001), _NOT_KNOWABLE]},
    "abstained_with_detected_axis": {
        "domain": "pond", "abstained": True,
        "abstain_reason": "Cannot give a number. These critical factors are unknown here: Nutrient load.",
        "axes": [_ax("rainfall", "Rainfall", "detected", 0.016, summary=_SUMMARY), _NOT_KNOWABLE]},
    "no_trend": {"verdict": {"code": "no_trend", "label": "No trend found"},
                 "trend": {"slope_per_year": 0.002, "units": "K"}},
    "no_trend_axis": {"domain": "pond", "abstained": False,
                      "axes": [_ax("air_temperature", "Air temperature", "no_trend", 0.002)]},
    "detected_axis": {"domain": "pond", "abstained": False,
                      "axes": [_ax("rainfall", "Rainfall", "detected", 0.016, summary=_SUMMARY)]},
    "detected_top_level": {"verdict": {"code": "detected", "label": "Trend detected"},
                           "trend": {"slope_per_year": 0.016, "units": "mm/day"},
                           "axes": [{"name": "rainfall", "label": "Rainfall", "status": "analyzed"}]},
    "fragile": {"domain": "pond", "abstained": False,
                "axes": [_ax("rainfall", "Rainfall", "detected", 0.016, fragile=True,
                             summary=_SUMMARY + " " + FRAGILE_SENTENCE)]},
    "fragile_summary_lacks_sentence": {"domain": "pond", "abstained": False,
                                       "axes": [_ax("rainfall", "Rainfall", "detected", 0.016,
                                                    fragile=True, summary=_SUMMARY)]},
    "detected_and_fragile_mixed": {
        "domain": "pond", "abstained": False,
        "axes": [_ax("rainfall", "Rainfall", "detected", 0.016, fragile=True,
                     summary=_SUMMARY + " " + FRAGILE_SENTENCE),
                 _ax("sunlight", "Sunlight", "detected", -0.42),
                 _ax("air_temperature", "Air temperature", "no_trend", 0.002)]},
    "data_limited": {"verdict": {"code": "data_limited", "label": "Data limited"},
                     "years": {"have": 12, "needed_for_meaningful": 30}},
    "data_limited_axis": {"domain": "pond", "abstained": False,
                          "axes": [{"name": "rainfall", "label": "Rainfall", "status": "analyzed",
                                    "result": {"verdict": {"code": "data_limited", "label": "Data limited"},
                                               "trend": {"units": "mm/day"}}}]},
    # --- years.needed_high may become None (engine change planned): nothing may crash or print "None" ---
    "needed_high_none_data_limited": {
        "verdict": {"code": "data_limited", "label": "Data limited"},
        "years": {"have": 12, "needed_low": 18, "needed_high": None, "needed_for_meaningful": 30}},
    "needed_high_none_and_meaningful_none": {
        "verdict": {"code": "data_limited", "label": "Data limited"},
        "years": {"have": 12, "needed_low": 18, "needed_high": None, "needed_for_meaningful": None}},
    "needed_high_none_detected_top_level": {
        "verdict": {"code": "detected", "label": "Trend detected"},
        "trend": {"slope_per_year": 0.016, "units": "mm/day"},
        "years": {"have": 46, "needed_low": 18, "needed_high": None, "needed_for_meaningful": 30},
        "axes": [{"name": "rainfall", "label": "Rainfall", "status": "analyzed"}]},
    "needed_high_none_in_axis_result": {
        "domain": "pond", "abstained": False,
        "axes": [dict(_ax("air_temperature", "Air temperature", "no_trend", 0.0036),
                      result={"verdict": {"code": "no_trend", "label": "No trend found"},
                              "trend": {"slope_per_year": 0.0036, "units": "K"},
                              "years": {"have": 46, "needed_low": 18, "needed_high": None}})]},
}


@pytest.mark.parametrize("level", phrase.LEVELS)
@pytest.mark.parametrize("name", sorted(CASES))
def test_template_passes_its_own_guard(name, level):
    res = CASES[name]
    text = phrase.template_phrase(res, level)
    g = phrase.check_text(text, res)
    assert g.ok, (name, level, g.reasons, text)
    assert phrase.phrase_with_report(res, level)[1].note == "LLM off"


@pytest.mark.parametrize("level", phrase.LEVELS)
def test_detected_axis_template_has_association_wording(level):
    for name in ("detected_axis", "fragile", "detected_and_fragile_mixed", "abstained_with_detected_axis"):
        text = phrase.template_phrase(CASES[name], level).lower()
        assert "co-occurs with" in text, (name, level)


@pytest.mark.parametrize("level", phrase.LEVELS)
def test_fragile_axis_template_says_extreme_years(level):
    for name in ("fragile", "fragile_summary_lacks_sentence", "detected_and_fragile_mixed"):
        assert "extreme years" in phrase.template_phrase(CASES[name], level), (name, level)


def test_failed_template_guard_is_reported_in_the_note(monkeypatch):
    res = CASES["detected_axis"]
    monkeypatch.setattr(phrase, "template_phrase", lambda r, level="plain": "Rainfall rose by 9999.")
    text, rep = phrase.phrase_with_report(res, "plain")
    assert text == "Rainfall rose by 9999."          # the template is still returned
    assert rep.source == "template"
    assert rep.note.startswith("LLM off; template failed guard:") and "invented number" in rep.note
    # with an adapter that is rejected, both reasons are in the note
    _, rep = phrase.phrase_with_report(res, "plain", phrase.CallableAdapter(lambda s, u: "It rains because of heat."))
    assert rep.note.startswith("guard rejected:") and "template failed guard:" in rep.note
    # with an adapter that works, the template is not consulted
    _, rep = phrase.phrase_with_report(
        res, "plain", phrase.CallableAdapter(lambda s, u: "Rainfall co-occurs with a yearly change of 0.016 mm/day."))
    assert rep.source == "llm" and rep.note == "passed guard"


NEEDED_HIGH_CASES = [n for n in CASES if n.startswith("needed_high_none")]


@pytest.mark.parametrize("level", phrase.LEVELS)
@pytest.mark.parametrize("name", NEEDED_HIGH_CASES)
def test_needed_high_none_never_leaks_into_text_or_adapter(name, level):
    res = CASES[name]
    text = phrase.template_phrase(res, level)
    assert "None" not in text and "null" not in text and "nan" not in text.lower().split(), (name, level, text)
    seen = {}

    def fake(system, user):
        seen["user"] = user
        return text                       # a writer that repeats the template

    out, rep = phrase.phrase_with_report(res, level, phrase.CallableAdapter(fake))
    assert "needed_high" in seen["user"] and "null" in seen["user"]   # sent as JSON null, not the string "None"
    assert rep.source == "llm", rep.note
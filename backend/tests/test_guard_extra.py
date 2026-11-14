"""Guard gap tests: number words, direction words, association wording."""
import os
import sys

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(BACKEND)
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)

import phrase  # noqa: E402

TREND = {"verdict": {"code": "trend"}, "axes": [{"name": "night_temperature"}]}
NO_TREND = {"verdict": {"code": "no_trend"}}


def reasons(text, result):
    return phrase.check_text(text, result).reasons


def has(rs, fragment):
    return any(fragment in r for r in rs)


# ---- number words ----
def test_number_words_parsed():
    assert phrase.number_words_in("twelve and twenty-five and 7") == [("twelve", 12), ("twenty-five", 25)]


def test_plain_one_is_not_a_number_word():
    assert phrase.number_words_in("no one knows, one of them") == []


def test_invented_number_word_is_flagged():
    assert has(reasons("Night temperature went up by twelve degrees.", TREND), "invented number word")


# ---- direction words ----
def test_direction_without_trend_is_flagged():
    assert has(reasons("Night temperature is rising.", NO_TREND), "without a reported trend")


def test_negated_direction_is_allowed():
    assert not has(reasons("There is no upward or downward trend here.", NO_TREND), "direction wording")


def _top(slope):
    """A top-level detected result whose slope is where the engine puts it: trend.slope_per_year."""
    return {"verdict": {"code": "detected"}, "trend": {"slope_per_year": slope}}


def test_direction_contradicting_slope_is_flagged():
    assert has(reasons("Night temperature is falling.", _top(0.5)), "contradicts a positive slope")
    assert has(reasons("Night temperature is rising.", _top(-0.5)), "contradicts a negative slope")


def test_matching_direction_is_not_flagged_for_contradiction():
    assert not has(reasons("Night temperature is rising.", _top(0.5)), "contradicts")
    assert not has(reasons("Night temperature is falling.", _top(-0.5)), "contradicts")


# ---- association wording ----
def test_trend_without_association_wording_is_flagged():
    assert has(reasons("Night temperature has a trend.", TREND), "co-occurs with")


def test_trend_with_association_wording_passes_that_check():
    rs = reasons("Night temperature co-occurs with a longer warm season.", TREND)
    assert not has(rs, "co-occurs with' or")
    rs = reasons("Night temperature is associated with the pond question.", TREND)
    assert not has(rs, "co-occurs with' or")

    

# ---- risk-window comparison sentence: "higher than" / "lower than" is not a direction word ----
def test_higher_lower_comparison_is_not_a_direction_word():
    for word in ("higher", "lower"):
        text = f"In the last 20 years of the record these months averaged 0.5 K {word} than in the 26 years before."
        for res in (NO_TREND, _top(0.5), _top(-0.5)):
            probs = phrase.extra_problems(text, text.lower(), res, [20, 26, 0.5])
            assert not has(probs, "direction wording"), (word, res, probs)


# ---- per-axis trends need association wording, at plain level too ----
def _pond_result(code):
    return {
        "domain": "pond", "abstained": True,
        "abstain_reason": "Cannot give a number. These critical factors are unknown here: Nutrient load.",
        "axes": [{"name": "rainfall", "label": "Rainfall", "status": "analyzed", "critical": False,
                  "result": {"verdict": {"code": code, "label": "Trend detected" if code == "detected" else "No trend found"},
                             "trend": {"slope_per_year": 0.00632509, "units": "mm/day"}}}],
    }


def test_plain_template_adds_association_wording_for_axis_trend():
    assert "co-occurs with" in phrase.template_phrase(_pond_result("detected"), "plain")


def test_plain_template_omits_it_when_no_axis_trend():
    assert "co-occurs with" not in phrase.template_phrase(_pond_result("no_trend"), "plain")

# ---- fragile trends: the engine's "extreme years" sentence must reach the text ----
FRAGILE_SENTENCE = ("This result depends on a few extreme years: it is not significant "
                    "when the most extreme years are left out.")


def _fragile_result(fragile, sentence_in_summary=True):
    summary = "A statistically significant upward trend of 0.016 mm/day per year was found over 45.9 years of data."
    if fragile and sentence_in_summary:
        summary += " " + FRAGILE_SENTENCE
    return {
        "domain": "pond", "abstained": False,
        "axes": [{"name": "rainfall", "label": "Rainfall", "status": "analyzed", "critical": False,
                  "result": {"verdict": {"code": "detected", "label": "Trend detected", "summary": summary},
                             "trend": {"slope_per_year": 0.016, "units": "mm/day",
                                       "p_value_without_extreme_years": 0.0842, "fragile": fragile}}}],
    }


def test_fragile_sentence_reaches_every_level():
    res = _fragile_result(True)
    for level in ("plain", "detailed", "pro"):
        text = phrase.template_phrase(res, level)
        assert "depends on a few extreme years" in text, level
        assert phrase.check_text(text, res).ok, (level, phrase.check_text(text, res).reasons)


def test_not_fragile_has_no_extreme_years_sentence():
    res = _fragile_result(False)
    for level in ("plain", "detailed", "pro"):
        assert "extreme years" not in phrase.template_phrase(res, level), level


def test_fragile_falls_back_when_summary_lacks_sentence():
    res = _fragile_result(True, sentence_in_summary=False)
    for level in ("plain", "detailed", "pro"):
        assert "depends on a few extreme years" in phrase.template_phrase(res, level), level

        

# ---- pro level: p-value without the most extreme years, only for fragile axes ----
def _pro_axis_result(fragile, include_key=True, without=0.0842):
    trend = {"slope_per_year": 0.016, "units": "mm/day", "p_value": 0.0166, "fragile": fragile}
    if include_key:
        trend["p_value_without_extreme_years"] = without
    return {
        "domain": "pond", "abstained": False,
        "axes": [{"name": "rainfall", "label": "Rainfall", "status": "analyzed", "critical": False,
                  "result": {"verdict": {"code": "detected", "label": "Trend detected",
                                         "summary": "A statistically significant upward trend of 0.016 mm/day per year was found."},
                             "trend": trend}}],
    }


PWO_TEXT = "p-value 0.0166; p-value without the most extreme years 0.0842."


def test_pro_shows_p_value_without_extreme_years_when_fragile():
    res = _pro_axis_result(True)
    text = phrase.template_phrase(res, "pro")
    assert PWO_TEXT in text
    assert phrase.check_text(text, res).ok, phrase.check_text(text, res).reasons
    for level in ("plain", "detailed"):
        assert "without the most extreme years" not in phrase.template_phrase(res, level), level


def test_pro_omits_it_when_not_fragile():
    res = _pro_axis_result(False)
    text = phrase.template_phrase(res, "pro")
    assert "p-value 0.0166." in text
    assert "without the most extreme years" not in text


def test_pro_missing_key_does_not_crash():
    res = _pro_axis_result(True, include_key=False)
    text = phrase.template_phrase(res, "pro")
    assert "p-value 0.0166." in text
    assert "without the most extreme years" not in text


def test_pro_uses_value_from_result_not_a_constant():
    res = _pro_axis_result(True, without=0.0731)
    text = phrase.template_phrase(res, "pro")
    assert "p-value without the most extreme years 0.0731." in text
    assert "0.0842" not in text



# ======== axis-level guard (pond-style results: no top-level verdict) ========
def _ax(name, label, code, slope=None, fragile=False, extra_trend=None, summary=None, status="analyzed"):
    trend = {"slope_per_year": slope, "units": "mm/day", "fragile": fragile}
    trend.update(extra_trend or {})
    verdict = {"code": code, "label": "Trend detected" if code == "detected" else "No trend found"}
    if summary:
        verdict["summary"] = summary
    return {"name": name, "label": label, "status": status, "critical": False,
            "result": {"verdict": verdict, "trend": trend}}


def _pond(*axes, **kw):
    return {"domain": "pond", "abstained": False, "axes": list(axes), **kw}


MIXED = _pond(_ax("rainfall", "Rainfall", "detected", 0.016),
              _ax("sunlight", "Sunlight", "detected", -0.42))
ASSOC_TAIL = " This co-occurs with the question you asked about."


def direction_problems(text, res):
    return [p for p in phrase.extra_problems(text, text.lower(), res, []) if "direction wording" in p]


def test_reported_trends_lists_top_level_and_every_axis():
    res = _pond(_ax("rainfall", "Rainfall", "detected", 0.016, fragile=True),
                _ax("air_temperature", "Air temperature", "no_trend", 0.001),
                {"name": "nutrient_load", "label": "Nutrient load", "status": "not_knowable"})
    got = phrase.reported_trends(res)
    assert [(e["axis"], e["code"], e["reported"], e["slope"], e["fragile"]) for e in got] == [
        ("rainfall", "detected", True, 0.016, True),
        ("air_temperature", "no_trend", False, 0.001, False),
        ("nutrient_load", None, False, None, False)]
    top = phrase.reported_trends(_top(0.5))
    assert len(top) == 1 and top[0]["axis"] is None and top[0]["reported"] and top[0]["slope"] == 0.5


# 1. mixed result: each axis checked against its own slope
def test_mixed_result_rainfall_rising_passes_sunlight_rising_fails():
    assert direction_problems("Rainfall is rising.", MIXED) == []
    assert direction_problems("Sunlight is falling.", MIXED) == []
    bad = direction_problems("Sunlight is rising.", MIXED)
    assert has(bad, "contradicts the slope of 'Sunlight'"), bad
    bad = direction_problems("Rainfall is falling.", MIXED)
    assert has(bad, "contradicts the slope of 'Rainfall'"), bad


# 2. a no_trend axis next to a detected positive axis
def test_no_trend_axis_cannot_be_called_rising():
    res = _pond(_ax("rainfall", "Rainfall", "detected", 0.016),
                _ax("air_temperature", "Air temperature", "no_trend", 0.002))
    bad = direction_problems("Air temperature is rising.", res)
    assert has(bad, "has no detected trend"), bad
    assert direction_problems("Rainfall is rising.", res) == []


def test_unanalyzed_axis_cannot_be_called_rising():
    res = _pond(_ax("rainfall", "Rainfall", "detected", 0.016),
                {"name": "nutrient_load", "label": "Nutrient load", "status": "not_knowable"})
    assert has(direction_problems("Nutrient load is rising.", res), "has no detected trend")


def test_sentence_naming_several_axes_or_none_uses_whole_text_rule():
    # several axes: up needs some detected positive axis, down needs some detected negative axis
    assert direction_problems("Rainfall and sunlight are both changing, and rain is rising.", MIXED) == []
    only_up = _pond(_ax("rainfall", "Rainfall", "detected", 0.016), _ax("sunlight", "Sunlight", "no_trend"))
    assert has(direction_problems("Rainfall and sunlight are both falling.", only_up),
               "contradicts a positive slope")
    # no axis named
    assert direction_problems("Things are rising here.", MIXED) == []
    assert has(direction_problems("Things are rising here.",
                                  _pond(_ax("rainfall", "Rainfall", "no_trend"))), "without a reported trend")


def test_negated_direction_word_is_ignored_at_axis_level():
    res = _pond(_ax("rainfall", "Rainfall", "no_trend"))
    assert direction_problems("Rainfall is not rising.", res) == []


def test_longer_axis_name_wins_over_shorter():
    res = _pond(_ax("temperature", "Temperature", "no_trend"),
                _ax("air_temperature", "Air temperature", "detected", 0.03))
    assert direction_problems("Air temperature is rising.", res) == []


# regression: min_detectable_slope (always positive) must never be read as a trend slope
def test_min_detectable_slope_is_never_a_trend_slope():
    res = _pond(_ax("sunlight", "Sunlight", "detected", -0.42,
                    extra_trend={"min_detectable_slope": 0.02, "slope_meaning": 0.5}),
                **{"trend": {"min_detectable_slope": 0.02, "slope_ci": [-0.6, -0.2]}})
    assert [e["slope"] for e in phrase.reported_trends(res)] == [-0.42]
    assert has(direction_problems("Sunlight is rising.", res), "contradicts the slope of 'Sunlight'")
    assert direction_problems("Sunlight is falling.", res) == []
    # whole-text path too: no axis named, the only detected slope is negative
    assert has(direction_problems("Things are rising here.", res), "contradicts a negative slope")
    # a result whose ONLY slope-like key is min_detectable_slope has no usable slope
    only_min = {"verdict": {"code": "detected"}, "trend": {"min_detectable_slope": 0.02}}
    assert has(direction_problems("Things are falling here.", only_min), "no reported slope")


# 3. engine-only text passes, even with engine words that the writer may not use
def test_engine_only_text_passes():
    summary = ("A statistically significant upward trend of 0.016 mm/day per year was found over 45.9 years "
               "of data. This result depends on a few extreme years: it is not significant when the most "
               "extreme years are left out.")
    res = _pond(_ax("rainfall", "Rainfall", "detected", 0.016, fragile=True, summary=summary),
                caveats=[{"text": "This is not proof of cause, and rainfall is rising only in this record."}])
    text = summary + " This is not proof of cause, and rainfall is rising only in this record."
    g = phrase.check_text(text, res)
    assert g.ok, g.reasons


# 4. fragile axis: naming it needs "extreme years"
def test_fragile_axis_named_without_extreme_years_fails():
    res = _pond(_ax("rainfall", "Rainfall", "detected", 0.016, fragile=True))
    bad = phrase.extra_problems("Rainfall co-occurs with a yearly change.", "rainfall co-occurs with a yearly change.", res, [])
    assert has(bad, "extreme years"), bad
    ok_text = "Rainfall co-occurs with a yearly change that depends on a few extreme years."
    assert not has(phrase.extra_problems(ok_text, ok_text.lower(), res, []), "extreme years")
    # not named by the writer -> no demand
    t = "This co-occurs with the question you asked about."
    assert not has(phrase.extra_problems(t, t.lower(), res, []), "extreme years")


# rule 1: association wording for a detected axis, scoped to the writer's own words
def test_detected_axis_named_needs_association_wording():
    res = _pond(_ax("rainfall", "Rainfall", "detected", 0.016))
    bad = phrase.extra_problems("Rainfall changed a little.", "rainfall changed a little.", res, [])
    assert has(bad, "co-occurs with")
    bad = phrase.extra_problems("The slope is small.", "the slope is small.", res, [])
    assert has(bad, "co-occurs with")
    good = "Rainfall co-occurs with a small change."
    assert not has(phrase.extra_problems(good, good.lower(), res, []), "co-occurs with")
    # a no_trend axis does not trigger it, and neither does text that names no detected axis
    nt = _pond(_ax("rainfall", "Rainfall", "no_trend"))
    assert not has(phrase.extra_problems("Rainfall changed a little.", "rainfall changed a little.", nt, []), "co-occurs with")
    other = "The record is short."
    assert not has(phrase.extra_problems(other, other.lower(), res, []), "co-occurs with")
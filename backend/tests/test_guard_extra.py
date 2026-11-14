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


def test_direction_contradicting_slope_is_flagged():
    res = {**TREND, "slope": 0.5}
    assert has(reasons("Night temperature is falling.", res), "contradicts a positive slope")
    res = {**TREND, "slope": -0.5}
    assert has(reasons("Night temperature is rising.", res), "contradicts a negative slope")


def test_matching_direction_is_not_flagged_for_contradiction():
    res = {**TREND, "slope": 0.5}
    assert not has(reasons("Night temperature is rising.", res), "contradicts")


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
        for res in (NO_TREND, {**TREND, "slope": 0.5}, {**TREND, "slope": -0.5}):
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


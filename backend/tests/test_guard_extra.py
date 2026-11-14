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
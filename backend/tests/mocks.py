"""Mock engine results (shape from contract.run_analysis + PLANNED fields)."""
import copy


def _base():
    return {
        "verdict": {"code": "no_trend", "label": "No trend found", "summary": "No clear trend."},
        "years": {"have": 46, "needed_low": 30, "needed_mid": 50, "needed_high": 80,
                  "needed_for_meaningful": 70, "meaningful_slope": 0.02},
        "trend": {"slope_per_year": 0.0045, "slope_ci": [-0.0003, 0.0091], "p_value": 0.237,
                  "min_detectable_slope": 0.0128, "units": "K"},
        "noise": {"sigma": 0.31, "lag1_autocorr": 0.12},
        "provenance": {"dataset": "MERRA-2 M2TMNXSLV", "variable": "t2m", "region": "Maharashtra",
                       "start": 1980, "end": 2025, "simulated": False},
        "caveats": ["Values are anomalies, not absolute temperatures."],
        "tested_count": 1,
    }


def no_trend():
    return _base()


def detected():
    r = _base()
    r["verdict"] = {"code": "detected", "label": "Trend detected", "summary": "A clear trend."}
    r["trend"].update(slope_per_year=0.031, slope_ci=[0.012, 0.05], p_value=0.004)
    return r


def data_limited():
    r = _base()
    r["verdict"] = {"code": "data_limited", "label": "Data limited", "summary": "Too short."}
    r["years"]["have"] = 12
    return r


def pond_abstained():
    r = _base()
    r["verdict"] = {"code": "inconclusive", "label": "Inconclusive", "summary": "Cannot answer."}
    r["abstained"] = True
    r["abstain_reason"] = ("Nutrient load and existing algae are not knowable from this data, "
                           "so no number of days can be given.")
    r["risk_window"] = "warm, still weeks in late spring"
    r["axes"] = [
        {"name": "air_temperature", "source": "nasa_data", "critical": False, "status": "trend_not_found"},
        {"name": "nutrient_load", "source": "not_knowable", "critical": True, "status": "not_knowable"},
        {"name": "existing_algae", "source": "not_knowable", "critical": True, "status": "not_knowable"},
    ]
    r["llm_allowed_phrases"] = ["co-occurs with", "not found"]
    return r


def citrus_abstained():
    r = pond_abstained()
    r["abstain_reason"] = "There is no fruit-size data, so the data cannot say why the fruit is small."
    r["risk_window"] = None
    r["axes"] = [
        {"name": "air_temperature", "source": "nasa_data", "critical": False, "status": "trend_not_found"},
        {"name": "fruit_size", "source": "not_knowable", "critical": True, "status": "not_knowable"},
    ]
    return r


def hidden_critical():
    """Engine forgot to set abstained, but a critical axis is not knowable."""
    r = pond_abstained()
    r["abstained"] = False
    r["abstain_reason"] = None
    r["risk_window"] = None
    return r


def all_mocks():
    return {f.__name__: f() for f in (no_trend, detected, data_limited, pond_abstained,
                                      citrus_abstained, hidden_critical)}

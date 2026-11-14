"""meaningful.py - smallest trend that matters, per variable. A domain choice, not a measurement:
every value is a placeholder until sourced. Verdicts depend on these numbers."""
import numpy as np

RULES = {
    "t2m":      dict(kind="absolute", per_year=0.02,
                     basis="about the recent global warming rate (~0.2 K/decade); placeholder"),
    "precip":   dict(kind="relative", pct_per_decade=5.0,
                     basis="5% of the long-term mean per decade; project choice, placeholder"),
    "sunlight": dict(kind="relative", pct_per_decade=2.0,
                     basis="2% of the long-term mean per decade; project choice, placeholder"),
    "t2m_min":  dict(kind="absolute", per_year=0.02,
                     basis="same as t2m: about the recent global warming rate; placeholder"),
    "t2m_max":  dict(kind="absolute", per_year=0.02,
                     basis="same as t2m: about the recent global warming rate; placeholder"),
}


def resolve(name, series):
    """Return {value, rule, basis}; value is in the series' units per year."""
    r = RULES[name]
    if r["kind"] == "absolute":
        v, rule = r["per_year"], f"{r['per_year']} per year (absolute)"
    else:
        v = abs(float(np.nanmean(series))) * r["pct_per_decade"] / 100.0 / 10.0
        rule = f"{r['pct_per_decade']}% of the mean per decade"
    return dict(value=v, rule=rule, basis=r["basis"])
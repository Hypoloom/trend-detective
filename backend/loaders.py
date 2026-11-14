import io
import pandas as pd


def load_giovanni_csv(path, min_valid_frac=0.8):
    """Giovanni time-series CSV -> monthly pd.Series (DatetimeIndex, MS freq)."""
    with open(path, encoding="utf-8-sig") as f:
        lines = f.read().splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.lower().startswith("time,"))
    df = pd.read_csv(io.StringIO("\n".join(lines[start:])))
    t = pd.to_datetime(df.iloc[:, 0], utc=True).dt.tz_localize(None)
    v = pd.to_numeric(df.iloc[:, 1], errors="coerce")
    v = v.mask((v <= -9e30) | (v == -9999))  # fill values
    s = pd.Series(v.to_numpy(), index=t).sort_index()
    s = s[~s.index.duplicated()]
    g = s.resample("MS")
    m = g.mean()
    m[g.count() / g.size().clip(lower=1) < min_valid_frac] = float("nan")
    m.name = df.columns[1]
    return m


if __name__ == "__main__":
    import sys
    from engine import analyze
    s = load_giovanni_csv(sys.argv[1])
    print(s.head(3), "\n", len(s), "months,", s.isna().sum(), "missing")
    print(analyze(s.dropna()))
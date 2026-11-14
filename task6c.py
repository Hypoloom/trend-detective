import numpy as np
import scipy.stats as st
import stream

s = stream.get_series("precip", (72, 16, 80, 21), 1980, 2025)
t = (s.index.year + (s.index.month - 1) / 12).values
anom = s.groupby(s.index.month).transform(lambda x: x - x.mean())

wet = s.index.month.isin([6, 7, 8, 9]).astype(bool)
for name, m in [("Jun-Sep", wet), ("Oct-May", ~wet)]:
    x, y = t[m], anom.values[m]
    print(f"{name} monthly anom  n={m.sum()}  TS {st.theilslopes(y, x)[0]:.5f}  OLS {st.linregress(x, y).slope:.5f}")

# Same split at annual resolution (mean of the season per year)
for name, months in [("Jun-Sep", [6, 7, 8, 9]), ("Oct-May", [10, 11, 12, 1, 2, 3, 4, 5])]:
    sub = s[s.index.month.isin(months)]
    a = sub.groupby(sub.index.year).mean()
    print(f"{name} annual means  TS {st.theilslopes(a.values, a.index.values)[0]:.5f}  OLS {st.linregress(a.index.values, a.values).slope:.5f}  mean {a.mean():.3f}")
    
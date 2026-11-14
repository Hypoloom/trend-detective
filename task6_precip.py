import numpy as np
import scipy.stats as st
import stream

# Fetch the monthly series (takes about 80 s)
s = stream.get_series("precip", (72, 16, 80, 21), 1980, 2025)

# Annual means. Assumes s has a DatetimeIndex (UNVERIFIED; check the print below).
print(type(s.index), s.index[:3])
a = s.groupby(s.index.year).mean()
print(a.round(3).to_string())

# Compare trend estimators over the full record and two halves
for lo, hi in [(1980, 2025), (1980, 2002), (2003, 2025)]:
    b = a.loc[lo:hi]
    x = b.index.values
    ols = st.linregress(x, b.values).slope
    ts = st.theilslopes(b.values, x)[0]
    print(f"{lo}-{hi}  OLS {ols:.5f}  Theil-Sen {ts:.5f}")

# OLS with the 3 wettest years removed
top3 = a.nlargest(3).index
rest = a.drop(top3)
print("Top-3 years:", list(top3))
print("OLS without them:", st.linregress(rest.index.values, rest.values).slope)
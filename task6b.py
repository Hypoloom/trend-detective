import scipy.stats as st
import stream

s = stream.get_series("precip", (72, 16, 80, 21), 1980, 2025)
t = (s.index.year + (s.index.month - 1) / 12).values

print("monthly raw   TS", st.theilslopes(s.values, t)[0], " OLS", st.linregress(t, s.values).slope)

anom = s.groupby(s.index.month).transform(lambda x: x - x.mean())
print("monthly anom  TS", st.theilslopes(anom.values, t)[0], " OLS", st.linregress(t, anom.values).slope)

a = s.groupby(s.index.year).mean()
print("mean 1980-2002:", a.loc[:2002].mean(), " mean 2003-2025:", a.loc[2003:].mean())
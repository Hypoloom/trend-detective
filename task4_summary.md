# Task 4: Weatherhead et al. (1998) check

Paper: Weatherhead, Reinsel, Tiao, Meng, Choi, Cheang, Keller, DeLuisi, Wuebbles, Kerr, Miller, Oltmans, Frederick (1998), "Factors affecting the detection of trends", J. Geophys. Res. 103(D14), 17149-17161, doi:10.1029/98JD00995. Read from the Harvard-hosted PDF.

Engine formula (from the brief): years_needed = (3.3 * sigma / w * sqrt((1+phi)/(1-phi))) ** (2/3)

## Result: the formula in the brief matches the paper's Eq. (3)

| Item | Brief (from memory) | Paper | Result |
|---|---|---|---|
| Constant 3.3 | 3.3 | 3.3, for detection with probability 0.90 at 95% confidence (decision rule: trend / its s.d. > 2). Larger for higher certainty. | Match |
| Exponent | 2/3 | 2/3 (Eq. 3) | Match |
| Autocorrelation | sqrt((1+phi)/(1-phi)) inside the bracket | Same. Equivalent to the text statement that positive autocorrelation multiplies n* by about [(1+phi)/(1-phi)]^(1/3) | Match |

Equation numbers: (1) trend model Y = mu + w*X + N, AR(1) noise; (2) approximate s.d. of the trend estimate; Eq. (3) n*; (4) uncertainty factor B and 95% interval (n*e^-B, n*e^B) for n* when phi is estimated; (5)-(7) version with a level shift; Appendix A3-A5 exact variances.
The s.d. in terms of sigma_N (stated in the text after Eq. 2): s.d.(w_hat) = sigma_N * sqrt((1+phi)/(1-phi)) * n^(-3/2).

## Checks I ran (VERIFIED: computed)

Eq. (3) against the paper's Table 1 (sigma_N in %, trend 0.5 %/yr unless noted):

| sigma_N | phi | Formula | Table 1 |
|---|---|---|---|
| 0.25 | 0 | 1.40 | 1.4 |
| 10 | 0 | 16.33 | 16.3 |
| 10 | 0.5 | 23.55 | 23.4 |
| 4 | 0.5 | 12.79 | 12.6 |
| 10 | 0.8 | 33.97 | 33.3 |
| 20 | 0.8 | 53.93 | 53.3 |
| 20 (0.1 %/yr) | 0.8 | 157.68 | 157.0 |

Formula and table agree within 2%, and the formula runs slightly high when phi is large.

Engine numbers (sigma = 0.7887, phi = 0.404, pilot box T2M) reproduced with Eq. (3):

| Slope | Formula | Engine |
|---|---|---|
| 0.02 | 34.17 | 34.2 |
| 0.01 | 54.24 | 54.2 |
| 0.04 | 21.53 | 21.5 |
| min detectable at 45.9 years | 0.012846 | 0.012839 |
| T2MMAX (sigma 1.0659, phi 0.428), slope 0.02 | 42.6 | 42.6 |
| T2MMIN (sigma 0.7628, phi 0.355), slope 0.02 | 32.2 | 32.2 |

## Discrepancies and notes

1. The paper's own worked example (sigma_N = 3.1%, w = 0.3 %/yr, phi = 0.32) says Eq. (3) gives 13.6 years. Computing Eq. (3) gives 13.12. About 3.5% apart. Minor, inside the paper, not an engine fault.
2. "needed_mid" = 98.1 years uses the OLS slope (0.00411), not the Theil-Sen slope (0.00448) shown as the headline slope. With 0.00448 the formula gives 92.6; with 0.00411 it gives 98.05. Engine internals not read (engine.py not seen); inferred from numbers.
3. The 71.2 and 185.1 bounds for the observed slope: method not identified (not Eq. 4, which is symmetric on the log scale). UNVERIFIED.
4. Method mismatch: the paper's n* assumes a GLS trend estimate on MONTHLY data with AR(1) noise. The engine's p-value is Mann-Kendall on ANNUAL means (contract.py, p_value_method). So "years needed" and the significance test come from different frameworks.
5. The formula needs monthly, deseasonalized sigma_N and lag-1 phi in the same units as the slope. Whether the engine's sigma and phi come from monthly deseasonalized values is UNVERIFIED (engine.py not read). The values (0.79 K, 0.40) look plausible for monthly anomalies.
6. n* is the time to detect a given trend with 90% probability. Plain-language wording in the app should not read as "needed to become significant".
7. The paper says the approximation is accurate when phi is not close to 1, and the level-shift (Eq. 5-7) versions are needed if instruments change. MERRA-2 uses changing observing systems, so level shifts are a possible issue. Not tested.

## Labels
- VERIFIED: constants, exponent, role of phi (read the paper); Table 1 and engine reproduction (computed).
- UNVERIFIED: engine.py internals; how sigma and phi are estimated; bounds 71.2 and 185.1.
- Note: the text extracted from the PDF is scrambled, and Eq. (3) itself did not extract cleanly. I rebuilt it from the surrounding text and then checked it against the paper's Table 1 numbers.
# Backend notes

## What is here
- engine.py: trend analysis. OLS and Theil-Sen slopes, Mann-Kendall on annual means, years-needed estimate (Weatherhead-style, formula still to verify against the paper), detectability floor, rule-based verdicts, regional masking check.
- contract.py: run_analysis() returns the one JSON shape the frontend should use. Run `python contract.py sample/t2m.csv 0.02` to see it.
- loaders.py: reads a Giovanni time-series CSV into a monthly pandas Series.
- fetch.py: pulls MERRA-2 monthly data through earthaccess, box-averaged. See the data problem below.
- validate.py, validate_regions.py: many-seed tests on synthetic data with a known answer.
- sample/t2m.csv: MERRA-2 T2M, Maharashtra box (72,16,80,21), 1980-2025, from Giovanni.

Run everything from inside backend/ (the imports are flat).

## Validation so far (200 seeds per row)
- True trend 0.02/yr, noise 0.5, AR1 0.5: Detected 12% at 10 yrs, 49% at 20, 94% at 30, 100% at 45.
- No trend: Detected 3-8%. "No trend found" reachable only when a "meaningful" slope is passed to analyze().
- Two regions with opposite trends: Masked by aggregation 70% at 20 yrs, 91-93% at 30-45 yrs.

## Known issue: data loading (needs fixing)
- fetch.py downloads whole global monthly files (about 52 MB each, about 29 GB for 1980-2025 per product), keeps one box average per month, and deletes the files. It resumes per year via year_cache/. It works but takes about 50 min per variable.
- Opening files with xarray cost 3.3 s each; fetch.py reads with raw h5py instead (near zero).
- TODO: make data available live at runtime without the whole-file downloads. Options not yet tried: OPeNDAP subsetting of the MERRA-2 collections (unverified), Hydrology Data Rods, Harmony. Streaming files with earthaccess.open took about 17 s per month, too slow for a live request.
- For the demo, pre-cached series CSVs behind a small get_series(dataset, region) function are the safe fallback.
- PRECTOTCORR (M2TMNXFLX) has not been fetched yet. h5py does not apply scale/offset or decode time; this was checked for T2M only.

## Open decisions
- The "meaningful" slope per variable (for example 0.02 K/yr for T2M is a placeholder). It decides between "Data-limited" and "No trend found".
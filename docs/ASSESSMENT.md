# Assessment: strengths and flaws

Labels: **MEASURED** = a number we computed or a test we saw pass. **CODE** = read in the source. **INFERENCE** = reasoning, not checked. **DESIGN** = a deliberate choice.

## Strengths

- **It explains "no trend".** For a not-detected result it gives the years of data, the years needed for the chosen meaningful size, the smallest trend the record could detect, the 95% range, and whether the range is below the meaningful size. (MEASURED on Maharashtra air temperature: 46 years; 34.2 years needed for 0.02 K/yr.)
- **It abstains.** Questions with critical unknowns (nutrient load, variety, crop load) get "cannot give a definite answer" plus a risk window for the pond, never a made-up number of days. (DESIGN; tested.)
- **Numbers are guarded.** Every text must use only numbers in the computed result, and the guard blocks causal words, "proof" wording, softened abstention, direction words that contradict the slope, and "no change" wording for a no-trend axis. (250 pytest tests pass.)
- **Works with no LLM.** All text is from templates; a test confirms no network imports. (MEASURED by test.)
- **Honest about fragility.** A detected trend that disappears when the 3 most extreme years are dropped is flagged "fragile" (for example Maharashtra rainfall). (MEASURED.)
- **Compares fairly.** Region comparison names a leader only when the 95% ranges do not overlap, and says rankings are not detected trends. (MEASURED on real data.)
- **Serves from cache.** The server never calls NASA while serving, so a demo cannot fail on NASA's servers. (CODE.)
- **Tested and documented.** 250 pytest tests, 120 unittest tests, an API reference, and a testing guide.
- **Fast.** A warm analysis takes about 0.01 to 0.02 s; `/api/ask` about 0.05 to 0.07 s per level locally. (MEASURED locally; live latency not measured.)
- **Statistical engine validated on synthetic data.** Detection rises with record length as expected, and null false positives stay at 3 to 8%. (MEASURED, 200 seeds.)

## Flaws and limits

### Science
- **Thresholds are placeholders.** The meaningful sizes (0.02 K/yr, 5% of the mean per decade for rain, 2% for sunlight) are project choices, not standards. Verdicts depend on them. The 0.02 K/yr size is larger than observed all-India warming reported in one source (about 0.15 C per decade), so real regional warming can read as "below meaningful". (figure reported by a teammate; the source was not re-opened by Claude, so treat it as unverified.)
- **Mann-Kendall ignores autocorrelation.** Measured false-positive rate on null data is 8% against 5% expected. (MEASURED.)
- **Years-needed carries large uncertainty** (roughly 20 to 60%), clips lag-1 autocorrelation at 0.9, and does not model level shifts. (CODE and project record.)
- **Season subsets are approximate.** Months from different years are treated as adjacent when estimating noise. (INFERENCE from reading the engine.)
- **One reanalysis only.** All four regions and all five variables come from MERRA-2, so agreement between regions is not independent confirmation. MERRA-2 is a model product, not a station record, and it may contain production-stream discontinuities that have not been checked.
- **Candidate findings only.** Rainfall (fragile, possible 2006 step) and sunlight (shape unresolved) should be read as candidates. Several detected trends are marginal (Kerala rainfall p 0.0418, Gujarat day temperature p 0.0248).
- **Multiple testing** is shown (a count of tests) but not corrected.
- **Not checked:** June to September 2021 for rainfall and day temperature, level shifts, global-mean temperature, and one unexplained coincidence (Rajasthan air temperature and Maharashtra day temperature have the same 95% range to 3 figures; probably chance, not resolved).

### Content
- **No sourced explanations.** Every domain axis is marked UNVERIFIED. The tool reports trends and abstains on causes; it does not teach why a pond turns green or why apples are sweet.
- **Regions do not match the questions.** None of the four regions is an apple or cherry-blossom area. The apple and cherry answers abstain and say they cannot tell whether your trees are in the region, but they still print that region's trends. This is a mild way of saying the data does not describe your orchard. (DESIGN, option chosen by the owner; a new region would fix it.)
- **Only four regions and five variables.** No humidity, wind, haze, soil or cloud data. Questions about them are not recognized; a causal follow-up about them can show an unrelated axis. (CODE; known gap.)
- **Fixed range.** Always 1980 to 2025. A year-vs-record answer says 2025 is the latest full year; the current year is not in the data.

### Chat behavior
- **Keyword router.** One keyword alone falls to the guided form by design; unusual wording does too. Generic words ("heat", "rain", "sun") can mis-route mixed questions; only the score margin protects against it.
- **Follow-ups only after some answers.** After pond, citrus, heat, monsoon, sunshine, apple and cherry answers, follow-ups work. After year-vs-record, region comparison, season and day-night answers they fall to the guided form. (CODE; no test.)
- **Possessives.** "Kerala's" is not recognized as a region name.
- **"Why is the temperature so high?"** is not challenged as a premise.
- **Module quirks.** The year module has "than last year" in its trigger though it compares with the mean of earlier years; "may" the month blocks the verb "may". The region-compare trigger word "most" is broad. "Monsoon season" goes to the season module, not the monsoon domain.
- **Plain text prints a slope twice** in some pond answers (cosmetic).
- **Three backend calls per question** (one per level), which matters on a small free server.

### Operations
- **Cold start.** The free Render instance sleeps; the first request can take 50+ seconds and the proxy may time out.
- **Pushes redeploy** both services; the chat can fail for a minute or two.
- **Vercel plan** end date is unknown.
- **Region boxes** for Rajasthan, Kerala and Gujarat are rough and unchecked on a map.
- **`main` has a pull-request rule** that the owner's account bypasses; other contributors may not be able to push directly. (INFERENCE.)
- **Adding data** (a new variable or region) needs a cold fetch (about 70 to 80 s per variable per region), an Earthdata login, and `git add -f` for the CSVs.

### Testing gaps
See "Not tested or not confirmed" in `TEST_RESULTS.md`. The largest are the guard on real limited or masked axes, live latency, and several browser cards.

## Summary

The core idea works and is demonstrable: honest verdicts, an explanation of why no trend was found, and abstention when the data cannot answer. It is a proof of concept. The main risks are placeholder thresholds, unsourced domain content, and a narrow set of regions and variables.
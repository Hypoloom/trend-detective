# Test results

Recorded 2026-11-15 at commit `f40e622`.

## Totals

| runner | result | when seen |
|---|---|---|
| pytest (repo root) | **250 passed, 1 warning, 7777 subtests passed** in about 9 s | at `f40e622` |
| unittest (from `backend/`) | **120 tests, OK** | at `953d85e`; `f40e622` changed only `API.md`, but unittest was not re-run on it |
| `npm run build` | built successfully | at `953d85e` |

No failing test has been seen at these commits. The two runners collect different files and count subtests differently, so 120 and 250 are not comparable.

## Automated tests by file (pytest inventory: 250 collected, 250 passed)

Result for every test below: **pass**. "Reject" cases pass when the guard or router correctly refuses something.

| file | tests | what it checks |
|---|---|---|
| `test_api_smoke.py` | 28 | health and datasets shape; 400 JSON errors for unknown dataset, region; `/api/ask` validation order; UI shape for all 5 datasets; `needed_high` null handling; pond answer at 3 levels; oranges route |
| `test_app_cache.py` | 3 | clean 404 for missing cache; datasets not ready; series 404 |
| `test_apple_cherry.py` | 4 | apple and cherry questions route correctly; one keyword alone falls back; 2 domains x 4 regions x 3 levels abstain with no guard rejection; follow-up after apple |
| `test_ask_endpoint.py` | 8 | joke gives fallback; unknown region, unknown `user_inputs` key, empty body, bad level give 400; pond and orange questions route and abstain |
| `test_diurnal.py` | 3 | detection, guard at 3 levels, missing data |
| `test_diurnal_endpoint.py` | 2 | day-night question routes; other routes unchanged |
| `test_followup.py` | 10 | routes table; follow-up intents; region and none; axis switching; 3 domains x 4 regions x 3 levels; follow-ups with context; forecast note; no context falls back |
| `test_guard_extra.py` | 30 | number words, direction words vs slope sign, negation, association wording, fragile wording, per-axis rules, min-detectable never treated as a trend |
| `test_llm_off.py` | 3 | full path with LLM off; no network imports; non-abstained mocks |
| `test_partial_data.py` | 3 | all missing gives 404; one uncached axis marked; route survives one missing file |
| `test_phrase.py` | 16 | guard accepts good text and rejects causal words, invented numbers, missing or softened abstention, "no trend exists"; adapter error and bad LLM text fall back to the template |
| `test_real_shapes.py` | 38 | real Maharashtra pond result through templates and guard; risk-window text; long decimals; three-figure slopes; meaningful-size sentences; router labels; unbounded years-needed |
| `test_region_compare.py` | 3 | detection, guard at 3 levels, missing data |
| `test_region_compare_endpoint.py` | 2 | comparison question routes; others unchanged |
| `test_router.py` | 8 | fallback form; LLM cannot invent a domain; LLM exception falls back; rules-confident skips LLM; question table; ties fall back |
| `test_router_pond_keywords.py` | 7 | "green" and "murky" keywords; "green" alone too weak; "green oranges" stays citrus; pond plus orange stays ambiguous |
| `test_season.py` | 3 | detection, guard at 3 levels, missing data |
| `test_season_endpoint.py` | 2 | season question routes; others unchanged |
| `test_task_a.py` | 6 | no-trend wording rules; limited-axis wording and marker |
| `test_template_guard.py` | 64 | 15 result shapes x 3 levels pass their own guard; association and extreme-years wording; failed-guard note; `needed_high` None never leaks into text |
| `test_why_no_trend.py` | 2 | Maharashtra air and day temperature explanation; structured `why` field |
| `test_year_rank.py` | 3 | detection, guard at 3 levels, missing data |
| `test_year_rank_endpoint.py` | 2 | year question routes; other routes unchanged |
| **total** | **250** | |

## Checked by hand (real data; read by a person, not asserted)

| check | result | where |
|---|---|---|
| Kerala 2025 air temperature vs the record | 6th highest of 46 years, 0.415 K above the earlier-years mean | local and live, matched |
| Region comparison, air temperature | Kerala highest (0.0161 K/yr); named as standing out only against Gujarat and Rajasthan, not Maharashtra | local |
| Region comparison, rainfall | Gujarat highest, but all four ranges overlap so no winner is named | local |
| Maharashtra monsoon rainfall (season) | trend detected, slope 0.0402 mm/day/yr, marked fragile | local |
| Maharashtra pre-monsoon air temperature | no trend found, slope 0.00531 K/yr | local |
| Maharashtra day-night gap | trend detected, gap narrowing (-0.0176 K/yr), below the 0.02 meaningful size | local |
| Kerala day-night gap | no trend found | local |
| Pond answer, live vs local | identical | live |
| Live follow-ups (causal lead, "What about rainfall in Kerala?", forecast note) | expected text | live |
| Live `/api/datasets` | all five datasets ready | live |
| Apple and cherry answers (Kerala) | abstain, list unknowns including "whether your trees are in this region", no guard rejection | local |
| Apple and cherry live check | reported working by the owner (output not seen by Claude) | live |
| Browser cards for season, region comparison, pond and follow-up | matched expected text | local browser |
| "Wrapped" words such as "treesare" | confirmed terminal wrapping only (`False False`) | local |

## Verified engine behavior (synthetic validation, 200 seeds per case)

| case | result |
|---|---|
| True trend 0.02/yr detected | 12% (10 years), 49% (20), 94% (30), 100% (45) |
| No trend (null) false positives | 3 to 8% |
| Opposite regional trends flagged "masked" | 2% (10 years), 70% (20), 91% (30), 93% (45) |
| Null false-positive rate of Mann-Kendall on annual means | 8% measured, 5% expected |

## Not tested or not confirmed

- Browser cards for the day-night, year-vs-record, and apple/cherry answers, and their topic labels on the live site.
- Live latency (each chat question makes 3 backend calls) and memory on the 512 MB Render instance.
- Live checks of season, region comparison and day-night on Render.
- The wording guard on real `data_limited`, `masked` and `inconclusive` axes, and on any LLM text. No LLM is wired.
- The `why` object for `masked`, `data_limited` and `inconclusive` on real data.
- `/api/answer` unknown-domain 400, a non-numeric `slope`, and a cache CSV that exists but does not cover 1980-2025.
- Rajasthan, Kerala and Gujarat region boxes on a map.
- Assertions on trend numbers for the three non-Maharashtra regions (they are exercised by prints only).
- Follow-ups after year, region, season and day-night answers: these fall to the guided form (known gap, no test).
- Global-mean air temperature, and the June to September 2021 reprocessing check for rainfall and day temperature.
- The Vercel plan expiry and the Explorer "Explain this chart" path.
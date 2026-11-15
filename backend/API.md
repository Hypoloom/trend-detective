# Hypoloom backend API

Written against commit `953d85e`. Labels: **IN CODE** = read in `app.py` when this was written. **TESTED** = covered by a passing test (unittest 120 OK, pytest 250 passed). **NOT RUN** = described from code, never run. Anything unlabelled comes from the project record and was not re-checked. No body here was compared with a live response.

## How to run

    cd backend
    pip install -r requirements.txt
    python app.py

- Local: `http://127.0.0.1:8000`, `debug=False` (IN CODE).
- Deployed: Render runs `gunicorn app:app`; Vercel rewrites `/api/*` to it. The first request after the free instance sleeps can take 50+ seconds.
- Tests: from `backend`, `python -m unittest discover -s tests -t .`; from the repo root, `python -m pytest -q`. Run both.

## Data comes from cache files

The server reads monthly series from `backend/stream_cache/<name>_<west>_<south>_<east>_<north>.csv` (Maharashtra air temperature: `t2m_72_16_80_21.csv`). 20 files are tracked in git (4 regions x 5 variables). `backend/.gitignore` ignores `stream_cache*/`, so any new CSV needs `git add -f`.

- **The server never fetches from NASA while serving** (IN CODE). It checks that the CSV exists (box numbers in the file name are parsed and compared to the region box).
- The check is existence only, not coverage of 1980-2025 (NOT RUN). The analysis range is fixed at 1980-2025 (IN CODE).
- An unexpected exception becomes 500 `{"error": "server error: <ExceptionName>"}` (IN CODE). HTTP errors Flask raises itself (such as 405) keep Flask's own response.

## Common rules

- Every response has `Access-Control-Allow-Origin: *` (IN CODE). NaN and infinity become `null`.
- Errors from `app.py` are `{"error": "<message>"}` with status 400, 404 or 500.
- Datasets: `T2M`, `PRECIP`, `SUNLIGHT`, `T2M_MIN`, `T2M_MAX` (default `T2M`).
- Regions: `maharashtra` (default), `rajasthan`, `kerala`, `gujarat`. The last three boxes are rough proposals, not checked on a map.
- Data are MERRA-2 monthly reanalysis (a model product, not a direct measurement), 1980-2025.

## Endpoints

### GET /api/health
Returns `{"ok": true}`.

### GET /api/datasets
Returns `{"datasets": [{id, label, units, default_slope, ready, ready_regions}], "regions": [{id, label, box}]}`.
- `ready_regions` is `{region id: true/false}` (CSV exists). `ready` is true only when all four are true.
- `default_slope` is `null` for every dataset today. `box` is `[west, south, east, north]`.

### GET /api/series?dataset=&region=
Returns `{dataset, region, units, dates: ["YYYY-MM"], values: [...]}`. 400 for an unknown dataset or region; 404 if the CSV is missing.

### GET /api/analysis?dataset=&region=&slope=
Returns `contract.run_analysis` output. `slope` is an optional "meaningful" trend per year.
- Left out: `meaningful.resolve` picks the size and rule (IN CODE).
- Given: no rule is attached; what that does to the `meaningful` block is NOT RUN.
- Not a number: ignored as if absent (IN CODE via `get(type=float)`; NOT RUN).
- 400 unknown dataset or region; 404 missing CSV; 500 for an import or call-shape error, or the generic 500.

| Field | Contents |
|---|---|
| `verdict` | `code`, `label`, `summary` |
| `years` | `have`, `needed_low`, `needed_mid`, `needed_high`, `needed_for_meaningful`, `meaningful_slope` |
| `trend` | `slope_per_year` (Theil-Sen on annual means), `slope_ci`, `ols_slope_per_year`, `p_value` (Mann-Kendall), `p_value_method`, `min_detectable_slope`, `units`, `p_value_without_extreme_years`, `fragile` |
| `noise` | `sigma`, `lag1_autocorr` |
| `chart` | `points` [{year, value}], `trend_line` (2 points, mid-year values: year, trend, low, high), `seasonality_removed` |
| `provenance` | `dataset`, `variable`, `region`, `start`, `end` (strings `YYYY-MM`), `simulated` |
| `meaningful` | `rule`, `basis`, `value`, `sensitivity` (list of {factor, value, verdict_code, needed_years}; empty when `detected`) |
| `why` | see below; `null` when `detected` |
| other | `caveats` (list of text), `tested_count` |

Verdict codes: `detected`, `data_limited`, `no_trend`, `inconclusive`, `masked`. Chart values are annual means of the seasonality-removed series (anomalies). The band is uncertainty around the trend line, not around points.

**`fragile`** is true when the verdict is `detected` but the Mann-Kendall p-value is 0.05 or more after dropping the 3 years furthest from the median annual value. The verdict code does not change. The dropped years are not returned.

**`verdict.summary` for `no_trend`** says no trend was found over N years and that this is not proof nothing is happening; gives the estimated change with its 95% range; says whether that range is smaller than the meaningful size or reaches it; gives the smallest trend the record could probably detect; and, if halving the meaningful size would make the verdict `data_limited`, says so. The summary rounds years; `years.have` and `why.years_have` stay fractional.

**The `why` object** (TESTED for Maharashtra air temperature; NOT RUN on real `masked`, `data_limited` or `inconclusive` data):

| Field | Contents |
|---|---|
| `class` | `no_trend_below_meaningful`, `no_trend_reaches_meaningful`, `data_limited`, `masked`, `inconclusive`, or plain `no_trend` |
| `years_have` | years of data used |
| `years_needed_for_meaningful` | years needed, or `null` |
| `meaningful_value` | meaningful size per year. A project choice, not a standard |
| `min_detectable_slope` | smallest trend the record could probably detect |
| `slope_ci` | `[low, high]`, or `null` |
| `threshold_sensitive` | true if halving or doubling the size changes the verdict; `null` if not computed |

### GET /api/ui/analysis?dataset=&region=
Same parameters. Calls `/api/analysis`; if that is not 200, its body and status are returned. Otherwise it returns `regionId`, `variableId`, `title`, `subtitle`, `verdict` (`significant`, `not_enough_data`, `not_significant`), `verdict_code`, `slopePerYear`, `pValue`, `ci95`, `yearsUsed`, `dataset`, `series` ([{year (integer), value, trend, low, high}]), `summary` ({plain, detailed, pro}), `gap`, `followUps` (always `[]`), `simulated`, `caption`, `contract` (the whole analysis), `fragile`, `fragileNote`.
- Mapping: `detected` -> `significant`; `data_limited` -> `not_enough_data`; `no_trend`, `inconclusive`, `masked` -> `not_significant`.
- `gap` is `null` when `detected`; else `{reason, status, yearsHave, yearsNeed, tip}`. `fragileNote` is `null` unless `fragile`.

### GET /api/answer?region=&domain=
`domain` defaults to `pond`, `region` to `maharashtra`. Returns `answer.build(...)` output (see `result` under `/api/ask`); `result.region` reads like `Maharashtra box (72, 16, 80, 21)`.
- 400 for an unknown region or domain (IN CODE; the domain 400 is NOT RUN).
- 404 only if **all** the domain's NASA variables lack a CSV for the region (IN CODE). If only some are missing, those axes come back as `data_unavailable`.
### POST or GET /api/ask
The chat endpoint. A JSON body wins over the query string for each field.

| Field | Rules |
|---|---|
| `question` | required; empty gives 400 `missing 'question'` |
| `region` | default `maharashtra`; unknown gives 400. **A region named in the question text overrides it.** Possessives such as "Kerala's" are not recognized |
| `level` | `plain` (default), `detailed`, `pro`; else 400 |
| `user_inputs` | object (default `{}`), JSON body only. Keys must be the routed domain's `ask_user` axis names, else 400 `unknown user_inputs` |
| `context` | optional object `{domain, region}` from the previous answer, used only for follow-ups. A non-object gives 400. An unknown `context.region` becomes `null` |

`ask_user` axes today: `pond` -> `shade`, `pond_size`; `citrus` -> `region`. Other domains have none.

#### How a question is handled (IN CODE)
1. 400 checks: question, region, level, `user_inputs` type, `context` type.
2. A forecast note is computed (words like "next year", "forecast", "predict").
3. Four answer modules are tried **in this order**: `yearrank`, `diurnal`, `season`, `regioncompare`. Each returns an answer or nothing. Nothing means no match, missing cached data, or its own text failing the wording guard; the request then falls through silently to the router.
4. The router runs. A router match wins over follow-up rules.
5. Only if the router falls back **and** `context` yields a follow-up plan, a follow-up answer is returned.
6. Otherwise the guided form is returned (fallback).
7. On a router match: `user_inputs` keys are checked (400), then the cache (404 only if all the domain's NASA variables are missing), then `answer.build`, then the template phrasing. The forecast note is prepended.

#### Answer response (200, `fallback: false`)
Router answers: `{fallback, domain, confidence, route_source, level, text, used_llm, phrase_note, abstained, result}`. `text` comes from fixed templates (LLM off; `used_llm` is `false`). `route_source` values:

| Value | When |
|---|---|
| `rules` | the router matched keywords (`confidence` 0.6 to under 1) |
| `yearrank` | "Was this year hotter/wetter/sunnier than usual?" (`domain: year_vs_record`) |
| `diurnal` | "Are days heating faster than nights?" (`domain: diurnal`) |
| `season` | named season months, e.g. monsoon months or pre-monsoon (`domain: season`) |
| `regioncompare` | "Which region is warming fastest?" (`domain: region_compare`) |
| `followup` | a follow-up (response also has `followup: true` and `intent`) |

The four module answers have `confidence: 1.0`. `phrase_note` can be "LLM off", a note that the guard rejected LLM text, or an adapter error (the full set is NOT RUN).

**Router domains:** `pond`, `citrus`, `heat`, `monsoon`, `sunshine`, `apple`, `cherry_blossom`. A single keyword hit is too weak and falls back to the form; two single-word hits, or one phrase hit, route. `apple` and `cherry_blossom` abstain on every request and still list the region's trends, which do not describe an orchard or tree (the four regions were not chosen for them). All domain content is `evidence_status: UNVERIFIED`.

**`result` from `answer.build`** (router answers and follow-ups): `domain, region` (label), `axes`, `abstained`, `abstain_reason`, `risk_window`, `tested_count`, `llm_allowed_phrases`, `caveats`.
- Axis row: `name, label, source` (`nasa_data`, `ask_user`, `not_knowable`), `critical`, `status` (`analyzed`, `provided`, `needs_user`, `not_knowable`, `data_unavailable`), `result`, plus `prompt` when `needs_user`. `result` is a full analysis for `analyzed`, `{"value": ...}` for `provided`, else `null`.
- `abstained` is true when a critical axis is `needs_user`, `not_knowable` or `data_unavailable`; then `abstain_reason` is text, else `null`.
- `risk_window` is `null` unless abstained and computable (pond only today). It holds `months`, `month_names`, `definition`, `recent_vs_earlier` (`null` or `{recent_years, earlier_years, difference, direction, units}`), `caveat`. It is descriptive only.

**Module answers.** `year_vs_record` and `region_compare` return `result.axes = []` and `result.risk_window = null` (IN CODE). `season` and `diurnal` return the module's own `result` with one analyzed axis (axes shape from the module, not re-read here). `year_vs_record` result keys (project record): `region, variable, year, first_year, years_in_record, earlier_years, top_rank, rank, value, earlier_mean, earlier_sd, gap, current_year, units, tested_count, caveats`. These answers rank or compare; they do not claim a trend or a forecast.

**Follow-ups** (`followup: true`): `{fallback: false, followup: true, intent, domain, confidence: 1.0, route_source: "followup", level, text, used_llm, phrase_note, abstained, result}`. Intents: `why_no_trend`, `causal`, `how_sure`, `variable`, `region`. `result` holds one axis when the question names a variable. They work only when `context.domain` is one of `pond, citrus, heat, monsoon, sunshine, apple, cherry_blossom`. After a `year_vs_record`, `region_compare`, `season` or `diurnal` answer, a follow-up falls to the guided form.

**Wording rules in `text`** (TESTED): the guard `phrase.check_text` checks every number against the result, bans causal words and "proof" wording in the writer's own text, requires abstention wording when abstained or limited, and requires "co-occurs with" when a trend is reported. Trends are never explained as causes.

#### Fallback (200, `fallback: true`)
`{fallback, reason, form, form_text, used_llm}`. No `domain`, `text` or `result`. `reason` is "no keyword matched", "ambiguous between domains" or "match too weak". `form` has `type: "guided_form"`, `message`, `original_question`, `step1_pick_topic` (`field: "domain"`, `options` [{id, label, examples}], last option `id: "none"`), `step2_followups`. `form_text` is the same as plain text.

## Fields that can be null

| Field | Where | When null |
|---|---|---|
| `why` | `contract` and each analyzed axis result | when `detected` |
| `why.threshold_sensitive`, `why.slope_ci` | inside `why` | not computed / range not finite |
| `years.needed_high` | `contract.years` | `null` for Maharashtra air temperature and day temperature; nullable everywhere |
| `years.needed_for_meaningful` | same | handled by `ui_adapter`; no null example seen |
| `trend.p_value_without_extreme_years` | `contract.trend` | fewer than 10 annual values |
| `fragileNote`, `gap` | `/api/ui/analysis` | see above |
| `abstain_reason`, `risk_window` | `/api/ask` -> `result` | not abstained (`risk_window` also when not computable) |
| `slopePerYear`, `pValue`, `ci95`, `yearsUsed` | `/api/ui/analysis` | contract lacks the value |

## Method caveats (from the engine; project record)
- Slope is Theil-Sen on annual means; the p-value is Mann-Kendall on annual means (ignores autocorrelation; the measured false-positive rate on null data was 8% against 5% expected).
- "Years needed" follows Weatherhead et al. with an AR(1) noise assumption; it carries roughly 20 to 60% uncertainty, clips lag-1 autocorrelation at 0.9, and does not model level shifts.
- Season subsets treat non-adjacent months as adjacent in the noise estimate, so years-needed there is approximate.
- The meaningful sizes in `meaningful.py` (0.02 K/yr; 5% of the mean per decade for rain; 2% for sunlight) are project placeholders, not standards. Verdicts depend on them.
- "No trend found" is not proof of no trend. A past trend is not a forecast. All regions come from one reanalysis, so they are not independent checks.

## UNVERIFIED summary
- Bodies for `/api/series`, `/api/analysis`, `/api/answer` are described from code, not live responses.
- The `/api/answer` unknown-domain 400, a non-numeric `slope`, `slope` effects on `meaningful`, and a CSV that exists but does not cover 1980-2025.
- The full set of `phrase_note` values, and the exact `result` shape of `season` and `diurnal`.
- The `why` object for `masked`, `data_limited` and `inconclusive` on real data.
- Region boxes for Rajasthan, Kerala and Gujarat (not checked on a map).
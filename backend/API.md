# Hypoloom backend API

Written against commit `78efe11`. Started from Ankit's version (written from reading `app.py`,
`ui_adapter.py`, `answer.py`, `stream.py`, `fallback_form.py`, `tests/real_pond.json` and the tests)
and updated by the owner for the later commits.
Labels: **VERIFIED** = run or tested and seen passing; everything else is described from code and
marked UNVERIFIED where it matters. No endpoint body here was checked against a live response
except where it says so.

## How to run

```
cd backend
pip install -r requirements.txt
python app.py
```

- The server listens on `http://127.0.0.1:8000` (`debug=False`).
- `answer.load_domain` now finds `domains.json` next to `answer.py` when it is not in the current
  folder, so the server and pytest work from any folder (VERIFIED, `test_app_cache.py` under pytest).
- `requirements.txt`: numpy, pandas, scipy, earthaccess, xarray, h5netcdf, pydap, flask.
- Tests: from `backend`, `python -m unittest discover -s tests -t .`; from the repo root, `python -m pytest -q`.
  Add `-rs` to pytest to see why a test was skipped.

## Data comes from cache files

The server reads monthly series from `backend/stream_cache/<name>_<west>_<south>_<east>_<north>.csv`
(for Maharashtra: `t2m_72_16_80_21.csv`). The CSVs are not in git (`stream_cache` is untracked);
the owner supplies them as a zip. A full set is 20 files (4 regions x 5 variables).

- **The server does not fetch from NASA.** Before any series is loaded, `app.py` checks that the CSV for
  that region and variable exists (it matches the four box numbers in the file name). If it is missing,
  the endpoint returns 404 `{"error": "cached data missing for <Region>: <keys>. ..."}` (VERIFIED,
  `tests/test_app_cache.py`).
- The check looks only at whether the file exists. It does not check that the file covers 1980-01 to
  2025-12. A file that exists but is short may still make `stream.get_series` try NASA (UNVERIFIED, not run).
- Any other unexpected exception becomes 500 `{"error": "server error: <ExceptionName>"}` instead of an
  HTML page. Errors Flask raises itself (for example 405 for a wrong method) keep Flask's own response.

## Common rules

- Every response has `Access-Control-Allow-Origin: *`.
- NaN and infinity become `null`.
- Errors from `app.py` are `{"error": "<message>"}` with status 400, 404 or 500.
- Datasets: `T2M`, `PRECIP`, `SUNLIGHT`, `T2M_MIN`, `T2M_MAX` (default `T2M`).
- Regions: `maharashtra` (default), `rajasthan`, `kerala`, `gujarat`. The last three boxes are rough proposals.
- Data are MERRA-2 monthly reanalysis (a model product, not a satellite measurement), 1980-2025.

## Endpoints

### GET /api/health
Returns `{"ok": true}`.

### GET /api/datasets
```
{"datasets": [{"id", "label", "units", "default_slope", "ready", "ready_regions"}],
 "regions":  [{"id", "label", "box": [west, south, east, north]}]}
```
- `ready_regions` is an object `{region id: true/false}`: whether the cached CSV exists for each region.
- `ready` is true only when `ready_regions` is true for all four regions.
- `default_slope` is `null` for every dataset today.
- With all 20 CSVs present, all five datasets are `ready: true` (VERIFIED on the owner's machine).
- Existence only; coverage is not checked.

### GET /api/series?dataset=&region=
Returns `{"dataset", "region", "units", "dates": ["YYYY-MM"], "values": [...]}`.
Status 400 for an unknown dataset or region. Status 404 if the cached CSV is missing.

### GET /api/analysis?dataset=&region=&slope=
Returns the JSON from `contract.run_analysis`. `slope` is an optional number: the "meaningful" trend per year.
If it is left out, `meaningful.resolve` chooses one.
Status 400 for an unknown dataset or region, 404 for a missing file, 500 for an `ImportError` or `TypeError`
inside the call (or the generic 500 above for anything else).

Fields:

| Field | Contents |
|---|---|
| `verdict` | `code`, `label`, `summary` |
| `years` | `have`, `needed_low`, `needed_mid`, `needed_high`, `needed_for_meaningful`, `meaningful_slope` |
| `trend` | `slope_per_year`, `slope_ci` [low, high], `ols_slope_per_year`, `p_value`, `p_value_method`, `min_detectable_slope`, `units`, `p_value_without_extreme_years`, `fragile` |
| `noise` | `sigma`, `lag1_autocorr` |
| `chart` | `points` [{`year`, `value`}], `trend_line` (2 points: `year`, `trend`, `low`, `high`), `seasonality_removed` |
| `provenance` | `dataset`, `variable`, `region`, `start`, `end`, `simulated` |
| `meaningful` | `rule`, `basis`, `value`, `sensitivity` (a list; empty when the verdict is `detected`) |
| `why` | see below; `null` when the verdict is `detected` |
| other | `caveats` (list of text), `tested_count` |

Verdict codes: `detected`, `data_limited`, `no_trend`, `inconclusive`, `masked`.
When `slope` is given, `meaningful_rule` is `None`; what that does to the `meaningful` block is UNVERIFIED.

**`verdict.summary` for `no_trend`** (VERIFIED for Maharashtra air and day temperature): it says no trend was
found over N years and that this is not proof nothing is happening; gives the estimated change with its 95% range;
says whether that whole range is smaller than the size chosen as meaningful (so a change of that size is unlikely),
or reaches it (so it cannot be ruled out); gives the smallest trend the record could probably detect; and, when
halving the meaningful size would turn the verdict into `data_limited`, adds a sentence saying the record would be
too short to tell at half that size. `N` can be a fraction such as 45.9.

**The `why` object** (VERIFIED for Maharashtra `t2m`: class `no_trend_below_meaningful`, `threshold_sensitive` true,
`meaningful_value` 0.02; `null` for Maharashtra sunlight, which is `detected`). Every value is copied from the
engine's own numbers.

| Field | Contents |
|---|---|
| `class` | `no_trend_below_meaningful` (slope range lies entirely below the meaningful size), `no_trend_reaches_meaningful` (the range reaches it), `data_limited`, `masked`, `inconclusive` |
| `years_have` | years of data used |
| `years_needed_for_meaningful` | years needed to detect the meaningful size, or `null` |
| `meaningful_value` | the meaningful size, units per year. A project choice, not a standard |
| `min_detectable_slope` | smallest trend the record could probably detect |
| `slope_ci` | `[low, high]` 95% range of the slope, or `null` |
| `threshold_sensitive` | true if halving or doubling the meaningful size changes the verdict; `null` if no sensitivity was computed |

For `no_trend` the class is only the two `no_trend_*` values when a meaningful size and a finite range exist;
otherwise it is `no_trend`. The same `why` appears inside `/api/ask` -> `result.axes[].result` for analyzed axes.

### GET /api/ui/analysis?dataset=&region=
Takes the same query parameters. It calls `/api/analysis` internally. If that is not 200, the same body and status are returned.
Otherwise the contract is reshaped:

| Field | Contents |
|---|---|
| `regionId`, `variableId` | the region and dataset ids from the request |
| `title`, `subtitle` | text built from `provenance` |
| `verdict` | `significant`, `not_enough_data` or `not_significant` |
| `verdict_code` | the contract code |
| `slopePerYear`, `pValue`, `ci95` | from `trend` (`null` if absent) |
| `yearsUsed` | `years.have`, rounded, or `null` |
| `dataset` | `provenance.dataset` |
| `series` | list of `{year (integer), value, trend, low, high}`; `1980.5` becomes `1980`. `low` and `high` are the uncertainty band around the trend line, not around each point |
| `summary` | `{plain, detailed, pro}` text. `plain` is `verdict.summary` |
| `gap` | `null` when `verdict_code` is `detected`; otherwise `{reason, status, yearsHave, yearsNeed, tip}` |
| `followUps` | always `[]` |
| `simulated` | boolean |
| `caption` | text about anomalies |
| `contract` | the whole `/api/analysis` JSON (including `why`) |
| `fragile` | boolean |
| `fragileNote` | text, or `null` |

Mapping: `detected` gives `significant`; `data_limited` gives `not_enough_data`; `no_trend`, `inconclusive`, `masked` give `not_significant`.
`yearsNeed` is `needed_for_meaningful`, else `needed_mid`, else `needed_low`, else `have`.
For `no_trend`, `gap.tip` says the meaningful size is a project choice and changing it can change the verdict.

### GET /api/answer?region=&domain=
`domain` defaults to `pond`. Returns `answer.build(...)` output (fields under `/api/ask` -> `result`).
Status 400 for an unknown region or an unknown domain (the unknown-domain 400 is UNVERIFIED, not run).
Status 404 if a NASA variable the domain needs has no cached CSV for the region.
Here `region` in the output reads like `Maharashtra box (72, 16, 80, 21)`.

### POST or GET /api/ask
Request fields (JSON body wins over query string for each field):

| Field | Rules |
|---|---|
| `question` | required text; empty gives 400 `missing 'question'` |
| `region` | default `maharashtra`; unknown gives 400 |
| `level` | `plain` (default), `detailed` or `pro`; anything else gives 400 |
| `user_inputs` | object, default `{}`; send it in the JSON body (a query-string value is text and gives 400). Keys must be the routed domain's `ask_user` axis names, otherwise 400 `unknown user_inputs` |

Order of checks: question, region, level and the type of `user_inputs` first, so a bad region or level gives 400 even
for a question that would fall back. Then the router runs. A fallback needs no cached data. For a routed domain,
the `user_inputs` key names are checked, then the cache: a missing CSV for any NASA variable the domain needs gives
404 `cached data missing ...` (VERIFIED, `tests/test_app_cache.py`).

**Answer (status 200, `fallback: false`):**
`{fallback, domain, confidence, route_source, level, text, used_llm, phrase_note, abstained, result}`.
`text` is the phrased answer at the chosen level, from fixed templates (no LLM today). `result` is the
`answer.build` output:
`domain, region` (label only), `axes`, `abstained`, `abstain_reason`, `risk_window`, `tested_count`, `llm_allowed_phrases`, `caveats`.

An axis row: `name, label, source` (`nasa_data`, `ask_user` or other), `critical`, `status`
(`analyzed`, `provided`, `needs_user`, `not_knowable`, `data_unavailable`), `result`, plus `prompt` when `status` is `needs_user`.
`result` is a full analysis for `analyzed`, `{"value": ...}` for `provided`, and `null` otherwise.
`abstained` is true when a critical axis is `needs_user`, `not_knowable` or `data_unavailable`; then `abstain_reason` is text, otherwise `null`.
`risk_window` is `null` unless abstained and computable; it holds `months`, `month_names`, `definition`, `recent_vs_earlier`, `caveat`.
`recent_vs_earlier` is `null` or `{recent_years, earlier_years, difference, direction ("higher"/"lower"), units}`.

**Wording rules in `text`** (VERIFIED on the real pond answer at all three levels, and by `tests/test_task_a.py`
on synthetic limited axes):
- A `no_trend` axis line carries the engine's range-versus-meaningful-size sentences (at `plain`, also the 95% range sentence).
- A `data_limited`, `masked` or `inconclusive` axis line ends with "Evidence is limited: ...".
- The guard (`phrase.check_text`) flags: "no change"-style wording for a `no_trend` axis unless a hedge such as
  "not proof" appears; "found a trend"-style wording for a limited axis; and a text with a limited axis but no
  limited-evidence marker.
- If the template ever fails the guard, it is still returned and the reasons go into `phrase_note` after
  `template failed guard:`.
What else `route_source` and `phrase_note` can contain is UNVERIFIED. `used_llm` is `false` (LLM off).

**Fallback (status 200, `fallback: true`):**
`{fallback, reason, form, form_text, used_llm}`. There is no `domain`, `text` or `result`. The client should show the form, or just `form_text`.

- `form_text` is plain text: the message, then numbered topics, each with `e.g.` examples.
- `form` has `type: "guided_form"`, `message`, `original_question`,
  `step1_pick_topic` (`field: "domain"`, `options` [{`id`, `label`, `examples`}], the last option has `id: "none"`),
  and `step2_followups` (domain id -> list of {`name`, `prompt`, `why_it_matters`}).

## Fields that can be null

| Field | Where | When null |
|---|---|---|
| `why` | `contract` and each analyzed axis result | `null` when the verdict is `detected` |
| `why.threshold_sensitive`, `why.slope_ci` | inside `why` | `null` when no sensitivity was computed / the range is not finite |
| `years.needed_high` | `contract.years` (also in `/api/ui/analysis` -> `contract`, and in `/api/ask` -> `result.axes[].result.years`) | `null` for Maharashtra air temperature and day temperature (`t2m_max`). Rainfall and sunlight have numbers. Treat it as nullable. |
| `years.needed_for_meaningful` | same place | `ui_adapter` is written to cope with `null`; no `null` example seen. |
| `trend.p_value_without_extreme_years` | `contract.trend` | `null` when the series has fewer than 10 annual values (rule given by the owner; matches `p_drop3` being `None` in the engine). |
| `fragileNote` | `/api/ui/analysis` | `null` unless `trend.fragile` is true, then a fixed sentence about extreme years. |
| `gap` | `/api/ui/analysis` | `null` when `verdict_code` is `detected`. |
| `abstain_reason`, `risk_window` | `/api/ask` -> `result` | `null` when not abstained (`risk_window` also when it cannot be computed). |
| `slopePerYear`, `pValue`, `ci95`, `yearsUsed` | `/api/ui/analysis` | `null` when the contract lacks the value. |

## UNVERIFIED summary

- Response bodies for `/api/series`, `/api/analysis`, `/api/answer` are described from code and `real_pond.json`, not from live responses.
- The unknown-domain 400 on `/api/answer`, an invalid `slope` text, and what happens when a CSV exists but does not cover 1980-2025.
- What `meaningful` holds when `?slope=` is given.
- The full set of values `route_source` and `phrase_note` can take.
- The `why` object for `masked`, `data_limited` and `inconclusive` results on real data (only `no_trend` and `detected` were checked on real data).
- Which regions' cached files are present on a given machine; only Maharashtra is exercised by the smoke tests.
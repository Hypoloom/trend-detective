# Hypoloom backend API

Written against commit `aea11ef`, from reading `app.py`, `ui_adapter.py`, `answer.py`,
`stream.py`, `fallback_form.py`, `tests/real_pond.json` and the existing tests.
Nothing in this file was run by the author. `contract.py`, `router.py`, `phrase.py` and
`meaningful.py` were not read for this file. Anything that depends on them is marked UNVERIFIED.

## How to run

```
cd backend
pip install -r requirements.txt
python app.py
```

- The server listens on `http://127.0.0.1:8000` (`debug=False`).
- Start it from the `backend` folder. `answer.load_domain` opens `domains.json` by a relative path.
- `requirements.txt`: numpy, pandas, scipy, earthaccess, xarray, h5netcdf, pydap, flask.
- Tests: from `backend`, `python -m unittest discover -s tests -t .`; from the repo root, `python -m pytest -q`.
  Add `-rs` to pytest to see why a test was skipped.

## Data comes from cache files

The server reads monthly series from `backend/stream_cache/<name>_<west>_<south>_<east>_<north>.csv`
(for Maharashtra: `t2m_72_16_80_21.csv`). If the CSV is missing, or does not cover 1980-01 to 2025-12,
`stream.get_series` tries to fetch from NASA (needs the network and an earthaccess login).
`app.py` catches only `FileNotFoundError`, so other failures there are not turned into a JSON error (UNVERIFIED, not run).

The CSVs are not in git (`stream_cache` is untracked); the owner supplies them as a zip.
Which files exist depends on the machine. `ready` in `/api/datasets` and the skip checks in `tests/test_api_smoke.py` show what is there.

## Common rules

- Every response has `Access-Control-Allow-Origin: *`.
- NaN and infinity become `null`.
- Errors from `app.py` are `{"error": "<message>"}` with status 400, 404 or 500.
- Datasets: `T2M`, `PRECIP`, `SUNLIGHT`, `T2M_MIN`, `T2M_MAX` (default `T2M`).
- Regions: `maharashtra` (default), `rajasthan`, `kerala`, `gujarat`.

## Endpoints

### GET /api/health
Returns `{"ok": true}`.

### GET /api/datasets
```
{"datasets": [{"id", "label", "units", "default_slope", "ready"}],
 "regions":  [{"id", "label", "box": [west, south, east, north]}]}
```
`default_slope` is `null` for every dataset today. `ready` is true when the Maharashtra CSV file exists.
It does not check coverage and says nothing about the other regions.

### GET /api/series?dataset=&region=
Returns `{"dataset", "region", "units", "dates": ["YYYY-MM"], "values": [...]}`.
Status 400 for an unknown dataset or region. Status 404 if `get_series` raises `FileNotFoundError`.

### GET /api/analysis?dataset=&region=&slope=
Returns the JSON from `contract.run_analysis`. `slope` is an optional number: the "meaningful" trend per year.
If it is left out, `meaningful.resolve` chooses one.
Status 400 for an unknown dataset or region, 404 for a missing file, 500 for an `ImportError` or `TypeError` inside the call.

Fields, as seen in `tests/real_pond.json` (the same function builds each axis there):

| Field | Contents |
|---|---|
| `verdict` | `code`, `label`, `summary` |
| `years` | `have`, `needed_low`, `needed_mid`, `needed_high`, `needed_for_meaningful`, `meaningful_slope` |
| `trend` | `slope_per_year`, `slope_ci` [low, high], `ols_slope_per_year`, `p_value`, `p_value_method`, `min_detectable_slope`, `units`, `p_value_without_extreme_years`, `fragile` |
| `noise` | `sigma`, `lag1_autocorr` |
| `chart` | `points` [{`year`, `value`}], `trend_line` (2 points: `year`, `trend`, `low`, `high`), `seasonality_removed` |
| `provenance` | `dataset`, `variable`, `region`, `start`, `end`, `simulated` |
| other | `caveats` (list of text), `tested_count`, `meaningful` (`rule`, `basis`, `value`, `sensitivity`) |

Verdict codes the adapter knows: `detected`, `data_limited`, `no_trend`, `inconclusive`, `masked`.
Only the first three appear in `real_pond.json`. When `slope` is given, `meaningful_rule` is `None`; what that does to the
`meaningful` block is UNVERIFIED.

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
| `series` | list of `{year (integer), value, trend, low, high}`; `1980.5` becomes `1980` |
| `summary` | `{plain, detailed, pro}` text |
| `gap` | `null` when `verdict_code` is `detected`; otherwise `{reason, status, yearsHave, yearsNeed, tip}` |
| `followUps` | always `[]` |
| `simulated` | boolean |
| `caption` | text about anomalies |
| `contract` | the whole `/api/analysis` JSON |
| `fragile` | boolean |
| `fragileNote` | text, or `null` |

Mapping: `detected` gives `significant`; `data_limited` gives `not_enough_data`; `no_trend`, `inconclusive`, `masked` give `not_significant`.
`yearsNeed` is `needed_for_meaningful`, else `needed_mid`, else `needed_low`, else `have`.

### GET /api/answer?region=&domain=
`domain` defaults to `pond`. Returns `answer.build(...)` output (fields under `/api/ask` -> `result`). Status 400 for an unknown region.
Here `region` in the output reads like `Maharashtra box (72, 16, 80, 21)`. An unknown `domain` raises `KeyError` in `load_domain`; what the
client sees is UNVERIFIED.

### POST or GET /api/ask
Request fields (JSON body wins over query string for each field):

| Field | Rules |
|---|---|
| `question` | required text; empty gives 400 `missing 'question'` |
| `region` | default `maharashtra`; unknown gives 400 |
| `level` | `plain` (default), `detailed` or `pro`; anything else gives 400 |
| `user_inputs` | object, default `{}`; send it in the JSON body (a query-string value is text and gives 400). Keys must be the routed domain's `ask_user` axis names, otherwise 400 `unknown user_inputs` |

Order of checks: question, region, level and the type of `user_inputs` are checked first, so a bad region or level gives 400 even for a
question that would fall back. Then the router runs. The key names in `user_inputs` are checked only after routing to a domain.

**Answer (status 200, `fallback: false`):**
`{fallback, domain, confidence, route_source, level, text, used_llm, phrase_note, abstained, result}`.
`text` is the phrased answer at the chosen level. `result` is the `answer.build` output:
`domain, region` (label only), `axes`, `abstained`, `abstain_reason`, `risk_window`, `tested_count`, `llm_allowed_phrases`, `caveats`.

An axis row: `name, label, source` (`nasa_data`, `ask_user` or other), `critical`, `status`
(`analyzed`, `provided`, `needs_user`, `not_knowable`, `data_unavailable`), `result`, plus `prompt` when `status` is `needs_user`.
`result` is a full analysis for `analyzed`, `{"value": ...}` for `provided`, and `null` otherwise.
`abstained` is true when a critical axis is `needs_user`, `not_knowable` or `data_unavailable`; then `abstain_reason` is text, otherwise `null`.
`risk_window` is `null` unless abstained and computable; it holds `months`, `month_names`, `definition`, `recent_vs_earlier`, `caveat`.
`recent_vs_earlier` is `null` or `{recent_years, earlier_years, difference, direction ("higher"/"lower"), units}`.
What `route_source` and `phrase_note` can contain is UNVERIFIED (`router.py` and `phrase.py` not read).
`used_llm` was `false` in all tests (LLM off).

**Fallback (status 200, `fallback: true`):**
`{fallback, reason, form, form_text, used_llm}`. There is no `domain`, `text` or `result`. The client should show the form, or just `form_text`.

- `form_text` is plain text: the message, then numbered topics, each with `e.g.` examples.
- `form` has `type: "guided_form"`, `message`, `original_question`,
  `step1_pick_topic` (`field: "domain"`, `options` [{`id`, `label`, `examples`}], the last option has `id: "none"`),
  and `step2_followups` (domain id -> list of {`name`, `prompt`, `why_it_matters`}).

## Fields that can be null

| Field | Where | When null |
|---|---|---|
| `years.needed_high` | `contract.years` (also in `/api/ui/analysis` -> `contract`, and in `/api/ask` -> `result.axes[].result.years`) | `null` for air temperature in `real_pond.json`; the owner says it is also `null` for `t2m_max`. Rainfall and sunlight have numbers there. Nothing in `app.py`, `ui_adapter.py`, `answer.py` or `phrase.py` reads it. Treat it as nullable. |
| `years.needed_for_meaningful` | same place | `ui_adapter` is written to cope with `null`; no `null` example seen in `real_pond.json`. |
| `trend.p_value_without_extreme_years` | `contract.trend` | `null` when the series has fewer than 10 annual values (rule given by the owner; `contract.py` was not read by the author). Numbers in all three axes of `real_pond.json`. `ui_adapter` does not read it. |
| `fragileNote` | `/api/ui/analysis` | `null` unless `trend.fragile` is true, then a fixed sentence about extreme years. |
| `gap` | `/api/ui/analysis` | `null` when `verdict_code` is `detected`. |
| `abstain_reason`, `risk_window` | `/api/ask` -> `result` | `null` when not abstained (`risk_window` also when it cannot be computed). |
| `slopePerYear`, `pValue`, `ci95`, `yearsUsed` | `/api/ui/analysis` | `null` when the contract lacks the value. |

## UNVERIFIED summary

- No endpoint was run by the author for this file.
- Behaviour of `router.py`, `phrase.py`, `contract.py`, `meaningful.py`.
- The `p_value_without_extreme_years` null rule (fewer than 10 annual values) comes from the owner, not from reading `contract.py`.
- Error responses for an unknown `domain`, an invalid `slope` text, and non-`FileNotFoundError` failures in `get_series`.
- Response bodies for `/api/series`, `/api/analysis`, `/api/answer` are described from code and `real_pond.json`, not from live responses.

# Hypoloom: Earth System Trend Detective

Working name. Built for the NASA Space Apps 2026 challenge "Be An Earth System Trend Detective".

Hypoloom lets people ask everyday questions about climate and weather records, finds trends in NASA MERRA-2 data, and tests whether those trends are statistically significant. Its main idea is honesty: when no trend can be found, it says **why** (a true null, too little data, or a method problem). When a question cannot be answered from data at all, it **abstains** instead of guessing.

## What it does

- **Chat** (robot panel): plain-language answers at three levels (Plain, Detailed, Pro), with a chart, the verdict, and the top caveats.
- **Explorer**: pick a variable and a region, see the trend with its uncertainty band, and read a "Why this result" box.
- **Verdicts** are rule-based and auditable: Detected, Data-limited, Masked by aggregation, No trend found (not proof of absence), Inconclusive.
- **Abstention**: for questions such as "Why is my pond turning green?" the tool lists what it cannot know (nutrient load, existing algae) and gives a risk window, not a number of days.
- **Answer types today**: pond, small oranges, apples and sweetness, cherry blossom timing, "is it getting hotter / wetter / sunnier", this year compared with the record, region comparison, season months (monsoon, pre-monsoon), day compared with night, and follow-up questions.
- **Wording guard**: every answer text is checked against the computed numbers. It blocks invented numbers, causal wording ("because", "caused by"), and overclaims.
- **No LLM is wired.** All text comes from fixed templates. The tool is designed to work with the LLM off.

## Data

- NASA **MERRA-2** monthly reanalysis (a model product, not a direct measurement), 1980 to 2025.
- Five variables: air temperature (T2M), rainfall (PRECTOTCORR), sunlight at the surface (SWGDN), night temperature (T2MMIN), day temperature (T2MMAX).
- Four regions: Maharashtra, Rajasthan, Kerala, Gujarat (boxes for the last three are rough and not checked on a map).
- The server serves **cached CSV files** (`backend/stream_cache/`, 20 files tracked in git). It never calls NASA while serving.

## Run it locally

Backend (terminal 1):

    cd backend
    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    python app.py

Frontend (terminal 2, from the repo root):

    npm install
    npm run dev

Open `http://localhost:5173`. The dev server proxies `/api` to `http://127.0.0.1:8000`. Restart the backend after editing `app.py`.

Production build: `npm run build`.

## Test it

    pip install -r requirements-dev.txt
    cd backend
    python -m unittest discover -s tests -t .
    cd ..
    python -m pytest -q

Run **both**. They collect different files and count subtests differently. See `docs/TESTING.md`.

## How it is deployed

Browser, then Vercel (static Vite build), then a rewrite of `/api/*` to a Render service running `gunicorn app:app`. The free Render instance sleeps when idle, so the first request after a pause can take 50+ seconds. Pushes to `main` redeploy both.

## Repo layout

    backend/
      app.py            Flask server and endpoints
      engine.py         trend analysis (Theil-Sen, Mann-Kendall, years needed)
      contract.py       turns engine output into JSON (verdict, why, caveats)
      answer.py         builds an answer from a domain definition
      domains.json      domains, axes, router keywords
      router.py         rules-first question router
      followup.py       follow-up question rules
      phrase.py         template wording and the wording guard
      yearrank.py, regioncompare.py, season.py, diurnal.py   extra answer types
      meaningful.py     "meaningful size" placeholders
      stream.py         fetch from NASA (only used to add data, never when serving)
      ui_adapter.py     reshapes analysis for the Explorer
      stream_cache/     20 cached CSV files
      tests/            automated tests
      API.md            endpoint reference
    src/                React frontend (pages, components, api.js, askAdapter.js)
    docs/               assessment, testing guide, test results
    vercel.json         Vercel rewrites

## Documentation

- `backend/API.md`: every endpoint and response shape.
- `docs/ASSESSMENT.md`: strengths and flaws, labelled as measured, from code, or inference.
- `docs/TESTING.md`: how to test everything.
- `docs/TEST_RESULTS.md`: every automated test with its recorded result, what was checked by hand, and what was not tested.

## Honest limits

- Verdicts depend on "meaningful size" thresholds that are project placeholders, not standards.
- Not finding a trend is not proof that nothing is happening. A past trend is not a forecast.
- All regions come from one reanalysis, so they are not independent confirmations.
- Domain content is not yet backed by sourced studies; the tool says so instead of explaining causes.
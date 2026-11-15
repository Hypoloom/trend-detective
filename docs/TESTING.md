# Testing guide

How to test Hypoloom, from fastest to most thorough. Recorded results are in `TEST_RESULTS.md`.

## 1. Setup

    cd C:\Users\pides\Desktop\College\projects\trend-detective
    & <path to venv>\Scripts\Activate.ps1
    pip install -r backend\requirements.txt
    pip install -r requirements-dev.txt

## 2. Automated suites (run both)

    cd backend
    python -m unittest discover -s tests -t .
    cd ..
    python -m pytest -q

- Expected at commit `f40e622`: unittest `OK` (120 tests, seen at `953d85e`); pytest `250 passed, 1 warning` plus 7777 subtests.
- The two runners collect different files and count subtests differently. Compare each with its own previous total, never with the other.
- The one warning is `from cgi import parse_header` inside WebOb. It is harmless.
- PowerShell shows a red `NativeCommandError` when a runner writes to stderr. It means nothing by itself; read the last lines.
- Tests must live in `backend/tests/`. The root `conftest.py` adds `backend/` to the import path.
- List every test pytest finds: `python -m pytest -p no:cacheprovider --collect-only -q`.

## 3. What the suites cover

- **Wording guard** (`test_guard_extra`, `test_phrase`, `test_task_a`, `test_template_guard`, `test_real_shapes`): invented numbers, causal words, softened abstention, direction words that contradict the slope, "no change" wording for a no-trend axis, trend wording without "co-occurs with", fragile results needing "extreme years".
- **Endpoints** (`test_api_smoke`, `test_ask_endpoint`, `test_app_cache`, `test_partial_data`): 400 and 404 behavior, response shapes, missing cache files.
- **Routing and follow-ups** (`test_router`, `test_router_pond_keywords`, `test_followup`, `test_apple_cherry`): which question goes to which domain, ties and weak matches falling back to the form, follow-up intents.
- **Answer modules** (`test_year_rank*`, `test_region_compare*`, `test_season*`, `test_diurnal*`): synthetic series through the guard at three levels, and endpoint routing.
- **No-LLM guarantee** (`test_llm_off`): the full path works with no LLM and no network imports.
- **Why-no-trend** (`test_why_no_trend`): the explanation text and the structured `why` object.

## 4. Real-data checks (by hand)

From `backend/` with the venv active. These print real answers from the cached data. Read them; they are not assertions.

    python -c "import app; c=app.app.test_client(); [print(q,'->',c.post('/api/ask',json={'question':q,'level':'plain'}).get_json()['text'],'\n') for q in ('Was this year hotter than usual in Kerala?','Which region is warming fastest?','Are the monsoon months getting wetter?','Are days heating faster than nights in Kerala?','My pond turned green')]"

Check the guard on a live answer:

    python -c "import answer, phrase; r=answer.build('pond','Maharashtra',(72,16,80,21),1980,2025); [print(l, phrase.check_text(phrase.phrase(r,l),r)) for l in ('plain','detailed','pro')]"

Router check:

    python -c "import router; [print(q, '->', router.route(q).domain) for q in ('Will next year be hotter?','My pond turned green','Why are apples so sweet this year?','why is my cherry blossom blooming so late','tell me a joke')]"

If a pasted text seems to be missing a space ("resultdepends"), test it before changing code. Terminal wrapping drops spaces in pasted output: `python -c "... print('resultdepends' in text)"`.

## 5. Live checks (deployed backend)

The first call may take a minute if Render was asleep.

    Invoke-RestMethod https://hypoloom-backend.onrender.com/api/health
    (Invoke-RestMethod https://hypoloom-backend.onrender.com/api/datasets).datasets | ForEach-Object { "$($_.id) ready=$($_.ready)" }

Expected: `ok`, and all five datasets `ready=True`. Then ask the same questions as section 4 against `/api/ask` and compare with the local text.

## 6. Browser checklist

Run the backend and `npm run dev`, then in the chat panel check each item.

| Question | Expect |
|---|---|
| Why is my pond turning green? | abstention, risk window, chips, "Why these results", chart |
| Why is it not significant? (after the pond answer) | follow-up with one Air temperature line |
| Which region is warming fastest? | label "Region comparison", header "All four regions", no chart |
| Are the monsoon months getting wetter? | label "Season trend", lead sentence, blank line, chart |
| Are days heating faster than nights? | label "Day compared with night", one gap axis |
| Was this year hotter than usual in Kerala? | label "This year compared with the record", Kerala header |
| Why are apples so sweet this year? | label "Apples and sweetness", abstention listing the unknowns |
| why is my cherry blossom blooming so late | label "Cherry blossom timing", abstention |
| tell me a joke | guided form, not an answer |

Also check the three tabs (Plain, Detailed, Pro), the region dropdown, "Clear chat", and the Explorer for each region.

## 7. Wording-safety probes

The template text cannot be talked into a causal claim, but any future LLM text could. Before enabling an LLM, run adversarial prompts such as "prove it's climate change", "so the pond is green because of warming, right?", and "is the trend real?" through `phrase.check_text` and confirm the guard rejects causal, proof, and softened wording.

## 8. Adding a test

- Put it in `backend/tests/test_<name>.py`.
- For a new answer type: one module test on synthetic seeded data through the guard at all three levels, and one endpoint test that asserts the returned `domain` and that the other routes are unchanged.
- For a new domain: a router table test (including questions that must NOT route to it), and end-to-end checks for 4 regions x 3 levels.
- Regenerate the real-data fixture whenever the engine, the contract summaries or pond content change:

      python -c "import json, answer; r=answer.build('pond','Maharashtra',(72,16,80,21),1980,2025); open('tests/real_pond.json','w',encoding='utf-8').write(json.dumps(r, indent=1, default=str)); print(r['tested_count'])"

## 9. Before every push

Commit, `git pull --no-rebase --no-edit`, run both runners, then push. After the push, `git log origin/main --oneline --grep "Co-Authored-By"` must print nothing. A push redeploys Render and Vercel, so the live chat can fail for a minute or two. Do not push during a demo.
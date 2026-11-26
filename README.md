# QA Prompt Pack

The 12 prompts software testers use most with ChatGPT, Claude, Copilot and Cursor, rewritten to be shorter, more structured and harder to hallucinate. Every pair is tested side by side on public demo apps, with the results and the harness in this repo.

Built by [SprintSynergy](https://sprintsynergy.com), an AI-based QA automation company (AI testing agents plus our QA team).

## What's inside
| # | Task | How often it appears in 34 public prompt sources |
|---|------|------|
| 01 | Test cases from a user story | 18 |
| 02 | Playwright UI test from a user journey | 16 |
| 03 | API tests | 15 |
| 04 | Review a test file | 13 |
| 05 | Bug report from rough notes | 11 |
| 06 | Edge-case inputs | 10 |
| 07 | Test data | 10 |
| 08 | Flaky / failing test diagnosis | 7 |
| 09 | Test plan | 13 |
| 10 | k6 load script | 8 |
| 11 | Security checks | 8 |
| 12 | Locator fix | 7 |

- `prompts/original/`: the popular version, quoted with credit (see [SOURCES.md](SOURCES.md))
- `prompts/optimized/`: our version, copy-paste ready. Replace the `{{file}}` slot with your own input.
- `inputs/`: the shared test input: [TodoMVC demo](https://demo.playwright.dev/todomvc/) (real DOM and Playwright aria snapshot) and the [JSONPlaceholder](https://jsonplaceholder.typicode.com) API
- `eval/`: the A/B harness (any OpenAI-compatible model endpoint, blind judge, deterministic checks)
- `results/`: token counts and quality results
- `research/`: source × task matrix

## What we changed, and why
1. **No role line.** "You are a senior QA engineer…" costs tokens and doesn't make structured output better.
2. **Input in tags** (`<req>`, `<spec>`, `<snapshot>`) so instructions and data don't blur.
3. **"Output only …"** with an exact table or code-block format. No intro, no summary.
4. **Hard caps** (max 20 rows, max 5 questions) to stop duplicate-case spam.
5. **No guessing:** "Unknown", `[unconfirmed]`, `test.fixme` for behavior the spec doesn't define.
6. **Real locators:** give UI prompts the page's Playwright aria snapshot (184 tokens for our demo page vs 317 for raw HTML) and ban CSS/XPath/`nth`/`waitForTimeout`.
7. **Drop categories that don't apply** (no "auth bypass" cases for an app with no login).

## How we test
Each prompt pair runs 3 times on the same input. Scoring:
- **Code** (UI, API, review, flaky): must compile (`tsc`) and pass against the live demo.
- **Load:** must parse with `k6 inspect` and carry the requested options and thresholds.
- **Locator:** must match exactly the right element on the real page.
- **Text:** checked for coverage of the requirement's rules, invented details and JSON validity.
- **Judge:** a second model grades each pair blind, in random order.

Token counts use `tiktoken` (o200k_base) plus the API's own usage numbers.

Run it yourself. Locally with Claude (default models `claude-haiku-5-5` for generation, `claude-sonnet-5-5` as judge):
```bash
pip install -r eval/requirements.txt
(cd eval/harness && npm install && npx playwright install chromium)
python eval/count_tokens.py
export ANTHROPIC_API_KEY=...            # never commit it
BUDGET_USD=3 K6_BIN=/path/to/k6 python eval/run_eval.py --runs 3   # stops before exceeding BUDGET_USD (spend in runs/spend.json or SPEND_FILE)
python eval/summarize.py
```
Options: `EVAL_MODEL` / `EVAL_JUDGE` (or `--model` / `--judge`), `--tasks 07,09`, `--score-only` (re-score and judge only new outputs), and `--judge-spec original` (judge against the original prompt text instead of the neutral task in `eval/judge_tasks.py`). Any other model id goes to an OpenAI-compatible endpoint: `MODELS_URL` + `MODELS_API_KEY`. On GitHub, add the repo secret `ANTHROPIC_API_KEY` (or `MODELS_API_KEY`) and trigger **Actions → prompt-eval**. Without a secret, the workflow runs only the self-test.

## Results
See [results/results.md](results/results.md). Headline: blind judge prefers the optimized prompt in 28 of 36 pairs (3 for the original); deterministic checks 0.877 → 0.951; output tokens −43%. Where it breaks and what we fixed is listed there too.

## License
MIT for everything we wrote (optimized prompts, inputs, harness, results). The quoted originals belong to their authors; see [SOURCES.md](SOURCES.md).

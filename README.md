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

Run it yourself: set the repo secret `MODELS_API_KEY` and variable `MODELS_URL` (any OpenAI-compatible chat-completions endpoint), then trigger **Actions → prompt-eval**, or run locally:
```bash
pip install -r eval/requirements.txt
(cd eval/harness && npm install && npx playwright install chromium)
python eval/count_tokens.py
MODELS_URL=https://api.openai.com/v1/chat/completions MODELS_API_KEY=... K6_BIN=/path/to/k6 python eval/run_eval.py --runs 3
```

## Results
See [results/results.md](results/results.md). Where it breaks is listed there too: prompts where the short version doesn't win, and why.

## License
MIT for everything we wrote (optimized prompts, inputs, harness, results). The quoted originals belong to their authors; see [SOURCES.md](SOURCES.md).

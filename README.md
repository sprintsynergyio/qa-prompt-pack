# QA Prompt Pack

33 AI prompts for software testers, for ChatGPT, Claude, Copilot and Cursor. They cover manual testing, test automation and four industries. Each one is rewritten to be more structured and harder to hallucinate, and tested on real checks with the harness and raw results in this repo.

Built by [SprintSynergy](https://sprintsynergy.com), an AI-based QA automation company (AI testing agents plus our QA team).

## Results at a glance
| Pack | Prompts | How it's scored | Result |
|---|---|---|---|
| Manual testing | 11 (10 A/B + 1 standalone) | popular original vs ours, 3 runs each | 10 beat, 0 lost; standalone m05 3/3 pass |
| Automation testing | 6 (all A/B) | code compiled and run on a live demo | 5 beat, 1 matched, 0 lost |
| Industry | 16 standalone | domain checks + judge rubric | 48/48 runs pass, judge 7.5/10 |

Across all 16 A/B prompts (48 blind pairs): **our version wins 40, the original 3, ties 5**. Judge score 5.85 → 7.77, deterministic checks 0.865 → 0.961, **output tokens −47%**. The prompts themselves are about the same length (input tokens +3%). The gain is leaner, more usable answers, not shorter prompts. Generation `claude-haiku-5-5`, blind judge `claude-sonnet-5-5` with a neutral task statement (it never sees either prompt).

Score columns below: deterministic checks 0-1, then judge 1-10, original → ours, mean of 3 runs.

## Manual testing
| # | Task | Checks | Judge | Wins (ours/orig/tie) |
|---|---|---|---|---|
| 01 | Test cases from a user story | 0.80 → 1.00 | 6.0 → 7.3 | 2/1/0 |
| 05 | Bug report from rough notes | 1.00 → 1.00 | 6.3 → 7.0 | 2/1/0 |
| 06 | Edge-case inputs | 0.96 → 0.93 | 5.3 → 8.0 | 3/0/0 |
| 07 | Test data | 0.78 → 0.75 | 6.7 → 8.0 | 2/0/1 |
| 09 | Test plan | 1.00 → 0.96 | 5.7 → 7.7 | 3/0/0 |
| 11 | Security checks | 0.96 → 0.99 | 6.3 → 7.7 | 2/0/1 |
| m01 | Exploratory testing charters + session notes | 0.77 → 0.96 | 5.0 → 8.0 | 3/0/0 |
| m02 | Regression/smoke checklist from a release change list | 0.93 → 1.00 | 4.3 → 8.0 | 3/0/0 |
| m03 | Test run summary report (go/no-go) | 0.91 → 1.00 | 6.3 → 8.7 | 3/0/0 |
| m04 | Acceptance-criteria review before testing | 0.71 → 1.00 | 6.0 → 8.0 | 3/0/0 |
| m05 | Cross-browser/device test matrix (standalone) | 1.00, 3/3 pass | 8.0 (absolute) | n/a |

- General manual prompts: `prompts/original/` and `prompts/optimized/` (01, 05, 06, 07, 09, 11). New manual prompts: `prompts/manual/original/` and `prompts/manual/optimized/` (m01-m05).
- Manual inputs `inputs/m-*.md` are synthetic and fictional. Each has planted traps, for example a lead's note that counts blocked cases as executed (m03), and two ACs that contradict each other (m04).
- Manual results: [results/manual.md](results/manual.md) (method, traps, honest notes) and [results/manual_summary.md](results/manual_summary.md). On 07 test data and 09 test plan, ours scores slightly lower on the checks but wins the judge. m03 writes longer answers than the original (2,112 vs 1,509 output tokens per run), because it recomputes the totals.

## Automation testing
| # | Task | Checks | Judge | Wins (ours/orig/tie) |
|---|---|---|---|---|
| 02 | Playwright UI test from a user journey | 0.71 → 0.93 | 5.0 → 9.0 | 3/0/0 |
| 03 | API tests (Playwright request) | 0.69 → 1.00 | 6.3 → 6.3 | 2/1/0 |
| 04 | Review a test file | 0.75 → 0.85 | 5.3 → 6.7 | 3/0/0 |
| 08 | Flaky / failing test diagnosis | 0.87 → 1.00 | 5.0 → 8.0 | 3/0/0 |
| 10 | k6 load script | 1.00 → 1.00 | 6.0 → 8.0 | 3/0/0 |
| 12 | Locator fix | 1.00 → 1.00 | 8.0 → 8.0 | 0/0/3 |

Code answers have to compile with `tsc` and pass against the live [TodoMVC demo](https://demo.playwright.dev/todomvc/) or [JSONPlaceholder](https://jsonplaceholder.typicode.com). k6 scripts must pass `k6 inspect`, and locators must match the right element on the real page. General results (prompts 01-12): [results/results.md](results/results.md).

How often each general task (01-12) appears in 34 public prompt sources: test cases 18, UI test 16, API 15, review 13, test plan 13, bug report 11, edge cases 10, test data 10, load 8, security 8, flaky 7, locator 7 ([research/](research/)).

## Industry
Four prompts each for healthcare, financial, e-commerce and SaaS testing. There are no client names in the fixtures. These prompts were written for this pack (there's no public original to A/B against), so they are scored on their own: deterministic domain checks plus a judge rubric. **48 of 48 runs pass; mean judge 7.5/10; weakest: fi04 audit trail (judge 6).** Details: [results/industry.md](results/industry.md).

| ID | Domain | Task |
|---|---|---|
| hc01 | Healthcare | HIPAA/PHI-safe synthetic test data |
| hc02 | Healthcare | Appointment and prescription flow test cases |
| hc03 | Healthcare | PHI leakage checks in logs, UI and API |
| hc04 | Healthcare | WCAG 2.2 AA test cases for a patient portal |
| fi01 | Financial | Money rounding, currency and precision edge cases |
| fi02 | Financial | Payment and refund flow tests |
| fi03 | Financial | Fraud and transaction-limit rule tests |
| fi04 | Financial | Audit trail checks |
| ec01 | E-commerce | Cart and checkout edge cases |
| ec02 | E-commerce | Discounts, tax and coupons |
| ec03 | E-commerce | Inventory race conditions |
| ec04 | E-commerce | Peak-load k6 script |
| sa01 | SaaS | RBAC permission matrix tests |
| sa02 | SaaS | Multi-tenant isolation tests |
| sa03 | SaaS | Subscription billing proration |
| sa04 | SaaS | API contract tests |

- `prompts/industry/`: copy-paste ready. Replace the `{{file}}` slot with your own input.
- `inputs/hc-*.md`, `inputs/fi-*.md`, `inputs/ec-*.md`, `inputs/sa-*.md`: synthetic fixtures only (no real patient, cardholder or customer data; card numbers are documented test PANs such as 4242424242424242).
- Domain checks live in `eval/industry_score.py` (reserved SSNs only, test-card allowlist, exact rounding and proration, 404 not 403 for cross-tenant ids, valid JSON). Run `python eval/industry_selftest.py` with no API key.
- The industry suite runs separately from the general pack: 16 prompts × 3 runs = 48 generation calls, plus 16 absolute judge calls (one per prompt, all 3 runs together). Results are in [results/industry_summary.md](results/industry_summary.md).

```bash
python eval/count_tokens.py --suite industry
python eval/industry_selftest.py
export ANTHROPIC_API_KEY=...
BUDGET_USD=1 K6_BIN=/path/to/k6 python eval/run_eval.py --suite industry --runs 3
python eval/summarize.py --suite industry
```

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
- **Text:** checked for coverage of the input's rules and planted traps, invented details/IDs, recomputed numbers and JSON validity.
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
# manual pack: --suite manual (also run python eval/manual_selftest.py, no key needed)
```
Options: `EVAL_MODEL` / `EVAL_JUDGE` (or `--model` / `--judge`), `--tasks 07,09`, `--score-only` (re-score and judge only new outputs), and `--judge-spec original` (judge against the original prompt text instead of the neutral task in `eval/judge_tasks.py`). Any other model id goes to an OpenAI-compatible endpoint: `MODELS_URL` + `MODELS_API_KEY`. On GitHub, add the repo secret `ANTHROPIC_API_KEY` (or `MODELS_API_KEY`) and trigger **Actions → prompt-eval**. Without a secret, the workflow runs only the self-test.

## Repo layout
- `prompts/original/`, `prompts/manual/original/`: the popular versions, quoted with credit (see [SOURCES.md](SOURCES.md))
- `prompts/optimized/`, `prompts/manual/optimized/`, `prompts/industry/`: our versions, copy-paste ready. Replace the `{{file}}` slot with your own input.
- `inputs/`: the shared test inputs (TodoMVC DOM and aria snapshot, JSONPlaceholder API) and synthetic manual (`m-*`) and industry (`hc-*`, `fi-*`, `ec-*`, `sa-*`) fixtures
- `eval/`: the harness (Claude or any OpenAI-compatible endpoint, blind judge, deterministic checks; `manual_score.py`, `industry_score.py`)
- `results/`: token counts and quality results per pack
- `research/`: source × task matrix and industry research notes

## License
MIT for everything we wrote (optimized prompts, manual and industry prompts, inputs, harness, results). The quoted originals belong to their authors; see [SOURCES.md](SOURCES.md).

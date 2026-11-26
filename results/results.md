# Prompt Pack results
Status 26 Nov 2026, 7:30 PM PKT

## Output quality: NOT MEASURED YET
The first eval run on GitHub Actions (https://github.com/sprintsynergyio/qa-prompt-pack/actions/runs/45854931101) got `HTTP 200 text/plain "OK"` from `models.github.ai` for all 72 generation calls, with no completions, so it produced 0 scored outputs. GitHub Models was retired on 30 Jul 2026 (https://github.blog/changelog/2026-07-30-github-models-is-now-retired/), and its endpoint no longer serves completions. The harness now points at any OpenAI-compatible endpoint through `MODELS_URL` + `MODELS_API_KEY`, and the workflow fails loudly if the endpoint doesn't return a completion.

Scoring is deterministic: tsc + live Playwright, `k6 inspect`, a live locator check, coverage and invented-detail checks. A blind judge model also grades each pair. The self-test on hand-written answers is in `eval/selftest/`.

## Token savings (measured, tiktoken o200k_base)
"Instruction" = the prompt text without the shared input. "Full prompt" = what is actually sent.

| Prompt | Instruction tokens (orig → opt) | Saved | Full prompt incl. input (orig → opt) | Saved |
|---|---|---|---|---|
| 01_test_cases | 117 → 67 | 43% | 310 → 260 | 16% |
| 02_ui_script | 86 → 72 | 16% | 172 → 343 | -99% |
| 03_api_tests | 48 → 44 | 8% | 155 → 151 | 3% |
| 04_test_review | 153 → 64 | 58% | 288 → 383 | -33% |
| 05_bug_report | 117 → 66 | 44% | 174 → 123 | 29% |
| 06_edge_cases | 38 → 53 | -40% | 118 → 134 | -14% |
| 07_test_data | 40 → 40 | 0% | 81 → 81 | 0% |
| 08_flaky | 100 → 64 | 36% | 479 → 443 | 8% |
| 09_test_plan | 30 → 64 | -113% | 222 → 257 | -16% |
| 10_load_script | 46 → 62 | -35% | 107 → 123 | -15% |
| 11_security | 67 → 57 | 15% | 260 → 250 | 4% |
| 12_locator_fix | 35 → 56 | -60% | 391 → 280 | 28% |
| TOTAL | 877 → 709 | 19% | 2757 → 2828 | -3% |
How to read this:
- Savings are real on the five long, role-heavy prompts (test review −58%, bug report −44%, test cases −43%, flaky −36%, security −15%).
- Six originals were already very short but under-specified (API, test data, edge cases, load, test plan, locator). Our versions add output format and anti-invention rules, so the instructions are the same length or longer.
- Two prompts (UI script, test review) add a 184-token element list captured from the real page; the full prompt grows, by design.
- The locator prompt *shrinks* by 28% overall because it sends that 184-token element list instead of 317 tokens of raw HTML.
- The bet is fewer output tokens and fewer failed or invented outputs. That part needs the model run.

## To finish
Add a model key, either an OpenAI API key with gpt-4o-mini (cheapest) or a Microsoft Foundry deployment, as repo secret `MODELS_API_KEY`, with variable `MODELS_URL`. Then re-run **prompt-eval**. Roughly 108 calls per full run (72 generation + 36 judge).

# Prompt Pack results
Status 26 Nov 2026, 7:30 PM PKT

## Output quality: NOT MEASURED
The run against GitHub Models could not happen from the box. The box's network proxy answers every request to `models.github.ai` with `200 text/plain "OK"` (no model output, even without a token). The older `models.inference.ai.azure.com` host doesn't connect at all. Other hosts (api.openai.com, api.github.com) behave normally, so this is a block on that specific host, not a bad token. No model output exists, so there are no quality scores, judge verdicts, winners or losers yet. Nothing has been invented here.

The eval is ready to run anywhere that can reach GitHub Models:
- `run_eval.py`: GitHub Models, 3 runs per variant, 6 s pacing between calls, backoff on 429/5xx with Retry-After, stops on a daily-limit response. A blind, order-randomized judge (openai/gpt-4.1) scores each run pair. It fails loudly if the endpoint returns non-JSON.
- Deterministic scores per prompt (0–1): tsc compile + live Playwright pass rate + banned patterns (UI/API/review/flaky); requirement coverage (test cases, test plan); edge-case coverage; bug-report fields + invented versions + "Unknown" marking; JSON validity + valid/invalid split (test data); `k6 inspect` + options/thresholds (load); relevant vs irrelevant security rows; live locator check on the real TodoMVC page (locator fix).
- Self-test on hand-written answers (not model output): grounded UI test 1.0, made-up Playwright API 0.2 (tsc fails), API reference 1.0, k6 reference 1.0, Playwright and CSS locators 1.0, wrong locator 0.2. See `runs/selftest/selftest_results.txt`.

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
Run `.github/workflows/eval.yml` (manual trigger) in the future `sprintsynergyio/qa-prompt-pack` repo. In GitHub Actions, `GITHUB_TOKEN` with `permissions: models: read` calls GitHub Models directly. Alternatively, run `python run_eval.py --runs 3` on any machine with normal internet access. Expected budget: 72 generation calls (gpt-4o-mini, low tier: 15/min, 150/day) + 36 judge calls (gpt-4.1, high tier: 10/min, 50/day). That fits one day's free quota.

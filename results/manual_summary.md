## Manual testing: original vs optimized (24 outputs; generation claude-haiku-5-5; blind pairwise judge)
Quality = deterministic checks 0-1 (mean of runs). Judge = blind, order-randomized pairwise 1-10. Token counts from API usage.

| Prompt | Quality orig | Quality opt | Judge orig | Judge opt | Judge wins opt/orig/tie | Tokens in orig→opt | Tokens out orig→opt | Gen cost orig→opt (USD) | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| m01_exploratory_charters | 0.767 | 0.963 | 5.0 | 8.0 | 3/0/0 | 479→538 | 7973→3233 | 0.0121→0.0050 | beat |
| m02_regression_checklist | 0.933 | 1.0 | 4.33 | 8.0 | 3/0/0 | 492→444 | 6952→2254 | 0.0106→0.0035 | beat |
| m03_run_summary | 0.911 | 1.0 | 6.33 | 8.67 | 3/0/0 | 451→583 | 1509→2112 | 0.0024→0.0033 | beat |
| m04_ac_review | 0.712 | 1.0 | 6.0 | 8.0 | 3/0/0 | 628→328 | 5452→4351 | 0.0084→0.0066 | beat |

**Overall:** quality 0.831 → 0.991; judge 5.42 → 8.17; judge wins optimized 12, original 0, tie 0 (of 12). Mean tokens per call summed over prompts: in 2050 → 1893, out 21886 → 11950 (-42.2% total). Generation cost 0.0334 → 0.0185 USD. Verdicts: beat 4, matched 0, LOST 0

## Manual testing: standalone (no public original) (3 outputs; generation claude-haiku-5-5; absolute judge)
Quality = deterministic domain checks 0-1 (mean of runs). Judge = absolute rubric 1-10 (one call per prompt across its runs).

| Prompt | Quality (checks) | Runs passing (≥0.8) | Judge | Consistency | Tokens in | Tokens out | Gen cost (USD) | Verdict |
|---|---|---|---|---|---|---|---|---|
| m05_browser_matrix | 1.0 | 3/3 | 8.0 | 10.0 | 520 | 1509 | 0.0024 | strong |

**Pass rate:** 3/3 runs (100%); prompts with all runs passing: 1/1. Mean quality 1.0, mean judge 8.0.

Total API spend recorded in /workspace/prompt-pack/spend_manual.json: $0.2382 over 40 calls.

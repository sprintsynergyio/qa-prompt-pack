# Industry pack results (v0.2)
Status 26 Nov 2026, 9:13 PM PKT

## Output quality: NOT MEASURED ON MODELS YET
Deterministic domain checks are in place and the self-test fixtures all pass (`python eval/industry_selftest.py`, 23 fixtures). The model run (3 generations per prompt + one absolute judge call per prompt) has not been completed, so there are no quality scores, judge verdicts or rewrite-after-loss notes yet. Nothing has been invented here.

A full industry eval is 48 generation calls (`openai/gpt-4o-mini`, low tier: 15/min, 150/day) plus 16 absolute judge calls (`openai/gpt-4.1`, high tier: 10/min, 50/day). That fits one day's free quota if it is not run on the same day as the 12-prompt general pack.

Run it with **Actions → prompt-eval-industry**, or:

```bash
python eval/industry_selftest.py
GITHUB_TOKEN=... K6_BIN=/path/to/k6 python eval/run_eval.py --suite industry --runs 3
python eval/summarize.py --suite industry
```

The general `prompt-eval` workflow is unchanged and should not be started from this branch on the same day if the free-tier budget is already in use.

## Domain checks (deterministic, no model)
Hand-written reference answers score 1.0 (or ≥0.8) and planted-bad answers score below 0.5 on:

- **hc01** JSON fixtures: 8 valid / 8 invalid, reserved SSN areas only (flags 078-05-1120), SYN- MRNs, @example.com, provenance, no Luhn-valid non-test PANs
- **hc02** appointment + prescription rule coverage (double-book, past slot, no-show, refill_too_soon, allergy, 403/404)
- **hc03** planted leak recall (LEAK-01..04) and precision (CLEAN-01..03 must stay clean)
- **hc04** WCAG 2.2 AA coverage for the listed portal controls only
- **fi01** exact expected rounding (USD half-up/half-even, JPY 0 dp, BHD 3 dp, 10.00 split, 2% fee)
- **fi02** payment/refund state-machine coverage, test-card allowlist
- **fi03** inclusive limits 200000/200001, daily cap across channels, velocity, cooling, no invented scoring weights
- **fi04** required audit fields, immutability (405), no PAN/CVV/token
- **ec01** cart/checkout edges plus the two charge/order invariants
- **ec02** exact discount/tax/total strings (SAVE10 NY total 94.72, stack_ok 89.98, and the other five cases)
- **ec03** "exactly one" winner on last-unit races, holds, sold-out between cart and pay
- **ec04** k6 stages 100/300/50, p(95)<800, p(99)<1500, failed rate<0.02, SKU-HOT, 200 or 409
- **sa01** all 55 role × action cells (200/403 and persist/no-change)
- **sa02** 404 not 403, list/search/export scope, spoofed tenant header, cache, jobs, three tenants
- **sa03** documented proration method (upgrade day 10 due 26.66, not 26.67), cancel due 0.00, webhook replay
- **sa04** documented ops and error shape only; invented endpoints are penalized

## Token counts (measured, tiktoken o200k_base)
Instruction = the prompt text without the shared input. Full prompt = what is actually sent. There is no original to compare, so these are absolute lengths.

| Prompt | Instruction tokens | Full prompt incl. input |
|---|---|---|
| hc01_phi_testdata | 180 | 470 |
| hc02_clinical_flows | 92 | 443 |
| hc03_phi_leakage | 101 | 361 |
| hc04_accessibility | 104 | 315 |
| fi01_rounding_currency | 61 | 345 |
| fi02_payment_refund | 103 | 425 |
| fi03_fraud_limits | 91 | 284 |
| fi04_audit_trail | 85 | 249 |
| ec01_cart_checkout | 95 | 282 |
| ec02_discounts_tax | 67 | 489 |
| ec03_inventory_race | 84 | 288 |
| ec04_peak_load | 123 | 225 |
| sa01_rbac_matrix | 82 | 249 |
| sa02_tenant_isolation | 104 | 319 |
| sa03_billing_proration | 87 | 384 |
| sa04_api_contract | 77 | 313 |
| TOTAL | 1536 | 5441 |

Source file: [industry_token_counts.csv](industry_token_counts.csv).

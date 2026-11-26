# Industry pack results (v0.2)
Status 26 Nov 2026, 10:55 PM PKT

## Output quality (measured)
Generation `claude-haiku-5-5`, 3 runs per prompt (48 outputs). Each run is scored by the deterministic domain checks below; a run passes at ≥ 0.8. Judge: `claude-sonnet-5-5`, one absolute rubric call per prompt that sees all 3 runs (1-10 for typical quality and for consistency). Judge reasons are in `industry_judge.json`.

- **Pass rate: 48/48 runs (100%); 16/16 prompts pass on every run.** Mean check score 0.977, mean judge 7.5/10.
- Weakest by judge: fi04 audit trail (6/10, consistency 5). Its checks pass, but runs differ in how many refusal/correction rows they write, and some invent rows. sa01 RBAC (consistency 5) is correct on all 55 cells, but runs format `expected_http` and read results differently.
- Industry cost: $0.59 including all re-runs and re-judging.

| Prompt | Quality (checks) | Runs passing (≥0.8) | Judge | Consistency | Tokens in | Tokens out | Gen cost (USD) | Verdict |
|---|---|---|---|---|---|---|---|---|
| ec01_cart_checkout | 0.969 | 3/3 | 7.0 | 7.0 | 448 | 3234 | 0.0050 | ok |
| ec02_discounts_tax | 1.0 | 3/3 | 10.0 | 10.0 | 750 | 1520 | 0.0025 | strong |
| ec03_inventory_race | 1.0 | 3/3 | 7.0 | 7.0 | 518 | 2548 | 0.0040 | ok |
| ec04_peak_load | 1.0 | 3/3 | 7.0 | 8.0 | 332 | 2939 | 0.0045 | ok |
| fi01_rounding_currency | 1.0 | 3/3 | 8.0 | 7.0 | 496 | 977 | 0.0016 | strong |
| fi02_payment_refund | 0.879 | 3/3 | 7.0 | 7.0 | 646 | 6400 | 0.0098 | ok |
| fi03_fraud_limits | 1.0 | 3/3 | 7.0 | 7.0 | 478 | 2359 | 0.0037 | ok |
| fi04_audit_trail | 1.0 | 3/3 | 6.0 | 5.0 | 396 | 2758 | 0.0043 | ok |
| hc01_phi_testdata | 1.0 | 3/3 | 8.0 | 9.0 | 690 | 5403 | 0.0083 | strong |
| hc02_clinical_flows | 1.0 | 3/3 | 7.0 | 6.0 | 740 | 6589 | 0.0101 | ok |
| hc03_phi_leakage | 1.0 | 3/3 | 9.0 | 10.0 | 595 | 1027 | 0.0017 | strong |
| hc04_accessibility | 1.0 | 3/3 | 7.0 | 8.0 | 478 | 4392 | 0.0067 | ok |
| sa01_rbac_matrix | 0.948 | 3/3 | 7.0 | 5.0 | 404 | 3837 | 0.0059 | ok |
| sa02_tenant_isolation | 0.887 | 3/3 | 7.0 | 8.0 | 529 | 2368 | 0.0037 | ok |
| sa03_billing_proration | 0.991 | 3/3 | 8.0 | 6.0 | 619 | 1163 | 0.0019 | strong |
| sa04_api_contract | 0.965 | 3/3 | 8.0 | 8.0 | 454 | 2561 | 0.0040 | strong |

### Fixes made
| Prompt | Problem | Fix | Before → after |
|---|---|---|---|
| ec03_inventory_race | 0/3 runs passing (0.75). The outputs were right ("Exactly 1 response 200", "qty exceeds stock") but the check regex only accepted "exactly one" / "qty > stock" | Checker fix, no prompt change: accept "exactly 1" and "exceeds stock" / "qty=2 … stock=1" | 0.75, 0/3 → 1.0, 3/3 |
| hc03_phi_leakage | 2/3 passing. Run 1 put the LEAK-xx IDs in `artifact` and its own F1..F4 in `id` | Prompt now says `id` = the input's artifact ID, `artifact` = its type | 0.87, 2/3 → 1.0, 3/3; judge 9 |
| (all) | The first judge pass cut answers at 4-14k characters, so it reported "truncated" outputs | Judge caps raised to 20k per run / 60k total, and everything was re-judged | e.g. hc01 3 → 8, sa01 4 → 7, fi02 5 → 7 |
| fi04_audit_trail (tried, reverted) | Judge 6/10 | Tried "every action × outcome, rows self-contained" | Output tokens +60%, judge 6 → 6, consistency 5. Reverted to the shorter prompt |

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

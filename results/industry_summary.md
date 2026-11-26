## Industry suite (48 outputs; generation claude-haiku-5-5; absolute judge)
Quality = deterministic domain checks 0-1 (mean of runs). Judge = absolute rubric 1-10 (one call per prompt across its runs).

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

**Pass rate:** 48/48 runs (100%); prompts with all runs passing: 16/16. Mean quality 0.977, mean judge 7.5.

Total API spend recorded in /workspace/prompt-pack/spend_industry.json: $0.5852 over 88 calls.

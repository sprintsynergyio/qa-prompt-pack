# Manual testing pack results (v0.3)
Status 27 Nov 2026, about 1:00 AM PKT. Generation `claude-haiku-5-5`, 3 runs per prompt. Judge `claude-sonnet-5-5`: blind, order-randomized pairwise for m01-m04 with a neutral task statement and the shared input (`eval/judge_tasks.py`); absolute rubric for m05. Cost: $0.24 for 40 API calls.

## Headline (m01-m04, original vs ours, 12 blind pairs)
- Judge: **ours wins 12 of 12**. Mean 5.42 → 8.17.
- Deterministic checks: 0.831 → 0.991.
- Output tokens: 21,886 → 11,950 per 3-run set (−45%). Input tokens 2,050 → 1,893.
- m05 browser/device matrix (standalone): 3/3 runs pass, checks 1.0, judge 8/10, consistency 10.

Per-prompt table: [manual_summary.md](manual_summary.md). Raw rows: [manual_quality.csv](manual_quality.csv). Judge reasons: [manual_judge.json](manual_judge.json).

## What the checks look for (synthetic inputs, planted traps)
- **m01 exploratory charters** (`m-feature.md`, password reset): coverage of the 11 stated risks: expiry, single use, old links invalidated, rate limit, no account enumeration, password rules, other sessions signed out, case-insensitive email, link scanners (bug history), SSO, new email queue. Also: charter missions, timeboxes, oracles and a notes template. Inventing SMS or security-question flows is penalized.
- **m02 regression checklist** (`m-release-changes.md`): every change CHG-101..105 mapped, the docs-only CHG-106 explicitly skipped, a smoke pass of the 3 critical paths, P0/P1 priorities, change-specific checks (order-total tax, E.164 phone, 24 per page, midnight UTC dates), no invented change IDs.
- **m03 run summary** (`m-run-results.md`): counts recomputed from module rows (120 planned, 106 executed, 98 passed, 8 failed, 6 blocked, 8 not run, 92.5% pass rate). The lead's "112 executed, 95%" must be flagged, the recommendation must be No-Go (BUG-311 critical open), open defects cited, and no invented bug IDs.
- **m04 AC review** (`m-story-acs.md`): finds the AC1 "immediately" vs AC4 "batch every 15 minutes" contradiction; flags "appropriate", "fast" and "gracefully"; raises "user" vs account owner, notification channel, AC5 counting/resume rules and non-owner permissions. It must also give per-AC verdicts, Given/When/Then rewrites and questions.
- **m05 browser matrix** (`m-browser-traffic.md`): the 6 combos with ≥4% share are covered; IE11 and Opera are not tested; iOS Safari runs on the real iPhone; full = 3 h and smoke = 45 min, within 16 h.

Scorer self-test: `python eval/manual_selftest.py` (10 fixtures; reference answers ≥ 0.8, planted-bad answers < 0.5).

## Honest notes
- **No prompt lost, so none was rewritten.** One check was loosened after the run, and it applies to both variants. m03 had two false negatives: "do not match" (the regex had only "does not match") and a failed count shown only as "98 + 8". With the fix, ours goes 0.931 → 1.0. The original stays at 0.911.
- **m03 (ours) writes longer answers than the original** (2,112 vs 1,509 output tokens per run), because it recomputes and reconciles every total. The original's one-liner caught the lead's wrong figure in 3/3 runs too, but one run reported a wrong pass rate.
- **m01:** ours missed one risk in 2 of 3 runs (sessions signed out once, case-insensitive email once). The original covered every risk but never said how to recognize a failure (oracle), and never gave a notes template. It also ran into the 8,000-token output cap in 2 of 3 runs, so those answers were cut off.
- **m04:** the original never asked who "the user" is (owner vs other roles) in any run.
- m05 has no public original, so it's scored standalone.

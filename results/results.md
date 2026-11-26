# Prompt Pack results
Status 26 Nov 2026, 10:40 PM PKT. Generation model `claude-haiku-5-5`, judge `claude-sonnet-5-5` (Anthropic Messages API). 12 prompts × original vs optimized × 3 runs = 72 outputs, 36 blind judge pairs.

## Headline
- **Judge (blind, order-randomized, neutral task):** optimized wins 28 of 36 pairs, original 3, ties 5. Mean score 6.0 → 7.64 out of 10.
- **Deterministic checks** (compile + live run, k6 inspect, live locator, coverage): mean 0.877 → 0.951.
- **Output tokens:** 53,693 → 28,121 per 3-run set (−43%). Generation cost $0.082 → $0.044 for the whole suite.
- **Prompt (input) tokens:** about flat, 4,429 → 4,753 per 3-run set (+7%). The savings come from shorter, usable answers, not shorter prompts.
- Verdicts: 11 beat, 1 matched (locator fix: both always correct), 0 lost.

## Per prompt
Quality = deterministic checks 0-1, mean of 3 runs. Judge = 1-10, mean of 3 blind pairs. Tokens and cost are summed over 3 runs, from API usage.

| Prompt | Quality orig | Quality opt | Judge orig | Judge opt | Judge wins opt/orig/tie | Tokens in orig→opt | Tokens out orig→opt | Gen cost orig→opt (USD) | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 01_test_cases | 0.8 | 1.0 | 6.0 | 7.33 | 2/1/0 | 514→426 | 5953→4198 | 0.0091→0.0064 | beat |
| 02_ui_script | 0.708 | 0.933 | 5.0 | 9.0 | 3/0/0 | 285→536 | 4335→1799 | 0.0066→0.0029 | beat |
| 03_api_tests | 0.692 | 1.0 | 6.33 | 6.33 | 2/1/0 | 248→237 | 4965→2637 | 0.0075→0.0040 | beat |
| 04_test_review | 0.75 | 0.85 | 5.33 | 6.67 | 3/0/0 | 455→587 | 5362→3296 | 0.0082→0.0051 | beat |
| 05_bug_report | 1.0 | 1.0 | 6.33 | 7.0 | 2/1/0 | 293→201 | 2002→1368 | 0.0031→0.0021 | beat |
| 06_edge_cases | 0.963 | 0.926 | 5.33 | 8.0 | 3/0/0 | 208→245 | 5855→2732 | 0.0088→0.0042 | beat |
| 07_test_data | 0.783 | 0.75 | 6.67 | 8.0 | 2/0/1 | 143→332 | 3709→2927 | 0.0056→0.0045 | beat |
| 08_flaky | 0.867 | 1.0 | 5.0 | 8.0 | 3/0/0 | 753→697 | 4505→2028 | 0.0070→0.0033 | beat |
| 09_test_plan | 1.0 | 0.96 | 5.67 | 7.67 | 3/0/0 | 354→429 | 7595→3157 | 0.0115→0.0049 | beat |
| 10_load_script | 1.0 | 1.0 | 6.0 | 8.0 | 3/0/0 | 157→180 | 2382→1047 | 0.0036→0.0016 | beat |
| 11_security | 0.96 | 0.987 | 6.33 | 7.67 | 2/0/1 | 421→440 | 6668→2776 | 0.0101→0.0043 | beat |
| 12_locator_fix | 1.0 | 1.0 | 8.0 | 8.0 | 0/0/3 | 598→443 | 362→156 | 0.0007→0.0004 | matched |

## How the judge was set up, and why it matters
The judge sees a **neutral task statement plus the shared input files** (`eval/judge_tasks.py`). It sees neither prompt. Any framework or format is accepted if a QA engineer can use it.

We first ran the judge with the *original prompt* as the task. Then it graded both answers against the original's own wording: "Python CSS selector", "at least 2 security cases", "unicode". Original won 31 of 36 and scored 7.56 vs 4.78. That setup rewards following the original's wording, not usefulness, so it is not the headline. Both judgments are in `results/judge_neutral.json` and `results/judge_original_spec.json`; reproduce with `--judge-spec original`. The original-spec file still holds the pre-fix outputs. That run also surfaced real gaps in our prompts, fixed below.

## Fixes made (optimized prompt lost, fixed, re-ran 3 runs)
| Prompt | Problem | Fix | Before → after |
|---|---|---|---|
| 07_test_data | No unicode/special characters, duplicate valid cases (judge 3.0 vs 8.67, 0/3 wins) | Ask for no duplicates, unicode/emoji, special characters, untrimmed and too-long cases | judge 3.0 → 7.0 (2/3 wins) |
| 07_test_data (2nd) | The model miscounted "200-char" titles (actual 120-320 chars), so the length boundary was wrong | Prompt carries the exact 200-char string to copy. The scorer now also requires real 200/201-char titles (applies to both variants; original drops 0.9 → 0.783) | judge 7.0 → 8.0 (2 wins, 1 tie, 0 losses), quality 0.75 |
| 06_edge_cases | Missed "very long" and newline inputs (quality 0.815) | Add newline/tab and length 1/max/max+1/very long paste | quality 0.815 → 0.926, judge 8.0 (3/3) |
| 09_test_plan | Missed the empty-edit-deletes and "1 item left" rules (0.907) | Every rule in scope must map to ≥1 test | quality 0.907 → 0.96, judge 7.67 (3/3) |
| 11_security | Missed CSP/headers and vulnerable-dependency checks (0.853) | Name OWASP A05/A06 as applying to a client-only app | quality 0.853 → 0.987, judge 7.67 (2 wins, 1 tie) |

Still weaker than the original on one number: **07_test_data quality 0.75 vs 0.783**. It is within the margin and wins the judge. The 200-char literal costs about 90 prompt tokens. Without it, Haiku miscounts long strings on both prompts: the original hit an exact 200/201 only 1 time in 3.

## Token counts (tiktoken o200k_base)
"Instruction" = prompt text without the shared input. "Full prompt" = what is actually sent.

| Prompt | Instruction tokens (orig → opt) | Saved | Full prompt incl. input (orig → opt) | Saved |
|---|---|---|---|---|
| 01_test_cases | 117 → 67 | 42.7% | 310 → 260 | 16.1% |
| 02_ui_script | 86 → 72 | 16.3% | 172 → 343 | -99.4% |
| 03_api_tests | 48 → 44 | 8.3% | 155 → 151 | 2.6% |
| 04_test_review | 153 → 64 | 58.2% | 288 → 383 | -33.0% |
| 05_bug_report | 117 → 66 | 43.6% | 174 → 123 | 29.3% |
| 06_edge_cases | 38 → 67 | -76.3% | 118 → 148 | -25.4% |
| 07_test_data | 40 → 133 | -232.5% | 81 → 174 | -114.8% |
| 08_flaky | 100 → 64 | 36.0% | 479 → 443 | 7.5% |
| 09_test_plan | 30 → 75 | -150.0% | 222 → 268 | -20.7% |
| 10_load_script | 46 → 62 | -34.8% | 107 → 123 | -15.0% |
| 11_security | 67 → 82 | -22.4% | 260 → 275 | -5.8% |
| 12_locator_fix | 35 → 56 | -60.0% | 391 → 280 | 28.4% |
| TOTAL | 877 → 852 | 2.9% | 2757 → 2971 | -7.8% |

After the fixes, instruction tokens are flat (877 → 852). The prompts were never much shorter, because six originals were short but under-specified. The measured gain is on the output side: about half the output tokens, and answers that compile, run and match the real page more often.

## Cost
Whole general suite including the judge, both judge setups and all fix re-runs: **$1.47** (195 API calls; Haiku generation $0.14, Sonnet judge the rest).

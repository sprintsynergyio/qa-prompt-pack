## General suite (72 outputs; generation claude-haiku-5-5; blind pairwise judge)
Quality = deterministic checks 0-1 (mean of runs). Judge = blind, order-randomized pairwise 1-10. Token counts from API usage.

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

**Overall:** quality 0.877 → 0.951; judge 6.0 → 7.64; judge wins optimized 28, original 3, tie 5 (of 36). Mean tokens per call summed over prompts: in 4429 → 4753, out 53693 → 28121 (-43.4% total). Generation cost 0.0819 → 0.0436 USD. Verdicts: beat 11, matched 1, LOST 0

Total API spend recorded in /workspace/prompt-pack/spend_total.json: $1.4677 over 195 calls.

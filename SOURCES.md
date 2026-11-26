# Sources of the "original" prompts
The files in `prompts/original/` are popular public prompts. We quote them for side-by-side comparison, with the placeholder slots filled with our test input. They belong to their authors and are **not** covered by this repo's MIT license. Everything else here (optimized prompts, inputs, eval harness, results) is MIT.

| File | Source |
|---|---|
| 01_test_cases | The Testing Academy, https://app.thetestingacademy.com/blog/chatgpt-for-testers |
| 02_ui_script | testcraft-ai/qa-ai-prompts (MIT), prompts/e2e-ui-testing.md |
| 03_api_tests | BrowserStack Test Companion prompt guide, https://www.browserstack.com/docs/test-companion/best-practices/prompts |
| 04_test_review | testcraft-ai/qa-ai-prompts (MIT), prompts/test-code-review.md |
| 05_bug_report | The Testing Academy (URL above) |
| 06_edge_cases | ClawGear on dev.to, https://dev.to/clawgear/35-chatgpt-prompts-for-qa-engineers-test-cases-bug-reports-and-automation-scripts-that-actually-198b |
| 07_test_data | dashatsion/qa-advanced-prompting (MIT), prompts/QA_Prompt_Library.md |
| 08_flaky | testcraft-ai/qa-ai-prompts (MIT), prompts/e2e-ui-testing.md |
| 09_test_plan | PractiTest, https://www.practitest.com/resource-center/blog/chatgpt-prompts-for-software-testing/ |
| 10_load_script | Software Test Pilot, prompt 26, https://www.softwaretestpilot.com/blog/ai-in-testing/chatgpt-prompts-software-testers-50-examples |
| 11_security | DeviQA, https://www.deviqa.com/blog/50-chatgpt-prompts-for-qa-testing-every-qa-engineer-should-know/ |
| 12_locator_fix | simplified.guide, https://www.simplified.guide/selenium/ai-selector-update |

Systems under test are public demos: https://demo.playwright.dev/todomvc/ and https://jsonplaceholder.typicode.com.

## Industry packs (v0.2)
The files in `prompts/industry/` were written for this pack and are covered by the repo MIT license. There is no quoted "original" to compare: short public industry prompts that matched these tasks were not used, and we did not copy long vendor articles. Research that informed the themes (not the prompt wording) is in [research/industry_sources.md](research/industry_sources.md).

If a short, credited public original is added later, place it in `prompts/industry-original/` with the same filename; the harness will then run a blind original-vs-optimized judge for that task only.


## Manual testing pack (v0.3)
The files in `prompts/manual/original/` are popular public prompts, quoted for side-by-side comparison with our synthetic input in the placeholder slot. They belong to their authors and are **not** covered by this repo's MIT license.

| File | Source | Notes |
|---|---|---|
| m01_exploratory_charters | AlwaysQA prompt library, "Create exploratory testing charters", https://alwaysqa.com/prompt-library/exploratory-testing/ | verbatim, `[DESCRIBE FEATURE OR PAGE]` filled |
| m02_regression_checklist | QATechTools, "How to Create Regression Test Ideas from Release Notes with AI" (8 Jul 2026), https://qatechtools.com/2026/07/08/how-to-create-regression-test-ideas-from-release-notes-with-ai/ | steps 1 and 3 run as one prompt (the article's step 2 table review is skipped, as in one-shot use) |
| m03_run_summary | Revive Techno, "10 ChatGPT Prompts for Software Testers", prompt 8, https://www.revivetechno.com/blogs/10-chatgpt-prompts-every-software-tester-should-bookmark | verbatim, `[paste results]` filled |
| m04_ac_review | AgenticSkillset.org, "The AC Testability Audit Prompt", https://agenticskillset.org/en/topics/evaluating-acceptance-criteria-for-testability/ | verbatim; story and ACs are one input file, so the ACs slot says "(included with the story above)" |

`prompts/manual/optimized/m05_browser_matrix.txt` has no short public original we could quote, so it's scored standalone (domain checks + absolute judge), like the industry pack. All manual inputs (`inputs/m-*.md`) are synthetic, fictional apps.

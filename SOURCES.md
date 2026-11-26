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


"""Source x task matrix. 1 = the source explicitly lists a prompt/use case for that task.
Built by reading each source (downloaded copies in sources/ where fetchable). Run: python3 tally.py"""
import csv
T = ["test_cases","ui_script","bug_report","api_tests","edge_boundary","test_data","flaky","test_review","bdd","regression_select","sql_db","locators","test_plan","exploratory","perf_load","security"]
S = {
 # community
 "reddit_softwaretesting_1plgv7p|https://www.reddit.com/r/softwaretesting/comments/1plgv7p/": "test_cases edge_boundary api_tests security",
 "reddit_QA_14md5iz|https://www.reddit.com/r/QualityAssurance/comments/14md5iz/": "test_cases test_data test_plan",
 "reddit_QA_1kb5z6c|https://www.reddit.com/r/QualityAssurance/comments/1kb5z6c/": "test_cases",
 "reddit_Playwright_1pd18f5|https://www.reddit.com/r/Playwright/comments/1pd18f5/": "locators ui_script",
 "mot_challenge_105|https://www.ministryoftesting.com/challenges/105": "test_cases bdd test_review test_plan",
 "mot_club_78635|https://club.ministryoftesting.com/t/prompting-for-testers-setting-the-right-context-for-your-prompts-activity/78635": "edge_boundary ui_script test_review",
 # article lists
 "deviqa_50|https://www.deviqa.com/blog/50-chatgpt-prompts-for-qa-testing-every-qa-engineer-should-know/": "test_cases bdd edge_boundary exploratory test_plan ui_script test_review api_tests flaky perf_load security bug_report test_data",
 "testingacademy_10|https://app.thetestingacademy.com/blog/chatgpt-for-testers": "test_cases bug_report test_review",
 "qable_10|https://www.qable.io/blog/top-10-chatgpt-prompts-for-quality-testing": "test_cases edge_boundary bug_report test_review test_data perf_load exploratory test_plan",
 "devto_clawgear_35|https://dev.to/clawgear/35-chatgpt-prompts-for-qa-engineers-test-cases-bug-reports-and-automation-scripts-that-actually-198b": "test_cases edge_boundary bug_report test_plan api_tests ui_script perf_load security",
 "practitest_10|https://www.practitest.com/resource-center/blog/chatgpt-prompts-for-software-testing/": "test_cases edge_boundary ui_script regression_select perf_load bug_report test_plan",
 "qahub_10|https://qahub.ai/blog/chatgpt-prompts-qa": "test_cases bug_report api_tests security regression_select test_data perf_load exploratory",
 "softwaretestpilot_50|https://www.softwaretestpilot.com/blog/ai-in-testing/chatgpt-prompts-software-testers-50-examples": "test_cases bug_report api_tests ui_script flaky test_review test_data sql_db perf_load security test_plan",
 "qasphere_10|https://qasphere.com/blog/chatgpt-for-software-testing/": "test_cases edge_boundary bug_report test_review test_data api_tests regression_select exploratory",
 "qapractices|https://qapractices.com/prompts/ai-prompt-generate-test-cases-from-requirements/": "test_cases sql_db",
 "sqaexperts_pdf|https://www.sqaexperts.com/resources/prompt-library-for-software-testers-sqaexperts.pdf": "test_cases edge_boundary test_review",
 # vendor
 "browserstack_prompt_guide|https://www.browserstack.com/docs/test-companion/best-practices/prompts": "ui_script api_tests edge_boundary",
 "browserstack_chatgpt_guide|https://www.browserstack.com/guide/mastering-test-automation-with-chatgpt": "ui_script test_plan",
 "katalon_docs|https://docs.katalon.com/katalon-studio/create-test-cases/generate-api-tests-with-ai-beta": "api_tests test_data",
 "lambdatest_agent_skills|https://github.com/LambdaTest/agent-skills/blob/main/api-skill/api-to-testcase-generator/SKILL.md": "api_tests",
 # topic playbooks / guides
 "stp_playwright|https://www.softwaretestpilot.com/blog/ai-in-testing/chatgpt-playwright-tests": "ui_script locators flaky",
 "stp_api|https://www.softwaretestpilot.com/blog/ai-in-testing/chatgpt-for-api-testing": "api_tests",
 "stp_regression|https://www.softwaretestpilot.com/blog/ai-in-testing/chatgpt-for-regression-testing": "regression_select",
 "stp_gherkin|https://www.softwaretestpilot.com/blog/ai-in-testing/chatgpt-gherkin-scenarios": "bdd",
 "qatribe_flaky|https://qatribe.in/debugging-flaky-tests-with-ai/": "flaky",
 "simplified_guide_selectors|https://www.simplified.guide/selenium/ai-selector-update": "locators",
 "roboqa_locators|https://www.roboqa.tech/learn/career-roadmaps/ai-careers/ai-for-testers/generating-locators-with-ai": "locators",
 "fenbs_cursor_rules|https://fenbs.ai/blog/cursor-rules-playwright": "ui_script locators",
 # GitHub prompt repos
 "gh_testcraft-ai/qa-ai-prompts|https://github.com/testcraft-ai/qa-ai-prompts": "test_cases bdd api_tests bug_report sql_db ui_script flaky test_review test_data exploratory perf_load security test_plan",
 "gh_dashatsion/qa-advanced-prompting|https://github.com/dashatsion/qa-advanced-prompting": "ui_script flaky test_review test_data regression_select locators",
 "gh_vpdinesh/TestPrompts|https://github.com/vpdinesh/TestPrompts": "test_cases ui_script bug_report api_tests test_review security test_plan",
 "gh_tayyabakmal1/qa-prompt-library|https://github.com/tayyabakmal1/qa-prompt-library": "test_cases bug_report test_plan api_tests ui_script sql_db test_data locators regression_select exploratory perf_load security",
 "gh_naodeng/awesome-qa-prompt|https://github.com/naodeng/awesome-qa-prompt": "test_cases edge_boundary api_tests ui_script test_review flaky test_plan",
 "gh_jaktestowac/awesome-copilot-for-testers|https://github.com/jaktestowac/awesome-copilot-for-testers": "bdd ui_script api_tests test_review test_plan",
}
counts = {t:0 for t in T}
rows=[]
for k,v in S.items():
    name,url=k.split("|",1); tags=set(v.split())
    assert tags<=set(T),(name,tags-set(T))
    for t in tags: counts[t]+=1
    rows.append([name,url]+[int(t in tags) for t in T])
with open(__import__("pathlib").Path(__file__).resolve().parent.parent/"research"/"source_matrix.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["source","url"]+T); w.writerows(rows)
print(f"{len(S)} sources")
for t,c in sorted(counts.items(), key=lambda x:-x[1]): print(f"{c:3d}  {t}")

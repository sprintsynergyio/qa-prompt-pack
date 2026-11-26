"""Neutral task statements for the pairwise judge.

The judge must not see either prompt: grading against the original prompt's wording
rewards whichever answer follows that wording (e.g. "Python CSS selector"), not the
answer a QA engineer can use. Each entry = what the engineer actually needs + the shared
input files both prompts were given. Any format/framework is acceptable if usable.
"""
NEUTRAL = {
 "01_test_cases": ("Write executable test cases for this requirement: every rule covered, plus relevant negative, boundary and security cases; expected results precise enough to pass/fail without interpretation; ambiguities flagged as questions instead of guessed.", ["requirement.md"]),
 "02_ui_script": ("Write a Playwright TypeScript test for this journey that would run green against the real page (its aria snapshot is given): locators that exist on the page, assertions after each state change, no hard waits, setup/isolation handled.", ["journey.md", "locators.md"]),
 "03_api_tests": ("Write Playwright TypeScript API tests (request fixture) for POST /todos on the service described. Tests must be correct against the real service as documented: assert the documented response, and do not assert behavior the service does not have (it fakes writes and has no validation) unless clearly marked as a known gap.", ["api.md"]),
 "04_test_review": ("Review this Playwright test: find the real problems (flakiness, false passes, brittle selectors, isolation, missing assertions) with line references, severity and concrete fixes usable against the real page (aria snapshot given).", ["review-target.spec.ts", "locators.md"]),
 "05_bug_report": ("Turn these notes into a bug report a developer can act on: accurate title, justified severity, environment, reproduction steps, expected vs actual. Only facts from the notes; missing information marked as missing, not invented.", ["bug-notes.md"]),
 "06_edge_cases": ("List edge-case inputs to test this todo title field (valid, invalid, empty/whitespace, boundaries, unicode, injection/XSS) with expected results that follow the spec; unknown expectations flagged, not invented.", ["field-spec.md"]),
 "07_test_data": ("Produce a JSON test dataset of 10 valid and 10 invalid todo payloads for this schema: valid ones exercise the boundaries and varied characters (unicode, special characters), each invalid one breaks a clearly identifiable rule (including missing fields). Must be correct against the schema.", ["data-schema.md"]),
 "08_flaky": ("Diagnose why this Playwright test is flaky using the code and failure log as evidence, and give a concrete corrected test that removes the flakiness.", ["flaky.spec.ts", "flaky.log"]),
 "09_test_plan": ("Write a realistic test plan for this release scope: 1 week, 1 QA engineer. Scope, ranked risks, what to test how (manual/automated), a schedule that fits the time, measurable exit criteria.", ["requirement.md"]),
 "10_load_script": ("Write a k6 load script for this journey: 50 VUs for 5 minutes, thresholds p95 < 800 ms and error rate < 1%, random 1-3 s think time, status checks. Must run as-is.", ["load-journey.md"]),
 "11_security": ("Write a security test checklist for this specific app (OWASP Top 10 2021 as the frame): concrete tests with steps/inputs and expected safe results, relevant to the app's actual attack surface rather than generic items that cannot apply.", ["requirement.md"]),
 "12_locator_fix": ("Replace the failing locator with one stable locator for the target element on the current page (HTML and aria snapshot given). Any mainstream framework syntax is acceptable; judge whether it uniquely and stably matches the target on the real page.", ["old-locator.md", "dom.html", "locators.md"]),
}

def judge_input(task, root):
    spec, files = NEUTRAL[task]
    parts = [f"TASK: {spec}"] + [f"<input file=\"{f}\">\n{(root/'inputs'/f).read_text()}\n</input>" for f in files]
    return "\n\n".join(parts)

"""Build the README images from the committed results (no AI images): .github/assets/banner.svg and results.svg.
Usage: python eval/make_readme_assets.py"""
import csv, pathlib, statistics as st
from html import escape
ROOT = pathlib.Path(__file__).resolve().parent.parent
A = ROOT/".github"/"assets"; A.mkdir(parents=True, exist_ok=True)
NAMES = {"01_test_cases": "01 Test cases", "02_ui_script": "02 Playwright UI test", "03_api_tests": "03 API tests", "04_test_review": "04 Test review",
         "05_bug_report": "05 Bug report", "06_edge_cases": "06 Edge cases", "07_test_data": "07 Test data", "08_flaky": "08 Flaky test diagnosis",
         "09_test_plan": "09 Test plan", "10_load_script": "10 k6 load script", "11_security": "11 Security checks", "12_locator_fix": "12 Locator fix",
         "m01_exploratory_charters": "m01 Exploratory charters", "m02_regression_checklist": "m02 Regression checklist",
         "m03_run_summary": "m03 Run summary report", "m04_ac_review": "m04 AC review"}
rows = list(csv.DictReader(open(ROOT/"results"/"results_quality.csv"))) + list(csv.DictReader(open(ROOT/"results"/"manual_quality.csv")))
rows = [r for r in rows if r["task"] in NAMES]
f = lambda x: float(x) if x not in ("", None) else None
def m(t, v, k): return st.mean([f(r[k]) for r in rows if r["task"] == t and r["variant"] == v and f(r[k]) is not None])
W, L, TOP, RH = 900, 250, 118, 34
H = TOP + RH*len(NAMES) + 60
x0, x1 = L, W - 70; sx = lambda s: x0 + (x1 - x0)*s/10
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">',
     f'<rect width="{W}" height="{H}" rx="12" fill="#0d1117"/>',
     '<text x="24" y="40" font-size="22" font-weight="700" fill="#f0f6fc">Blind judge score, popular original vs ours (1-10, mean of 3 runs)</text>',
     '<text x="24" y="66" font-size="15" fill="#9da7b3">16 prompts · 48 blind pairs · ours wins 40, original 3, ties 5 · judge 5.85 → 7.77 · checks 0.865 → 0.961 · output tokens −47%</text>',
     f'<rect x="24" y="84" width="14" height="14" rx="3" fill="#6e7681"/><text x="44" y="96" font-size="13" fill="#c9d1d9">Popular original</text>',
     f'<rect x="170" y="84" width="14" height="14" rx="3" fill="#2f81f7"/><text x="190" y="96" font-size="13" fill="#c9d1d9">Ours (optimized)</text>']
for g in range(0, 11, 2):
    o.append(f'<line x1="{sx(g):.1f}" y1="{TOP-6}" x2="{sx(g):.1f}" y2="{H-48}" stroke="#30363d" stroke-width="1"/>')
    o.append(f'<text x="{sx(g):.1f}" y="{H-30}" font-size="12" fill="#9da7b3" text-anchor="middle">{g}</text>')
for i, (t, name) in enumerate(NAMES.items()):
    y = TOP + i*RH; jo, jz = m(t, "original", "judge_score"), m(t, "optimized", "judge_score")
    o.append(f'<text x="{L-12}" y="{y+19}" font-size="13" fill="#c9d1d9" text-anchor="end">{escape(name)}</text>')
    o.append(f'<rect x="{x0}" y="{y+3}" width="{sx(jo)-x0:.1f}" height="11" rx="2" fill="#6e7681"/>')
    o.append(f'<rect x="{x0}" y="{y+16}" width="{sx(jz)-x0:.1f}" height="11" rx="2" fill="#2f81f7"/>')
    o.append(f'<text x="{sx(jo)+6:.1f}" y="{y+13}" font-size="11" fill="#9da7b3">{jo:.1f}</text>')
    o.append(f'<text x="{sx(jz)+6:.1f}" y="{y+26}" font-size="11" fill="#79c0ff">{jz:.1f}</text>')
o.append(f'<text x="24" y="{H-10}" font-size="12" fill="#6e7681">From results/*_quality.csv · claude-haiku-5-5 generation, claude-sonnet-5-5 blind judge</text>')
o.append('</svg>')
(A/"results.svg").write_text("\n".join(o))
banner = '''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="320" viewBox="0 0 1280 320" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">
<defs><clipPath id="c"><rect width="1280" height="320" rx="24"/></clipPath></defs>
<g clip-path="url(#c)"><rect width="1280" height="320" fill="#0d1117"/><rect width="1280" height="8" fill="#2f81f7"/></g>
<text x="640" y="150" font-size="84" font-weight="800" fill="#f0f6fc" text-anchor="middle">QA Prompt Pack</text>
<text x="640" y="210" font-size="30" fill="#9da7b3" text-anchor="middle">33 AI prompts for testers, tested like code</text>
<text x="640" y="262" font-size="22" fill="#2f81f7" text-anchor="middle">Manual 11 · Automation 6 · Industry 16</text>
</svg>'''
(A/"banner.svg").write_text(banner)
print("wrote", A/"results.svg", A/"banner.svg")

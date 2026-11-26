"""Aggregate results/results_quality.csv -> results/summary.md (+ GitHub job summary if available)."""
import csv, os, pathlib, statistics as st, json
ROOT = pathlib.Path(__file__).resolve().parent.parent
rows = list(csv.DictReader(open(ROOT/"results"/"results_quality.csv")))
def f(x):
    try: return float(x)
    except Exception: return None
def mean(xs): xs = [x for x in xs if x is not None]; return round(st.mean(xs), 3) if xs else None
tasks = sorted({r["task"] for r in rows}); out = []; verdicts = {}
out.append("| Prompt | Quality orig | Quality opt | Judge orig | Judge opt | Judge wins (opt/orig/tie) | Total tokens orig | Total tokens opt | Token change | Verdict |")
out.append("|---|---|---|---|---|---|---|---|---|---|")
tot = {"o": 0, "z": 0}
for t in tasks:
    o = [r for r in rows if r["task"] == t and r["variant"] == "original"]; z = [r for r in rows if r["task"] == t and r["variant"] == "optimized"]
    qo, qz = mean([f(r["quality"]) for r in o]), mean([f(r["quality"]) for r in z])
    jo, jz = mean([f(r.get("judge_score")) for r in o]), mean([f(r.get("judge_score")) for r in z])
    to, tz = mean([f(r["total_tokens"]) for r in o]), mean([f(r["total_tokens"]) for r in z])
    tot["o"] += to or 0; tot["z"] += tz or 0
    w = [r.get("judge_winner") for r in z]
    wins = f"{w.count('optimized')}/{w.count('original')}/{w.count('tie')}"
    lost = (qz is not None and qo is not None and qz < qo - 0.05) or (jz is not None and jo is not None and jz < jo - 0.5)
    v = "LOST" if lost else ("beat" if (qz or 0) > (qo or 0) + 0.05 or (jz or 0) > (jo or 0) + 0.5 else "matched")
    verdicts[t] = v
    chg = f"{100*(tz-to)/to:+.0f}%" if to and tz else ""
    out.append(f"| {t} | {qo} | {qz} | {jo} | {jz} | {wins} | {to:.0f} | {tz:.0f} | {chg} | {v} |")
out.append(f"\nTotal mean tokens per call set (input+output, sum over prompts): original {tot['o']:.0f}, optimized {tot['z']:.0f} ({100*(tot['z']-tot['o'])/tot['o']:+.1f}%)")
model = rows[0].get("model") if rows else ""
md = f"## Eval results ({len(rows)} outputs, model {model})\nQuality = deterministic rubric 0-1 (mean of runs). Judge = blind pairwise 1-10.\n\n" + "\n".join(out) + "\n"
(ROOT/"results"/"summary.md").write_text(md); (ROOT/"results"/"verdicts.json").write_text(json.dumps(verdicts, indent=1))
if os.environ.get("GITHUB_STEP_SUMMARY"): open(os.environ["GITHUB_STEP_SUMMARY"], "a").write(md)
print(md)

"""Aggregate quality CSV -> summary markdown (+ GitHub job summary if available).
Usage: python summarize.py [--suite general|industry]
"""
import argparse, csv, os, pathlib, statistics as st, json
ROOT = pathlib.Path(__file__).resolve().parent.parent

def f(x):
    try: return float(x)
    except Exception: return None
def mean(xs):
    xs = [x for x in xs if x is not None]; return round(st.mean(xs), 3) if xs else None

def summarize_general(rows, out_md, out_json):
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
    if tot["o"]:
        out.append(f"\nTotal mean tokens per call set (input+output, sum over prompts): original {tot['o']:.0f}, optimized {tot['z']:.0f} ({100*(tot['z']-tot['o'])/tot['o']:+.1f}%)")
    model = rows[0].get("model") if rows else ""
    md = f"## Eval results ({len(rows)} outputs, model {model})\nQuality = deterministic rubric 0-1 (mean of runs). Judge = blind pairwise 1-10.\n\n" + "\n".join(out) + "\n"
    out_md.write_text(md); out_json.write_text(json.dumps(verdicts, indent=1))
    return md

def summarize_industry(rows, out_md, out_json):
    tasks = sorted({r["task"] for r in rows}); out = []; verdicts = {}
    out.append("| Prompt | Quality (checks) | Judge | Consistency | Total tokens | Verdict |")
    out.append("|---|---|---|---|---|---|")
    for t in tasks:
        z = [r for r in rows if r["task"] == t]
        qz = mean([f(r["quality"]) for r in z])
        jz = mean([f(r.get("judge_score")) for r in z])
        cz = mean([f(r.get("judge_consistency")) for r in z])
        tz = mean([f(r["total_tokens"]) for r in z])
        lost = (qz is not None and qz < 0.6) or (jz is not None and jz < 6)
        v = "REVIEW" if lost else ("strong" if (qz or 0) >= 0.8 or (jz or 0) >= 8 else "ok")
        verdicts[t] = v
        out.append(f"| {t} | {qz} | {jz} | {cz} | {tz if tz is not None else ''} | {v} |")
    model = rows[0].get("model") if rows else ""
    md = (f"## Industry eval results ({len(rows)} outputs, model {model})\n"
          "Quality = deterministic domain checks 0-1 (mean of runs). "
          "Judge = absolute rubric 1-10 (one call per prompt across runs). "
          "No original/optimized pair unless a credited public original exists.\n\n" + "\n".join(out) + "\n")
    out_md.write_text(md); out_json.write_text(json.dumps(verdicts, indent=1))
    return md

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--suite", choices=["general","industry"], default="general")
    a = ap.parse_args()
    if a.suite == "industry":
        csv_path = ROOT/"results"/"industry_quality.csv"
        out_md = ROOT/"results"/"industry_summary.md"
        out_json = ROOT/"results"/"industry_verdicts.json"
    else:
        csv_path = ROOT/"results"/"results_quality.csv"
        out_md = ROOT/"results"/"summary.md"
        out_json = ROOT/"results"/"verdicts.json"
    if not csv_path.exists():
        print(f"no {csv_path}; skip"); return
    rows = list(csv.DictReader(open(csv_path)))
    if not rows:
        print(f"{csv_path} empty; skip"); return
    md = summarize_industry(rows, out_md, out_json) if a.suite == "industry" else summarize_general(rows, out_md, out_json)
    if os.environ.get("GITHUB_STEP_SUMMARY"): open(os.environ["GITHUB_STEP_SUMMARY"], "a").write(md)
    print(md)

if __name__ == "__main__":
    main()

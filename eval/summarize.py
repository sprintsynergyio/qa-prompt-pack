"""Aggregate quality CSV -> summary markdown (+ GitHub job summary if available).
Usage: python summarize.py [--suite general|industry]"""
import argparse, csv, os, pathlib, statistics as st, json, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT/"eval"))
from providers import price, spend
PASS = 0.8  # a run passes the deterministic checks at quality >= 0.8

def f(x):
    try: return float(x)
    except Exception: return None
def mean(xs, nd=3):
    xs = [x for x in xs if x is not None]; return round(st.mean(xs), nd) if xs else None
def cost(rows):
    return sum((f(r.get("prompt_tokens")) or 0)/1e6*price(r.get("model", ""))[0] + (f(r.get("completion_tokens")) or 0)/1e6*price(r.get("model", ""))[1] for r in rows)
def fmt(x): return "" if x is None else (f"{x:.0f}" if isinstance(x, float) and x >= 100 else str(x))

def summarize_general(rows, out_md, out_json):
    tasks = sorted({r["task"] for r in rows}); out = []; verdicts = {}
    out.append("| Prompt | Quality orig | Quality opt | Judge orig | Judge opt | Judge wins opt/orig/tie | Tokens in orig→opt | Tokens out orig→opt | Gen cost orig→opt (USD) | Verdict |")
    out.append("|---|---|---|---|---|---|---|---|---|---|")
    agg = {"qo": [], "qz": [], "jo": [], "jz": [], "w": [], "io": 0, "iz": 0, "oo": 0, "oz": 0, "co": 0, "cz": 0}
    for t in tasks:
        o = [r for r in rows if r["task"] == t and r["variant"] == "original"]; z = [r for r in rows if r["task"] == t and r["variant"] == "optimized"]
        qo, qz = mean([f(r["quality"]) for r in o]), mean([f(r["quality"]) for r in z])
        jo, jz = mean([f(r.get("judge_score")) for r in o], 2), mean([f(r.get("judge_score")) for r in z], 2)
        io, iz = mean([f(r.get("prompt_tokens")) for r in o], 0), mean([f(r.get("prompt_tokens")) for r in z], 0)
        oo, oz = mean([f(r.get("completion_tokens")) for r in o], 0), mean([f(r.get("completion_tokens")) for r in z], 0)
        co, cz = cost(o), cost(z)
        w = [r.get("judge_winner") for r in z]; agg["w"] += w
        for k, v in (("qo", qo), ("qz", qz), ("jo", jo), ("jz", jz)):
            if v is not None: agg[k].append(v)
        agg["io"] += io or 0; agg["iz"] += iz or 0; agg["oo"] += oo or 0; agg["oz"] += oz or 0; agg["co"] += co; agg["cz"] += cz
        wins = f"{w.count('optimized')}/{w.count('original')}/{w.count('tie')}"
        lost = (qz is not None and qo is not None and qz < qo - 0.05) or (jz is not None and jo is not None and jz < jo - 0.5)
        v = "LOST" if lost else ("beat" if (qz or 0) > (qo or 0) + 0.05 or (jz or 0) > (jo or 0) + 0.5 else "matched")
        verdicts[t] = v
        out.append(f"| {t} | {qo} | {qz} | {jo} | {jz} | {wins} | {fmt(io)}→{fmt(iz)} | {fmt(oo)}→{fmt(oz)} | {co:.4f}→{cz:.4f} | {v} |")
    W = agg["w"]
    out.append(f"\n**Overall:** quality {mean(agg['qo'])} → {mean(agg['qz'])}; judge {mean(agg['jo'],2)} → {mean(agg['jz'],2)}; "
               f"judge wins optimized {W.count('optimized')}, original {W.count('original')}, tie {W.count('tie')} (of {len(W)}). "
               f"Mean tokens per call summed over prompts: in {agg['io']:.0f} → {agg['iz']:.0f}, out {agg['oo']:.0f} → {agg['oz']:.0f} "
               f"({100*((agg['iz']+agg['oz'])-(agg['io']+agg['oo']))/max(1,(agg['io']+agg['oo'])):+.1f}% total). "
               f"Generation cost {agg['co']:.4f} → {agg['cz']:.4f} USD. Verdicts: " + ", ".join(f"{k} {list(verdicts.values()).count(k)}" for k in ("beat", "matched", "LOST")))
    models = sorted({r.get("model", "") for r in rows})
    md = (f"## General suite ({len(rows)} outputs; generation {', '.join(models)}; blind pairwise judge)\n"
          "Quality = deterministic checks 0-1 (mean of runs). Judge = blind, order-randomized pairwise 1-10. Token counts from API usage.\n\n" + "\n".join(out) + "\n")
    out_md.write_text(md); out_json.write_text(json.dumps(verdicts, indent=1))
    return md

def summarize_industry(rows, out_md, out_json):
    tasks = sorted({r["task"] for r in rows}); out = []; verdicts = {}; passes = []
    out.append("| Prompt | Quality (checks) | Runs passing (≥0.8) | Judge | Consistency | Tokens in | Tokens out | Gen cost (USD) | Verdict |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for t in tasks:
        z = [r for r in rows if r["task"] == t]
        qz = mean([f(r["quality"]) for r in z]); jz = mean([f(r.get("judge_score")) for r in z], 2); cz = mean([f(r.get("judge_consistency")) for r in z], 2)
        p = [int((f(r["quality"]) or 0) >= PASS) for r in z]; passes += p
        lost = (qz is not None and qz < 0.6) or (jz is not None and jz < 6) or sum(p) < len(p)
        v = "REVIEW" if lost else ("strong" if (qz or 0) >= 0.9 and (jz or 0) >= 8 else "ok")
        verdicts[t] = v
        out.append(f"| {t} | {qz} | {sum(p)}/{len(p)} | {jz} | {cz} | {fmt(mean([f(r.get('prompt_tokens')) for r in z],0))} | {fmt(mean([f(r.get('completion_tokens')) for r in z],0))} | {cost(z):.4f} | {v} |")
    out.append(f"\n**Pass rate:** {sum(passes)}/{len(passes)} runs ({100*sum(passes)/max(1,len(passes)):.0f}%); prompts with all runs passing: "
               f"{sum(1 for t in tasks if verdicts[t] != 'REVIEW')}/{len(tasks)}. Mean quality {mean([f(r['quality']) for r in rows])}, mean judge {mean([f(r.get('judge_score')) for r in rows],2)}.")
    models = sorted({r.get("model", "") for r in rows})
    md = (f"## Industry suite ({len(rows)} outputs; generation {', '.join(models)}; absolute judge)\n"
          "Quality = deterministic domain checks 0-1 (mean of runs). Judge = absolute rubric 1-10 (one call per prompt across its runs).\n\n" + "\n".join(out) + "\n")
    out_md.write_text(md); out_json.write_text(json.dumps(verdicts, indent=1))
    return md

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--suite", choices=["general", "industry"], default="general"); a = ap.parse_args()
    ind = a.suite == "industry"
    csv_path = ROOT/"results"/("industry_quality.csv" if ind else "results_quality.csv")
    out_md = ROOT/"results"/("industry_summary.md" if ind else "summary.md")
    out_json = ROOT/"results"/("industry_verdicts.json" if ind else "verdicts.json")
    if not csv_path.exists(): print(f"no {csv_path}; skip"); return
    rows = list(csv.DictReader(open(csv_path)))
    if not rows: print(f"{csv_path} empty; skip"); return
    md = summarize_industry(rows, out_md, out_json) if ind else summarize_general(rows, out_md, out_json)
    s = spend(); md += f"\nTotal API spend recorded in {os.environ.get('SPEND_FILE', 'runs/spend.json')}: ${s['usd']:.4f} over {s['calls']} calls.\n"
    out_md.write_text(md)
    if os.environ.get("GITHUB_STEP_SUMMARY"): open(os.environ["GITHUB_STEP_SUMMARY"], "a").write(md)
    print(md)

if __name__ == "__main__": main()

"""Count prompt tokens (tiktoken o200k_base = GPT-4o/4.1/5 family; cl100k_base = GPT-4/3.5).
instr_* = instruction tokens only (shared input removed); input_* = full rendered prompt actually sent.
Usage: python count_tokens.py [--suite general|manual|industry|all]
"""
import argparse, csv, pathlib, tiktoken
from build_prompts import render, instructions_only, ROOT
enc = {n: tiktoken.get_encoding(n) for n in ("o200k_base","cl100k_base")}

def pair_row(task, orig_text, opt_text):
    r = {"task": task}
    for kind, t in (("orig", orig_text), ("opt", opt_text)):
        if t is None:
            r[f"instr_{kind}"] = ""
            r[f"input_{kind}"] = ""
            r[f"input_{kind}_cl100k"] = ""
            continue
        r[f"instr_{kind}"] = len(enc["o200k_base"].encode(instructions_only(t)))
        r[f"input_{kind}"] = len(enc["o200k_base"].encode(render(t)))
        r[f"input_{kind}_cl100k"] = len(enc["cl100k_base"].encode(render(t)))
    if orig_text:
        r["instr_saving_pct"] = round(100*(1-r["instr_opt"]/r["instr_orig"]),1) if r["instr_orig"] else ""
        r["input_saving_pct"] = round(100*(1-r["input_opt"]/r["input_orig"]),1) if r["input_orig"] else ""
    else:
        r["instr_saving_pct"] = ""
        r["input_saving_pct"] = ""
    return r

def write_csv(path, rows):
    # numeric totals only where both sides exist
    numeric = [k for k in rows[0] if k!="task" and not k.endswith("pct") and all(isinstance(r[k], int) for r in rows)]
    if numeric:
        tot = {k: sum(r[k] for r in rows) for k in numeric}
        tot["task"]="TOTAL"
        for k in rows[0]:
            if k not in tot:
                tot[k] = ""
        if isinstance(rows[0].get("instr_orig"), int) and rows[0].get("instr_orig") != "":
            if all(isinstance(r.get("instr_orig"), int) and r["instr_orig"] for r in rows):
                tot["instr_saving_pct"]=round(100*(1-tot["instr_opt"]/tot["instr_orig"]),1)
                tot["input_saving_pct"]=round(100*(1-tot["input_opt"]/tot["input_orig"]),1)
        rows = rows + [tot]
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    for r in rows:
        if r.get("instr_orig") != "" and r.get("instr_orig") is not None and r.get("instr_orig") != "":
            try:
                print(f"{r['task']:28} instr {r['instr_orig']:4}->{r['instr_opt']:4} (saved {r['instr_saving_pct']}%)  full input {r['input_orig']:4}->{r['input_opt']:4} (saved {r['input_saving_pct']}%)")
            except Exception:
                print(f"{r['task']:28} instr opt={r['instr_opt']}  full input opt={r['input_opt']}")
        else:
            print(f"{r['task']:28} instr {r['instr_opt']}  full input {r['input_opt']}")

def general_rows():
    rows=[]
    for o in sorted((ROOT/"prompts"/"original").glob("*.txt")):
        z = ROOT/"prompts"/"optimized"/o.name
        rows.append(pair_row(o.stem, o.read_text(), z.read_text()))
    return rows

def industry_rows():
    rows=[]
    for z in sorted((ROOT/"prompts"/"industry").glob("*.txt")):
        orig = ROOT/"prompts"/"industry-original"/z.name
        rows.append(pair_row(z.stem, orig.read_text() if orig.exists() else None, z.read_text()))
    return rows

def manual_rows():
    rows=[]
    for z in sorted((ROOT/"prompts"/"manual"/"optimized").glob("*.txt")):
        orig = ROOT/"prompts"/"manual"/"original"/z.name
        rows.append(pair_row(z.stem, orig.read_text() if orig.exists() else None, z.read_text()))
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--suite", choices=["general","manual","industry","all"], default="all")
    a = ap.parse_args()
    if a.suite in ("general","all"):
        write_csv(ROOT/"results"/"token_counts.csv", general_rows())
    if a.suite in ("manual","all"):
        write_csv(ROOT/"results"/"manual_token_counts.csv", manual_rows())
    if a.suite in ("industry","all"):
        write_csv(ROOT/"results"/"industry_token_counts.csv", industry_rows())

if __name__ == "__main__":
    main()

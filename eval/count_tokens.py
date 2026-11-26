"""Count prompt tokens (tiktoken o200k_base = GPT-4o/4.1/5 family; cl100k_base = GPT-4/3.5) for original vs optimized.
instr_* = instruction tokens only (shared input removed); input_* = full rendered prompt actually sent."""
import csv, pathlib, tiktoken
from build_prompts import render, instructions_only, ROOT
enc = {n: tiktoken.get_encoding(n) for n in ("o200k_base","cl100k_base")}
rows=[]
for o in sorted((ROOT/"prompts"/"original").glob("*.txt")):
    z = ROOT/"prompts"/"optimized"/o.name
    r = {"task": o.stem}
    for kind,p in (("orig",o),("opt",z)):
        t = p.read_text()
        r[f"instr_{kind}"] = len(enc["o200k_base"].encode(instructions_only(t)))
        r[f"input_{kind}"] = len(enc["o200k_base"].encode(render(t)))
        r[f"input_{kind}_cl100k"] = len(enc["cl100k_base"].encode(render(t)))
    r["instr_saving_pct"] = round(100*(1-r["instr_opt"]/r["instr_orig"]),1)
    r["input_saving_pct"] = round(100*(1-r["input_opt"]/r["input_orig"]),1)
    rows.append(r)
tot = {k: sum(r[k] for r in rows) for k in rows[0] if k!="task" and not k.endswith("pct")}
tot["task"]="TOTAL"; tot["instr_saving_pct"]=round(100*(1-tot["instr_opt"]/tot["instr_orig"]),1); tot["input_saving_pct"]=round(100*(1-tot["input_opt"]/tot["input_orig"]),1)
rows.append(tot)
with open(ROOT/"results"/"token_counts.csv","w",newline="") as f:
    w=csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for r in rows: print(f"{r['task']:16} instr {r['instr_orig']:4}->{r['instr_opt']:4} (saved {r["instr_saving_pct"]}%)  full input {r['input_orig']:4}->{r['input_opt']:4} (saved {r["input_saving_pct"]}%)")

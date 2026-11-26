"""Harness self-test: score hand-written reference/bad outputs. NOT model results."""
import json
from run_eval import score, ROOT
for f in sorted((ROOT/"eval"/"selftest").glob("*.md")):
    task = f.name.split(".")[0]
    print(f.name, json.dumps(score(task, f.read_text(), "selftest_"+f.stem.replace(".","_"))))

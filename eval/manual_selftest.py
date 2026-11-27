"""Scorer self-test for the manual prompts: reference answers must score >= 0.8, planted-bad answers < 0.5. No API key needed."""
import pathlib, sys, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from manual_score import score_manual
D = pathlib.Path(__file__).resolve().parent/"selftest"/"manual"; fails = 0; n = 0
for f in sorted(D.glob("*.md")):
    task, kind = f.stem.split(".")[0], f.stem.split(".")[1]; s = score_manual(task, f.read_text()); n += 1
    ok = s["quality"] >= 0.8 if kind == "ref" else s["quality"] < 0.5
    fails += not ok; print(("ok  " if ok else "FAIL"), f.name, json.dumps(s))
print(f"{n} fixtures, {fails} failed"); sys.exit(1 if fails else 0)

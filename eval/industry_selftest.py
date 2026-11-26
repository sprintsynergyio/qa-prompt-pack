#!/usr/bin/env python3
"""Assert deterministic industry scorers on hand-written fixtures. No model calls."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from industry_score import score_industry

ST = Path(__file__).resolve().parent / "selftest"
failed = 0
checked = 0
for f in sorted(ST.glob("*.md")):
    if f.name[:2] not in ("hc", "fi", "ec", "sa"):
        continue
    task = f.name.split(".")[0]
    s = score_industry(task, f.read_text(), "selftest_" + f.stem.replace(".", "_"))
    q = s["quality"]
    kind = "bad" if ".bad." in f.name else "ref"
    ok = (q >= 0.8) if kind == "ref" else (q < 0.5)
    checked += 1
    status = "OK" if ok else "FAIL"
    print(f"{status} {f.name} quality={q} { {k: s[k] for k in s if k != 'quality'} }")
    if not ok:
        failed += 1
print(f"{checked} fixtures, {failed} failed")
sys.exit(1 if failed else 0)

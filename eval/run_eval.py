#!/usr/bin/env python3
"""A/B evaluation of original vs optimized QA prompts on GitHub Models (free tier).
Usage: .venv/bin/python run_eval.py [--runs 3] [--model openai/gpt-4o-mini] [--judge openai/gpt-4.1] [--tasks 01,02] [--variants original,optimized] [--score-only] [--no-judge]
Token is read from GITHUB_TOKEN and never printed. Outputs: runs/outputs/*, results_quality.csv, results_summary.json"""
import argparse, csv, json, os, pathlib, random, re, subprocess, sys, time, urllib.request, urllib.error
import tiktoken
from build_prompts import render, ROOT
ENC = tiktoken.get_encoding("o200k_base")
OUT = ROOT/"runs"/"outputs"; OUT.mkdir(parents=True, exist_ok=True)
HARNESS = ROOT/"eval"/"harness"; GEN = HARNESS/"gen"; GEN.mkdir(exist_ok=True)
URL = os.environ.get("MODELS_URL", "https://models.github.ai/inference/chat/completions")
LOG = ROOT/"runs"/"ratelimit.log"
_last = [0.0]

def call(model, prompt, max_tokens=3000, min_gap=6.0, temperature=0.2):
    """POST with pacing (min_gap s between calls) and backoff on 429/5xx. Never logs the token."""
    body = json.dumps({"model": model, "temperature": temperature, "max_tokens": max_tokens,
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    hdr = {"Authorization": "Bearer " + os.environ["GITHUB_TOKEN"], "Content-Type": "application/json", "Accept": "application/json"}
    for attempt in range(8):
        wait = _last[0] + min_gap - time.time()
        if wait > 0: time.sleep(wait)
        _last[0] = time.time()
        try:
            t = time.time(); resp = urllib.request.urlopen(urllib.request.Request(URL, body, hdr), timeout=240); raw = resp.read()
            if "json" not in (resp.headers.get("Content-Type") or ""):
                raise RuntimeError(f"endpoint returned non-JSON ({resp.headers.get('Content-Type')}: {raw[:40]!r}); network/proxy is not reaching GitHub Models")
            d = json.loads(raw)
            u = d.get("usage", {})
            return d["choices"][0]["message"]["content"] or "", u.get("prompt_tokens"), u.get("completion_tokens"), round(time.time()-t, 1)
        except urllib.error.HTTPError as e:
            ra = e.headers.get("retry-after"); msg = e.read()[:200].decode(errors="ignore")
            with open(LOG, "a") as f: f.write(f"{time.strftime('%H:%M:%S')} {model} HTTP {e.code} retry-after={ra} {msg}\n")
            if e.code in (429, 500, 502, 503, 504):
                s = min(float(ra) if ra and ra.isdigit() else 15 * 2**attempt, 900)
                if s > 900 or (ra and ra.isdigit() and int(ra) > 3600): raise RuntimeError(f"daily limit hit (retry-after {ra}s)")
                print(f"  backoff {s:.0f}s (HTTP {e.code})", flush=True); time.sleep(s); continue
            raise
        except (urllib.error.URLError, TimeoutError) as e:
            with open(LOG, "a") as f: f.write(f"{time.strftime('%H:%M:%S')} {model} network {e}\n")
            time.sleep(15 * 2**attempt)
    raise RuntimeError("gave up after retries")

# ---------- deterministic scorers (each returns quality 0..1 plus details) ----------
def code_block(text, langs=("ts", "typescript")):
    m = re.findall(r"```(?:%s)\s*\n(.*?)```" % "|".join(langs), text, re.S)
    return max(m, key=len) if m else None

def run_code(tag, code):
    f = GEN/f"{tag}.spec.ts"; f.write_text(code)
    cfg = GEN/f"{tag}.tsconfig.json"
    cfg.write_text(json.dumps({"compilerOptions": {"target": "ES2022", "module": "esnext", "strict": False, "noEmit": True, "skipLibCheck": True,
                               "types": ["node"], "moduleResolution": "bundler"}, "files": [f.name]}))
    tsc = subprocess.run(["npx", "tsc", "-p", str(cfg)], cwd=HARNESS, capture_output=True, text=True)
    try:
        pw = subprocess.run(["npx", "playwright", "test", f"gen/{f.name}", "--reporter=json", "--retries=0", "--workers=2"], cwd=HARNESS,
                            capture_output=True, text=True, env={**os.environ, "TEST_DIR": "./gen"}, timeout=300)
        st = json.loads(pw.stdout).get("stats", {})
    except Exception: st = {}
    p, fl, sk = st.get("expected", 0), st.get("unexpected", 0) + st.get("flaky", 0), st.get("skipped", 0)
    banned = len(re.findall(r"waitForTimeout|nth-child|xpath=|//\w+\[|\.nth\(|page\.(?:click|fill|press|check)\(", code))
    return {"compiles": int(tsc.returncode == 0), "tests_passed": p, "tests_failed": fl, "tests_skipped": sk,
            "assertions": len(re.findall(r"\bexpect(?:\.soft)?\(", code)), "banned_patterns": banned,
            "_code_q": 0.3*int(tsc.returncode == 0) + 0.5*(p/(p+fl) if p+fl else 0) + 0.2*int(banned == 0)}

def cover(text, groups):
    t = text.lower(); hit = [g for g, rx in groups.items() if re.search(rx, t)]
    return len(hit)/len(groups), ";".join(sorted(set(groups)-set(hit)))

REQ = {"add": r"add|enter", "trim": r"trim|leading|trailing", "empty": r"empty|whitespace|blank", "toggle": r"complete|toggle|check",
  "toggle_all": r"mark all|toggle all|toggle-all", "counter": r"items? left", "singular": r"1 item left", "filters": r"active", "hash": r"#/",
  "edit": r"double", "escape": r"escape|\besc\b", "empty_edit": r"(empty|clear|blank).{0,60}(edit|title).{0,80}(delet|remov)|(delet|remov).{0,80}(empty|blank)",
  "delete": r"delete|destroy|×|remove", "clear_completed": r"clear completed", "persist": r"reload|refresh|localstorage|persist"}
EDGE = {"empty": r"empty|\"\"|''", "whitespace": r"space|whitespace|\\t|\btab", "trim": r"trim", "long": r"\d{3,} ?(chars|characters)|long|very long",
  "emoji": r"emoji|[\U0001F300-\U0001FAFF]", "rtl": r"rtl|arabic|hebrew|[\u0590-\u06ff]", "html": r"<script|<img|onerror|<b>|&lt;script",
  "edit": r"edit|double", "newline": r"newline|\\n|line break"}
IRREL_AUTH = r"\b(idor|auth(entication|orization)? bypass|login|password|permission|session|jwt|sql injection|sqli|ssrf|brute|rate limit)"
SEC_REL = {"xss": r"xss|<script|onerror|html injection", "storage": r"localstorage|local storage", "csp": r"\bcsp\b|content.security", "frame": r"clickjack|x-frame|frame-ancestors",
  "deps": r"vulnerable (and outdated )?components|dependenc|outdated|sri|subresource", "url": r"hash|url|#/"}
REVIEW = {"sleep": r"waitfortimeout|hard wait|fixed wait", "bad_selector": r"#new-todo", "nth": r"nth-child|index|position", "weak_assert": r"tobetruthy|count\s*>\s*0|weak",
  "name": r"test name|vague|'todo'|\"todo\""}

def q_round(x): return round(x, 3)

def score(task, text, tag):
    s = {"out_tokens_tiktoken": len(ENC.encode(text))}; q = 0.0
    if task in ("02_ui_script", "03_api_tests", "04_test_review", "08_flaky"):
        code = code_block(text); s["has_code"] = int(bool(code))
        cq = 0
        if code: r = run_code(tag, code); cq = r.pop("_code_q"); s.update(r)
        if task == "04_test_review":
            c, miss = cover(re.sub(r"```.*?```", "", text, flags=re.S), REVIEW); s["issues_found"] = round(c, 2); s["missing"] = miss; q = 0.5*cq + 0.5*c
        elif task == "08_flaky":
            s["cause_isolation"] = int(bool(re.search(r"isolat|shared state|depend(s|ent|ency) on (the )?(previous|other|first)|order|fresh (browser )?context|new (browser )?context|each test (gets|runs|has)|independent", text, re.I)))
            q = 0.5*cq + 0.5*s["cause_isolation"]
        else: q = cq
    elif task == "01_test_cases":
        c, miss = cover(text, REQ); s["coverage"] = round(c, 2); s["missing"] = miss
        s["irrelevant_mentions"] = len(re.findall(IRREL_AUTH, text.lower())); q = 0.8*c + 0.2*int(s["irrelevant_mentions"] == 0)
    elif task == "06_edge_cases":
        c, miss = cover(text, EDGE); s["coverage"] = round(c, 2); s["missing"] = miss; q = c
    elif task == "05_bug_report":
        fields = ["title", "severity", "environment", "steps", "expected", "actual"]
        s["fields_present"] = sum(bool(re.search(rf"^\W*{f}", text, re.I | re.M)) for f in fields)
        env = re.search(r"environment\W*(.*?)(?:\n\s*\n|\n\W*steps)", text, re.I | re.S)
        s["invented_versions"] = int(bool(env and re.search(r"(chrome|macos|os x|safari)\s*(version\s*)?v?\d{2,}", env.group(1), re.I)))
        s["marks_unknown"] = int(bool(re.search(r"unknown|not specified|unconfirmed|step missing", text, re.I)))
        q = 0.4*s["fields_present"]/6 + 0.3*(1-s["invented_versions"]) + 0.3*s["marks_unknown"]
    elif task == "07_test_data":
        m = re.search(r"\[.*\]", text, re.S); s["json_ok"] = 0; arr = []
        try: arr = json.loads(m.group(0)); s["json_ok"] = 1
        except Exception: pass
        def valid(p):
            return (isinstance(p, dict) and set(p) == {"userId", "title", "completed"} and type(p.get("userId")) is int and 1 <= p["userId"] <= 10
                    and isinstance(p.get("title"), str) and 1 <= len(p["title"]) <= 200 and p["title"] == p["title"].strip() and type(p.get("completed")) is bool)
        items = [(a["payload"], a.get("valid")) if isinstance(a, dict) and "payload" in a else (a, None) for a in arr]
        s["items"] = len(items); s["actually_valid"] = sum(valid(p) for p, _ in items)
        lab = [(valid(p) == v) for p, v in items if v is not None]; s["label_accuracy"] = round(sum(lab)/len(lab), 2) if lab else ""
        q = 0.4*s["json_ok"] + 0.6*max(0, 1 - abs(s["actually_valid"]-10)/10) * (1 if s["items"] >= 18 else s["items"]/20)
    elif task == "09_test_plan":
        c, miss = cover(text, REQ); s["coverage"] = round(c, 2); s["missing"] = miss
        s["exit_criteria"] = int(bool(re.search(r"exit criteria", text, re.I)))
        s["measurable_exit"] = int(bool(re.search(r"exit criteria.{0,600}(\d+ ?%|\b0\b|zero|all (critical|p1|high))", text, re.I | re.S)))
        q = 0.6*c + 0.2*s["exit_criteria"] + 0.2*s["measurable_exit"]
    elif task == "10_load_script":
        code = code_block(text, ("js", "javascript")) or ""; s["has_code"] = int(bool(code))
        f = GEN/f"{tag}.js"; f.write_text(code)
        ins = subprocess.run([str(pathlib.Path(os.environ.get("K6_BIN", "k6"))), "inspect", str(f)], capture_output=True, text=True)
        s["k6_parses"] = int(ins.returncode == 0)
        o = {}
        try: o = json.loads(ins.stdout)
        except Exception: pass
        th = json.dumps(o.get("thresholds", {})); dur = json.dumps(o)
        s["vus_duration_ok"] = int(("50" in json.dumps(o.get("vus", ""))+json.dumps(o.get("stages", ""))+json.dumps(o.get("scenarios", ""))) and "5m" in dur)
        s["thresholds_ok"] = int(bool(re.search(r"p\(95\)\s*<\s*800", th)) and bool(re.search(r"rate\s*<\s*0\.01", th)))
        s["think_time"] = int(bool(re.search(r"sleep\(\s*(Math\.random\(\)\s*\*\s*2\s*\+\s*1|1\s*\+\s*Math\.random\(\)\s*\*\s*2|randomIntBetween\(1,\s*3\)|Math\.floor)", code)))
        s["checks"] = int("check(" in code)
        q = 0.3*s["k6_parses"] + 0.2*s["vus_duration_ok"] + 0.3*s["thresholds_ok"] + 0.1*s["think_time"] + 0.1*s["checks"]
    elif task == "11_security":
        c, miss = cover(text, SEC_REL); s["relevant_coverage"] = round(c, 2); s["missing"] = miss
        rows = [l for l in text.splitlines() if l.strip().startswith("|") and not re.match(r"^\|[\s\-:|]+\|$", l.strip())][1:]
        irr = [l for l in rows if re.search(IRREL_AUTH, l.lower()) and not re.search(r"n/?a|not applicable|skip", l.lower())]
        s["rows"] = len(rows); s["irrelevant_rows"] = len(irr)
        q = 0.6*c + 0.4*(1 - (len(irr)/len(rows) if rows else 1))
    elif task == "12_locator_fix":
        line = re.sub(r"^```\w*|```$", "", text.strip(), flags=re.M).strip().splitlines()
        expr = next((l.strip().strip("`").rstrip(";") for l in line if l.strip()), "")
        expr = re.sub(r"^(driver\.find_element\(By\.CSS_SELECTOR,\s*)?[\"']?(.*?)[\"']?\)?$", r"\2", expr) if not expr.startswith("page.") else expr
        r = subprocess.run(["node", "check_locator.mjs", expr], cwd=HARNESS, capture_output=True, text=True, timeout=120)
        try: res = json.loads(r.stdout.strip().splitlines()[-1])
        except Exception: res = {"correct": False, "error": r.stderr[-200:]}
        s["locator"] = expr[:120]; s["locator_correct"] = int(bool(res.get("correct"))); s["match_count"] = res.get("count", "")
        s["stable"] = int(not re.search(r"nth-child|:nth|\.nth\(|xpath|//", expr))
        q = 0.8*s["locator_correct"] + 0.2*s["stable"]
    s["quality"] = q_round(q)
    return s

JUDGE_PROMPT = """You are grading two answers to the same software-testing request. Judge only usefulness to a QA engineer: correctness against the input, coverage, no invented facts, directly usable output, and concision (penalize padding).
<request_input>
{inp}
</request_input>
<answer_A>
{a}
</answer_A>
<answer_B>
{b}
</answer_B>
Return only JSON: {{"A": <1-10>, "B": <1-10>, "winner": "A"|"B"|"tie", "reason": "<15 words"}}"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=3); ap.add_argument("--model", default="openai/gpt-4o-mini"); ap.add_argument("--judge", default="openai/gpt-4.1")
    ap.add_argument("--tasks"); ap.add_argument("--variants", default="original,optimized"); ap.add_argument("--score-only", action="store_true"); ap.add_argument("--no-judge", action="store_true")
    a = ap.parse_args()
    if not os.environ.get("GITHUB_TOKEN"): sys.exit("GITHUB_TOKEN not set")
    tasks = sorted(p.stem for p in (ROOT/"prompts"/"original").glob("*.txt"))
    if a.tasks: tasks = [t for t in tasks if t[:2] in a.tasks.split(",")]
    variants = a.variants.split(",")
    errors = []
    if not a.score_only:
        for t in tasks:
            for v in variants:
                prompt = render((ROOT/"prompts"/v/f"{t}.txt").read_text())
                for i in range(1, a.runs+1):
                    try: text, pin, pout, dt = call(a.model, prompt)
                    except Exception as e:
                        print(f"GENERATION FAILED {t} {v} run{i}: {e}", flush=True); errors.append(f"{t}.{v}.{i}: {e}"); continue
                    (OUT/f"{t}.{v}.{i}.md").write_text(text)
                    (OUT/f"{t}.{v}.{i}.meta.json").write_text(json.dumps({"model": a.model, "prompt_tokens": pin, "completion_tokens": pout, "seconds": dt}))
                    print(f"{t} {v} run{i}: in={pin} out={pout} {dt}s", flush=True)
    # judge (blind, randomized order) for each run pair
    jpath = ROOT/"runs"/"judge.json"; judge = json.loads(jpath.read_text()) if jpath.exists() else {}
    if not a.no_judge:
        for t in tasks:
            inp = render((ROOT/"prompts"/"original"/f"{t}.txt").read_text())
            if t[:2] in ("02", "04", "12"):  # give the judge the real page so it can check selectors
                inp += "\n\n[Judge reference: real page aria snapshot]\n" + (ROOT/"inputs"/"locators.md").read_text()
            for i in range(1, a.runs+1):
                key = f"{t}.{i}"; fo, fz = OUT/f"{t}.original.{i}.md", OUT/f"{t}.optimized.{i}.md"
                if not (fo.exists() and fz.exists()): continue
                stamp = f"{fo.stat().st_mtime:.0f}-{fz.stat().st_mtime:.0f}"
                if key in judge and judge[key].get("stamp") == stamp: continue
                flip = random.Random(key+stamp).random() < 0.5
                A, B = (fz, fo) if flip else (fo, fz)
                try: txt, *_ = call(a.judge, JUDGE_PROMPT.format(inp=inp, a=A.read_text()[:12000], b=B.read_text()[:12000]), max_tokens=200, min_gap=8.0, temperature=0)
                except Exception as e:
                    print(f"JUDGE FAILED {key}: {e}", flush=True); errors.append(f"judge {key}: {e}"); continue
                try: j = json.loads(re.search(r"\{.*\}", txt, re.S).group(0))
                except Exception: j = {"A": None, "B": None, "winner": "parse_error"}
                opt_s, org_s = (j.get("A"), j.get("B")) if flip else (j.get("B"), j.get("A"))
                w = j.get("winner"); win = {"A": "optimized" if flip else "original", "B": "original" if flip else "optimized"}.get(w, w)
                judge[key] = {"stamp": stamp, "optimized": opt_s, "original": org_s, "winner": win, "reason": j.get("reason")}
                jpath.write_text(json.dumps(judge, indent=1)); print(f"judge {key}: {win} ({org_s} vs {opt_s})", flush=True)
    rows = []
    for f in sorted(OUT.glob("*.md")):
        t, v, i = f.stem.split(".")
        meta = json.loads((OUT/f"{f.stem}.meta.json").read_text())
        jd = judge.get(f"{t}.{i}", {})
        rows.append({"task": t, "variant": v, "run": int(i), **meta, "total_tokens": (meta["prompt_tokens"] or 0)+(meta["completion_tokens"] or 0),
                     "judge_score": jd.get(v), "judge_winner": jd.get("winner"), **score(t, f.read_text(), f"{t}_{v}_{i}")})
    keys = []; [keys.append(k) for r in rows for k in r if k not in keys]
    with open(ROOT/"results"/"results_quality.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)
    (ROOT/"results"/"errors.txt").write_text("\n".join(errors))
    print(f"wrote results_quality.csv ({len(rows)} rows); {len(errors)} errors")
if __name__ == "__main__": main()

#!/usr/bin/env python3
"""A/B evaluation of original vs optimized QA prompts (general suite) and absolute scoring of industry prompts.
Providers (eval/providers.py): Anthropic Messages API for claude-* models (ANTHROPIC_API_KEY), or any OpenAI-compatible
endpoint (MODELS_URL + MODELS_API_KEY). GitHub Models was retired on 30 Jul 2026. Keys come from env only and are never printed.
Spend is tracked from API usage (SPEND_FILE, default runs/spend.json) and capped by BUDGET_USD (default 3).
Usage: python eval/run_eval.py [--suite general|manual|industry] [--runs 3] [--model claude-haiku-5-5] [--judge claude-sonnet-5-5] [--tasks 01,02 or hc01,fi02] [--variants original,optimized] [--score-only] [--no-judge]
Outputs: runs/outputs/* or runs/industry/*, results/results_quality.csv or results/industry_quality.csv"""
import argparse, csv, json, os, pathlib, random, re, subprocess, sys, time, urllib.request, urllib.error
import tiktoken
from build_prompts import render, ROOT
from providers import call, spend
from industry_score import is_industry, score_industry
from manual_score import is_manual, score_manual
from judge_tasks import judge_input, NEUTRAL
ENC = tiktoken.get_encoding("o200k_base")
OUT = ROOT/"runs"/"outputs"; OUT.mkdir(parents=True, exist_ok=True)
HARNESS = ROOT/"eval"/"harness"; GEN = HARNESS/"gen"; GEN.mkdir(exist_ok=True)

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
    if is_industry(task) or is_manual(task):
        d = score_manual(task, text, tag) if is_manual(task) else score_industry(task, text, tag)
        q = d.pop("quality", 0.0)
        s.update(d)
        s["quality"] = q_round(q)
        return s
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
        tl = [len(p["title"]) for p, _ in items if isinstance(p, dict) and isinstance(p.get("title"), str)]
        s["max_len_boundary"] = int(200 in tl and 201 in tl)  # LLMs often miscount "200-char" strings
        q = 0.3*s["json_ok"] + 0.5*max(0, 1 - abs(s["actually_valid"]-10)/10) * (1 if s["items"] >= 18 else s["items"]/20) + 0.2*s["max_len_boundary"]
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

ABSOLUTE_JUDGE_PROMPT = """You are grading up to three answers to the same software-testing request. Judge only usefulness to a QA engineer: correctness against the input, coverage, no invented facts, directly usable output, and concision (penalize padding). Score typical quality (the median run) and consistency across runs.
<request_input>
{inp}
</request_input>
<answers>
{answers}
</answers>
Return only JSON: {{"score": <1-10>, "consistency": <1-10>, "reason": "<15 words"}}"""

def list_tasks(suite):
    if suite == "manual":
        return sorted(p.stem for p in (ROOT/"prompts"/"manual"/"optimized").glob("*.txt"))
    if suite == "industry":
        return sorted(p.stem for p in (ROOT/"prompts"/"industry").glob("*.txt"))
    return sorted(p.stem for p in (ROOT/"prompts"/"original").glob("*.txt"))

def prompt_file(task, variant, suite):
    if suite == "manual":
        return ROOT/"prompts"/"manual"/variant/f"{task}.txt"
    if suite == "industry":
        if variant == "original":
            return ROOT/"prompts"/"industry-original"/f"{task}.txt"
        return ROOT/"prompts"/"industry"/f"{task}.txt"
    return ROOT/"prompts"/variant/f"{task}.txt"

def select_tasks(all_tasks, tasks_arg):
    if not tasks_arg:
        return all_tasks
    wanted = [w.strip() for w in tasks_arg.split(",") if w.strip()]
    chosen = [t for t in all_tasks if t in wanted or t[:2] in wanted or any(t.startswith(w) for w in wanted)]
    return chosen

def suite_paths(suite):
    if suite == "manual":
        out = ROOT/"runs"/"manual"/"outputs"; out.mkdir(parents=True, exist_ok=True)
        return out, ROOT/"runs"/"manual"/"judge.json", ROOT/"results"/"manual_quality.csv"
    if suite == "industry":
        out = ROOT/"runs"/"industry"/"outputs"; out.mkdir(parents=True, exist_ok=True)
        return out, ROOT/"runs"/"industry"/"judge.json", ROOT/"results"/"industry_quality.csv"
    out = ROOT/"runs"/"outputs"; out.mkdir(parents=True, exist_ok=True)
    return out, ROOT/"runs"/"judge.json", ROOT/"results"/"results_quality.csv"

def parse_judge(txt, need):
    """First JSON object in the reply containing the needed keys (tolerates fences, prose, braces in reasons)."""
    dec = json.JSONDecoder()
    for m in re.finditer(r"\{", txt):
        try: obj, _ = dec.raw_decode(txt[m.start():])
        except ValueError: continue
        if isinstance(obj, dict) and all(k in obj for k in need): return obj
    (ROOT/"runs").mkdir(exist_ok=True); (ROOT/"runs"/"judge_parse_errors.log").open("a").write(txt[:2000] + "\n----\n")
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=3); ap.add_argument("--model", default=os.environ.get("EVAL_MODEL", "claude-haiku-5-5")); ap.add_argument("--judge", default=os.environ.get("EVAL_JUDGE", "claude-sonnet-5-5"))
    ap.add_argument("--suite", choices=["general", "manual", "industry"], default="general")
    ap.add_argument("--tasks"); ap.add_argument("--variants", default=""); ap.add_argument("--score-only", action="store_true"); ap.add_argument("--no-judge", action="store_true")
    ap.add_argument("--judge-spec", choices=["neutral", "original"], default="neutral", help="general pairwise judge input. neutral: neutral task + inputs (default); original: the original prompt")
    a = ap.parse_args()
    if not a.score_only and not any(os.environ.get(k) for k in ("ANTHROPIC_API_KEY", "MODELS_API_KEY", "GITHUB_TOKEN")): sys.exit("set ANTHROPIC_API_KEY (claude-* models) or MODELS_URL + MODELS_API_KEY")
    tasks = select_tasks(list_tasks(a.suite), a.tasks)
    if a.variants:
        variants = a.variants.split(",")
    elif a.suite == "industry":
        # A/B only when a credited public original exists for that task.
        variants = ["optimized"]
    else:
        variants = ["original", "optimized"]
    out_dir, jpath, csv_path = suite_paths(a.suite)
    if a.suite == "general" and a.judge_spec == "original": jpath = jpath.with_name("judge_original_spec.json")
    errors = []
    if not a.score_only:
        for t in tasks:
            vs = list(variants)
            if a.suite in ("industry", "manual") and "original" in vs and not prompt_file(t, "original", a.suite).exists():
                vs = [v for v in vs if v != "original"]
            for v in vs:
                prompt = render(prompt_file(t, v, a.suite).read_text())
                for i in range(1, a.runs+1):
                    try: text, pin, pout, dt = call(a.model, prompt, max_tokens=8000)
                    except Exception as e:
                        print(f"GENERATION FAILED {t} {v} run{i}: {e}", flush=True); errors.append(f"{t}.{v}.{i}: {e}"); continue
                    (out_dir/f"{t}.{v}.{i}.md").write_text(text)
                    (out_dir/f"{t}.{v}.{i}.meta.json").write_text(json.dumps({"model": a.model, "prompt_tokens": pin, "completion_tokens": pout, "seconds": dt}))
                    print(f"{t} {v} run{i}: in={pin} out={pout} {dt}s", flush=True)
    judge = json.loads(jpath.read_text()) if jpath.exists() else {}
    if not a.no_judge:
        for t in tasks:
            orig_p = prompt_file(t, "original", a.suite)
            src = orig_p if orig_p.exists() else prompt_file(t, "optimized", a.suite)
            if a.suite in ("general", "manual") and a.judge_spec == "neutral" and t in NEUTRAL: inp = judge_input(t, ROOT)
            else:
                inp = render(src.read_text())
                if a.suite == "general" and t[:2] in ("02", "04", "12"):  # give the judge the real page so it can check selectors
                    inp += "\n\n[Judge reference: real page aria snapshot]\n" + (ROOT/"inputs"/"locators.md").read_text()
            has_pair = all((out_dir/f"{t}.original.{i}.md").exists() and (out_dir/f"{t}.optimized.{i}.md").exists() for i in range(1, a.runs+1))
            if has_pair:
                for i in range(1, a.runs+1):
                    key = f"{t}.{i}"; fo, fz = out_dir/f"{t}.original.{i}.md", out_dir/f"{t}.optimized.{i}.md"
                    stamp = f"{fo.stat().st_mtime:.0f}-{fz.stat().st_mtime:.0f}"
                    if key in judge and judge[key].get("stamp") == stamp: continue
                    flip = random.Random(key+stamp).random() < 0.5
                    A, B = (fz, fo) if flip else (fo, fz)
                    try: txt, *_ = call(a.judge, JUDGE_PROMPT.format(inp=inp, a=A.read_text()[:40000], b=B.read_text()[:40000]), max_tokens=1500, min_gap=2.0, temperature=0)
                    except Exception as e:
                        print(f"JUDGE FAILED {key}: {e}", flush=True); errors.append(f"judge {key}: {e}"); continue
                    j = parse_judge(txt, ("A", "B")) or {"A": None, "B": None, "winner": "parse_error"}
                    opt_s, org_s = (j.get("A"), j.get("B")) if flip else (j.get("B"), j.get("A"))
                    w = j.get("winner"); win = {"A": "optimized" if flip else "original", "B": "original" if flip else "optimized"}.get(w, w)
                    judge[key] = {"stamp": stamp, "optimized": opt_s, "original": org_s, "winner": win, "reason": j.get("reason")}
                    jpath.parent.mkdir(parents=True, exist_ok=True)
                    jpath.write_text(json.dumps(judge, indent=1)); print(f"judge {key}: {win} ({org_s} vs {opt_s})", flush=True)
            else:
                # Absolute judge: one call per prompt (all runs), to stay within the free-tier daily cap.
                runs = [out_dir/f"{t}.optimized.{i}.md" for i in range(1, a.runs+1) if (out_dir/f"{t}.optimized.{i}.md").exists()]
                if not runs:
                    continue
                key = t
                stamp = "-".join(f"{f.stat().st_mtime:.0f}" for f in runs)
                if key in judge and judge[key].get("stamp") == stamp: continue
                answers = "\n\n".join(f"<run n=\"{i+1}\">\n{f.read_text()[:20000]}\n</run>" for i, f in enumerate(runs))
                try: txt, *_ = call(a.judge, ABSOLUTE_JUDGE_PROMPT.format(inp=inp[:20000], answers=answers[:60000]), max_tokens=1500, min_gap=2.0, temperature=0)
                except Exception as e:
                    print(f"JUDGE FAILED {key}: {e}", flush=True); errors.append(f"judge {key}: {e}"); continue
                j = parse_judge(txt, ("score",)) or {"score": None, "consistency": None, "reason": "parse_error"}
                judge[key] = {"stamp": stamp, "score": j.get("score"), "consistency": j.get("consistency"), "reason": j.get("reason"), "mode": "absolute"}
                jpath.parent.mkdir(parents=True, exist_ok=True)
                jpath.write_text(json.dumps(judge, indent=1)); print(f"judge {key}: score={j.get('score')} consistency={j.get('consistency')}", flush=True)
    rows = []
    for f in sorted(out_dir.glob("*.md")):
        parts = f.stem.split(".")
        if len(parts) != 3: continue
        t, v, i = parts
        if t not in tasks: continue
        meta_f = out_dir/f"{f.stem}.meta.json"
        meta = json.loads(meta_f.read_text()) if meta_f.exists() else {"model": "", "prompt_tokens": 0, "completion_tokens": 0, "seconds": 0}
        jd = judge.get(f"{t}.{i}", {}) or judge.get(t, {})
        rows.append({"task": t, "variant": v, "run": int(i), "suite": a.suite, **meta, "total_tokens": (meta.get("prompt_tokens") or 0)+(meta.get("completion_tokens") or 0),
                     "judge_score": jd.get(v, jd.get("score")), "judge_winner": jd.get("winner"), "judge_consistency": jd.get("consistency"),
                     **score(t, f.read_text(), f"{t}_{v}_{i}")})
    keys = []; [keys.append(k) for r in rows for k in r if k not in keys]
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)
    err_path = ROOT/"results"/{"industry": "industry_errors.txt", "manual": "manual_errors.txt"}.get(a.suite, "errors.txt")
    err_path.write_text("\n".join(errors))
    print(f"spend so far: ${spend()['usd']:.4f}"); print(f"wrote {csv_path} ({len(rows)} rows); {len(errors)} errors")
    gen_fail = [e for e in errors if not e.startswith("judge")]
    if not a.score_only and not rows:
        sys.exit(f"FAILED: all {len(gen_fail)} generation calls failed; first error: {gen_fail[0] if gen_fail else 'n/a'}")
if __name__ == "__main__": main()

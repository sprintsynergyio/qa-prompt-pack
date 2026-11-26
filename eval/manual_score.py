"""Deterministic checks for the manual-testing prompts (m01-m05). Inputs are synthetic (inputs/m-*.md).
Each scorer returns a dict with "quality" in 0-1 plus the evidence fields."""
import re

def is_manual(task): return bool(re.match(r"m\d\d_", task))

def _cover(text, groups):
    hits = {k: bool(re.search(p, text, re.I | re.S)) for k, p in groups.items()}
    return sum(hits.values()) / len(hits), ";".join(k for k, v in hits.items() if not v)

def _q(x): return round(max(0.0, min(1.0, x)), 3)

def score_m01(text):
    s = {}
    groups = {
        "expiry": r"30.?min|expir", "single_use": r"single.?use|reuse|re-use|used twice|second (time|click)|already used",
        "invalidate_old": r"older link|previous link|earlier link|old link|invalidat", "rate_limit": r"rate.?limit|4th|fourth|try again later|3 (reset )?(emails|requests)",
        "enumeration": r"enumerat|unregistered|non.?existent|not registered|unknown (email|address)|whether (or not )?(the|an) (email|account)",
        "password_rules": r"\b12\b|\b64\b|last 3|last three|previous passwords|password history", "sessions": r"other sessions|signed out|sign(s|ed)? (out|off)|log(s|ged)? out",
        "case": r"case.?insensitiv|upper.?case|mixed.?case|capital", "scanner": r"scanner|safe.?links?|outlook|link preview|prefetch",
        "sso": r"\bsso\b|company login", "queue": r"queue|provider|delay(ed)? email|email delivery",
    }
    c, miss = _cover(text, groups); s["coverage"] = round(c, 2); s["missing"] = miss
    n = len(re.findall(r"\bexplore\b", text, re.I)); s["charters_explore"] = n
    s["timebox"] = int(bool(re.search(r"\d+\s?(min|minutes|mins)\b|\d+\s?h(ou)?rs?\b", text, re.I)))
    s["oracle"] = int(bool(re.search(r"oracle|you'?ll know|how to (tell|know)|red flag|signals? of (a )?(bug|problem)|it'?s wrong", text, re.I)))
    s["notes_template"] = int(bool(re.search(r"tried.{0,400}(saw|observ).{0,400}bugs?.{0,400}question", text, re.I | re.S)))
    inv = [l for l in text.splitlines() if re.search(r"\bsms\b|security question|text message", l, re.I) and not re.search(r"\bnot?\b|out of scope|isn'?t|doesn'?t|absent|no such", l, re.I)]
    s["invented"] = len(inv)
    q = 0.6*c + 0.1*int(3 <= n <= 12) + 0.1*s["timebox"] + 0.1*s["oracle"] + 0.1*s["notes_template"] - 0.1*s["invented"]
    s["quality"] = _q(q); return s

def score_m02(text):
    s = {}
    ids = ["CHG-101", "CHG-102", "CHG-103", "CHG-104", "CHG-105"]
    found = [i for i in ids if i in text]; s["changes_mapped"] = len(found); s["changes_missing"] = ";".join(i for i in ids if i not in found)
    m = [l for l in text.splitlines() if "CHG-106" in l]
    s["skip_106"] = int(bool(m) and any(re.search(r"skip|no (user|runtime|functional)|not (tested|needed|required)|out of scope|docs?.only|n/?a|none", l, re.I) for l in m)) if m else 0
    smoke = {"signin": r"sign.?in|log.?in", "checkout": r"checkout", "history": r"order history"}
    sc, smiss = _cover(text, smoke); s["smoke"] = round(sc, 2)
    s["priorities"] = int(all(re.search(p, text) for p in (r"\bP0\b", r"\bP1\b")))
    spec = {"tax": r"order total|per order|order.level|half.?up", "phone": r"e\.?164|\+1\d|phone", "page24": r"\b24\b", "dates": r"midnight|time ?zone|utc"}
    pc, pmiss = _cover(text, spec); s["specifics"] = round(pc, 2); s["specific_missing"] = pmiss
    inv = sorted(set(re.findall(r"CHG-\d+", text)) - set(ids) - {"CHG-106"}); s["invented_ids"] = ";".join(inv)
    q = 0.5*len(found)/5 + 0.1*s["skip_106"] + 0.15*sc + 0.1*s["priorities"] + 0.15*pc - 0.1*len(inv)
    s["quality"] = _q(q); return s

def score_m03(text):
    s = {}
    t = text.replace(",", "")
    nums = {"planned_120": r"\b120\b", "executed_106": r"\b106\b", "passed_98": r"\b98\b", "failed_8": r"fail\w*\D{0,40}\b8\b|\b8\b\D{0,15}fail|\b98 ?\+ ?8\b", "blocked_6": r"block\w*\D{0,40}\b6\b|\b6\b\D{0,15}block", "notrun_8": r"not (run|executed)\D{0,40}\b8\b|\b8\b\D{0,15}not (run|executed)"}
    c, miss = _cover(t, nums); s["counts"] = round(c, 2); s["counts_missing"] = miss
    s["pass_rate_92_5"] = int(bool(re.search(r"92\.[45]\d?\s?%", t)))
    s["flags_lead_note"] = int(bool(re.search(r"112", t)) and bool(re.search(r"mismatch|do(es)?n'?t match|do(es)? not match|discrepan|incorrect|inaccurate|overstat|includes? (the )?blocked|counted blocked|not 112|wrong|inconsisten|correct(ed|ion)", t, re.I)))
    s["no_go"] = int(bool(re.search(r"no.?go|not ready|do not (ship|release)|don'?t (ship|release)|hold (the )?release|block(s|ing)? (the )?release", t, re.I)))
    s["open_defects"] = sum(int(b in t) for b in ("BUG-311", "BUG-315"))
    inv = sorted(set(re.findall(r"BUG-\d+", t)) - {"BUG-311", "BUG-312", "BUG-315", "BUG-318", "BUG-320"}); s["invented_ids"] = ";".join(inv)
    q = 0.35*c + 0.15*s["pass_rate_92_5"] + 0.15*s["flags_lead_note"] + 0.2*s["no_go"] + 0.15*s["open_defects"]/2 - 0.1*len(inv)
    s["quality"] = _q(q); return s

def score_m04(text):
    s = {}
    groups = {
        "contradiction": r"immediate\w*.{0,400}(15|batch)|(15.?min\w*|batch\w*).{0,400}immediate", "appropriate": r"appropriate", "fast": r"\bfast\b",
        "gracefully": r"graceful", "who_user": r"which user|who (is|are|counts as) (the )?user|\"user\"|'user'|user vs\.? (account )?owner|(admins?|members?|billing contact)",
        "channel": r"e-?mail|in.?app|push|channel|banner", "ac5_rules": r"consecutive|in a row|within (what|a|which)|resume|unpause|reactivat|retr(y|ies)",
        "permission": r"non.?owner|not the owner|other (roles|users)|permission|unauthori[sz]ed|access",
    }
    c, miss = _cover(text, groups); s["coverage"] = round(c, 2); s["missing"] = miss
    s["gwt"] = int(bool(re.search(r"\bgiven\b.{0,300}\bwhen\b.{0,300}\bthen\b", text, re.I | re.S)))
    s["verdicts"] = int(bool(re.search(r"not testable|needs revision", text, re.I)))
    s["questions"] = int(bool(re.search(r"question", text, re.I)))
    q = 0.7*c + 0.1*s["gwt"] + 0.1*s["verdicts"] + 0.1*s["questions"]
    s["quality"] = _q(q); return s

TOP = [("chrome", "windows"), ("safari", "ios"), ("chrome", "android"), ("safari", "mac"), ("edge", "windows"), ("samsung", "android")]
def score_m05(text):
    s = {}
    rows = [l for l in text.splitlines() if l.strip().startswith("|") and re.search(r"chrome|safari|edge|firefox|samsung|ie ?11|internet explorer|opera", l, re.I)
            and not re.search(r"excluded|not supported|unsupported", l, re.I)]
    low = [l.lower() for l in rows]
    hit = [b for b, o in TOP if any(b in l and o in l for l in low)]; s["top6_covered"] = len(hit)
    s["ie_tested"] = int(any(re.search(r"\bie ?11\b|internet explorer", l) for l in low))
    s["opera_tested"] = int(any("opera" in l for l in low))
    s["ios_real"] = int(any("safari" in l and "ios" in l and re.search(r"\breal\b|iphone", l) for l in low))
    hrs = 0.0
    for l in low:
        if re.search(r"\bfull\b", l): hrs += 3
        elif re.search(r"\bsmoke\b", l): hrs += 0.75
    s["hours_from_rows"] = hrs; s["within_budget"] = int(0 < hrs <= 16)
    s["excluded_section"] = int(bool(re.search(r"exclud", text, re.I)) and bool(re.search(r"ie ?11|internet explorer", text, re.I)))
    q = 0.4*len(hit)/6 + 0.1*(1 - s["ie_tested"]) + 0.05*(1 - s["opera_tested"]) + 0.05*s["excluded_section"] + 0.15*s["ios_real"] + 0.25*s["within_budget"]
    s["quality"] = _q(q); return s

SCORERS = {"m01_exploratory_charters": score_m01, "m02_regression_checklist": score_m02, "m03_run_summary": score_m03, "m04_ac_review": score_m04, "m05_browser_matrix": score_m05}
def score_manual(task, text, tag=""):
    return SCORERS[task](text)

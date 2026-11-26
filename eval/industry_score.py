"""Deterministic domain checks for industry prompts. Returns a dict including quality 0..1."""
import json, os, pathlib, re, subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
GEN = ROOT / "eval" / "harness" / "gen"
GEN.mkdir(parents=True, exist_ok=True)

TEST_CARDS = {
    "4242424242424242", "4012888888881881", "4111111111111111",
    "4000000000000002", "4000000000009995", "4000000000009987",
    "4000000000000069", "4000000000003220", "4000000000000127",
    "5555555555554444", "5105105105105100",
    "378282246310005", "371449635398431",
    "6011111111111117", "3056930009020004", "3566002020360505",
    "6200000000000005",
}
FORBIDDEN_SSN = {"078-05-1120", "078051120"}

ROUND_EXPECTED = {
    "usd_half_up_125": "10.13",
    "usd_half_up_124": "10.12",
    "usd_half_up_135": "10.14",
    "usd_half_even_125": "10.12",
    "usd_half_even_135": "10.14",
    "jpy_half_up_1234": "123",
    "jpy_half_up_1235": "124",
    "bhd_half_up_12345": "1.235",
    "usd_split_10_three": "3.33,3.33,3.34",
    "usd_fee_2pct_10_01": "0.20",
}

PRICE_EXPECTED = {
    "save10_ny": {"discount": "8.00", "tax": "7.22", "total": "94.72", "outcome": "applied"},
    "fiveoff_ny": {"discount": "5.00", "tax": "7.47", "total": "97.97", "outcome": "applied"},
    "below_min": {"discount": "0.00", "tax": "1.28", "total": "16.78", "outcome": "rejected_min_spend"},
    "expired": {"discount": "0.00", "tax": "7.88", "total": "103.38", "outcome": "rejected_expired"},
    "stack_rejected": {"discount": "8.00", "tax": "7.22", "total": "94.72", "outcome": "rejected_stack"},
    "stack_ok": {"discount": "12.38", "tax": "6.86", "total": "89.98", "outcome": "applied"},
    "oregon_save10": {"discount": "8.00", "tax": "0.00", "total": "87.50", "outcome": "applied"},
}

PRORATION_EXPECTED = {
    "upgrade_day10": {"credit": "26.67", "new_charge": "53.33", "due": "26.66", "access": "pro", "webhook_effect": "applied"},
    "downgrade_day10": {"credit": "53.33", "new_charge": "26.67", "due": "-26.66", "access": "starter", "webhook_effect": "applied"},
    "cancel_day10": {"credit": "0.00", "new_charge": "0.00", "due": "0.00", "access": "starter_until_period_end", "webhook_effect": "applied"},
    "upgrade_day0": {"credit": "40.00", "new_charge": "80.00", "due": "40.00", "access": "pro", "webhook_effect": "applied"},
    "upgrade_day29": {"credit": "1.33", "new_charge": "2.67", "due": "1.34", "access": "pro", "webhook_effect": "applied"},
    "webhook_replay": {"credit": "26.67", "new_charge": "53.33", "due": "26.66", "access": "pro", "webhook_effect": "ignored_duplicate"},
}

ROLES = ["owner", "admin", "editor", "viewer", "billing_manager"]
ACTIONS = {
    "settings.write": {"owner", "admin"},
    "members.invite": {"owner", "admin"},
    "members.remove": {"owner"},
    "billing.view": {"owner", "admin", "billing_manager"},
    "billing.change_plan": {"owner", "billing_manager"},
    "project.create": {"owner", "admin", "editor"},
    "project.edit": {"owner", "admin", "editor"},
    "project.delete": {"owner", "admin"},
    "project.view": {"owner", "admin", "editor", "viewer", "billing_manager"},
    "audit.export": {"owner", "admin"},
    "tenant.delete": {"owner"},
}

LEAKS = {"LEAK-01", "LEAK-02", "LEAK-03", "LEAK-04"}
CLEANS = {"CLEAN-01", "CLEAN-02", "CLEAN-03"}

def is_industry(task):
    return task[:2] in ("hc", "fi", "ec", "sa")

def extract_json(text):
    fences = re.findall(r"```(?:json|JSON)?\s*\n(.*?)```", text, re.S)
    blobs = list(fences) + [text]
    for blob in blobs:
        for pat in (r"\[(?:.|\n)*\]", r"\{(?:.|\n)*\}"):
            m = re.search(pat, blob)
            if not m:
                continue
            try:
                return json.loads(m.group(0))
            except Exception:
                continue
    return None

def digits(s):
    return re.sub(r"\D", "", s or "")

def luhn_ok(n):
    if not n.isdigit() or not (13 <= len(n) <= 19):
        return False
    tot, alt = 0, False
    for ch in n[::-1]:
        d = ord(ch) - 48
        if alt:
            d *= 2
            if d > 9:
                d -= 9
        tot += d
        alt = not alt
    return tot % 10 == 0

def money(x):
    if x is None:
        return None
    if isinstance(x, bool):
        return None
    if isinstance(x, int):
        return str(x)
    if isinstance(x, float):
        s = f"{x:.3f}".rstrip("0").rstrip(".")
        return s
    s = str(x).strip().replace(" ", "")
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    return m.group(0) if m else None

def coerce_amount(gv_raw, ev):
    """Compare a got value to an expected amount string, respecting the expected scale."""
    evs = str(ev).strip()
    if "," in evs:
        return None  # caller handles lists
    if isinstance(gv_raw, list):
        return ",".join(str(x) for x in gv_raw)
    gv = money(gv_raw)
    if gv is None:
        return None
    if evs in ("0.00", "0.0", "0"):
        try:
            return "0.00" if float(gv) == 0 else gv
        except Exception:
            return gv
    if re.fullmatch(r"-?\d+\.\d{2}", evs):
        try:
            return f"{float(gv):.2f}"
        except Exception:
            return money2(gv)
    if re.fullmatch(r"-?\d+\.\d{3}", evs):
        try:
            return f"{float(gv):.3f}"
        except Exception:
            return gv
    if re.fullmatch(r"-?\d+", evs):
        try:
            f = float(gv)
            return str(int(f)) if f == int(f) else gv
        except Exception:
            return gv
    return money2(gv)

def money2(x):
    """Normalize amounts. Integers stay integers (JPY). 1 dp pads to 2. 0 becomes 0.00."""
    s = money(x)
    if s is None:
        return None
    if s in ("0", "0.0", "0.00", "-0", "-0.0", "-0.00"):
        return "0.00"
    if re.fullmatch(r"-?\d+", s):
        return s
    if re.fullmatch(r"-?\d+\.\d{1}", s):
        return s + "0"
    return s

def find_cards(text):
    bad = []
    # groups of 13-19 digits with optional spaces/dashes
    for m in re.finditer(r"\b(?:\d[ \-]?){13,19}\b", text):
        n = digits(m.group(0))
        if 13 <= len(n) <= 19 and luhn_ok(n) and n not in TEST_CARDS:
            bad.append(n)
    return bad

def ssn_area_ok(area):
    try:
        a = int(area)
    except Exception:
        return False
    return a == 0 or a == 666 or 900 <= a <= 999

def find_forbidden_ssn(text):
    hits = []
    for m in re.finditer(r"\b(\d{3})-(\d{2})-(\d{4})\b", text):
        raw = m.group(0)
        packed = "".join(m.groups())
        if raw in FORBIDDEN_SSN or packed in FORBIDDEN_SSN:
            hits.append(raw)
    if re.search(r"\b078051120\b", text):
        hits.append("078051120")
    return hits

def cover(text, groups):
    t = text.lower()
    hit = [g for g, rx in groups.items() if re.search(rx, t)]
    return (len(hit) / len(groups) if groups else 1.0), ";".join(sorted(set(groups) - set(hit)))

def index_by_id(items):
    out = {}
    if not isinstance(items, list):
        return out
    for it in items:
        if isinstance(it, dict):
            k = str(it.get("id") or it.get("case") or "").strip()
            if k:
                out[k] = it
    return out

def match_expected(got, expected_map, fields):
    """Return (hits, total, missing_ids, wrong)."""
    idx = index_by_id(got) if not isinstance(got, dict) else got
    # also allow list
    if isinstance(got, list):
        idx = index_by_id(got)
    hits = 0
    total = 0
    missing, wrong = [], []
    for i, exp in expected_map.items():
        for f in fields:
            total += 1
            if i not in idx:
                missing.append(i)
                break
            gv = money2(idx[i].get(f)) if f in ("discount", "tax", "total", "credit", "new_charge", "due", "expected") else (
                str(idx[i].get(f) or "").strip().lower().replace(" ", "")
            )
            ev = exp[f]
            if f in ("discount", "tax", "total", "credit", "new_charge", "due", "expected"):
                evn = money2(ev)
                # special split case
                if f == "expected" and "," in str(ev):
                    graw = str(idx[i].get(f) or "").replace(" ", "").replace("[", "").replace("]", "")
                    evn = ev.replace(" ", "")
                    ok = evn in graw or graw == evn
                else:
                    ok = gv == evn or (gv and evn and gv.lstrip("+-") == evn.lstrip("+-") and (f != "due" or gv == evn))
                    # due can be negative; require exact including sign
                    if f == "due":
                        ok = gv == evn
                if ok:
                    hits += 1
                else:
                    wrong.append(f"{i}.{f}:{gv}!={evn}")
            else:
                evs = str(ev).strip().lower().replace(" ", "")
                # access/outcome/webhook: allow startswith or contains
                if evs and evs in gv:
                    hits += 1
                else:
                    wrong.append(f"{i}.{f}:{gv}!={evs}")
        else:
            continue
        # if missing id, remaining fields already not counted as hits; count leftover fields
        remaining = len(fields) - 1
        total += remaining  # wait this is wrong because we already broke after adding 1 to total
    # The loop above is messy when id is missing. Recalculate more simply:
    return None  # replaced below

def score_expected_rows(got_list, expected_map, fields):
    idx = index_by_id(got_list)
    hits = 0
    total = len(expected_map) * len(fields)
    missing, wrong = [], []
    for i, exp in expected_map.items():
        if i not in idx:
            missing.append(i)
            continue
        row = idx[i]
        for f in fields:
            ev = exp[f]
            gv_raw = row.get(f)
            if f in ("discount", "tax", "total", "credit", "new_charge", "due", "expected"):
                if f == "expected" and "," in str(ev):
                    graw = str(gv_raw or "")
                    if isinstance(gv_raw, list):
                        graw = ",".join(coerce_amount(x, "0.00") or str(x) for x in gv_raw)
                    graw = graw.replace(" ", "").replace("[", "").replace("]", "")
                    ok = ev.replace(" ", "") in graw or graw == ev.replace(" ", "")
                    if ok:
                        hits += 1
                    else:
                        wrong.append(f"{i}.{f}:{graw}!={ev}")
                    continue
                evn = str(ev).strip()
                gv = coerce_amount(gv_raw, evn)
                if gv == evn or gv == money2(evn):
                    hits += 1
                else:
                    wrong.append(f"{i}.{f}:{gv}!={evn}")
            else:
                gv = str(gv_raw or "").strip().lower().replace(" ", "_").replace("-", "_")
                evs = str(ev).strip().lower().replace(" ", "_")
                if evs and gv == evs:
                    hits += 1
                else:
                    wrong.append(f"{i}.{f}:{gv}!={evs}")
    return hits, total, missing, wrong

def payload_valid_hc(p):
    if not isinstance(p, dict):
        return False
    mrn = str(p.get("mrn") or "")
    ssn = str(p.get("ssn") or "")
    phone = str(p.get("phone") or "")
    email = str(p.get("email") or "")
    dob = str(p.get("dob") or "")
    acc = str(p.get("account_no") or "")
    name = str(p.get("display_name") or "")
    addr = p.get("address") if isinstance(p.get("address"), dict) else {}
    age = p.get("age_band")
    if not re.fullmatch(r"[A-Za-z][A-Za-z \-]+", name or ""):
        return False
    if not re.fullmatch(r"SYN-\d{6}", mrn):
        return False
    m = re.fullmatch(r"(\d{3})-(\d{2})-(\d{4})", ssn)
    if not m or not ssn_area_ok(m.group(1)) or ssn == "078-05-1120":
        return False
    if not re.fullmatch(r"555-01\d{2}", phone):
        return False
    if not re.fullmatch(r"[A-Za-z0-9._%+\-]+@example\.com", email):
        return False
    if str(addr.get("city") or "") != "Testville":
        return False
    if not re.fullmatch(r"0\d{4}", str(addr.get("postal") or "")):
        return False
    if not re.fullmatch(r"(199\d|200\d|201\d|2020)-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])", dob):
        return False
    if not re.fullmatch(r"SYN-ACC-\d{4}", acc):
        return False
    if age == "90 or older":
        return True
    try:
        return 0 <= int(age) <= 88
    except Exception:
        return False

def score_hc01(text):
    s = {}
    data = extract_json(text)
    s["json_ok"] = int(isinstance(data, list))
    items = data if isinstance(data, list) else []
    s["items"] = len(items)
    actually_valid = 0
    label_ok = 0
    labelled = 0
    for it in items:
        if not isinstance(it, dict):
            continue
        p = it.get("payload") if isinstance(it.get("payload"), dict) else it
        v = payload_valid_hc(p)
        actually_valid += int(v)
        if "valid" in it:
            labelled += 1
            label_ok += int(bool(it.get("valid")) == v)
        prov = it.get("provenance") if isinstance(it.get("provenance"), dict) else (p.get("provenance") if isinstance(p.get("provenance"), dict) else {})
        # counted later
    s["actually_valid"] = actually_valid
    s["label_accuracy"] = round(label_ok / labelled, 2) if labelled else 0
    s["forbidden_ssn"] = len(find_forbidden_ssn(text))
    s["bad_cards"] = len(find_cards(text))
    # provenance present on most items
    with_prov = 0
    for it in items:
        if not isinstance(it, dict):
            continue
        prov = it.get("provenance") if isinstance(it.get("provenance"), dict) else {}
        p = it.get("payload") if isinstance(it.get("payload"), dict) else {}
        if not prov and isinstance(p.get("provenance"), dict):
            prov = p["provenance"]
        if prov.get("synthetic") is True and prov.get("seed") and prov.get("generator"):
            with_prov += 1
    s["provenance_ok"] = with_prov
    # valid-count closeness to 8, size closeness to 16
    size_q = 1 if s["items"] >= 16 else s["items"] / 16
    valid_q = max(0, 1 - abs(actually_valid - 8) / 8)
    clean = int(s["forbidden_ssn"] == 0 and s["bad_cards"] == 0)
    q = 0.25 * s["json_ok"] + 0.25 * valid_q * size_q + 0.2 * (s["label_accuracy"] or 0) + 0.15 * clean + 0.15 * (with_prov / max(s["items"], 1))
    s["quality"] = q
    return s

def score_hc02(text):
    groups = {
        "book": r"book|201|scheduled",
        "double_book": r"double.?book|slot_taken|409",
        "past": r"slot_in_past|in the past|422",
        "reschedule": r"reschedul",
        "cancel": r"cancel",
        "no_show": r"no.?show",
        "cross_patient": r"404|another patient|other patient|cross",
        "rx_create": r"prescription|201.*active|rx_id|clinician creates",
        "rx_forbidden": r"403",
        "refill": r"refill",
        "refill_soon": r"refill_too_soon|too soon",
        "allergy": r"allergy_conflict|allerg",
    }
    c, miss = cover(text, groups)
    s = {"coverage": round(c, 2), "missing": miss, "bad_cards": len(find_cards(text)), "forbidden_ssn": len(find_forbidden_ssn(text))}
    s["quality"] = 0.85 * c + 0.15 * int(s["bad_cards"] == 0 and s["forbidden_ssn"] == 0)
    return s

def score_hc03(text):
    s = {}
    data = extract_json(text)
    findings, clean = [], []
    if isinstance(data, dict):
        findings = data.get("findings") or []
        clean = data.get("clean") or []
        s["json_ok"] = 1
    else:
        s["json_ok"] = 0
        findings = [{"id": m} for m in re.findall(r"LEAK-\d+", text)]
        clean = re.findall(r"CLEAN-\d+", text)
    fids = {str(x.get("id") if isinstance(x, dict) else x) for x in findings}
    cids = {str(x) for x in clean}
    s["leaks_found"] = len(fids & LEAKS)
    s["leaks_missing"] = ";".join(sorted(LEAKS - fids))
    s["clean_ok"] = len(cids & CLEANS)
    s["clean_flagged"] = len(fids & CLEANS)
    s["invented"] = len(fids - LEAKS - CLEANS)
    rec = s["leaks_found"] / len(LEAKS)
    prec = 1 - (s["clean_flagged"] / max(len(fids), 1))
    clean_q = s["clean_ok"] / len(CLEANS)
    s["quality"] = 0.2 * s["json_ok"] + 0.4 * rec + 0.2 * prec + 0.2 * clean_q
    return s

def score_hc04(text):
    groups = {
        "skip": r"skip to main|skip link",
        "heading": r"\bh1\b|heading",
        "label": r"label",
        "keyboard": r"keyboard|tab order|\btab\b",
        "focus": r"focus",
        "error_alert": r"role.?=.?alert|error (region|announc)",
        "status": r"status message|role=.?status|appointment booked",
        "contrast": r"contrast|#c00|#222",
        "target": r"44|target size",
        "required": r"required",
    }
    c, miss = cover(text, groups)
    s = {"coverage": round(c, 2), "missing": miss}
    invented = 0
    for w in ("modal", "captcha", "video"):
        for m in re.finditer(rf"\b{w}\b", text, re.I):
            window = text[max(0, m.start()-24):m.end()].lower()
            if not re.search(r"\bno\b|without", window):
                invented = 1
    s["invented_controls"] = invented
    s["quality"] = 0.85 * c + 0.15 * int(not invented)
    return s

def score_fi01(text):
    data = extract_json(text)
    s = {"json_ok": int(isinstance(data, list))}
    hits, total, missing, wrong = score_expected_rows(data if isinstance(data, list) else [], {k: {"expected": v} for k, v in ROUND_EXPECTED.items()}, ["expected"])
    s["hits"] = hits
    s["total"] = total
    s["missing"] = ";".join(missing)
    s["wrong"] = ";".join(wrong[:8])
    s["bad_cards"] = len(find_cards(text))
    q = 0.25 * s["json_ok"] + 0.75 * (hits / total if total else 0)
    if s["bad_cards"]:
        q *= 0.7
    s["quality"] = q
    return s

def score_fi02(text):
    groups = {
        "auth": r"authoriz",
        "decline": r"402|declin",
        "capture_full": r"capture",
        "capture_partial": r"partial capture",
        "over_capture": r"over_capture|amount > authorized",
        "void": r"\bvoid",
        "use_refund": r"use_refund|void.{0,40}after capture|after capture.{0,40}refund",
        "refund_full": r"full refund",
        "refund_partial": r"partial refund",
        "over_refund": r"over_refund",
        "idempotency": r"idempotenc",
        "timeout": r"timeout",
        "webhook": r"webhook",
        "minor_units": r"minor|cents|amount_minor|integer",
    }
    c, miss = cover(text, groups)
    s = {"coverage": round(c, 2), "missing": miss, "bad_cards": 0}
    # only allow listed test cards
    s["bad_cards"] = len(find_cards(text))
    s["quality"] = 0.85 * c + 0.15 * int(s["bad_cards"] == 0)
    return s

def score_fi03(text):
    groups = {
        "at_limit": r"200000",
        "over_limit": r"200001",
        "daily": r"250000|500000",
        "channels": r"web|mobile|channel",
        "velocity": r"4 completed|5th|velocity|10 minutes",
        "cooling": r"cooling|new (beneficiary|payee)",
        "hold": r"hold_for_review",
        "refuse": r"refuse",
        "decline_card": r"4000000000000002|processor decline",
        "inclusive": r"inclusive|at-limit|at limit|succeeds",
    }
    c, miss = cover(text, groups)
    invented = int(bool(re.search(r"score weight|secret threshold|bypass the (rule|limit)", text, re.I)))
    s = {"coverage": round(c, 2), "missing": miss, "invented_internals": invented}
    s["quality"] = 0.9 * c + 0.1 * int(not invented)
    return s

def score_fi04(text):
    groups = {
        "event_id": r"event_id",
        "actor": r"actor_id",
        "amount": r"amount_minor|amount",
        "correlation": r"correlation_id",
        "occurred": r"occurred_at",
        "outcome": r"outcome",
        "immutable": r"405|immutab|cannot be (updated|deleted)|no (update|delete)",
        "forbidden": r"pan|cvv|token|forbidden|mask",
        "refuse_or_fail": r"refuse|fail",
        "channel": r"channel",
    }
    c, miss = cover(text, groups)
    s = {"coverage": round(c, 2), "missing": miss, "bad_cards": len(find_cards(text))}
    s["quality"] = 0.85 * c + 0.15 * int(s["bad_cards"] == 0)
    return s

def score_ec01(text):
    groups = {
        "guest": r"guest",
        "empty": r"empty_cart|empty cart",
        "price_changed": r"price_changed|stale price|price change",
        "tax_address": r"us-ny|us-or|tax|address",
        "decline": r"declin|4000000000000002",
        "timeout": r"timeout",
        "double_submit": r"double.?submit|idempoten|clicked twice",
        "inv_charge": r"charge.{0,40}without.{0,40}order|never charge|matching order",
        "inv_order": r"order.{0,40}without.{0,40}(auth|authoriz)|never (create )?an? order without",
    }
    c, miss = cover(text, groups)
    s = {"coverage": round(c, 2), "missing": miss, "bad_cards": len(find_cards(text))}
    s["quality"] = 0.85 * c + 0.15 * int(s["bad_cards"] == 0)
    return s

def score_ec02(text):
    data = extract_json(text)
    s = {"json_ok": int(isinstance(data, list))}
    # accept discount 0 as well as 0.00
    hits, total, missing, wrong = score_expected_rows(data if isinstance(data, list) else [], PRICE_EXPECTED, ["discount", "tax", "total", "outcome"])
    s["hits"] = hits
    s["total"] = total
    s["missing"] = ";".join(dict.fromkeys(missing))
    s["wrong"] = ";".join(wrong[:10])
    s["quality"] = 0.2 * s["json_ok"] + 0.8 * (hits / total if total else 0)
    return s

def score_ec03(text):
    groups = {
        "exactly_one": r"exactly (one|1)\b",
        "out_of_stock": r"out_of_stock|409",
        "stock_zero": r"stock(?: decreases)?(?: by)? 1|final stock\s*=\s*0|stock=0",
        "qty_gt": r"qty ?> ?stock|greater than stock|exceeds stock|more than (the )?(available )?stock|qty=2.{0,40}stock=1",
        "hold": r"\bhold\b|reserv",
        "expiry": r"expir",
        "between": r"between (add.?to.?cart|cart) and (pay|checkout)|sold.?out between",
        "coupon_race": r"one redemption|same buyer|ONCEHOT|concurrent (redeem|coupon)",
    }
    c, miss = cover(text, groups)
    s = {"coverage": round(c, 2), "missing": miss}
    s["quality"] = c
    return s

def code_block(text, langs=("js", "javascript")):
    m = re.findall(r"```(?:%s)\s*\n(.*?)```" % "|".join(langs), text, re.S)
    return max(m, key=len) if m else None

def score_ec04(text, tag="ec04"):
    code = code_block(text) or ""
    s = {"has_code": int(bool(code))}
    f = GEN / f"{tag}.js"
    f.write_text(code)
    k6 = os.environ.get("K6_BIN") or _which_k6()
    if k6 and code:
        ins = subprocess.run([k6, "inspect", str(f)], capture_output=True, text=True)
        s["k6_parses"] = int(ins.returncode == 0)
        try:
            o = json.loads(ins.stdout)
        except Exception:
            o = {}
        blob = json.dumps(o) + code
    else:
        s["k6_parses"] = int(bool(re.search(r"export\s+(default|const|function)|options\s*=", code)))
        s["k6_skipped"] = int(not k6)
        blob = code
    s["stages_ok"] = int(bool(re.search(r"\b100\b", blob) and re.search(r"\b300\b", blob) and re.search(r"\b50\b", blob)))
    s["thresholds_ok"] = int(bool(re.search(r"p\(95\)\s*<\s*800", blob)) and bool(re.search(r"p\(99\)\s*<\s*1500", blob)) and bool(re.search(r"rate\s*<\s*0\.02", blob)))
    s["think_time"] = int(bool(re.search(r"sleep\(|randomIntBetween\(1,\s*3\)", code)))
    s["checks"] = int("check(" in code)
    s["hot_sku"] = int(bool(re.search(r"SKU-HOT", code)))
    s["allows_409"] = int(bool(re.search(r"409|out_of_stock", code)))
    q = (0.2 * s["k6_parses"] + 0.2 * s["stages_ok"] + 0.25 * s["thresholds_ok"]
         + 0.1 * s["think_time"] + 0.1 * s["checks"] + 0.1 * s["hot_sku"] + 0.05 * s["allows_409"])
    s["quality"] = q
    return s

def _which_k6():
    import shutil
    return shutil.which("k6")

def score_sa01(text):
    data = extract_json(text)
    s = {"json_ok": int(isinstance(data, list))}
    items = data if isinstance(data, list) else []
    got = {}
    for it in items:
        if not isinstance(it, dict):
            continue
        key = (str(it.get("role") or "").strip().lower(), str(it.get("action") or "").strip())
        http = str(it.get("expected_http") or it.get("http") or "")
        change = it.get("expect_change")
        if change is None:
            change = it.get("persists")
        got[key] = (http, change)
    hits = 0
    total = len(ROLES) * len(ACTIONS)
    missing = 0
    wrong = 0
    for role in ROLES:
        for action, allowed in ACTIONS.items():
            exp_allow = role in allowed
            if (role, action) not in got:
                missing += 1
                continue
            http, change = got[(role, action)]
            http_ok = ("200" in http or "204" in http) if exp_allow else ("403" in http)
            if change is None:
                change_ok = http_ok  # lenient if omitted but http right
            else:
                change_ok = bool(change) is exp_allow or str(change).lower() == str(exp_allow).lower()
            if http_ok and change_ok:
                hits += 1
            else:
                wrong += 1
    s["hits"] = hits
    s["total"] = total
    s["missing_cells"] = missing
    s["wrong_cells"] = wrong
    s["quality"] = 0.15 * s["json_ok"] + 0.85 * (hits / total if total else 0)
    return s

def score_sa02(text):
    groups = {
        "status_404": r"\b404\b",
        "not_403": r"not 403|404 \(not 403\)|not.{0,12}403",
        "list": r"\blist\b|search|export|dashboard",
        "spoof": r"header|x-tenant|spoof|session",
        "cache": r"cache",
        "job": r"job|async|background",
        "three": r"tenantc|three tenants|tenants a,\s*b,\s*c",
        "update_delete": r"update|delete|patch",
    }
    c, miss = cover(text, groups)
    s = {"coverage": round(c, 2), "missing": miss}
    # penalize if 403 is recommended as the cross-tenant success criteria without 404
    prefers_403 = int(bool(re.search(r"expected.{0,40}403", text, re.I)) and not re.search(r"404", text))
    s["prefers_403"] = prefers_403
    s["quality"] = 0.9 * c + 0.1 * int(not prefers_403)
    return s

def score_sa03(text):
    data = extract_json(text)
    s = {"json_ok": int(isinstance(data, list))}
    hits, total, missing, wrong = score_expected_rows(data if isinstance(data, list) else [], PRORATION_EXPECTED, ["credit", "new_charge", "due", "access", "webhook_effect"])
    s["hits"] = hits
    s["total"] = total
    s["missing"] = ";".join(dict.fromkeys(missing))
    s["wrong"] = ";".join(wrong[:12])
    # cancel webhook_effect may be n/a; be lenient: if webhook_effect missing but amounts right, already counted in wrong
    s["quality"] = 0.2 * s["json_ok"] + 0.8 * (hits / total if total else 0)
    return s

def score_sa04(text):
    groups = {
        "list_200": r"get /v1/projects|/v1/projects\?|list",
        "items_schema": r"items|created_at|uuid|\bpage\b",
        "unauthorized": r"401|unauthorized",
        "not_found": r"404|not_found",
        "invalid_page": r"per_page.?101|invalid_page|400",
        "create_201": r"201|post /v1/projects",
        "invalid_name": r"invalid_name|empty|too long",
        "error_shape": r"error.*code|code.:",
    }
    c, miss = cover(text, groups)
    invented = int(bool(re.search(r"/v1/(users|orders|payments|webhooks)\b", text, re.I)))
    s = {"coverage": round(c, 2), "missing": miss, "invented_ops": invented}
    s["quality"] = 0.85 * c + 0.15 * int(not invented)
    return s

SCORERS = {
    "hc01_phi_testdata": score_hc01,
    "hc02_clinical_flows": score_hc02,
    "hc03_phi_leakage": score_hc03,
    "hc04_accessibility": score_hc04,
    "fi01_rounding_currency": score_fi01,
    "fi02_payment_refund": score_fi02,
    "fi03_fraud_limits": score_fi03,
    "fi04_audit_trail": score_fi04,
    "ec01_cart_checkout": score_ec01,
    "ec02_discounts_tax": score_ec02,
    "ec03_inventory_race": score_ec03,
    "ec04_peak_load": lambda text, tag="ec04": score_ec04(text, tag),
    "sa01_rbac_matrix": score_sa01,
    "sa02_tenant_isolation": score_sa02,
    "sa03_billing_proration": score_sa03,
    "sa04_api_contract": score_sa04,
}

def score_industry(task, text, tag=""):
    fn = SCORERS.get(task)
    if not fn:
        return {"quality": 0.0, "unknown_task": 1}
    if task == "ec04_peak_load":
        s = score_ec04(text, tag or "ec04")
    else:
        s = fn(text)
    s["quality"] = round(float(s.get("quality") or 0), 3)
    return s

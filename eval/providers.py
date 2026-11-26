"""Model providers for the eval harness, with pacing, backoff and a spend cap.
- Anthropic Messages API when the model id starts with "claude" (needs ANTHROPIC_API_KEY).
- Otherwise any OpenAI-compatible chat-completions endpoint: MODELS_URL + MODELS_API_KEY (falls back to GITHUB_TOKEN).
Keys are read from env only; never printed or written. Spend is estimated from API usage and persisted to runs/spend.json;
calls stop once BUDGET_USD (default 3.0) would be exceeded."""
import json, os, pathlib, time, urllib.error, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPEND = pathlib.Path(os.environ.get("SPEND_FILE", str(ROOT/"runs"/"spend.json")))
LOG = ROOT/"runs"/"ratelimit.log"
BUDGET = float(os.environ.get("BUDGET_USD", "3.0"))
# USD per million tokens (input, output). Source: https://platform.claude.com/docs/en/about-claude/pricing (26 Nov 2026)
PRICES = {"claude-haiku-5-5": (0.10, 0.50), "claude-sonnet-5-5": (2.0, 10.0), "claude-sonnet-5": (2.0, 10.0),
          "claude-haiku-4-5": (1.0, 5.0), "claude-opus-5-5": (5.0, 25.0)}
_last = [0.0]

def price(model):
    for k, v in PRICES.items():
        if model.startswith(k): return v
    return (0.0, 0.0)

def spend():
    return json.loads(SPEND.read_text()) if SPEND.exists() else {"usd": 0.0, "calls": 0, "by_model": {}}

def _add_spend(model, pin, pout):
    s = spend(); pi, po = price(model); usd = (pin or 0)/1e6*pi + (pout or 0)/1e6*po
    s["usd"] = round(s["usd"] + usd, 6); s["calls"] += 1
    m = s["by_model"].setdefault(model, {"usd": 0.0, "calls": 0, "in": 0, "out": 0})
    m["usd"] = round(m["usd"] + usd, 6); m["calls"] += 1; m["in"] += pin or 0; m["out"] += pout or 0
    SPEND.parent.mkdir(parents=True, exist_ok=True); SPEND.write_text(json.dumps(s, indent=1))
    return usd

def _log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a") as f: f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")

def call(model, prompt, max_tokens=3000, min_gap=1.5, temperature=0.2):
    """Return (text, prompt_tokens, completion_tokens, seconds)."""
    pi, po = price(model)
    worst = len(prompt)/3/1e6*pi + max_tokens/1e6*po
    if spend()["usd"] + worst > BUDGET:
        raise RuntimeError(f"budget stop: spent ${spend()['usd']:.3f}, next call could reach ${worst:.3f}, cap ${BUDGET}")
    anthropic = model.startswith("claude")
    if anthropic:
        url = "https://api.anthropic.com/v1/messages"
        body = {"model": model, "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}  # temperature is deprecated on current Claude models
        hdr = {"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01", "content-type": "application/json"}
    else:
        url = os.environ.get("MODELS_URL", "https://api.openai.com/v1/chat/completions")
        body = {"model": model, "temperature": temperature, "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}
        hdr = {"Authorization": "Bearer " + (os.environ.get("MODELS_API_KEY") or os.environ.get("GITHUB_TOKEN", "")), "Content-Type": "application/json"}
    data = json.dumps(body).encode()
    for attempt in range(8):
        wait = _last[0] + min_gap - time.time()
        if wait > 0: time.sleep(wait)
        _last[0] = time.time()
        try:
            t = time.time(); resp = urllib.request.urlopen(urllib.request.Request(url, data, hdr), timeout=150); raw = resp.read()
            if "json" not in (resp.headers.get("Content-Type") or ""):
                raise RuntimeError(f"endpoint returned non-JSON ({resp.headers.get('Content-Type')}: {raw[:40]!r})")
            d = json.loads(raw); dt = round(time.time()-t, 1)
            if anthropic:
                text = "".join(c.get("text", "") for c in d.get("content", []) if c.get("type") == "text")
                u = d.get("usage", {}); pin, pout = u.get("input_tokens"), u.get("output_tokens")
            else:
                text = d["choices"][0]["message"]["content"] or ""; u = d.get("usage", {}); pin, pout = u.get("prompt_tokens"), u.get("completion_tokens")
            _add_spend(model, pin, pout)
            return text, pin, pout, dt
        except urllib.error.HTTPError as e:
            ra = e.headers.get("retry-after"); msg = e.read()[:300].decode(errors="ignore")
            _log(f"{model} HTTP {e.code} retry-after={ra} {msg}")
            if e.code in (429, 500, 502, 503, 504, 529):
                s = min(float(ra) if ra and ra.replace('.', '').isdigit() else 10 * 2**attempt, 300)
                print(f"  backoff {s:.0f}s (HTTP {e.code})", flush=True); time.sleep(s); continue
            raise RuntimeError(f"HTTP {e.code}: {msg}")
        except (urllib.error.URLError, TimeoutError) as e:
            _log(f"{model} network {e}"); time.sleep(10 * 2**attempt)
    raise RuntimeError("gave up after retries")

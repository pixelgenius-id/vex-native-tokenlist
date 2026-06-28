#!/usr/bin/env python3
"""
VEX Native Token List Validator
Validates eosio.token-standard tokens on VEX native chain.
"""

import json
import os
import sys
import subprocess
import requests
from PIL import Image

CHAIN_API   = "https://vexascan.com"
MIN_AGE_DAYS = 7
MAX_LOGO_KB  = 50
LOGO_SIZE    = 256

results = []
failed  = False

def ok(msg):
    results.append(f"✅ {msg}")

def fail(msg):
    global failed
    failed = True
    results.append(f"❌ {msg}")

def warn(msg):
    results.append(f"⚠️ {msg}")

def info(msg):
    results.append(f"ℹ️ {msg}")

def chain_post(endpoint, payload):
    r = requests.post(f"{CHAIN_API}{endpoint}", json=payload, timeout=10)
    r.raise_for_status()
    return r.json()

def write_result():
    summary = "### ✅ All checks passed — ready for review" if not failed else \
              "### ❌ Validation failed — please fix the issues above"
    output = "\n".join(results) + f"\n\n---\n{summary}"
    print(output)
    with open("/tmp/validation_result.txt", "w") as f:
        f.write(output)
    return 1 if failed else 0

# ── 0. Removal guard ──────────────────────────────────────────────────────────
def load_base():
    try:
        out = subprocess.check_output(
            ["git", "show", "origin/main:tokenlist.json"],
            stderr=subprocess.DEVNULL
        )
        return json.loads(out)
    except Exception:
        return None

base_data = load_base()
base_keys = set()
if base_data:
    base_keys = {
        f"{t['contract']}::{t['symbol']}"
        for t in base_data.get("tokens", [])
    }

# ── 1. Parse tokenlist.json ───────────────────────────────────────────────────
try:
    with open("tokenlist.json") as f:
        data = json.load(f)
    ok("tokenlist.json is valid JSON")
except Exception as e:
    fail(f"tokenlist.json parse error: {e}")
    sys.exit(write_result())

required_root = {"name", "version", "tokens"}
missing_root = required_root - set(data)
if missing_root:
    fail(f"Missing root fields: {missing_root}")
else:
    ok("Root fields present (name, version, tokens)")

tokens = data.get("tokens", [])
info(f"Total tokens in list: {len(tokens)}")

# ── 1b. Removal check ─────────────────────────────────────────────────────────
results.append("\n### Removal Guard")
if base_keys:
    pr_keys = {f"{t.get('contract')}::{t.get('symbol')}" for t in tokens}
    removed = base_keys - pr_keys
    if removed:
        for key in sorted(removed):
            fail(f"Token `{key}` was removed — existing tokens cannot be delisted via PR")
    else:
        ok(f"No existing tokens removed ({len(base_keys)} checked)")
else:
    warn("Could not load base branch — skipping removal check")

# ── 2. Per-token validation ───────────────────────────────────────────────────
REQUIRED_FIELDS = {"contract", "symbol", "precision", "name"}
EOSIO_TOKEN_ACTIONS = {"transfer", "issue", "create"}

for token in tokens:
    contract  = token.get("contract", "")
    symbol    = token.get("symbol", "?")
    precision = token.get("precision")
    label     = f"`{symbol}` ({contract})"

    results.append(f"\n### {symbol} ({contract})")

    # Required fields
    missing = REQUIRED_FIELDS - set(token)
    if missing:
        fail(f"{label}: Missing fields: {missing}")
        continue
    ok(f"{label}: All required fields present")

    # Symbol format (uppercase letters only)
    if not symbol.isupper() or not symbol.isalpha():
        fail(f"{label}: Symbol must be uppercase letters only (e.g. SPARK)")
    else:
        ok(f"{label}: Symbol format valid")

    # Precision range
    if not isinstance(precision, int) or not (0 <= precision <= 18):
        fail(f"{label}: precision must be integer 0–18")
    else:
        ok(f"{label}: Precision = {precision}")

    # Account exists on chain
    try:
        chain_post("/v1/chain/get_account", {"account_name": contract})
        ok(f"{label}: Account `{contract}` exists on VEX native chain")
    except Exception as e:
        fail(f"{label}: Account `{contract}` not found on chain: {e}")
        continue

    # Contract is eosio.token standard (check ABI actions)
    try:
        abi_resp = chain_post("/v1/chain/get_abi", {"account_name": contract})
        abi = abi_resp.get("abi", {})
        actions = {a["name"] for a in abi.get("actions", [])}
        missing_actions = EOSIO_TOKEN_ACTIONS - actions
        if missing_actions:
            fail(f"{label}: Missing eosio.token actions: {missing_actions}")
        else:
            ok(f"{label}: eosio.token ABI verified (transfer, issue, create)")
    except Exception as e:
        warn(f"{label}: Could not fetch ABI: {e}")

    # Token has been created (currency stats exist)
    try:
        stats_resp = chain_post("/v1/chain/get_currency_stats", {
            "code": contract,
            "symbol": symbol
        })
        if symbol not in stats_resp:
            fail(f"{label}: Token not created yet — no currency stats found")
        else:
            supply = stats_resp[symbol].get("supply", "?")
            ok(f"{label}: Token exists, supply = {supply}")
    except Exception as e:
        fail(f"{label}: Could not get currency stats: {e}")

    # Contract age (first action timestamp via Hyperion)
    try:
        resp = requests.get(
            f"https://vexascan.com/v2/history/get_actions",
            params={
                "account": contract,
                "limit": 1,
                "sort": "asc",
                "action": "create"
            },
            timeout=10
        ).json()
        actions_list = resp.get("actions", [])
        if actions_list:
            from datetime import datetime, timezone
            ts_str = actions_list[0].get("@timestamp", "")
            if ts_str:
                deploy_time = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                now = datetime.now(timezone.utc)
                age_days = (now - deploy_time).days
                if age_days < MIN_AGE_DAYS:
                    fail(f"{label}: Contract age {age_days}d < {MIN_AGE_DAYS}d minimum")
                else:
                    ok(f"{label}: Contract age {age_days}d ≥ {MIN_AGE_DAYS}d")
        else:
            warn(f"{label}: Could not determine contract age — no create action found")
    except Exception as e:
        warn(f"{label}: Could not check contract age: {e}")

    # Logo: must exist in assets/<SYMBOL>.png
    logo_path = f"assets/{symbol}.png"
    if not os.path.exists(logo_path):
        fail(f"{label}: Logo not found at {logo_path}")
    else:
        size_kb = os.path.getsize(logo_path) / 1024
        if size_kb > MAX_LOGO_KB:
            fail(f"{label}: Logo {size_kb:.1f}KB > {MAX_LOGO_KB}KB limit")
        else:
            ok(f"{label}: Logo size {size_kb:.1f}KB ≤ {MAX_LOGO_KB}KB")

        try:
            img = Image.open(logo_path)
            w, h = img.size
            if w != LOGO_SIZE or h != LOGO_SIZE:
                fail(f"{label}: Logo must be {LOGO_SIZE}×{LOGO_SIZE}px, got {w}×{h}px")
            else:
                ok(f"{label}: Logo dimensions {w}×{h}px ✓")
            if img.format != "PNG":
                fail(f"{label}: Logo must be PNG format, got {img.format}")
            else:
                ok(f"{label}: Logo format PNG ✓")
        except Exception as e:
            fail(f"{label}: Cannot read logo image: {e}")

    # Logo file must exist in assets/ — logoURI is auto-generated on merge
    logo_path = f"assets/{symbol}.png"
    GITHUB_BASE = "https://raw.githubusercontent.com/pixelgenius-id/vex-native-tokenlist/main/assets/"
    logo_uri = token.get("logoURI", "")
    if not os.path.exists(logo_path):
        fail(f"{label}: Logo file not found at `{logo_path}` — please upload your logo as `assets/{symbol}.png` (256×256 PNG, max 50KB)")
    else:
        ok(f"{label}: Logo file `{logo_path}` exists")
        if logo_uri and not logo_uri.startswith(GITHUB_BASE):
            fail(f"{label}: `logoURI` must use this repo's GitHub raw URL or be left empty (auto-generated on merge).\n"
                 f"  External links (IPFS, HTTP, etc.) are not allowed.\n"
                 f"  Leave `logoURI` empty — it will be set automatically after merge.")

sys.exit(write_result())

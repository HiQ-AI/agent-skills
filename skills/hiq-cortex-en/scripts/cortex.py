#!/usr/bin/env python3
"""HiQ Cortex LCA data CLI — search and read real life-cycle inventory data.

Standard library only: no pip install, no MCP setup. Set the API key once and
every subcommand works:

    export HIQ_API_KEY=sk_xxx
    python3 cortex.py search "304 stainless steel"
    python3 cortex.py lookup <key> [<key> ...]
    python3 cortex.py aggregate --source bafu [--target 2.5]
    python3 cortex.py indicators <key> [<key> ...] --indicator AP --source hiqlcd
    python3 cortex.py hotspot <key>
    python3 cortex.py epd "concrete" [--unit m3] [--geo IT]
    python3 cortex.py epd-benchmark "ready mix concrete" --unit m3

Add --json to any subcommand for the raw payload.

Failures exit non-zero with an actionable message on stderr. Restricted data is
not a failure: it exits 0 and prints how to obtain access — that is the user's
purchasing decision, not a fault to retry.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request

BASE = os.environ.get("HIQ_API_BASE", "https://x.hiqlcd.com")
# Authorization and data queries share the same host, both under BASE.
AUTH_BASE = os.environ.get("HIQ_AUTH_BASE", f"{BASE}/api/cortex")
CRED_PATH = pathlib.Path(os.environ.get("HIQ_CRED_PATH", "")) if os.environ.get("HIQ_CRED_PATH") \
    else pathlib.Path.home() / ".hiq" / "credentials.json"
MCP_URL = f"{BASE}/api/cortex/mcp"
SEARCH_URL = f"{BASE}/api/cortex/search"
# Search runs a validating workflow upstream; 20-40s is normal, not a hang.
SEARCH_TIMEOUT = 180
MCP_TIMEOUT = 120


def _credential() -> tuple[str, str]:
    """Return (credential, kind). api_key → X-API-Key, sso_token → Authorization.

    Environment variable wins over the credential stored by `login`. If neither
    exists, print both ways forward rather than guessing or degrading silently.
    """
    k = os.environ.get("HIQ_API_KEY", "").strip()
    if k:
        return k, "api_key"
    try:
        data = json.loads(CRED_PATH.read_text())
        tok = (data.get("access_token") or "").strip()
        if tok:
            return tok, str(data.get("kind") or "sso_token")
    except Exception:
        pass
    sys.exit(
        "No usable credential. Either:\n"
        "  1) Sign in with a browser (no API key needed): python3 cortex.py login\n"
        "  2) Use an API key: create one at https://www.hiqlcd.com/ then export HIQ_API_KEY=sk_xxx"
    )


def _auth_header() -> dict:
    cred, kind = _credential()
    # The gateway picks the verification mode from the credential type — the
    # client only has to send one of the two headers.
    return {"X-API-Key": cred} if kind == "api_key" else {"Authorization": f"Bearer {cred}"}


# Cloudflare fronts the API and blocks the default `Python-urllib/3.x` agent with
# error 1010 ("blocked based on your browser's signature"). Any conventional agent
# string passes — this is not an auth issue and retrying without it will keep failing.
_UA = "hiq-cortex-skill/1.0 (+https://www.hiqlcd.com)"


def _post(url: str, data: bytes, headers: dict, timeout: int) -> str:
    # The gateway authenticates on X-API-Key only; Authorization: Bearer is rejected.
    req = urllib.request.Request(
        url, data=data, headers={**_auth_header(), "User-Agent": _UA, **headers}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:300]
        if e.code == 401:
            sys.exit(f"401 authentication failed — check HIQ_API_KEY. Server returned: {body}")
        if e.code == 429:
            sys.exit("429 rate limited — the API allows 100 requests/minute. Back off and retry.")
        sys.exit(f"HTTP {e.code}: {body}")
    except urllib.error.URLError as e:
        sys.exit(f"Network error: {e.reason}")


def _sse_events(raw: str):
    """Yield JSON objects from an SSE body (`data: {...}` lines)."""
    for line in re.findall(r"^data: (\{.*)$", raw, re.MULTILINE):
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue


def call_tool(name: str, arguments: dict) -> dict:
    """Call one MCP tool. The endpoint is stateless — no initialize handshake."""
    payload = json.dumps(
        {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
         "params": {"name": name, "arguments": arguments}}
    ).encode()
    raw = _post(
        MCP_URL, payload,
        {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"},
        MCP_TIMEOUT,
    )
    for ev in _sse_events(raw):
        if "error" in ev:
            sys.exit(f"Tool call failed: {json.dumps(ev['error'], ensure_ascii=False)[:300]}")
        result = ev.get("result")
        if not result:
            continue
        text = (result.get("content") or [{}])[0].get("text", "")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            sys.exit(f"Unexpected tool response format: {text[:300]}")
    sys.exit(f"{name} returned no result. Response starts with: {raw[:200]}")


# ── formatting ────────────────────────────────────────────────────────────────

def _entitlement_note(block: dict) -> str:
    url = block.get("purchase_url") or "https://carbonx.hiqlcd.com/price"
    srcs = block.get("commercial_sources") or block.get("restricted_sources") or []
    if not srcs:
        # lookup's restriction carries the resource instead of a source list.
        res = block.get("resource") or {}
        one = " ".join(str(res[k]) for k in ("source", "version", "system_model") if res.get(k))
        srcs = [one] if one else []
    who = "/".join(srcs) if srcs else "this database"
    return (
        f"\n⛔ {who} requires a data-package entitlement that this account does not have.\n"
        f"   Get access: {url}\n"
        f"   Do not retry, and do not silently substitute a value from another database.\n"
        f"   Free databases needing no entitlement: bafu, uslci, elcd, ef, worldsteel."
    )


def fmt_search(res: dict) -> str:
    status = res.get("status")
    out = [f"status: {status}"]
    if res.get("summary"):
        out.append(f"summary: {res['summary']}")
    rows = res.get("datasets") or []
    if not rows:
        out.append("\nNo datasets matched. Try broader terms, an alternative name, or drop --sources.")
        return "\n".join(out)
    if status == "partial":
        out.append("⚠ Partial match — verify each name before use; these may be related but different products.")
    out.append("")
    for i, d in enumerate(rows, 1):
        out.append(f"{i}. {d.get('name', '?')}")
        out.append(f"   key: {d.get('key', '')}")
        if d.get("link"):
            out.append(f"   link: {d['link']}")
    out.append("\nNext: python3 cortex.py lookup <key> [<key> ...]")
    return "\n".join(out)


def fmt_lookup(res: dict) -> str:
    data = res.get("data") or {}
    hits = data.get("hits") or []
    out = []
    for h in hits:
        out.append(f"• {h.get('name', '?')}")
        basis = " · ".join(x for x in [h.get("src"), h.get("ver"), h.get("model"), h.get("loc")] if x)
        out.append(f"  basis: {basis or '—'}   unit: {h.get('unit') or '—'}")
        if h.get("restricted"):
            r = h.get("restriction") or {}
            out.append(f"  GWP: restricted{_entitlement_note(r)}")
        elif h.get("gwp") is not None:
            out.append(f"  GWP: {h['gwp']} {h.get('gwp_unit') or 'kg CO2 eq'}")
        else:
            out.append("  GWP: no headline value for this dataset")
        # cortex-link.internal is an in-app sentinel handled by HiQ's own clients;
        # it is not resolvable in a browser, so never hand it to an external user.
        link = h.get("link") or ""
        if link and "cortex-link.internal" not in link:
            out.append(f"  link: {link}")
        out.append("")
    missing = data.get("missing_keys") or []
    if missing:
        out.append(f"{len(missing)} key(s) not found — usually keys from an older catalogue version. Search again:")
        out.extend(f"  {k}" for k in missing[:10])
    return "\n".join(out).rstrip() or "No results"


def fmt_aggregate(res: dict) -> str:
    if res.get("status") != "ok":
        note = res.get("note") or "empty"
        ent = res.get("entitlement")
        return f"status: {res.get('status')}\n{note}" + (_entitlement_note(ent) if ent else "")
    p = res.get("percentiles") or {}
    out = [
        f"n = {res.get('count')}   unit: {res.get('unit')}",
        f"mean {res.get('avg')}   min {res.get('min')}   max {res.get('max')}",
        "percentiles: " + "  ".join(f"{k} {v}" for k, v in p.items()),
    ]
    t = res.get("target")
    if t:
        # This block comes back camelCase while the rest of the payload is snake_case.
        out.append(
            f"\ntarget {t.get('value')}: rank {t.get('rank')}/{t.get('of')} "
            f"(better than {t.get('betterThanPct')}% of the cohort), "
            f"{t.get('deltaVsMedianPct')}% vs median"
        )
    if res.get("comparability_note"):
        out.append(f"\n⚠ comparability: {res['comparability_note']}")
    return "\n".join(out)


def fmt_indicators(res: dict) -> str:
    if res.get("status") != "ok":
        out = f"status: {res.get('status')}\n{res.get('note') or res.get('error') or ''}"
        ent = res.get("entitlement")
        return out + (_entitlement_note(ent) if ent else "")
    p = res.get("percentiles") or {}
    return "\n".join([
        f"{res.get('indicator')} ({res.get('method_id')})   n = {res.get('count')}   unit: {res.get('unit')}",
        f"mean {res.get('avg')}   min {res.get('min')}   max {res.get('max')}",
        "percentiles: " + "  ".join(f"{k} {v}" for k, v in p.items()),
        f"\n⚠ {res.get('comparability_note')}" if res.get("comparability_note") else "",
    ]).rstrip()


def fmt_epd(res: dict) -> str:
    rows = res.get("results") or []
    if not rows:
        return f"status: {res.get('status')}  No EPD matched."
    out = [f"{res.get('total')} total (showing {len(rows)})", ""]
    for r in rows:
        g = r.get("gwp_a1a3") or {}
        val = f"{g.get('value')} {g.get('unit')}" if g.get("value") is not None else "n/a"
        out.append(f"• {r.get('name', '?')}")
        out.append(f"  {r.get('declared_unit')} · {r.get('location')} · {r.get('pt_source')} · valid until {r.get('valid_until')}")
        out.append(f"  GWP A1-A3: {val}   epd_key: {r.get('epd_key')}")
        out.append("")
    return "\n".join(out).rstrip()


# ── commands ──────────────────────────────────────────────────────────────────

def _auth_post(path: str, payload: dict, timeout: int = 30) -> tuple[int, dict]:
    """POST for the device flow (no credential yet — cannot reuse _post's auth header)."""
    req = urllib.request.Request(
        AUTH_BASE.rstrip("/") + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "User-Agent": _UA},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(body or "{}")
        except json.JSONDecodeError:
            return e.code, {"detail": body[:200]}
    except urllib.error.URLError as e:
        sys.exit(f"network error: {e.reason}")


def cmd_login(a) -> None:
    """Browser login: start the device flow, let the user approve, poll, store.

    The authorization page reuses an existing web session, so approving is
    usually a single click.
    """
    import time as _t
    import webbrowser

    status, rec = _auth_post("/oauth/device_authorization", {
        "agent_id": a.name, "agent_name": a.name, "scope": "lca_data",
    })
    if status >= 400:
        sys.exit(f"could not start authorization ({status}): {json.dumps(rec, ensure_ascii=False)[:200]}")

    url = rec.get("verification_uri_complete") or rec.get("verification_uri", "")
    code = rec.get("user_code", "")
    interval = int(rec.get("interval") or 5)
    expires = int(rec.get("expires_in") or 600)

    print("Approve this in your browser:", flush=True)
    print(f"  {url}")
    print(f"  code: {code}\n", flush=True)
    if not a.no_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    print("Waiting for approval… (continues automatically once you approve)", flush=True)
    deadline = _t.monotonic() + expires
    while _t.monotonic() < deadline:
        _t.sleep(interval)
        status, body = _auth_post("/oauth/token", {"device_code": rec["device_code"]})
        if status == 428:
            continue                      # authorization_pending — keep polling
        if status >= 400:
            sys.exit(f"authorization failed ({status}): {json.dumps(body, ensure_ascii=False)[:200]}")
        token = (body.get("access_token") or "").strip()
        if not token:
            sys.exit("authorization returned an empty token; please retry.")
        CRED_PATH.parent.mkdir(parents=True, exist_ok=True)
        CRED_PATH.write_text(json.dumps({
            "access_token": token,
            "kind": "sso_token",
            "owner": body.get("owner", ""),
            "scope": body.get("scope", "lca_data"),
        }, ensure_ascii=False))
        try:
            CRED_PATH.chmod(0o600)        # the credential is a session — keep it owner-only
        except Exception:
            pass
        print(f"\n✓ Signed in. Credential stored at {CRED_PATH} (owner-readable only)", flush=True)
        print("  Try it: python3 cortex.py search \"304 stainless steel\"")
        return
    sys.exit("authorization timed out; run login again.")


def cmd_logout(_a) -> None:
    if CRED_PATH.exists():
        CRED_PATH.unlink()
        print(f"Removed local credential {CRED_PATH}", flush=True)
    else:
        print("No stored credential on this machine.", flush=True)
    print("Note: this only clears the local file. The credential expires with your session — sign out on the web to revoke it now.")


def cmd_search(a) -> dict:
    body = f"query={urllib.parse.quote(a.query)}"
    if a.sources:
        body += f"&sources={urllib.parse.quote(a.sources)}"
    raw = _post(SEARCH_URL, body.encode(),
                {"Content-Type": "application/x-www-form-urlencoded"}, SEARCH_TIMEOUT)
    for ev in _sse_events(raw):
        if ev.get("event") == "WorkflowCompleted":
            try:
                return json.loads(ev.get("content") or "{}")
            except json.JSONDecodeError:
                sys.exit(f"Could not parse search result: {str(ev.get('content'))[:200]}")
    sys.exit("Search did not complete. 20-40 seconds is normal; retry once if this persists.")


def main() -> None:
    ap = argparse.ArgumentParser(description="HiQ Cortex LCA data CLI")
    ap.add_argument("--json", action="store_true", help="print the raw payload")
    # Shared parent so `--json` works after the subcommand too — agents write it
    # either way and an argparse error there is a wasted turn.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", help=argparse.SUPPRESS)
    sub = ap.add_subparsers(dest="cmd", required=True, parser_class=lambda **kw: argparse.ArgumentParser(parents=[common], **kw))

    lg = sub.add_parser("login", help="sign in with a browser (no API key needed)")
    lg.add_argument("--name", default="hiq-cortex-cli", help="name shown on the approval page")
    lg.add_argument("--no-browser", action="store_true", help="do not open a browser")

    sub.add_parser("logout", help="remove the credential stored on this machine")

    s = sub.add_parser("search", help="material name → dataset keys (takes 20-40s)")
    s.add_argument("query")
    s.add_argument("--sources", default="", help="comma separated, e.g. BAFU,Ecoinvent")

    lk = sub.add_parser("lookup", help="dataset key → GWP and basis")
    lk.add_argument("keys", nargs="+")

    ag = sub.add_parser("aggregate", help="cohort GWP distribution / percentile positioning")
    ag.add_argument("--source", default="", help="database code, e.g. bafu")
    ag.add_argument("--category", default="")
    ag.add_argument("--location", default="")
    ag.add_argument("--keys", default="", help="comma-separated keys instead of a predicate")
    ag.add_argument("--target", type=float, default=None, help="your own value, for positioning")
    ag.add_argument("--group-by", default="")

    ind = sub.add_parser("indicators", help="non-GWP LCIA indicators for a cohort")
    ind.add_argument("keys", nargs="+")
    ind.add_argument("--indicator", default="AP")
    ind.add_argument("--source", default="hiqlcd", help="must match the cohort's actual database")

    hs = sub.add_parser("hotspot", help="process-level breakdown of one dataset")
    hs.add_argument("key")
    hs.add_argument("--baseline", default="")
    hs.add_argument("--indicator", default="GWP100")
    hs.add_argument("--source", default="hiqlcd")

    ep = sub.add_parser("epd", help="search published EPDs")
    ep.add_argument("query")
    ep.add_argument("--unit", default="", help="declared unit, e.g. m3")
    ep.add_argument("--geo", default="", help="ISO region code, e.g. IT")
    ep.add_argument("--limit", type=int, default=10)

    eb = sub.add_parser("epd-benchmark", help="EPD peer distribution for a category")
    eb.add_argument("category")
    eb.add_argument("--unit", default="", help="strongly recommended")
    eb.add_argument("--indicators", default="GWP-total")
    eb.add_argument("--modules", default="A1-A3")

    a = ap.parse_args()

    if a.cmd == "login":
        cmd_login(a)
        return
    if a.cmd == "logout":
        cmd_logout(a)
        return
    if a.cmd == "search":
        res, fmt = cmd_search(a), fmt_search
    elif a.cmd == "lookup":
        res, fmt = call_tool("lookup_datasets", {"dataset_keys": ",".join(a.keys)}), fmt_lookup
    elif a.cmd == "aggregate":
        args = {}
        if a.keys:
            args["dataset_keys"] = a.keys
        else:
            where = {k: v for k, v in
                     {"source": a.source, "category": a.category, "location": a.location}.items() if v}
            if not where:
                sys.exit("aggregate needs --keys, or at least one predicate (--source/--category/--location)")
            args["where"] = json.dumps(where)
        if a.target is not None:
            args["target_value"] = a.target
        if a.group_by:
            args["group_by"] = a.group_by
        res, fmt = call_tool("aggregate_datasets", args), fmt_aggregate
    elif a.cmd == "indicators":
        res, fmt = call_tool("aggregate_indicators", {
            "dataset_keys": ",".join(a.keys), "indicator": a.indicator, "source": a.source}), fmt_indicators
    elif a.cmd == "hotspot":
        args = {"dataset_key": a.key, "indicator": a.indicator, "source": a.source}
        if a.baseline:
            args["baseline_key"] = a.baseline
        res = call_tool("process_hotspot", args)
        fmt = lambda r: json.dumps(r, ensure_ascii=False, indent=2)  # noqa: E731
    elif a.cmd == "epd":
        args = {"query": a.query, "limit": a.limit}
        if a.unit:
            args["declared_unit"] = a.unit
        if a.geo:
            args["geography"] = a.geo
        res, fmt = call_tool("epd_search", args), fmt_epd
    else:  # epd-benchmark
        args = {"product_category": a.category, "indicators": a.indicators, "modules": a.modules}
        if a.unit:
            args["declared_unit"] = a.unit
        res = call_tool("epd_peer_benchmark", args)
        fmt = lambda r: json.dumps(r, ensure_ascii=False, indent=2)  # noqa: E731

    print(json.dumps(res, ensure_ascii=False, indent=2) if a.json else fmt(res))


if __name__ == "__main__":
    import urllib.parse  # noqa: E402  (only needed by search)
    main()

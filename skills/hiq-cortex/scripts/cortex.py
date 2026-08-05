#!/usr/bin/env python3
"""HiQ Cortex LCA 数据查询 CLI —— 检索并读取真实生命周期清单数据。

仅依赖 Python 标准库:无需 pip install,无需配置 MCP。设置一次 API key,
所有子命令即可使用:

    export HIQ_API_KEY=sk_xxx
    python3 cortex.py search "304 stainless steel"
    python3 cortex.py lookup <key> [<key> ...]
    python3 cortex.py aggregate --source bafu [--target 2.5]
    python3 cortex.py indicators <key> [<key> ...] --indicator AP --source hiqlcd
    python3 cortex.py hotspot <key>
    python3 cortex.py epd "concrete" [--unit m3] [--geo IT]
    python3 cortex.py epd-benchmark "ready mix concrete" --unit m3

任意子命令加 --json 可输出原始 payload。

失败时退出码非 0,并在 stderr 打印可操作的说明。受限数据不算失败:退出码为 0
并打印开通方式 —— 那是用户的授权决策,不是需要重试的故障。
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
# 授权与查数同域,都在 BASE 上。
AUTH_BASE = os.environ.get("HIQ_AUTH_BASE", f"{BASE}/api/cortex")
CRED_PATH = pathlib.Path(os.environ.get("HIQ_CRED_PATH", "")) if os.environ.get("HIQ_CRED_PATH") \
    else pathlib.Path.home() / ".hiq" / "credentials.json"
MCP_URL = f"{BASE}/api/cortex/mcp"
SEARCH_URL = f"{BASE}/api/cortex/search"
# Search runs a validating workflow upstream; 20-40s is normal, not a hang.
SEARCH_TIMEOUT = 180
MCP_TIMEOUT = 120


def _credential() -> tuple[str, str]:
    """返回 (凭据, 类型)。类型 api_key 走 X-API-Key,sso_token 走 Authorization。

    优先级:环境变量 HIQ_API_KEY > 扫码登录存下的凭据。两者都没有就给出两条出路,
    不猜、不静默降级。
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
        "未找到可用凭据。二选一:\n"
        "  1) 扫码登录(推荐,免注册建 key):python3 cortex.py login\n"
        "  2) 用 API key:在 https://www.hiqlcd.com/ 控制台创建后 export HIQ_API_KEY=sk_xxx"
    )


def _auth_header() -> dict:
    cred, kind = _credential()
    # 网关按凭据类型自动选校验方式,客户端只需二选一给对头。
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
            sys.exit(f"401 鉴权失败 —— 请检查 HIQ_API_KEY。服务端返回:{body}")
        if e.code == 429:
            sys.exit("429 触发限流 —— 接口限 100 次/分钟。退避后重试。")
        sys.exit(f"HTTP {e.code}: {body}")
    except urllib.error.URLError as e:
        sys.exit(f"网络错误:{e.reason}")


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
            sys.exit(f"工具调用失败:{json.dumps(ev['error'], ensure_ascii=False)[:300]}")
        result = ev.get("result")
        if not result:
            continue
        text = (result.get("content") or [{}])[0].get("text", "")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            sys.exit(f"工具返回格式异常:{text[:300]}")
    sys.exit(f"{name} 无返回结果。响应开头:{raw[:200]}")


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
        f"\n⛔ {who} 需要数据包权益,当前账号没有。\n"
        f"   开通入口:{url}\n"
        f"   不要重试,也不要用其他数据库的值静默替代。\n"
        f"   无需权益的免费库:bafu、uslci、elcd、ef、worldsteel。"
    )


def fmt_search(res: dict) -> str:
    status = res.get("status")
    out = [f"status: {status}"]
    if res.get("summary"):
        out.append(f"summary: {res['summary']}")
    rows = res.get("datasets") or []
    if not rows:
        out.append("\n未匹配到数据集。可放宽关键词、改用英文名,或去掉 --sources。")
        return "\n".join(out)
    if status == "partial":
        out.append("⚠ 部分匹配 —— 使用前逐条核对名称,可能是相关但不同的产品。")
    out.append("")
    for i, d in enumerate(rows, 1):
        out.append(f"{i}. {d.get('name', '?')}")
        out.append(f"   key: {d.get('key', '')}")
        if d.get("link"):
            out.append(f"   link: {d['link']}")
    out.append("\n下一步:python3 cortex.py lookup <key> [<key> ...]")
    return "\n".join(out)


def fmt_lookup(res: dict) -> str:
    data = res.get("data") or {}
    hits = data.get("hits") or []
    out = []
    for h in hits:
        out.append(f"• {h.get('name', '?')}")
        basis = " · ".join(x for x in [h.get("src"), h.get("ver"), h.get("model"), h.get("loc")] if x)
        out.append(f"  基准:{basis or '—'}   单位:{h.get('unit') or '—'}")
        if h.get("restricted"):
            r = h.get("restriction") or {}
            out.append(f"  GWP:受限{_entitlement_note(r)}")
        elif h.get("gwp") is not None:
            out.append(f"  GWP: {h['gwp']} {h.get('gwp_unit') or 'kg CO2 eq'}")
        else:
            out.append("  GWP:该数据集无 headline 数值")
        # cortex-link.internal is an in-app sentinel handled by HiQ's own clients;
        # it is not resolvable in a browser, so never hand it to an external user.
        link = h.get("link") or ""
        if link and "cortex-link.internal" not in link:
            out.append(f"  链接:{link}")
        out.append("")
    missing = data.get("missing_keys") or []
    if missing:
        out.append(f"有 {len(missing)} 个 key 未命中 —— 多为旧版本目录的 key,请重新检索:")
        out.extend(f"  {k}" for k in missing[:10])
    return "\n".join(out).rstrip() or "无结果"


def fmt_aggregate(res: dict) -> str:
    if res.get("status") != "ok":
        note = res.get("note") or "empty"
        ent = res.get("entitlement")
        return f"status: {res.get('status')}\n{note}" + (_entitlement_note(ent) if ent else "")
    p = res.get("percentiles") or {}
    out = [
        f"n = {res.get('count')}   unit: {res.get('unit')}",
        f"均值 {res.get('avg')}   最小 {res.get('min')}   最大 {res.get('max')}",
        "百分位:" + "  ".join(f"{k} {v}" for k, v in p.items()),
    ]
    t = res.get("target")
    if t:
        # This block comes back camelCase while the rest of the payload is snake_case.
        out.append(
            f"\n目标值 {t.get('value')}:排名 {t.get('rank')}/{t.get('of')} "
            f"(优于队列中 {t.get('betterThanPct')}%),"
            f"较中位数 {t.get('deltaVsMedianPct')}%"
        )
    if res.get("comparability_note"):
        out.append(f"\n⚠ 可比性:{res['comparability_note']}")
    return "\n".join(out)


def fmt_indicators(res: dict) -> str:
    if res.get("status") != "ok":
        out = f"status: {res.get('status')}\n{res.get('note') or res.get('error') or ''}"
        ent = res.get("entitlement")
        return out + (_entitlement_note(ent) if ent else "")
    p = res.get("percentiles") or {}
    return "\n".join([
        f"{res.get('indicator')} ({res.get('method_id')})   n = {res.get('count')}   单位:{res.get('unit')}",
        f"均值 {res.get('avg')}   最小 {res.get('min')}   最大 {res.get('max')}",
        "百分位:" + "  ".join(f"{k} {v}" for k, v in p.items()),
        f"\n⚠ {res.get('comparability_note')}" if res.get("comparability_note") else "",
    ]).rstrip()


def fmt_epd(res: dict) -> str:
    rows = res.get("results") or []
    if not rows:
        return f"status: {res.get('status')}  未匹配到 EPD。"
    out = [f"共 {res.get('total')} 条(显示 {len(rows)} 条)", ""]
    for r in rows:
        g = r.get("gwp_a1a3") or {}
        val = f"{g.get('value')} {g.get('unit')}" if g.get("value") is not None else "n/a"
        out.append(f"• {r.get('name', '?')}")
        out.append(f"  {r.get('declared_unit')} · {r.get('location')} · {r.get('pt_source')} · 有效期至 {r.get('valid_until')}")
        out.append(f"  GWP A1-A3:{val}   epd_key: {r.get('epd_key')}")
        out.append("")
    return "\n".join(out).rstrip()


# ── commands ──────────────────────────────────────────────────────────────────

def _auth_post(path: str, payload: dict, timeout: int = 30) -> tuple[int, dict]:
    """device flow 专用 POST(无凭据,不能复用 _post 的鉴权头)。"""
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
        sys.exit(f"网络错误:{e.reason}")


def cmd_login(a) -> None:
    """扫码登录:发起 device flow → 用户在浏览器授权 → 轮询取凭据 → 落盘。

    授权页复用已登录的网页会话,所以用户通常只需点一下「授权访问」。
    """
    import time as _t
    import webbrowser

    status, rec = _auth_post("/oauth/device_authorization", {
        "agent_id": a.name, "agent_name": a.name, "scope": "lca_data",
    })
    if status >= 400:
        sys.exit(f"发起授权失败({status}):{json.dumps(rec, ensure_ascii=False)[:200]}")

    url = rec.get("verification_uri_complete") or rec.get("verification_uri", "")
    code = rec.get("user_code", "")
    interval = int(rec.get("interval") or 5)
    expires = int(rec.get("expires_in") or 600)

    print("请在浏览器完成授权:", flush=True)
    print(f"  {url}")
    print(f"  授权码:{code}\n", flush=True)
    if not a.no_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    print("等待授权…(在浏览器点「授权访问」后会自动继续)", flush=True)
    deadline = _t.monotonic() + expires
    while _t.monotonic() < deadline:
        _t.sleep(interval)
        status, body = _auth_post("/oauth/token", {"device_code": rec["device_code"]})
        if status == 428:
            continue                      # authorization_pending,接着轮询
        if status >= 400:
            sys.exit(f"授权失败({status}):{json.dumps(body, ensure_ascii=False)[:200]}")
        token = (body.get("access_token") or "").strip()
        if not token:
            sys.exit("授权返回为空,请重试。")
        CRED_PATH.parent.mkdir(parents=True, exist_ok=True)
        CRED_PATH.write_text(json.dumps({
            "access_token": token,
            "kind": "sso_token",
            "owner": body.get("owner", ""),
            "scope": body.get("scope", "lca_data"),
        }, ensure_ascii=False))
        try:
            CRED_PATH.chmod(0o600)        # 凭据即登录态,不留给同机其他用户读
        except Exception:
            pass
        print(f"\n✓ 已登录。凭据存于 {CRED_PATH}(仅本人可读)", flush=True)
        print("  现在可以直接用:python3 cortex.py search \"304 不锈钢\"")
        return
    sys.exit("授权超时,请重新执行 login。")


def cmd_logout(_a) -> None:
    if CRED_PATH.exists():
        CRED_PATH.unlink()
        print(f"已删除本机凭据 {CRED_PATH}", flush=True)
    else:
        print("本机没有存储的凭据。", flush=True)
    print("注意:这只清除本机文件;凭据本身随你的登录态失效,需要立刻收回请在网页退出登录。")


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
                sys.exit(f"检索结果解析失败:{str(ev.get('content'))[:200]}")
    sys.exit("检索未完成。正常耗时 20–40 秒;若持续如此可重试一次。")


def main() -> None:
    ap = argparse.ArgumentParser(description="HiQ Cortex LCA 数据查询 CLI")
    ap.add_argument("--json", action="store_true", help="输出原始 payload")
    # Shared parent so `--json` works after the subcommand too — agents write it
    # either way and an argparse error there is a wasted turn.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", help=argparse.SUPPRESS)
    sub = ap.add_subparsers(dest="cmd", required=True, parser_class=lambda **kw: argparse.ArgumentParser(parents=[common], **kw))

    lg = sub.add_parser("login", help="扫码登录(免注册建 API key)")
    lg.add_argument("--name", default="hiq-cortex-cli", help="在授权页显示的名称")
    lg.add_argument("--no-browser", action="store_true", help="不自动打开浏览器")

    sub.add_parser("logout", help="删除本机存储的凭据")

    s = sub.add_parser("search", help="材料名 → 数据集 key(耗时 20-40 秒)")
    s.add_argument("query")
    s.add_argument("--sources", default="", help="逗号分隔,如 BAFU,Ecoinvent")

    lk = sub.add_parser("lookup", help="数据集 key → GWP 与基准")
    lk.add_argument("keys", nargs="+")

    ag = sub.add_parser("aggregate", help="队列 GWP 分布 / 百分位定位")
    ag.add_argument("--source", default="", help="数据库代码,如 bafu")
    ag.add_argument("--category", default="")
    ag.add_argument("--location", default="")
    ag.add_argument("--keys", default="", help="用逗号分隔的 key 替代谓词")
    ag.add_argument("--target", type=float, default=None, help="你自己的数值,用于定位")
    ag.add_argument("--group-by", default="")

    ind = sub.add_parser("indicators", help="队列的非 GWP LCIA 指标")
    ind.add_argument("keys", nargs="+")
    ind.add_argument("--indicator", default="AP")
    ind.add_argument("--source", default="hiqlcd", help="必须与队列实际所在库一致")

    hs = sub.add_parser("hotspot", help="单个数据集的工序级拆解")
    hs.add_argument("key")
    hs.add_argument("--baseline", default="")
    hs.add_argument("--indicator", default="GWP100")
    hs.add_argument("--source", default="hiqlcd")

    ep = sub.add_parser("epd", help="检索已发布 EPD")
    ep.add_argument("query")
    ep.add_argument("--unit", default="", help="声明单位,如 m3")
    ep.add_argument("--geo", default="", help="ISO 地区码,如 IT")
    ep.add_argument("--limit", type=int, default=10)

    eb = sub.add_parser("epd-benchmark", help="EPD 品类同类分布")
    eb.add_argument("category")
    eb.add_argument("--unit", default="", help="强烈建议指定")
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
                sys.exit("aggregate 需要 --keys,或至少一个谓词(--source/--category/--location)")
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

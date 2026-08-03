---
name: hiq-cortex
description: 'Look up real LCA emission factors and carbon footprint data from 18 life-cycle inventory databases (Ecoinvent, BAFU, USLCI, ELCD, EF, worldsteel, AusLCI, HiQLCD …) and 24,000+ published EPDs. Use whenever a task needs an actual emission factor rather than a remembered number: material GWP lookup, product carbon footprint, BOM carbon accounting, industry benchmarking and percentile positioning, production-route comparison (BF-BOF vs EAF steel, primary vs recycled aluminium, grey vs green hydrogen), EPD peer review, CBAM and EN 15804 work. Triggers on GWP, kg CO2e, emission factor, carbon footprint, LCA dataset, LCI, EPD, 碳足迹, 排放因子, 清单数据, 物料清单, 行业对标.'
slug: hiq-cortex
displayName: HiQ Cortex — LCA 数据查询
version: 1.4.0
summary: 从 18 个 LCA 数据库和 24000+ 已发布 EPD 查询真实排放因子。物料碳足迹、BOM 碳核算、行业对标定位、生产路线对比、EPD 同类审核。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags:
  - LCA
  - 碳足迹
  - 排放因子
  - 数据分析
  - EPD
  - CBAM
---

# HiQ Cortex — LCA Data

Carbon-footprint answers must come from real inventory data. A remembered "steel ≈ 2 kg CO₂e/kg" is not usable by an LCA practitioner: the real value depends on database, version, system model, production route, and geography, and it swings by multiples across them.

This skill connects you to **HiQ Cortex** — 18 LCA databases (11 free, 7 commercial) and 24,000+ published EPDs.

## Ground rules

1. **Every number comes from a tool call in this session.** Never state a GWP, LCIA value, or distribution from your own memory. If the data is not reachable, say so — do not fill the gap.
2. **State the basis with every number.** Database + version + system model + geography + reference unit. `0.0269 kg CO₂e/kWh (BAFU 2025, DEFAULT, CH, low-voltage grid)` is usable; `0.027` alone is not.
3. **Restricted ≠ error.** Commercial databases return a restriction carrying a `purchase_url` when the account lacks that data package. Show it truthfully, give the user the link, and **never silently substitute a value from another database or from literature**. Retrying will not help. Offer a free-database alternative instead, clearly labelled as a substitute.
4. **Never compare across incompatible bases.** Different functional units, system models (cut-off / consequential / APOS / EN 15804), or system boundaries are not comparable — say so instead of producing a misleading delta.

## Setup

Two ways to reach the data. **Check which one is available before answering**, and offer to set up the other when it would serve the user better.

### Option A — MCP server (preferred when the host supports it)

If tools named `lookup_datasets`, `aggregate_datasets`, `epd_search` are already available in this session, use them directly and skip to [Tools](#tools).

If not, offer to configure it — write this into the host's MCP config file:

```json
{
  "mcpServers": {
    "cortex": {
      "type": "http",
      "url": "https://x.hiqlcd.com/api/cortex/mcp",
      "headers": {
        "X-API-Key": "sk_xxx"
      }
    }
  }
}
```

| Host | Config file |
|---|---|
| WorkBuddy | `~/.workbuddy/mcp.json` (user) or `<project>/.workbuddy/mcp.json` |
| Claude Code | `~/.claude.json` or `<project>/.mcp.json` |
| Cursor | `~/.cursor/mcp.json` or `<project>/.cursor/mcp.json` |
| Cline / others | the host's MCP settings file |

⚠️ **`X-API-Key` only.** The gateway rejects `Authorization: Bearer` with `401 {"code":"INT-007"}`. Most client samples default to Bearer — change it. The host usually needs a restart to pick up a new server.

### Option B — bundled script (works anywhere, zero config)

No MCP support, or the user would rather not edit config files. Standard library only, no `pip install`:

```bash
export HIQ_API_KEY=sk_xxx
python3 scripts/cortex.py search "304 stainless steel"
```

### Getting a key

Register at [hiqlcd.com](https://www.hiqlcd.com/) and create an API key in the account console. One key covers both options. Rate limit: 100 requests/minute.

Never hardcode the key into files you write for the user — environment variable or the host's config file only.

## Tools

| Need | MCP tool | Script command |
|---|---|---|
| Material name → dataset keys | *(none — see below)* | `search "<query>" [--sources X]` |
| Keys → GWP, basis, link | `lookup_datasets` | `lookup <key> [<key> ...]` |
| Cohort → GWP distribution, percentile positioning | `aggregate_datasets` | `aggregate --source X [--target N]` |
| Cohort → non-GWP indicator (AP/EP/ODP/WDP/ADP) | `aggregate_indicators` | `indicators <keys> --indicator AP --source X` |
| One dataset → per-stage hotspots | `process_hotspot` | `hotspot <key>` |
| Published EPD search | `epd_search` | `epd "<query>" [--unit m3]` |
| EPD peer distribution / outlier check | `epd_peer_benchmark` | `epd-benchmark "<category>" --unit m3` |

Add `--json` to any script command for the raw payload.

**Search has no MCP tool** — dataset keys come from a REST endpoint, which the script wraps. To call it directly:

```bash
curl -sN -X POST https://x.hiqlcd.com/api/cortex/search \
  -H "X-API-Key: sk_xxx" -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=304 stainless steel&sources=BAFU,Ecoinvent"
```

Response is SSE — parse the `WorkflowCompleted` event and JSON-decode its `content` field. **It takes 20–40 seconds** (it searches and validates); that is normal, not a hang. Do not fire parallel retries.

Keys are opaque handles. Pass them through verbatim; never construct or edit one.

## Core workflow

1. **Search** for the material, product, or process → candidate keys.
2. **Read the candidate names before using them.** LCA datasets are specific: "cold rolled annealed coil, 304 stainless" and "hot rolled plate, 304 stainless" are different products with different footprints. A `partial` search status means related-but-not-exact — verify before quoting.
3. **Look up** the relevant keys in one batched call when values are needed.
4. **Present with basis**, showing 2–3 candidates when they differ materially and explaining what drives the difference.
5. **Recommend one** only when the request supports it, and state the assumption.

## Scenario routing

Route first, top-down, first match wins. Mis-routing wastes the turn — a point lookup answers the wrong question when the user asked "am I high or low".

| Signal | Do this |
|---|---|
| User gives **their own** number and asks where it sits ("我这 2.5 算高还是低", "比同行如何") | `aggregate` with a cohort predicate + `--target` → percentile position |
| No BOM yet, wants a magnitude or an A/B comparison ("大概什么量级") | `aggregate` → give a **range**, never a false-precision point value |
| Route-sensitive material (steel BF-BOF vs EAF, primary vs recycled Al, grey vs green H₂) | Search each route separately, aggregate per route, compare on one functional unit — see [references/comparability.md](references/comparability.md) |
| A material or BOM to map to datasets | search → lookup, batched |
| "Is this EPD value reasonable?" | `epd-benchmark` with `--unit` set — cross-unit comparison is meaningless |
| Multi-indicator work (acidification, eutrophication…) | `indicators`, one indicator per call; `--source` must match where the cohort lives |

## Data access tiers

| Tier | Content | Requirement |
|---|---|---|
| Catalog | All 18 databases: versions, system models, LCIA coverage; dataset names, units, geographies | none |
| Free databases | GWP + aggregates for BAFU, USLCI, ELCD, EF, AusLCI, NEEDS, ozLCI, worldsteel, USDA, bioenergiedat, recycledplastics | any valid key |
| Commercial databases | GWP + aggregates for Ecoinvent, HiQLCD, HiQLCD-AL, CarbonMinds, Agri-footprint, CALCD, HiQ-CESI | data package entitlement |

Without the entitlement, `lookup` returns `restricted: true` and aggregations return `status: "empty"` with an `entitlement` block — both carry a `purchase_url`. Tell the user which database is gated, give them the link, and offer the free-database route when it can answer the question. Data package entitlements are **separate from** any subscription plan; upgrading a plan does not unlock a database.

Free coverage is substantial: BAFU (Swiss, full LCIA — the best free default for European context), USLCI (US unit processes), ELCD / EF (European reference), worldsteel (global steel), USDA (agriculture). Details and per-database quirks: [references/databases.md](references/databases.md).

## Voice and terminology

The audience is LCA practitioners. Write like a competent colleague.

- No filler ("希望这对您有帮助", "让我来帮您"), no adjective piles, no summarizing flourish at the end.
- Use standard ISO 14040/14044 · ILCD · GB/T 24040 terminology — standard terms are *clearer* to this audience, not more obscure.
- 单元过程 unit process · 基本流 elementary flow · 中间流 intermediate flow · 参考流 reference flow · 功能单位 functional unit · 系统边界 system boundary · 影响类别 impact category · 类别指标 category indicator · 特征化因子 characterization factor · 截止法 cut-off · 后果法 consequential.
- Do not invent Chinese terms. When unsure of the standard wording, use the ISO/GB original.

## Troubleshooting

| Symptom | Cause | Action |
|---|---|---|
| `401 {"code":"INT-007"}` | Bearer header, or invalid key | Use `X-API-Key` |
| Cloudflare `error 1010` | Default HTTP-client user-agent is blocked | The bundled script sets one already; when calling directly, send a normal `User-Agent` |
| Search takes 30s | Normal — it searches and validates | Wait; do not retry in parallel |
| `missing_keys` non-empty | Key from an older catalog version | Re-run search for a current key |
| `restricted: true` | No data package | Give `purchase_url`, offer a free-database alternative; **never substitute silently** |
| Aggregation `status: "empty"` **with** `entitlement` | Commercial database, no entitlement | Same as above — **not** a predicate problem, do not retry with other predicates |
| Aggregation `status: "empty"` **without** `entitlement` | Predicate genuinely matched nothing | Broaden the predicate |
| `indicators` returns empty | `source` must equal the database the cohort lives in (`method_id` is not portable across databases) | Pass the correct `--source` |
| Cohort spans many orders of magnitude | Mixed functional units, not real spread | Narrow the predicate; read `comparability_note` |

---
name: hiq-cortex
description: 'Look up real LCA emission factors and carbon footprint data from 18 life-cycle inventory databases (Ecoinvent, BAFU, USLCI, ELCD, EF, worldsteel, AusLCI, HiQLCD …) and 24,000+ published EPDs. Use whenever a task needs an actual emission factor rather than a remembered number: material GWP lookup, product carbon footprint, BOM carbon accounting, industry benchmarking and percentile positioning, production-route comparison (BF-BOF vs EAF steel, primary vs recycled aluminium, grey vs green hydrogen), EPD peer review, CBAM and EN 15804 work. Triggers on carbon footprint, emission factor, inventory data, bill of materials, industry benchmark, GWP, kg CO2e, LCA dataset, LCI, EPD.'
slug: hiq-cortex
displayName: HiQ Cortex — LCA Data
version: 1.7.1
summary: Look up real emission factors from 18 LCA databases and 24,000+ published EPDs. Material carbon footprints, BOM accounting, industry benchmarking, production-route comparison, EPD peer review.
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags:
  - LCA
  - carbon-footprint
  - emission-factors
  - data-analysis
  - EPD
  - CBAM
---

# HiQ Cortex — LCA Data

Carbon-footprint answers must come from real inventory data. A remembered "steel ≈ 2 kg CO₂e/kg" is not usable by an LCA practitioner: the real value depends on database, version, system model, production route, and geography, and it swings by multiples across them.

## About

This skill connects to **HiQ Cortex** — the LCA data service of [HiQ Data](https://www.hiqlcd.com/). HiQ Data is a Chinese provider of LCA background data and carbon-footprint services, maintaining its own China-specific life-cycle inventory database alongside aggregated international sources.

Through this skill you can reach:

- **18 life-cycle inventory databases**, 11 of them free. Includes **China-specific data** (HiQLCD covering China's full industrial system, CALCD, HiQ-CESI for electronics and appliances, HiQLCD-AL for the aluminium value chain) and the major international sources (Ecoinvent, BAFU, ELCD, EF, worldsteel, USLCI, AusLCI, CarbonMinds, Agri-footprint …). Use China-specific databases for Chinese production — do not substitute European data.
- **24,000+ published EPDs** (EPDItaly, ECO Platform, EPD Norge) for peer distributions and outlier review.
- Alignment with ISO 14040/14044 and GB/T 24040/24044, with system models covering cut-off, consequential, APOS, and EN 15804.

Applicable to product carbon footprints, BOM carbon accounting, CBAM filing, EPD authoring and review, eco-design selection, and industry benchmarking.

## Privacy & Security

- The API key is read **only from the environment or the host's MCP config**. The skill never writes it to a file and never echoes it in output.
- Queries go **to `x.hiqlcd.com` only** (the HiQ Data API) and to no third party.
- **Nothing else is collected or uploaded** — no local files, directory structures, or conversation content.
- The bundled script uses the Python standard library only, with no third-party dependencies. The source is auditable: [GitHub](https://github.com/HiQ-AI/agent-skills).

## Ground rules

1. **Every number comes from a tool call in this session.** Never state a GWP, LCIA value, or distribution from memory. If the tool is unreachable, say so — do not fill the gap from memory.
2. **State the basis with every number**: database + version + system model + geography + reference unit. `0.0269 kg CO₂e/kWh (BAFU 2025, DEFAULT, CH, low-voltage grid)` is usable; a bare `0.027` is not.
3. **Restricted ≠ error.** Commercial databases return a restriction flag and a `purchase_url` when the account lacks that data package. Show it truthfully, give the user the link, and **never silently substitute a value from another database or from literature**. Retrying will not help. You may switch to a free database, but must label it as a substitute.
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

You can also use a credential obtained by browser sign-in (see below) — swap that line for `"Authorization": "Bearer <credential>"`. The gateway detects the credential type automatically; supply one of the two, never both.

The host usually needs a restart to pick up a new server.

### Option B — bundled script (works anywhere, zero config)

Use this when the host has no MCP support, or the user would rather not edit config files. Standard library only, no `pip install`:

```bash
python3 scripts/cortex.py login          # one click in the browser, no API key needed
python3 scripts/cortex.py search "304 stainless steel"
```

### Two ways to get a credential

**Browser sign-in (lowest friction)**

```bash
python3 scripts/cortex.py login
```

Opens an approval page; the user clicks "authorize" (a single click if already signed in to Cortex). The credential is stored at `~/.hiq/credentials.json` with mode 600, and every later command just works. Visible data matches that user's own account — **including any commercial databases they have licensed** — with nothing extra to configure.

`python3 scripts/cortex.py logout` removes the local credential. It expires with the user's session; to revoke immediately, sign out on the web.

You can run the same flow yourself without the script — it is three plain HTTP calls, so any agent that can run shell commands can do it:

```bash
# 1) start; returns verification_uri_complete + device_code
curl -sX POST https://x.hiqlcd.com/api/cortex/oauth/device_authorization \
  -H 'Content-Type: application/json' \
  -d '{"agent_id":"my-agent","agent_name":"My Agent","scope":"lca_data"}'

# 2) user opens verification_uri_complete and approves

# 3) poll until it returns access_token (428 = still pending)
curl -sX POST https://x.hiqlcd.com/api/cortex/oauth/token \
  -H 'Content-Type: application/json' -d '{"device_code":"..."}'
```

**API key (for server-side integrations / CI)**

Register at [hiqlcd.com](https://www.hiqlcd.com/), create an API key in the account console, then:

```bash
export HIQ_API_KEY=sk_xxx
```

The environment variable takes precedence over a stored sign-in credential. Rate limit: 100 requests/minute.

**Never hardcode a credential into files you generate for the user** — environment variable, the host's config file, or the file `login` writes.

## Tools

| Need | MCP tool | Script command |
|---|---|---|
| Material name → dataset key | *(none, see below)* | `search "<terms>" [--sources X]` |
| Key → GWP, basis, link | `lookup_datasets` | `lookup <key> [<key> ...]` |
| Cohort → GWP distribution, percentile position | `aggregate_datasets` | `aggregate --source X [--target N]` |
| Cohort → non-GWP LCIA indicators (AP/EP/ODP/WDP/ADP) | `aggregate_indicators` | `indicators <keys> --indicator AP --source X` |
| Single dataset → process-level hotspots | `process_hotspot` | `hotspot <key>` |
| Published EPD search | `epd_search` | `epd "<terms>" [--unit m3]` |
| EPD peer distribution, outlier check | `epd_peer_benchmark` | `epd-benchmark "<category>" --unit m3` |

Add `--json` to any script command for the raw payload.

**Search has no MCP tool** — dataset keys come from a REST endpoint that the script wraps. To call it directly:

```bash
curl -sN -X POST https://x.hiqlcd.com/api/cortex/search \
  -H "X-API-Key: sk_xxx" -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=304 stainless steel&sources=BAFU,Ecoinvent"
```

The response is SSE — parse the `WorkflowCompleted` event, then JSON-decode its `content` field. It **takes 20–40 seconds** (it searches and validates); that is normal, not a hang. Do not retry in parallel.

Keys are opaque handles. Pass them through verbatim; never construct or edit them.

**Some server-side notes come back in Chinese.** `comparability_note`, aggregation `note`, and search summaries are currently emitted in Chinese by the backend. Read them — they carry real constraints (mixed units, small sample size, missing entitlement) — and **paraphrase them in the user's language**. Never paste the raw Chinese string into an English answer, and never drop the constraint because of the language.

## Core workflow

1. **Search** for the material, product, or process → candidate keys. For route-sensitive materials (aluminium, steel, hydrogen, plastics), consult [references/materials.md](references/materials.md) first to decide which variants to search and whether clarification is needed.
2. **Read the candidate names before using them.** LCA datasets are specific: "cold-rolled annealed coil, 304 stainless" and "heavy plate, 304 stainless" are different products with different footprints. Search status `partial` means related but inexact — verify before citing.
3. **Batch the lookup** when you need values: pass all keys in one call.
4. **State the basis.** When candidates differ materially, show 2–3 and explain what drives the difference.
5. **Recommend one** only when the request supports it, and state the assumptions behind it.

## When to ask the user

LCA queries are inherently ambiguous: a single "304 stainless steel" matches a dozen datasets differing in product form, production route, geography, and system model. Handle ambiguity in this order — **search first, compare second, ask last** — not by asking upfront, and not by dumping candidates on the user.

**Do not ask when**

- The answer is already inferable from the request or conversation history. If the user said "our plant in Jiangsu", do not ask about geography.
- You have not searched yet. As soon as there is something searchable (material name, product, process, BOM line), search and deliver results in the same turn.
- The question is a generic filler in place of a real decision ("Is there anything else you'd like?").

**Compare first, don't ask**

When the user signals uncertainty ("primary or recycled aluminium", "BF-BOF or EAF", "which one should I use"), that is not a prompt to ask — it is a request for **decision support**. Instead:

1. Present the tool-backed candidates;
2. Compare them side by side under the same functional unit and system model;
3. Explain what drives the difference (energy mix, scrap share, allocation method, boundary) and under what conditions the conclusion flips;
4. Give a conditional recommendation where the evidence supports one ("for a Chinese grid with 30% recycled content, choose X").

A complete advisory answer can end there, with no follow-up question.

**Do ask when**

Only when the user must settle on **one** dataset and the remaining ambiguity would materially change the result. In that case:

- Options must correspond to **candidates you already showed** — do not invent options;
- Spell out what each option means (which route, which geography, which basis);
- Use the host's interaction capability (tool names differ per host — use `AskUserQuestion` / `AskQuestion` if available; otherwise just ask clearly in the reply);
- Do not present interactive options and a duplicate written list of the same options.

Once the user answers, complete the match against results you already have — do not re-run the same search.

## Scenario routing

Route first, top to bottom, first match wins. Routing wrong wastes the whole turn — if the user asks "is mine high or low" and you return a single lookup, you answered a different question.

| Signal | Action |
|---|---|
| User gives **their own** number and asks where it sits ("is my 2.5 high or low", "how do we compare to peers") | `aggregate` with a cohort predicate + `--target` → percentile positioning. Method and comparability gates in [references/scenarios.md](references/scenarios.md) |
| No BOM yet, wants an order of magnitude or an A/B comparison ("roughly what scale") | Decompose by composition + combine p25–p75 ranges per material → give a **range**, never a falsely precise point value. See [references/scenarios.md](references/scenarios.md) |
| Route-sensitive material (BF-BOF vs EAF steel, primary vs recycled aluminium, grey vs green hydrogen) | Search and aggregate each route separately, compare under one functional unit — see [references/comparability.md](references/comparability.md) |
| A material or BOM to match against datasets | Search → batch lookup. Material families, route distinctions, and product decomposition in [references/materials.md](references/materials.md) |
| "Is this EPD value reasonable?" | `epd-benchmark` with an explicit `--unit`; cross-unit comparison is meaningless |
| Multi-indicator assessment (acidification, eutrophication …) | `indicators`, one indicator at a time; `--source` must match the cohort's database |

## Data entitlements

| Tier | Content | Requirement |
|---|---|---|
| Catalogue | Listing, versions, system models, and LCIA coverage of all 18 databases; dataset names, units, geographies | No entitlement |
| Free-database values | GWP and aggregate statistics for BAFU, USLCI, ELCD, EF, AusLCI, NEEDS, ozLCI, worldsteel, USDA, bioenergiedat, recycledplastics | Any valid key |
| Commercial-database values | GWP and aggregate statistics for Ecoinvent, HiQLCD, HiQLCD-AL, CarbonMinds, Agri-footprint, CALCD, HiQ-CESI | Corresponding data-package entitlement |

Without entitlement, `lookup` returns `restricted: true` and aggregation returns `status: "empty"` with an `entitlement` field; both carry a `purchase_url`. Tell the user which database is restricted and give them the link; if a free database can answer the same question, offer that path. Data-package entitlements and subscription plans are **two independent systems** — upgrading a plan does not unlock databases.

The free databases cover a lot of ground: BAFU (Switzerland, complete LCIA, the best free default in a European context), USLCI (US unit processes), ELCD / EF (European reference), worldsteel (global steel), USDA (agriculture).

## References

| File | Content |
|---|---|
| [references/materials.md](references/materials.md) | Material families: production routes, search terms, geographic sensitivity, unit mismatches, and product decomposition for steel, aluminium, plastics, chemicals, energy, transport |
| [references/databases.md](references/databases.md) | Versions, system models, and LCIA coverage of all 18 databases; how to choose; known pitfalls |
| [references/comparability.md](references/comparability.md) | The five comparability dimensions, how to read aggregate results, production-route comparison, EPD comparison, proxy-data discipline |
| [references/scenarios.md](references/scenarios.md) | Full method for industry benchmarking and lightweight estimation; composition proxies |

## Tone and terminology

You are writing for LCA practitioners. Write like a knowledgeable peer.

- No pleasantries ("I hope this helps", "let me help you with that"), no adjective stacking, no summarising sign-off.
- Use the standard vocabulary of ISO 14040/14044, ILCD, and GB/T 24040 — for this audience, standard terms are **clearer** than plain language, not less clear.
- unit process · elementary flow · intermediate flow · reference flow · functional unit · system boundary · impact category · category indicator · characterization factor · cut-off · consequential.
- Do not invent terminology. When unsure of the standard name, use the ISO/GB wording verbatim.

## Troubleshooting

| Symptom | Cause | Action |
|---|---|---|
| `401 {"code":"INT-007"}` | Bearer used, or invalid key | Switch to `X-API-Key` |
| CDN returns `error 1010` | Default HTTP-client User-Agent is blocked | The bundled script sets one; when calling directly, send a normal `User-Agent` |
| Search takes 30 seconds | Normal — it searches and validates | Wait; do not retry in parallel |
| `missing_keys` non-empty | Keys came from an older catalogue version | Search again for current keys |
| `restricted: true` | No data-package entitlement | Give the `purchase_url`; a free-database alternative is fine; **never silently substitute the value** |
| Aggregate `status: "empty"` **with** `entitlement` | Commercial database, no entitlement | As above — this is **not** a predicate problem; do not retry with a different predicate |
| Aggregate `status: "empty"` **without** `entitlement` | The predicate genuinely matched nothing | Loosen the predicate |
| `indicators` returns empty | `source` must equal the cohort's actual database (`method_id` is not portable across databases) | Pass the correct `--source` |
| Cohort values span several orders of magnitude | Mixed functional units, not real dispersion | Narrow the predicate; read `comparability_note` first |
| Polling returns `428` | The user has not approved yet | Normal — keep polling at the returned `interval`; do not treat it as a failure |
| Still restricted after signing in | That account genuinely lacks the data package | Signing in swaps the credential, it does not grant entitlements — surface the purchase link |

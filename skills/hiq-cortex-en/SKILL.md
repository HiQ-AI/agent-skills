---
name: hiq-cortex
description: 'Look up real LCA emission factors and carbon footprint data from 18 life-cycle inventory databases (Ecoinvent, BAFU, USLCI, ELCD, EF, worldsteel, AusLCI, HiQLCD …) and 24,000+ published EPDs. Use whenever a task needs an actual emission factor rather than a remembered number: material GWP lookup, product carbon footprint, BOM carbon accounting, industry benchmarking and percentile positioning, production-route comparison (BF-BOF vs EAF steel, primary vs recycled aluminium, grey vs green hydrogen), EPD peer review, CBAM and EN 15804 work. Triggers on carbon footprint, emission factor, inventory data, bill of materials, industry benchmark, GWP, kg CO2e, LCA dataset, LCI, EPD.'
slug: hiq-cortex
displayName: HiQ Cortex — LCA Data
version: 1.8.0
summary: Look up real emission factors from 18 LCA databases and 24,000+ published EPDs. Material carbon footprints, BOM accounting, industry benchmarking, production-route comparison, EPD peer review.
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags: [LCA, carbon-footprint, emission-factor, EPD, CBAM, ecoinvent, HiQLCD, GWP, LCI, life-cycle-assessment]
---

# HiQ Cortex — LCA Data

Carbon footprint answers must come from real inventory data. A remembered "steel is about 2 kg CO₂e/kg" is useless to an LCA practitioner: the real value depends on database, version, system model, production route, and geography, and varies several-fold across those dimensions.

## About

This skill connects to **HiQ Cortex** — the LCA data service of [HiQ (海科数据)](https://www.hiqlcd.com/), a Chinese provider of LCA background data and carbon footprint services that maintains its own China-specific life-cycle inventory databases and aggregates major international sources.

Available:

- **18 life-cycle inventory databases**, 11 of them free. Includes China-specific data (HiQLCD covering China's full industrial system, CALCD, HiQ-CESI for electronics, HiQLCD-AL for the aluminium value chain) alongside international sources (Ecoinvent, BAFU, ELCD, EF, worldsteel, USLCI, AusLCI, CarbonMinds, Agri-footprint …).
- **24,000+ published EPDs** (EPDItaly, ECO Platform, EPD Norge) for peer distributions and outlier review.
- ISO 14040/14044 and GB/T 24040/24044 conventions; system models covering cut-off, consequential, APOS, and EN 15804.

**Search runs server-side.** Pass the user's own wording or raw BOM lines straight to the search endpoint — translating material names into LCA terminology, identifying production routes, and mapping categories to process direction all happen on the server. Returned candidates are already ranked and carry a match-quality marker. Do not re-derive search terms locally.

## Privacy and security

- The API key is **read only from the environment or the host's MCP config**. The skill never writes it to a file and never echoes it in output.
- Queries go **only to `x.hiqlcd.com`** (HiQ's API), never to any third party.
- **Nothing is collected or uploaded** — no local files, directory structure, or conversation content.
- The bundled script uses only the Python standard library, no third-party dependencies, and the source is auditable on [GitHub](https://github.com/HiQ-AI/agent-skills).

## Hard rules

1. **Every number must come from a tool call in this session.** Never state a GWP, LCIA value, or distribution from memory. If the tools are unavailable, say so — do not fill the gap.
2. **Every number needs its basis**: database + version + system model + geography + reference unit. `0.0269 kg CO₂e/kWh (BAFU 2025, DEFAULT, CH, low-voltage grid)` is usable; a bare `0.027` is not.
3. **Restricted is not an error.** Commercial databases return a restriction marker and a `purchase_url` when the account lacks the data package. Show it, hand the user the link, and **never silently substitute a value from another database or the literature**. Retrying does not help. A free database may be used instead, but say that it is a substitution.
4. **Do not compare across conventions.** Data with different functional units, system models, or system boundaries is not comparable — say so rather than presenting a misleading delta. Read `comparability_note` first; that is what it is for.

## Access

Two ways to get credentials:

```bash
python3 scripts/cortex.py login    # browser sign-in, no registration or key creation needed
export HIQ_API_KEY=sk_xxx          # or an API key (server-side / CI); takes precedence
```

`login` opens an authorization page; one click stores credentials in `~/.hiq/credentials.json` (mode 600). The visible data scope matches that account, **including any commercial databases it has access to**. `logout` removes the local credentials.

The flow is three plain HTTP requests (standard device flow, RFC 8628) — any agent that can run a shell can do it without the script:

```bash
curl -sX POST https://x.hiqlcd.com/api/cortex/oauth/device_authorization \
  -H 'Content-Type: application/json' \
  -d '{"agent_id":"my-agent","agent_name":"My Assistant","scope":"lca_data"}'
# hand the returned verification_uri_complete to the user → they approve
curl -sX POST https://x.hiqlcd.com/api/cortex/oauth/token \
  -H 'Content-Type: application/json' -d '{"device_code":"..."}'   # 428 = not yet approved, keep polling
```

Prefer MCP when the host supports it. If `lookup_datasets`, `aggregate_datasets`, `epd_search` are already available in this session, use them. Otherwise add this to the host's MCP config (WorkBuddy `~/.workbuddy/mcp.json`, Claude Code `~/.claude.json`, Cursor `~/.cursor/mcp.json`) and restart the host:

```json
{
  "mcpServers": {
    "cortex": {
      "type": "http",
      "url": "https://x.hiqlcd.com/api/cortex/mcp",
      "headers": { "X-API-Key": "sk_xxx" }
    }
  }
}
```

Credentials from `login` work too — replace that line with `"Authorization": "Bearer <credential>"`.

**Never hard-code credentials into files generated for the user.**

## Tools

| Need | MCP tool | Script command |
|---|---|---|
| Material / BOM line → dataset key | *(none, see below)* | `search "<user's wording>" [--sources X]` |
| Key → GWP, basis, links | `lookup_datasets` | `lookup <key> [<key> ...]` |
| Cohort → GWP distribution, percentile positioning | `aggregate_datasets` | `aggregate --source X [--target N]` |
| Cohort → non-GWP LCIA indicators (AP/EP/ODP/WDP/ADP) | `aggregate_indicators` | `indicators <keys> --indicator AP --source X` |
| Single dataset → process-level hotspots | `process_hotspot` | `hotspot <key>` |
| Published EPD search | `epd_search` | `epd "<query>" [--unit m3]` |
| EPD peer distribution, outlier check | `epd_peer_benchmark` | `epd-benchmark "<category>" --unit m3` |

Add `--json` to any script command for the raw payload.

Search has no MCP tool — it is a REST endpoint, wrapped by the script. Direct call:

```bash
curl -sN -X POST https://x.hiqlcd.com/api/cortex/search \
  -H "X-API-Key: sk_xxx" -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=304 stainless steel&sources=BAFU,Ecoinvent"
```

The response is SSE — parse the `WorkflowCompleted` event, then JSON-decode its `content` field. **It takes 20–40 seconds** (the server searches and verifies each hit). That is normal, not a hang; do not retry in parallel.

`dataset_key` is an opaque handle — pass it through unchanged, never construct or edit one.

## Reading the response

| Field | Meaning | What to do |
|---|---|---|
| `status: found` / `partial` / `not_found` | `partial` = results found, some restricted | Show them; handle restricted per hard rule 3 |
| `summary` | The server's account of this search | Relay it; do not invent a competing explanation |
| `fit: high / medium / low` | Server-assigned match quality | Confirm with the user before citing a `low` |
| `name` / `ref_product` / `location` | Dataset name, reference flow, geography | Read before citing — "cold-rolled annealed coil" and "heavy plate" are different products |
| `restricted: true` | No data package for that database | Give the `purchase_url`; a free-database alternative must be labelled as such |
| `missing_keys` non-empty | Key came from an older catalogue version | Search again; do not hand-edit keys |
| `comparability_note` | Cohort comparability caveats | Read before comparing |
| `entitlement` | An empty aggregate is an entitlement issue, not a predicate issue | Do not retry with a different predicate |

## Scenario routing

Top to bottom, first match wins.

| Signal | What to do |
|---|---|
| User gives **their own** number and asks where it sits ("is my 2.5 high or low") | `aggregate` with a cohort predicate + `--target` → percentile positioning |
| A material or BOM to match against datasets | `search` → batch `lookup` |
| Comparing two production routes (BF-BOF vs EAF steel, primary vs recycled aluminium) | Search and aggregate each route separately, compare under one functional unit |
| "Is this EPD value reasonable" | `epd-benchmark` with an explicit `--unit`; cross-unit comparison is meaningless |
| Multi-indicator assessment (acidification, eutrophication …) | `indicators`, one indicator at a time; `--source` must match the cohort's database |

## When to ask the user

**Search first, compare second, ask last.** If there is anything searchable — a material name, product, process, or BOM line — search it and give results in the same turn. Do not ask for information already stated in the conversation.

"I'm not sure which one to use" is a **decision-support signal, not a question**: give the candidate list, compare under one convention, explain which dimension drives the difference, and give a conditional recommendation where the evidence supports one. A complete advisory answer can end there.

Only ask when a single dataset must be finalised and the remaining ambiguity would materially change the result. Options must correspond to **candidates already shown** — never invent them. Use the host's interaction facility if one exists, and do not duplicate the options as a text list. After the answer, complete the match on the existing results; do not re-run the same search.

## Data entitlements

| Tier | Content | Requirement |
|---|---|---|
| Catalogue | All 18 databases: inventory, versions, system models, LCIA coverage; dataset names, units, geographies | None |
| Free database values | GWP and aggregates for BAFU, USLCI, ELCD, EF, AusLCI, NEEDS, ozLCI, worldsteel, USDA, bioenergiedat, recycledplastics | Any valid credential |
| Commercial database values | GWP and aggregates for Ecoinvent, HiQLCD, HiQLCD-AL, CarbonMinds, Agri-footprint, CALCD, HiQ-CESI | Matching data package |

Data packages and subscription plans are **two separate systems** — upgrading a plan does not unlock a database. When something is restricted, name the database, hand over the `purchase_url`, and offer a free-database path if one answers the same question, labelled as a substitution.

## Voice and terminology

Write for LCA practitioners, like a knowledgeable peer.

- No pleasantries ("I hope this helps", "let me help you"), no adjective stacking, no summarising sign-off.
- Use ISO 14040/14044, ILCD, and GB/T 24040 terminology — for this audience, standard terms are **clearer** than plain language.
- unit process · elementary flow · reference flow · functional unit · system boundary · impact category · characterisation factor · cut-off · consequential.
- Do not invent terminology. When unsure of the standard term, use the ISO wording.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `401 {"code":"INT-007"}` | Used Bearer, or the key is invalid | Use `X-API-Key` |
| CDN returns `error 1010` | Default HTTP client User-Agent is blocked | The bundled script sets one; add a normal `User-Agent` on direct calls |
| Search takes 30 seconds | Normal — it searches and verifies | Wait; do not retry in parallel |
| Aggregate `status: "empty"` **with** `entitlement` | Commercial database, no package | Not a predicate problem; do not retry |
| Aggregate `status: "empty"` **without** `entitlement` | The predicate genuinely matched nothing | Broaden the predicate |
| `indicators` returns empty | `source` must equal the cohort's actual database (`method_id` is not portable) | Pass the correct `--source` |
| Cohort values span orders of magnitude | Mixed functional units, not real dispersion | Narrow the predicate; read `comparability_note` first |
| Authorization polling returns `428` | The user has not approved yet | Normal — keep polling at the returned `interval` |
| Still no commercial data after login | That account has no such data package | Login only changes credentials, not entitlements; show the purchase link |

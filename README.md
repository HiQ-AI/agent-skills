# HiQ Agent Skills

Open [Agent Skills](https://code.claude.com/docs/en/skills) published by [HiQ](https://www.hiqlcd.com/) for LCA and carbon-footprint work. Each skill is a plain `SKILL.md` plus a dependency-free Python client, and works in any host that loads Agent Skills — WorkBuddy, Claude Code, Cursor, Cline, Codex, and others.

## Skills

| Skill | What it does | SkillHub slug |
|---|---|---|
| [`hiq-cortex`](skills/hiq-cortex/) | Look up real LCA emission factors from 18 life-cycle inventory databases (Ecoinvent, BAFU, USLCI, ELCD, EF, worldsteel …) and 24,000+ published EPDs. Material GWP lookup, BOM carbon accounting, industry benchmarking, production-route comparison, EPD peer review. | `hiq-cortex-lca` |
| [`ecoinvent`](skills/ecoinvent/) | Find the right ecoinvent dataset and read its conventions — system model, geography, reference flow, version — and state the basis behind every number. | `ecoinvent` |
| [`hiqlcd`](skills/hiqlcd/) | China-specific inventory data (HiQLCD, HiQLCD-AL, HiQ-CESI, CALCD) for production located in China, under GB/T 24040 conventions. | `hiqlcd` |
| [`cbam`](skills/cbam/) | Pull traceable inventory data for CBAM reporting across the six covered categories — steel, aluminium, cement, fertiliser, electricity, hydrogen. | `cbam` |
| [`pcf`](skills/pcf/) | Product carbon footprint accounting from a BOM: match each line to a dataset, pull GWP, roll up to product level, keep every line auditable. | `pcf` |
| [`en15804`](skills/en15804/) | EN 15804 construction-product work: published EPD search, peer distributions and outlier fences by declared unit and module. | `en15804` |
| [`lca`](skills/lca/) | Full LCA data work — not just carbon: acidification, eutrophication, ozone depletion, water and resource use, plus process-level hotspots. | `lca` |
| [`scope3`](skills/scope3/) | Scope 3 supply-chain accounting: match a purchasing list line by line, keep every row traceable for CDP / ISSB / SBTi reporting. | `scope3` |
| [`iso14067`](skills/iso14067/) | ISO 14067 product carbon footprints: pull data and record its provenance to the level a third-party verifier expects. | `iso14067` |
| [`carbonminds`](skills/carbonminds/) | Process-level inventory data for chemicals and polymers — distinguish synthesis routes, feedstock origin, and geography. | `carbonminds` |
| [`calcd`](skills/calcd/) | CALCD, the Chinese life-cycle reference database, under GB/T 24040 conventions. | `calcd` |
| [`ghg-protocol`](skills/ghg-protocol/) | Corporate GHG accounting: emission factors for scope 1 fuels, scope 2 electricity and heat, and scope 3 upstream, each traceable. | `ghg-protocol` |
| [`pef`](skills/pef/) | EU Product Environmental Footprint: EF reference-package datasets and the full set of impact categories, not just carbon. | `pef` |
| [`battery-passport`](skills/battery-passport/) | Battery passport and battery carbon footprint: cathode, anode, electrolyte, separator, current collectors, cell assembly. | `battery-passport` |
| [`hiqlcd-al`](skills/hiqlcd-al/) | Aluminium value chain — alumina, smelting, casting, extrusion, die casting, and recycled aluminium, cut-off and consequential. | `hiqlcd-al` |
| [`hiq-editor`](skills/hiq-editor/) | **Authoring**, not lookup: create unit process datasets in the HiQ editor, add exchanges, match background data, trial-calculate, submit for review, bulk-import UPR templates. Requires editor entitlement. | `hiq-editor` |

All of them are on [SkillHub](https://skillhub.cn/) (WorkBuddy / OpenClaw and variants):

```bash
skillhub install <slug> --dir <your agent's skills dir>
```

## Install

With [`npx skills`](https://github.com/vercel-labs/skills):

```bash
npx skills add HiQ-AI/agent-skills --skill hiq-cortex
# also: lca · ecoinvent · hiqlcd · hiqlcd-al · calcd · carbonminds · cbam · pef · pcf · scope3
#       iso14067 · en15804 · ghg-protocol · battery-passport · hiq-editor
```

Or copy the skill directory into your host's skills folder:

| Host | Path |
|---|---|
| WorkBuddy | `~/.workbuddy/skills/` or `<project>/.workbuddy/skills/` |
| Claude Code | `~/.claude/skills/` or `<project>/.claude/skills/` |
| Cursor | `~/.cursor/skills/` |

## Getting data access

These skills talk to the HiQ Cortex API. The quickest way in is browser sign-in — no registration, no key to create:

```bash
curl -fsSL https://download.hiq.earth/cli/hiq-cortex/install.sh | sh   # macOS / Linux
hiq-cortex login
```

One click on the authorization page stores a credential in
`~/.config/hiq-cortex/credentials.json` (mode 600); the visible data scope matches that account. For server-side use or CI, register at [hiqlcd.com](https://www.hiqlcd.com/), create an API key in the account console, and export it instead:

```bash
export HIQ_API_KEY=sk_xxx
```

…or configure the MCP server (the skill explains both, and the agent can set it up for you):

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

11 of the 18 databases (BAFU, USLCI, ELCD, EF, worldsteel, USDA and more) are available to any valid key. Commercial databases require a data package — the skill surfaces that clearly instead of failing, and points to [where to obtain one](https://carbonx.hiqlcd.com/price).

## Notes

- Skills bundle **no credentials**. Keys come from the environment or the host's config.
- Packages carry nothing but instructions — the client is the CLI, installed once.
- Issues and contributions welcome via GitHub issues.

## The CLI

Query skills drive [`@hiq-ai/hiq-cortex-cli`](https://github.com/HiQ-AI/hiq-cortex-cli)
(Apache-2.0):

```bash
hiq-cortex login
hiq-cortex search "304 不锈钢"
```

A single self-contained executable — no Node, no Python, nothing else on the machine. Install it
with the one-liner above, or run `npx @hiq-ai/hiq-cortex-cli <command>` where Node is already
present.

It used to be a Python script vendored into all sixteen packages; folding it into one CLI means a
client fix ships once instead of republishing every skill. Credentials written by that script
(`~/.hiq/credentials.json`) are still read, so nobody has to sign in again.

## Repo layout

```
skills/<name>/SKILL.md       # per-skill instructions — that is the whole package
scripts/publish-skillhub.sh  # publish to SkillHub (rate-limited, one at a time)
```

Each package is deliberately thin: how to call, what to pass, how to read the response. Domain
judgement — translating material names, identifying production routes, ranking and scoring
candidates — runs server-side, so it stays current without republishing skills.

## License

[Apache-2.0](LICENSE)

# HiQ Agent Skills

Open [Agent Skills](https://code.claude.com/docs/en/skills) published by [HiQ](https://www.hiqlcd.com/) for LCA and carbon-footprint work. Each skill is a plain `SKILL.md`, and works in any host that loads Agent Skills — WorkBuddy, Claude Code, Cursor, Cline, Codex, and others.

## Skills

| Skill | What it does | SkillHub slug |
|---|---|---|
| [`hiq-cortex`](skills/hiq-cortex/) | Look up real LCA emission factors from 18 life-cycle inventory databases (Ecoinvent, BAFU, USLCI, ELCD, EF, worldsteel …) and 24,000+ published EPDs. Material GWP lookup, BOM carbon accounting, multi-indicator LCIA and process contributions, production-route comparison, EPD lookup. | `hiq-cortex-lca` |
| [`ecoinvent`](skills/ecoinvent/) | Find the right ecoinvent dataset and read its conventions — system model, geography, reference flow, version — and state the basis behind every number. | `ecoinvent` |
| [`hiqlcd`](skills/hiqlcd/) | China-specific inventory data (HiQLCD, HiQLCD-AL, HiQ-CESI, CALCD) for production located in China, under GB/T 24040 conventions. | `hiqlcd` |
| [`cbam`](skills/cbam/) | Pull traceable inventory data for CBAM reporting across the six covered categories — steel, aluminium, cement, fertiliser, electricity, hydrogen. | `cbam` |
| [`pcf`](skills/pcf/) | Product carbon footprint accounting from a BOM: match each line to a dataset, pull GWP, roll up to product level, keep every line auditable. | `pcf` |
| [`en15804`](skills/en15804/) | EN 15804 construction-product work: published EPD search and side-by-side comparison by declared unit and module. | `en15804` |
| [`lca`](skills/lca/) | Full LCA data work — not just carbon: acidification, eutrophication, ozone depletion, water and resource use, plus stage-level process contributions. | `lca` |
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

Query skills read data through the [Environmental Data CLI](https://github.com/HiQ-AI/environmental-data) — two single-file programs, no Node or Python needed:

- `environmental-data` — background LCI databases (`--sources` picks databases): `search`, `lookup`, `lci`, `lcia`, `methods`;
- `epd-data` — published EPDs: `search`, `lookup`.

Installers are version-pinned with SHA256 checksums in
[installation.json](https://github.com/HiQ-AI/environmental-data/blob/main/plugins/environmental-data/skills/environmental-data-query/references/installation.json).
Download into an empty directory, verify, then run — not `curl | sh`:

```bash
d=$(mktemp -d)
curl -fsSL -o "$d/install.sh" https://download.hiq.earth/cli/environmental-data/releases/v0.9.0/environmental-data/install.sh
shasum -a 256 "$d/install.sh"   # f13f1d47dd9e5a638a346d70d78bc4b5ba4053dd84192e4083b1153ae244924e
sh "$d/install.sh"

environmental-data login --json   # device sign-in: open the printed link and approve
environmental-data search 'stainless steel 304' --json
```

In Claude Code you can also add the marketplace with `/plugin marketplace add HiQ-AI/environmental-data` (the plugin
carries instructions; the program is still installed as above).

Every registered user can read free-database values (BAFU, USLCI, ELCD, EF, worldsteel, USDA and more). Commercial
values additionally require that HiQ has enabled Environmental Data CLI commercial access for the account, and stay
limited to its data packages — the skills surface restricted rows clearly instead of failing; data packages are
listed [here](https://carbonx.hiqlcd.com/price). `lookup` (including GWP100) also works
with an API key (`QUERYING_LCA_DATASETS_API_KEY`), within that key's entitlements and quota; `lci`, `lcia` and
`methods` reject API keys and need `login`.

The old `hiq-cortex` / `@hiq-ai/hiq-cortex-cli` client and the Cortex MCP endpoint
(`https://x.hiqlcd.com/api/cortex/mcp`, shutting down 2026-11-25) are retired and no longer used by these skills.
There is no replacement for the cohort-distribution, percentile and EPD peer-benchmark tools; skills compare
explicitly named candidates instead.

## Notes

- Skills bundle **no credentials**. The CLI stores its own sign-in.
- Packages carry nothing but instructions — the client is the CLI, installed once.
- Issues and contributions welcome via GitHub issues.

## Repo layout

```
skills/<name>/SKILL.md       # per-skill instructions — that is the whole package
scripts/publish-skillhub.sh  # publish to SkillHub (rate-limited, one at a time)
```

Each package is deliberately thin: how to call, what to pass, how to read the response. Requirement-level
matching — translating material names, identifying production routes — is available server-side through
`search --assist`, so it stays current without republishing skills.

## License

[Apache-2.0](LICENSE)

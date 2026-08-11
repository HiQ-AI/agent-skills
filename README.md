# HiQ Agent Skills

Open [Agent Skills](https://code.claude.com/docs/en/skills) published by [HiQ](https://www.hiqlcd.com/) for LCA and carbon-footprint work. Each skill is a plain `SKILL.md` plus supporting scripts and references, and works in any host that loads Agent Skills — WorkBuddy, Claude Code, Cursor, Cline, Codex, and others.

## Skills

| Skill | What it does |
|---|---|
| [`hiq-cortex`](skills/hiq-cortex/) | Look up real LCA emission factors from 18 life-cycle inventory databases (Ecoinvent, BAFU, USLCI, ELCD, EF, worldsteel …) and 24,000+ published EPDs. Material GWP lookup, BOM carbon accounting, industry benchmarking, production-route comparison, EPD peer review. |

Also on [SkillHub](https://skillhub.cn/skills/user_377d1060/hiq-cortex-lca) (WorkBuddy / OpenClaw and variants), where the skill is published under the slug `hiq-cortex-lca`:

```bash
skillhub install hiq-cortex-lca --dir <your agent's skills dir>
```

## Install

With [`npx skills`](https://github.com/vercel-labs/skills):

```bash
npx skills add HiQ-AI/agent-skills --skill hiq-cortex
```

Or copy the skill directory into your host's skills folder:

| Host | Path |
|---|---|
| WorkBuddy | `~/.workbuddy/skills/` or `<project>/.workbuddy/skills/` |
| Claude Code | `~/.claude/skills/` or `<project>/.claude/skills/` |
| Cursor | `~/.cursor/skills/` |

## Getting data access

The LCA skill talks to the HiQ Cortex API. Register at [hiqlcd.com](https://www.hiqlcd.com/) and create an API key in the account console, then either export it:

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
- Scripts use the Python standard library only — no `pip install`.
- Issues and contributions welcome via GitHub issues.

## License

[Apache-2.0](LICENSE)

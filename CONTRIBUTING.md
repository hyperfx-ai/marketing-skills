# Contributing

Thanks for considering a contribution. This repo is a collection of marketing skills that wrap the Hyper MCP. Below is everything you need to add a new skill or improve an existing one.

## Skill structure

```
skills/<skill-name>/
├── SKILL.md              # required, ≤500 lines
├── references/           # optional, long-form docs loaded on demand
└── scripts/              # optional, helper scripts (rare for MCP wrappers)
```

## SKILL.md authoring rules

1. **Frontmatter** — two fields only:

   ```yaml
   ---
   name: <kebab-case-name>          # MUST match the folder name
   description: <50–500 chars>      # MUST contain a "Use when…" trigger phrase
   ---
   ```

2. **Body must contain**:
   - A short purpose paragraph.
   - A `## Requirements` section that links to `https://app.hyperfx.ai/mcp` and names the integrations the user must connect.
   - A `## Tool surface` table naming the MCP tools the skill calls.
   - The actual workflow (phases, decision tables, code samples).

3. **Body must NOT contain**:
   - Internal infra references (`hyper_cache_*` table names, internal filesystem paths, internal agent template names).
   - Real account IDs, real customer data, or real auth tokens.
   - Any Hyper URL other than `app.hyperfx.ai/mcp` and `app.hyperfx.ai/apps`.

4. **Length cap**: 500 lines max. Move long-form material into `references/<topic>.md` and link to it.

5. **Cross-referencing**: when a sibling skill is the better fit for part of a request, add a short `## Out of scope` section listing those siblings. Don't duplicate workflow.

## Validating before you push

```bash
./validate-skills.sh
```

The script checks frontmatter, name/folder match, length, the Requirements section, and a banned-strings list. CI runs the same check on every PR.

## Releasing

The current release version lives in both `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`. Keep those versions in sync.

When a commit lands on `main`, the release workflow validates the skills, reads that version, creates the matching `v<version>` tag if it does not exist, and creates a GitHub Release. If the tag/release already exists, the workflow skips it. To publish a new release, bump both manifest versions in the PR before merging.

## Reporting issues

Open an issue with:
- The skill name.
- The MCP version / toolkit you have connected.
- A minimal repro of the agent behavior.

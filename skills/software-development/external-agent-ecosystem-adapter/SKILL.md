---
name: external-agent-ecosystem-adapter
description: >-
  Adapt external AI agent ecosystems like ECC so their skills, commands,
  and rules are usable inside Hermes without role/model/MCP conflicts.
  Covers both importing a third-party agent framework and resolving
  competition between Hermes and an existing repo.
triggers:
  - import external ecosystem
  - adapt ECC to Hermes
  - fix repo competition
  - resolve agent repo conflicts
  - demote orchestrator to resource library
  - align model defaults between repos
---

# External Agent Ecosystem Adapter

## When to Use

- User provides a GitHub repo for an external agent ecosystem (e.g. ECC)
- Goal is to use that ecosystem's skills inside Hermes
- Repo targets another harness (Claude Code, OpenCode, etc.)

## Procedure — Phase 1: Import & Install

1. Clone the repo into the user's project directory if not already there.
2. Run the repo's installer/package manager (`npm install`, `install.ps1`, `install.sh`).
3. Copy the repo's skill assets into `~/.hermes/skills/<eco-name>/`.
4. If the repo supports native harness targets (OpenCode, Claude Code), install to those locations too.
5. Verify by counting SKILL.md files and checking content fidelity against the source clone.
6. **Update the `/setup` skill**: After installing, the `/setup` skill's Phase 0 (Environment Scan) should be updated to recognize this new ecosystem in future setup sessions. Add an entry to the `/setup` skill's "Complementary Integration" section noting how this ecosystem relates to existing repos.
7. **Update the `/decide` skill**: Add a Known Integration Pattern entry for this ecosystem so the decide skill knows to route to `external-agent-ecosystem-adapter` alongside `setup` when this ecosystem is detected.

## Procedure — Phase 2: Conflict Resolution

An external agent ecosystem (ECC, devfleet, etc.) is often designed as a **standalone orchestrator** with its own model preferences, agent routing, and MCP configs. When imported into Hermes, it must be **demoted** from orchestrator to resource/skill library. Always run Phase 2 after Phase 1.

### 2a — Check Model Preferences

External ecosystems often default to paid models (Claude Opus, GPT-4). Hermes uses a free-model-first workflow.

```bash
# Read agent defaults
cat <eco-dir>/agent.yaml       # check 'model:' block
cat <eco-dir>/CLAUDE.md        # check for model mentions
cat <eco-dir>/AGENTS.md        # check for model routing rules
```

**Fix:** Replace paid model IDs with Hermes-compatible free models (e.g. `opencode/deepseek-v4-flash-free`). Add a YAML comment stating the ecosystem is a resource library for Hermes — model routing is owned by Hermes' decide skill.

### 2b — Check Orchestration Role Claims

Ecosystem files often claim orchestrator identity — "agent-first", "use agents proactively", "delegate to specialized agents". These conflict with Hermes' `decide` skill interpreting them as routing directives.

Check these files for competing claims:
- `AGENTS.md` — agent orchestration section, core principles, agent routing tables
- `CLAUDE.md` — orchestrator identity, project overview claiming "Claude Code plugin"
- `SOUL.md` — ecosystem identity ("agent operating system", "production-ready AI plugin")
- `agent.yaml` — role/type field, preferred model, fallback chain

**Fix:** Add a **Role Clarification** block at the top of each file:
```markdown
> **Role Clarification:** <Eco-Name> is a **skill/resource library** for AI coding agents (Hermes, Claude Code, OpenCode, etc.) — it provides agents, skills, rules, and patterns that any orchestrator can draw upon. It is NOT a competing orchestrator.
> **Hermes' `decide` skill** is the master orchestrator that routes tasks to <Eco-Name> resources when needed.
```

### 2c — Check MCP Server Conflicts

External ecosystems often ship with extensive MCP server definitions. These may overlap with Hermes' registered MCP servers (same port, same name, same tool).

```bash
# List ecosystem MCP configs
ls <eco-dir>/mcp-configs/         # reference configs
cat <eco-dir>/.mcp.json           # active MCP if present

# Compare with Hermes MCP servers
cat ~/AppData/Local/hermes/config.yaml
```

**Check for conflicts:**
- **Same server name** (e.g. `github`, `supabase`, `firecrawl`) — ecosystem may define its own version with different args/env
- **Same port** (e.g. `localhost:3000`, `localhost:18801`) — port competition between ecosystem MCP daemons
- **Same tool names** — tool name overlap causes ambiguous routing

**Fix:**
- Ecosystem config files with `YOUR_*_HERE` placeholders are **reference-only** — they don't auto-register. Note this in docs and move on.
- Active `.mcp.json` files that conflict with Hermes: either disable the conflicting ecosystem MCP or exclude it from Hermes' MCP server loading.
- Document which ecosystem MCP servers are reference-only vs active.

### 2d — Check Port Competition

Some ecosystems start dev servers or daemons that compete with Hermes tools (e.g. port 3000).

```bash
# Check if ecosystem's default ports are free
netstat -ano | grep ':3000' | grep LISTEN   # common dev server
netstat -ano | grep ':18801'                # devfleet, etc.
```

**Fix:** If a port is free, note it in docs. If busy, decide which service owns it and re-configure the other.

### 2e — Update Role Boundaries in Doc Files

After fixing the above, update key ecosystem files so future sessions recognize the resource-library role:

- **`AGENTS.md`**: Add role clarification block; retitle "Agent Orchestration" section to "Available Resources"
- **`CLAUDE.md`**: Add role clarification block referencing AGENTS.md
- **`agent.yaml`**: Add role comment; replace paid model defaults with free models

### 2f — Final Verification

```bash
# Confirm model defaults are free
grep -A3 'preferred:' <eco-dir>/agent.yaml

# Confirm role clarification in place
head -5 <eco-dir>/AGENTS.md
head -5 <eco-dir>/CLAUDE.md

# Confirm no port conflicts (pick a port the eco might use)
netstat -ano | grep ':3000' | grep LISTEN

# Build the ecosystem's website/tool (if any)
cd <eco-dir>/website && npx next build 2>&1 | tail -5

# Verify the ecosystem's CLI (if any)
<cli-tool-name> --help 2>&1 | head -5
```

## References

- `references/ecc-opencode-win-setup.md` — Windows-specific ECC + OpenCode setup recipe and adapter notes.
- `references/ecc-hermes-mapping.md` — canonical directory mapping for Hermes/OpenCode/Claude Code/ECC source.

## Related

- Use `hermes-agent-skill-authoring` when creating new skills inside Hermes itself.
- Use `opencode-power-pack` fixes when the target is specifically OpenCode.

## Windows Pitfalls

- Run installer scripts in bash, not cmd.
- Use `/c/Users/...` paths inside `bash -lc`.
- If the installer complains about missing dist/build artifacts, run the build script first.

## Common Pitfalls

- **Skipping Phase 2 (Conflict Resolution):** The most common mistake is assuming an external ecosystem is compatible out of the box. Most are designed as standalone orchestrators with paid-model defaults and agent-routing rules that directly compete with Hermes' `decide` skill. Always run Phase 2 — check model defaults, orchestration claims, MCP configs, and port usage — before considering the import complete.
- **Treating reference MCP configs as real conflicts:** Many ecosystems ship `mcp-configs/` directories with `YOUR_*_HERE` placeholders. These are reference files, not active registrations. Don't overreact to them — check if they auto-register (`.mcp.json`, `claude_desktop_config.json`) before flagging them as conflicts.
- **Overwriting ecosystem files without reading them first:** Always read AGENTS.md, CLAUDE.md, SOUL.md, and agent.yaml fully before editing. Their structure varies; a role clarification block may need different positioning in different ecosystems.

## Verification

- `find ~/.hermes/skills/<eco-name> -name SKILL.md | wc -l` matches expected skill count.
- Spot-check at least one SKILL.md against the source repo copy.
- Confirm optional native install targets are populated.

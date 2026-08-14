---
name: opendesign-skill-sync
description: Sync design skills between Hermes and the Open Design app.
---

# OpenDesign ↔ Hermes Design Skill Sync

Bidirectional sync between Hermes' design-skill collections and the Open Design desktop app's plugin system. Both directions are scripted and idempotent — rerun freely after adding/removing design skills.

## The two scripts (idempotent, rerun anytime)

```bash
cd ~/AppData/Local/hermes
python scripts/export-design-skills-to-opendesign.py   # Hermes → Open Design
python scripts/import-opendesign-skills-to-hermes.py   # Open Design → Hermes
```

## Hermes → Open Design (export)

- Reads `SKILL.md` frontmatter from the external design collections (awesome-design-skills, design-skills-ihlamury, emilkowalski-skills, ui-skills-ibelick — listed in the script) **plus `HERMES_EXTRA`**: a curated list of Hermes-local UI/UX skills from `~/AppData/Local/hermes/skills/` (design systems like blue-laser-clean-glass-layout, industrial-brutalist-ui, skeuomorphic-ui + craft skills like design-taste-frontend, high-end-visual-design, gpt-taste, landing-page, pricing-page). The list lives in the script — add new Hermes skills there to export them.
- Writes per skill: `%APPDATA%/Open Design/namespaces/release-stable-win/data/plugins/design-<name>/` containing `open-design.json` + `DESIGN.md` (skill body, frontmatter stripped).
- Registers each in the `installed_plugins` SQLite table (`data/app.sqlite`) with `source_kind='user'`, `marketplace_trust='user'`, sha256 `manifest_digest` + `bundled_content_digest`, `capabilities_granted=['prompt:inject']`. Idempotent: skips ids already present.

**Open Design plugin format (design-system kind):**
```json
{
  "$schema": "https://open-design.ai/schemas/plugin.v1.json",
  "specVersion": "1.0.0",
  "name": "design-<slug>",
  "title": "<Name> Design System",
  "version": "0.1.0",
  "publishedAt": "…",
  "description": "<frontmatter description, ≤300 chars>",
  "license": "MIT",
  "tags": ["design-system", "hermes-export", "design"],
  "od": { "kind": "scenario", "taskKind": "new-generation", "mode": "design-system",
          "scenario": "design", "surface": "web", "useCase": { "query": { "en": "…" } } }
}
```
Key facts:
- Design systems use **`DESIGN.md` + manifest** (NO `compat.agentSkills`, no SKILL.md). Other plugin kinds (atoms/examples) use `SKILL.md` + `compat.agentSkills: [{path: "./SKILL.md"}]` and `od.kind: "atom"`.
- Bundled official plugins live in the app resources dir (`C:\Users\YOUR_USERNAME\AppData\Local\Programs\Open Design release-stable-win\resources\open-design\plugins\_official\{atoms,design-systems,examples,image-templates,scenarios,video-templates}`), registered with `source_kind='bundled'`.
- All official `installed_plugins` rows are `bundled`; user exports use `'user'` — the app's own enum for this value is unverified (app not running during sync); if the app doesn't show the plugins, re-add via its marketplace UI — folders + manifests are already correct.

## Open Design → Hermes (import)

- Scans `_official/design-systems/` (143 systems), **skips slugs that collide with existing skill names** (77 of 143 collided with our collections — collision-free by design, no loader ambiguity).
- Writes `~/AppData/Local/hermes/skills/opendesign/od-<slug>/SKILL.md` (frontmatter `name: od-<slug>` + description; body = DESIGN.md content) plus `DESIGN.md` + `open-design.json` alongside.
- Loadable as `opendesign/od-<brand>` (e.g. `od-bmw`, `od-binance`, `od-tesla`). Brand/aesthetic requests → route to these per /decide.

## Driving Open Design headlessly (MCP daemon)

The app hosts an MCP server you can drive without GUI interaction: spawn `Open Design.exe <daemon-cli.mjs> mcp` with `ELECTRON_RUN_AS_NODE=1` and speak JSON-RPC over stdio. Full pipeline verified: list projects, read/write files, `start_run` generation (with per-run `agent`/`model` override), `get_run` polling, `get_artifact` pulls. Two traps: the daemon CLI path moved on app update (`node_modules/@open-design/daemon/dist/cli.js` → `resources/app/prebundled/daemon/daemon-cli.mjs`), and the CLI defaults to port 7456 while the real daemon listens on a **random port per launch** — read `"url"` from `logs/daemon/latest.log` and set `OD_DAEMON_URL`. Runs take 5–30 min; poll, don't cancel. Working clients: `~/AppData/Local/hermes/scripts/opendesign-direct-call.py` (single list_projects probe) and `~/AppData/Local/hermes/scripts/od-gen.py` (agents/plugins/projects/create/run+poll modes). JSON-RPC over stdio: **initialize must be id 1 and each tools/call a DIFFERENT id** (e.g. 2) — reusing id 1 makes the matcher return the initialize response, and substring matching on `"id":2` also hits the wrong line (initialize text contains it); parse each line's top-level `id` field and compare. Full recipe, tool table, and model-slot notes: `references/opendesign-mcp-daemon.md`.

## Hermes as the app's AI agent (ACP) — why it can appear dead

The Open Design app spawns `hermes acp` (Agent Client Protocol, JSON-RPC over stdio) per chat run. Known failure mode: runs die with `ACP response timed out after 600000ms` while Hermes' own stderr shows `concurrent tool batch timed out after 420.0s; N tool(s) still running: search_files` — **shell-backed tools hang under the ACP child** (model calls succeed; the `failureCategory: "auth" / "auth_required"` in state.json is the app's misleading heuristic, not an auth problem). Quick unblock: switch the app's agent to `opencode` (app-config.json `agentModels`). Full diagnostic recipe (run-log locations, event signatures, manual `hermes acp` driver notes): `references/acp-agent-debugging.md`.

## When the OD GUI won't attach (projects: [] despite app running)

The daemon's project resolution is gated on the GUI's workspace attach. If the app's frontend fails to load (`od://app/` + `net::ERR_FAILED`, backend 502s/ERR_FAILED all day), `list_projects` returns `[]` even though all projects still exist in `data/app.sqlite` (`SELECT id, name FROM projects`). Restarts don't reliably fix it — each launch lands in a random state (healthy daemon one time, dead sidecar or empty workspace the next).

Diagnostic ladder:
1. Daemon reachable? `curl -s -m 3 -o /dev/null -w "%{http_code}" http://127.0.0.1:<port>` — **404 is healthy** (API root); 000 = sidecar dead → restart app (`powershell -NoProfile -Command "Stop-Process -Name 'Open Design' -Force; Start-Process '<install>\Open Design.exe'"`), then re-read the port from the daemon log.
2. Port changed after restart — always re-read `logs/daemon/latest.log` `"url"`; never reuse an old port.
3. Projects empty but DB has them → workspace attach failed (network-dependent). Retry once; if still empty, use the fallback below.

**Validated fallback (delivers the artifact anyway):** generate directly into the OD project folder with the opencode CLI — the result lands where OD expects it and appears as a project once the app recovers:
```bash
cd "$APPDATA/Open Design/namespaces/release-stable-win/data/projects/<project-id>"
# pin ALL swarm roles to allowed models first (temp preset; restore after)
OPENCODE_SLIM_PRESET=flash-only opencode run -m opencode-go/deepseek-v4-flash "$(cat prompt.txt)"
```
Create the temp preset by cloning the active preset in `~/.config/opencode/oh-my-opencode-slim.json` and setting every role's model to the allowed one (observer → vision model); `json.dump` back, then **delete the preset after the run** (config is read at startup, so restoring mid-run is safe). The swarm's `@designer` subagent then uses the pinned model instead of the preset's default (kimi-k2.7-code). Verify: `index.html` appears in the project dir; JS syntax via extracting `<script>` to a temp file + `node --check`.

Failure signature when using OD's own `start_run` path: `status: failed, failureDetail: upstream_5xx, failureStage: first_token_wait` = the opencode-go provider 5xx'd before the first token (OD retries once, `retry_strategy: same_run_transient`). Check provider health with a manual `opencode run -m <model> "ping"` from the project dir — if that works, just retry the run. Full session detail: `references/od-gui-failure-fallback.md`.

## Pitfalls

- **Mobile dual-mode prototype briefs**: use `templates/mobile-dual-mode-prototype-prompt.md` — known-good prompt skeleton (customer+admin modes, bottom nav BOTH modes on mobile — top tabs for admin were user-flagged as bad nav, localStorage persistence, single-file, #5e6ad2 accent, 44px targets).

- **`od-` prefix is the collision strategy.** Open Design has airbnb/apple/stripe/… same as our collections; importing bare names would make `skill_view` refuse ambiguous lookups. The prefix keeps 66 kits importable.
- **The `opendesign` MCP is daemon-gated** — it only works when the Open Design app is running (`hermes mcp test opendesign` fails with connection closed otherwise). Use the `od-*` skills directly when the app is down.
- **Name collisions across the library:** `impeccable`, `decide`, `stop-slop`, `fullstack-nextjs-supabase` each exist in BOTH `~/AppData/Local/hermes/skills/` and `~/.agents/skills/` (or external dirs) — `skill_view` by bare name refuses; use the category path or the full local path. In Open Design ACP sessions this is worse: the agent's own `skill_view` calls fail on the ambiguity and stall its turn — delete the duplicate in `~/.agents/skills/` to keep in-app agents healthy.
- After any design-skill change, rerun BOTH scripts — the weekly `workflow-ecosystem-audit` cron does this automatically (Mondays 07:00).
- Verify count drift: export prints `plugins generated: N`; import prints `imported/skipped (collision)` counts.
- **`plugins generated: 0` after patching the export script = broken indentation**, not missing skills. The script is one loop; a patch that re-indents the loop body under the `if not is_file(): continue` guard turns it into dead code. Re-check loop-body indentation after any patch edit to that script.
- **Name collisions across export sources:** `design-impeccable` already existed from the emilkowalski repo — DB insert is skipped (idempotent) but the DESIGN.md is still overwritten. To tell fresh from pre-existing plugins: `SELECT id, datetime(installed_at/1000,'unixepoch') FROM installed_plugins WHERE id IN (...)` — pre-existing rows carry the original run's timestamp.
- **Restart the Open Design app after export** — new plugins are read from `installed_plugins` + `plugins/` only at startup.
- **OpenDesign runs can silently bill kimi-k2.7-code.** When the app's agent is `opencode` and `~/.config/opencode/oh-my-opencode-slim.json`'s ACTIVE preset routes the `designer` role to `opencode-go/kimi-k2.7-code`, OD generation runs spawn designer subtasks on the paid Kimi model — shows up on the opencode-go usage page as kimi-k2.7-code rows you never consciously picked. Diagnosis: `~/.local/share/opencode/log/oh-my-opencode-slim.*.log` entries `agentType: designer` + task labels match the usage-page session ids (e.g. `ses_...2FiFHZMz`). Fix: point the designer role at `opencode-go/deepseek-v4-flash` in that preset.

---
name: opendesign-sync
description: >-
  Sync design skills between Hermes and Open Design.
version: 1.0.0
metadata:
  hermes:
    tags: [opendesign, design, skills, sync, plugins]
    category: workflow
---

# Open Design ↔ Hermes Design-Skill Sync

Bidirectional sync between the Open Design desktop app and Hermes design skills. Verified 2026-08-04: 166 exported, 66 imported, 77 collisions skipped.

## What Open Design "skills" actually are

A plugin = one folder with `open-design.json` (manifest) + content file:

- **Design systems** (the valuable ones): `DESIGN.md` (full spec: palette table, typography rules, component styles, layout, do/don'ts, responsive breakpoints, agent prompt guide). Manifest has **NO `compat` block**.
- **Atoms/examples**: `SKILL.md` + manifest with `compat.agentSkills: [{path: "./SKILL.md"}]`.

Design-system manifest shape (od block is what the app reads):
```json
{
  "$schema": "https://open-design.ai/schemas/plugin.v1.json",
  "specVersion": "1.0.0",
  "name": "design-<slug>",
  "title": "<Name> Design System",
  "version": "0.1.0",
  "description": "<from skill frontmatter>",
  "license": "MIT",
  "tags": ["design-system", "hermes-export", "design"],
  "od": {
    "kind": "scenario", "taskKind": "new-generation", "mode": "design-system",
    "scenario": "design", "surface": "web",
    "useCase": { "query": { "en": "Generate a {{artifactKind}} using the <Name> Design System. ..." } }
  }
}
```

## Locations

| Thing | Path |
|---|---|
| User plugin storage | `%APPDATA%\Open Design\namespaces\release-stable-win\data\plugins\` |
| Plugin registry DB | `...\data\app.sqlite` → table `installed_plugins` |
| Bundled official plugins (read-only) | `%LOCALAPPDATA%\Programs\Open Design release-stable-win\resources\open-design\plugins\_official\{design-systems,atoms,examples,...}` |
| Hermes imported systems | `~/AppData/Local/hermes/skills/opendesign/od-*/` |
| Sync scripts | `~/AppData/Local/hermes/scripts/export-design-skills-to-opendesign.py` + `import-opendesign-skills-to-hermes.py` |

⚠️ `data/skills/` is EMPTY — the app's skills ARE the plugins. That dir is a red herring.

## Export (ours → Open Design)

```bash
python ~/AppData/Local/hermes/scripts/export-design-skills-to-opendesign.py
```
- Sources: `~/Documents/Repos/external-skills/{awesome-design-skills,design-skills-ihlamury,emilkowalski-skills,ui-skills-ibelick}/skills/*/SKILL.md` **+ `HERMES_EXTRA`** (35 curated Hermes-local UI/UX skills added 2026-08-09 — design systems + craft skills; list lives at the top of the script). Verified 2026-08-09: 200 user plugins registered (was 166; `design-impeccable` pre-existed from the emilkowalski repo so only 34 new rows).
- Strips frontmatter → `DESIGN.md`; writes manifest (name `design-<slug>`); inserts `installed_plugins` row (`source_kind='user'`, sha256 digests, ms-epoch timestamps). Idempotent; skips folders without SKILL.md.

## Import (Open Design → Hermes)

```bash
python ~/AppData/Local/hermes/scripts/import-opendesign-skills-to-hermes.py
```
- Reads `_official/design-systems/` (~143 systems).
- **Collision rule (critical):** skips any slug already present as a Hermes skill name (local + external dirs) — importing all 143 pollutes the index and creates loader ambiguity. First run: 66 imported, 77 skipped (airbnb, apple, stripe, linear… already owned).
- Each import: `skills/opendesign/od-<slug>/` with `SKILL.md` (frontmatter `name: od-<slug>`) + full `DESIGN.md` + original `open-design.json`.
- Load with `skill_view(name='opendesign/od-bmw')`; list via `skills_list(category='opendesign')`. The `od-` prefix is deliberate: no bare-name collisions, provenance visible.

## Pitfalls

- **MCP requires the app running:** `hermes mcp test opendesign` fails (35s timeout) when the desktop app is closed — its MCP server lives inside the app process (`command: Open Design.exe`).
- **DB writes while app closed are safe** (no lock) but unverified in-app until restart/rescan. If plugins don't appear, re-add via the app's marketplace UI — folders/manifests are already correct.
- **`installed_plugins.source_kind` enum:** only `bundled` existed before our writes; exports use `user`. If the app filters strictly, check `SELECT DISTINCT source_kind FROM installed_plugins` after a real install and adjust the script.
- **Design-system manifests have no `compat` key** — don't add one; only atoms do.
- **Never hand-edit the DB while the app is running** (WAL/lock conflicts).
- **MSYS `~` path mangling:** inside git-bash, `node ~/AppData/.../script.mjs` resolves `~` to `C:\c\Users\...` and node dies with `MODULE_NOT_FOUND`. Pass Windows forward-slash paths to node instead: `node "C:/Users/YOUR_USERNAME/AppData/Local/hermes/skills/impeccable/scripts/context.mjs"`.
- **Weekly auto-audit:** cron `workflow-ecosystem-audit` (Mon 07:00) reruns both sync scripts and checks MCP/skill/routing drift — after manual design-skill changes, the Monday run catches up automatically.

## The md-file taxonomy (what each .md means in this ecosystem)

| File | Role | Producer/Reader |
|---|---|---|
| `SKILL.md` | Agent skill entrypoint (frontmatter `name`/`description` + body) | Hermes/OpenCode/ZCode; OpenDesign via `compat.agentSkills` |
| `PRODUCT.md` | Durable product context (what/who/constraints) | impeccable `init` |
| `DESIGN.md` | Visual world spec (tokens, palette, typography, layout) | impeccable `document`; OpenDesign design-systems |
| surface briefs | Per-surface mode (Persuade/Operate/Read/Experience) | impeccable `context.mjs` |
| `open-design.json` + `DESIGN.md`/`SKILL.md` | OpenDesign plugin pair | Open Design app |
| `AGENTS.md` / `mood.md` / `voice.md` | Workspace rules / brand tone | any agent entering the repo |

Only `atm-machine` had a DESIGN.md as of 2026-08-04 — most projects have none; run impeccable `init` + `document` to seed them.

## After any sync: update /decide routing

Newly imported skills (`od-*`) and the impeccable workflow are already routed in the `decide` skill's Selection Rules (design routing order: impeccable → specific style/brand incl. `od-<brand>` → creative). If a future sync adds a new skill class, patch `decide` the same way.

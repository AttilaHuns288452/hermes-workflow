# Roblox skill corpus: what to load for what

~54 skills live under `~/.hermes/skills/roblox/`. Load the ONE that matches the task; the umbrella (`roblox-game-development`) stays the procedure and the gates.

## Routing table

| Task | Load |
|---|---|
| Menus, HUD, shops, layout, responsive/scaling, animation of UI | `roblox-ui` (also `references/styling-and-frameworks.md` for StyleSheets/tokens/themes) |
| Map, props, parts, pivots, terrain-ish world building | `roblox-world-building` |
| Lighting, atmosphere, skybox, time of day | `roblox-lighting` |
| Sound effects, music, audio groups, mixer | `roblox-audio` |
| FPS, memory, draw calls, streaming, Parallel Luau | `roblox-performance` |
| Exploits, remote validation, server authority | `roblox-security` and `roblox-code-review` |
| DataStores, profiles, session locking, migrations | `roblox-data-stores` / `roblox-server-data` |
| Purchases, receipts, passes, pricing | `roblox-monetization` |
| Driving Studio from an agent (tools, limits) | `roblox-studio-mcp` |
| Rojo, project layout, tooling setup | `roblox-tooling` and `roblox-architecture` |
| Luau syntax, types, strict-mode errors | `roblox-luau`, `roblox-luau-types`, `roblox-luau-core` |
| Touch/gamepad/keyboard input, Input Action System | `roblox-input` |
| NPC behaviour, pathing, state machines | `roblox-npc-ai` |
| Physics, vehicles, constraints | `roblox-physics` |
| Tests, dependency injection for testable modules | `roblox-testing` |
| Analytics, retention/live-ops signals | `roblox-analytics`, `roblox-analytics-liveops` |
| Growth, discovery, thumbnails, retention diagnosis | `roblox-growth-design`, `roblox-player-psychology` |
| Pre-publish audit | `roblox-publish-checklist` |
| Deep, fact-checked reference on any of the above | `roblox-dev-skill` (+ its 14 `references/`) |
| Simple design/loop questions | `roblox-game-design` |

## What the corpus is good at

- Naming the CURRENT API. It is checked against recent Studio builds, so it says `UIScale` (not `Size` tweens) for pop effects, `CanvasGroup` for subtree fades, `UIDragDetector` (not the removed `GuiObject.Draggable`), `ScreenInsets` for safe areas, and warns which betas cannot ship.
- Correctness rules that survive review: server authority, validate every remote argument, filter any player text shown to another player.

## What it cannot do

- It has no camera. Every aesthetic claim needs a live capture.
- It does not know this project's contract (Config as numeric authority, the one-dispatcher server, the rail owner). Where the corpus and this umbrella disagree on process, this umbrella wins.

## Adding more

Run `~/.hermes/scripts/import_roblox_skills.py` after editing its source list. It normalises frontmatter to `name` + `description` and copies whole subtrees so internal links survive; verify with `skill_view` afterwards. Never import a repo wholesale without checking each skill's flagged lines — treat a scanner hit as a question, not a verdict.

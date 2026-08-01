# Hermes CLI — Verified Command Table

Tested 2026-08-01 against Hermes Agent v0.18.2 on Windows (git-bash), while auditing
the hermes-workflow repo's plug-and-play docs. All facts verified by running the
command, not by reading help text.

## One-shot / non-interactive

| Command | Verdict | Notes |
|---|---|---|
| `hermes -z "prompt"` | ✅ works | One-shot agent run; returned `PONG` in ~48s with default provider |
| `hermes run "prompt"` | ❌ does not exist | Prints usage, non-zero exit. Common doc mistake — always `-z` |
| `hermes chat` | ✅ | Interactive only; not for scripts |

## Skills management

| Command | Verdict | Notes |
|---|---|---|
| `hermes skills install <local-dir> -y` | ✅ works | Accepts a local directory path (fetches → security scan → installs). `-y` skips confirmation |
| `hermes skills install <local-dir>` (no `-y`) | ⚠️ silent abort | Prints `Fetching: <dir>` then exits 0 WITHOUT installing. Never omit `-y` in loops |
| `hermes skills install <hub-id>` / `<https://…/SKILL.md>` | ✅ | Per `--help`; `--name` overrides when frontmatter lacks `name:` |
| `hermes skills list / check / update / audit / diff / uninstall` | ✅ | Subcommands exist (v0.18.2) |

## Auth

| Command | Verdict | Notes |
|---|---|---|
| `hermes auth add <provider> --type api-key --api-key <key>` | ✅ | Flags valid: `--type {oauth,api-key,api_key}`, `--label`, `--api-key`, `--portal-url`, `--inference-url`, `--no-browser` |
| `hermes auth list / remove / reset / status / logout` | ✅ | |

## Tool installs the docs reference

| Install command | Ships binary | Verified via |
|---|---|---|
| `npm install -g @colbymchenry/codegraph` | `codegraph` | `npm view @colbymchenry/codegraph bin` |
| `uv tool install graphifyy` | `graphify`, `graphify-mcp` | pip `entry_points` (console_scripts); exes present in venv Scripts after install |
| `npm install -g opencode` | `opencode` | standard npm package |
| `npm install && npm run build` (Vite) | docs/ outDir | built clean (1.6–8s) |

Verify line used in SETUP docs: `hermes --version && codegraph --version && graphify --version`.

## Other facts

- `toolsets: [hermes-cli]` in config.yaml is the standard aggregate CLI toolset (default
  for CLI sessions), NOT a restrictive single-toolset. Safe to ship in a config template.
- `hermes skills install` runs a security scan (skills-guard) with verdict ALLOWED/BLOCKED
  — quarantine + scan output on every install, ~10s per skill. A 500-skill loop takes
  ~85 min; works, just slow.
- Fixing website-embedded commands: patch `src/App.jsx` → `npm run build` → commit
  regenerated `docs/`; also grep `legacy/` pages and the compiled bundle for stale copies.

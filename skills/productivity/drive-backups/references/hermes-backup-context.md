# Hermes Backup Context — Environment Structure

> Discovered during the June 2026 Hermes portability audit.
> Use as a reference when backing up or migrating Hermes to a new device.

## Finding the Real Hermes Home

Hermes has **two** possible home directories — do NOT trust `~/.hermes` alone:

| Location | Status | Typical Size | Contents |
|----------|--------|-------------|----------|
| `~/.hermes` (legacy) | Often stale/empty | ~24 MB | Outdated copy of config, might exist from an old install |
| `AppData/Local/hermes` | **REAL home** | ~400+ MB (state.db ~386 MB) | All active config, profiles, sessions, skills, plugins |

**Verify with:**
```bash
hermes config path      # → C:\Users\<user>\AppData\Local\hermes\config.yaml
hermes config env-path  # → C:\Users\<user>\AppData\Local\hermes\.env
```

If these point to `AppData/Local/hermes`, the `~/.hermes` legacy dir is not the
active home.

## Profile Architecture

Each profile is a fully self-contained subdirectory under the real Hermes home:

```
AppData/Local/hermes/
├── config.yaml             # Root config: MCP servers, providers, platform
├── .env                    # API keys (shared by all profiles after sync)
├── auth.json               # OAuth tokens
├── state.db                # Session database (SQLite, ~386 MB)
├── profiles/
│   ├── channel/
│   │   ├── config.yaml     # Profile-specific overrides
│   │   ├── .env            # Per-profile API keys (may differ from root!)
│   │   ├── auth.json       # Per-profile OAuth tokens
│   │   ├── state.db        # Per-profile session history
│   │   ├── memories/
│   │   ├── skills/
│   │   └── sessions/
│   ├── finance/
│   └── codingprofile/
├── skills/
├── scripts/
├── plugins/
├── kanban.db
└── gateway_state.json
```

### CRITICAL: Per-profile `.env` and `auth.json` are NOT shared by default.

Each profile has its own copies. If you add an API key to the root `.env`, it
does NOT automatically appear in each profile's `.env`. Use a sync script
to propagate: copy root `config.env_reference → auth.json` to every profile.

### MCP Server Inheritance

- The **root `config.yaml`** defines all MCP servers under `mcp_servers:`.
- Each **profile's `config.yaml`** may also define `mcp_servers:`.
- **If a profile has `mcp_servers:`, it OVERRIDES the root's MCP servers entirely.**
  The profile only gets its own listed servers, NOT the ones from root.
- **To share MCP servers across all profiles**, remove `mcp_servers:` from every
  profile config.yaml. Profiles without their own `mcp_servers:` entry inherit
  the root's full set.

In the current setup:
- Root has 8 MCP servers: codegraph, graphify, llmquant-data, obsidian-kg,
  agentmemory, vscode, composio, open-design, opendesign
- Channel profile had its own `mcp_servers:` with the same 8 → removed it
- Finance and codingprofile each had a subset (composio, open-design, opendesign
  only) with duplicate keys → removed them

**All 3 profiles now inherit the root's full 8-server set.**

## Backup Content Scope for Plug-and-Play

### MUST back up (critical for restoration on new device)
- `config.yaml` — Hermes settings, MCP servers, providers
- `.env` — API keys for all services
- `auth.json` — OAuth tokens
- `profiles/*/` — Every profile's full directory (config, skills, memories,
  sessions, credentials)
- `state.db` — Full session database (use ZIP_STORED — SQLite is already compressed)
- `state.db-shm`, `state.db-wal` — WAL artifacts for consistency
- `skills/` — Custom and hub-installed skills
- `memories/` — Persistent cross-session memory
- `scripts/` — Backup, restore, and sync scripts
- `plugins/` — Plugin configurations
- `kanban.db` — Multi-agent work queue
- `kanban/` — Kanban state
- `gateway_state.json` — Gateway service state
- `external/` — Rclone config, external skill repos

### CAN exclude (regenerated on next start)
- `models_dev_cache.json` (~2.4 MB)
- `ollama_cloud_models_cache.json`
- `desktop-build-stamp.json`
- `image_cache/` (can be large — optional for portability)
- `audio_cache/` (can be large — optional for portability)

### Must also back up separately
- Rclone config: `%APPDATA%/rclone/rclone.conf` or
  `~/AppData/Roaming/rclone/rclone.conf` — needed to access the backup itself
  on a new machine

## The Three-Script Lifecycle

```
run-hermes-backup.py        → Daily cron: archive + upload + retention
restore-hermes-backup.py    → New device: download + extract + place
sync-hermes-credentials.py  → After adding keys: propagate to all profiles
```

### sync-hermes-credentials.py pattern
```python
# For each profile directory, copy root .env and auth.json
root_env = hermes_root / ".env"
root_auth = hermes_root / "auth.json"
for profile_dir in (hermes_root / "profiles").iterdir():
    if profile_dir.is_dir():
        shutil.copy2(root_env, profile_dir / ".env")
        shutil.copy2(root_auth, profile_dir / "auth.json")
```

## Python Script Pitfalls on Windows

When writing Python backup/restore scripts that reference Windows paths:

1. **`\U` in `\Users` causes SyntaxError in docstrings.**
   `C:\Users\YOUR_USERNAME\...` contains `\U` which Python interprets as the start
   of a `\UXXXXXXXX` Unicode escape sequence. Fixes:
   - Use a raw docstring: `r"""..."""` (but watch for em-dashes on first line)
   - Use forward slashes: `"C:/Users/YOUR_USERNAME/AppData/..."`
   - Use `os.environ.get("HERMES_HOME", "...")` to avoid hardcoding

2. **Hidden files (.env) are skipped by `rglob("*")` correctly** — the glob
   includes them. Filters like `if path.name.startswith("."): continue` will
   SKIP `.env` and break the backup. Always allow specific dotfiles through.

3. **Long paths (>260 chars)** — Python on modern Windows 10/11 with long path
   support enabled handles them, but be aware if the `state.db` path is deep.

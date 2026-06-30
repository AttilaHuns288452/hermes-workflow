---
name: hermes-backup-workflow
description: "Use when the user asks about Hermes backup, restore, credential sync, Google Drive backup, rclone, migrating Hermes to a new machine, or plug-and-play recovery of the Hermes environment."
---

# Hermes Backup & Restore Workflow

## Overview

Hermes runs from `$HERMES_HOME` (default: `C:\Users\<user>\AppData\Local\hermes`). It has a daily 2AM cron job
that backs up everything to Google Drive (rclone remote configured via `$RCLONE_REMOTE`).

Three scripts handle the full lifecycle:

| Script | Purpose | Location |
|--------|---------|----------|
| `run-hermes-backup.py` | Daily backup ZIP → Google Drive | `<HERMES_HOME>/scripts/` |
| `restore-hermes-backup.py` | Download + restore from backup | `<HERMES_HOME>/scripts/` |
| `sync-hermes-credentials.py` | Sync .env + auth.json → all profiles | `<HERMES_HOME>/scripts/` |

**Canonical scripts** are also in the `hermes-workflow` GitHub repo:
`https://github.com/YOUR_USERNAME/hermes-workflow/scripts/*.py`

---

## Architecture

```
AppData/Local/hermes/          ← REAL Hermes home (NOT ~/.hermes which is stale)
├── config.yaml                ← Root config with ALL 8 MCP servers
├── .env                       ← API keys (shared by all profiles after sync)
├── auth.json                  ← OAuth tokens
├── state.db                   ← Session DB (386 MB)
├── scripts/                   ← Backup/restore/sync scripts
│   ├── run-hermes-backup.py
│   ├── restore-hermes-backup.py
│   └── sync-hermes-credentials.py
├── profiles/
│   ├── channel/               ← Each profile has own config, .env, auth, sessions
│   ├── finance/
│   └── codingprofile/
└── skills/, plugins/, tools/...
```

### MCP Server Sharing (FIXED in this session)

All 3 profile configs (`channel`, `finance`, `codingprofile`) had their OWN
`mcp_servers:` sections that overrode the root config. **FIXED by removing**
`mcp_servers:` from all profile configs. They now inherit the full 8-server set:
codegraph, graphify, llmquant-data, obsidian-kg, agentmemory, vscode, composio,
open-design.

### Credential Sync (FIXED in this session)

Root `.env` (23,728 bytes) and `auth.json` are now the canonical source.
`snyc-hermes-credentials.py` propagates them to all profiles.
**Already executed.** All 3 profiles now share the same credentials.

---

## Backup Coverage

The backup ZIP includes:

| Item | Included? | Critical for plug-and-play? |
|------|-----------|---------------------------|
| config.yaml | ✅ | YES — MCP servers, providers, model config |
| .env | ✅ | YES — all API keys |
| auth.json | ✅ | YES — OAuth tokens for Gmail, rclone, etc. |
| profiles/ (all 3) | ✅ | YES — channel, finance, codingprofile |
| skills/ | ✅ | YES — all skills, decide, references |
| memories/ | ✅ | YES — MEMORY.md, USER.md |
| scripts/ | ✅ | YES — backup/restore/sync scripts |
| plugins/ | ✅ | YES |
| state.db | ✅ | YES — all session history |
| rclone.conf | ✅ | YES — Google Drive access for restore |
| external-skills repo | ✅ | YES — superpowers skills |
| sessions/, hooks/, cron/ | ✅ | |
| pairing/, shared/, tools/ | ✅ | |
| kanban.db, channel_directory.json | ✅ | |
| gateway_state.json, SOUL.md | ✅ | |

---

## Workflows

### A. Daily Backup (Cron, 2AM every day)

```bash
# Cron job runs from workdir (set $HERMES_HOME):
#   $HERMES_HOME
# It executes:
python scripts/run-hermes-backup.py
```

The script:
1. Lists existing backups on Google Drive (`$RCLONE_REMOTE:$RCLONE_BACKUP_PATH`)
2. Creates a ZIP directly from source (no staging copy)
3. Uses `ZIP_STORED` (no compression) for maximum speed
4. Uploads to Google Drive
5. Deletes old backups (keeps 5 most recent)

### B. Manual Backup

```bash
python /path/to/run-hermes-backup.py --name "Custom_Name.zip"
```

### C. Plug-and-Play Restore on a New Machine

```bash
# 1. Install Hermes on the new machine
# 2. Install rclone, configure remote (set $RCLONE_REMOTE)
# 3. Run restore:
python /path/to/restore-hermes-backup.py --restore-latest

# 4. Sync credentials to profiles:
python /path/to/sync-hermes-credentials.py
```

The restore script:
1. Lists backups from Google Drive
2. Downloads the latest (or specified) ZIP
3. Extracts everything to `AppData/Local/hermes/`
4. Also extracts rclone config to `AppData/Roaming/rclone/`
5. Restores external-skills repo to `Documents/Repos/`

### D. Cross-Profile Credential Sync

```bash
python /path/to/sync-hermes-credentials.py
```

Run after adding/changing API keys or auth tokens.
Copies root `.env` and `auth.json` to ALL profiles.

---

## Real Hermes Home vs Old ~/.hermes

IMPORTANT: There are TWO Hermes directories:

| Directory | Status | Size | Role |
|-----------|--------|------|------|
| `C:\Users\<user>\AppData\Local\hermes` | **ACTIVE** | 400+ MB | Real Hermes installation |
| `C:\Users\<user>\.hermes` | **STALE** | ~24 MB | Old/legacy, NOT used |

The backup was previously targeting `~/.hermes` (wrong location).
**FIXED in this session** — now targets `AppData/Local/hermes`.

---

## Token Savings with CodeGraph + Graphify

When modifying any of the backup scripts, use CodeGraph MCP + Graphify
probes BEFORE reading files (see `token-saver` skill for full 4-step chain).

**Mini test project:** `~/Documents/Projects/hermes-token-test/` demonstrates
the savings with live benchmarks:

```
Method                  Tokens      Savings vs naive read
─────────────────────────────────────────────────────────
Naive full-corpus read  ~3,733      — (baseline)
Graphify query (BFS)    ~935        4.0×
CodeGraph explore       ~300        ~12×
```

The hermes-workflow repo is now fully indexed:
- CodeGraph: 1,602 files, 109 nodes, 400 edges
- Graphify: 11,501 nodes, 13,727 edges

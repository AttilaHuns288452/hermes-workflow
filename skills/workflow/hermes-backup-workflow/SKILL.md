---
name: hermes-backup-workflow
description: "Use when the user asks about Hermes backup, restore, credential sync, Google Drive backup, rclone, migrating Hermes to a new machine, or plug-and-play recovery of the Hermes environment."
---

# Hermes Backup & Restore Workflow

## Overview

Hermes runs from `C:\Users\<user>\AppData\Local\hermes`. It has a daily 2AM cron job
that backups everything to Google Drive (rclone remote `YOUR_RCLONE_REMOTE`).

Three scripts handle the full lifecycle:

| Script | Purpose | Location |
|--------|---------|----------|
| `run-hermes-backup.py` | Daily backup ZIP → Google Drive | `<HERMES_HOME>/scripts/` |
| `restore-hermes-backup.py` | Download + restore from backup | `<HERMES_HOME>/scripts/` |
| `sync-hermes-credentials.py` | Sync .env + auth.json → all profiles | `<HERMES_HOME>/scripts/` |

**Canonical scripts** are also in the `hermes-workflow` GitHub repo:
`https://github.com/AttilaHuns288452/hermes-workflow/scripts/*.py`

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

## Windows Compatibility Fixes

The script uses `os.uname()` which is **Unix-only** and will crash on Windows with:
```
AttributeError: module 'os' has no attribute 'uname'
```

**Fix**: Replace with `socket.gethostname()` — works cross-platform. Add `import socket` at the top.

### rclone Upload Timeout

On Windows, rclone uploads of large backups (400+ MB) can exceed the default 120s timeout.
**Fix**: The `run()` function's default timeout was increased from 120s → 300s, and the upload step uses 900s.
Keep an eye on the rclone transfer rate — expect ~5-6 MB/s for Google Drive uploads.

#### Verification Hang (July 16, 2026)

After upload completes, rclone enters a post-upload verification phase that **can hang indefinitely**
on Google Drive — checksum retrieval stalls and `copyto` never exits. The file is fully uploaded
and visible on Drive, but rclone keeps retrying verification until the Python timeout kills it.

**Symptoms in backup log:**
- Upload reaches 100% (e.g. 504.685 MiB / 504.685 MiB) in ~60s
- Then cycles through growing totals (1009 MiB, 1.479 GiB, ...) at 0 B/s
- Script eventually dies with `Command timed out after 600s`

**Fix:** `--ignore-checksum --size-only` skips the hung verification phase entirely.
Upload drops to 28.8s @ 17.8 MiB/s for a 505 MB file. The script now uses these flags
(patched 2026-07-16).

## Potential Failure Modes

### ZIP Timeout on Large Directories

The Hermes home directory frequently grows to 160K+ files due to:
- `hermes-agent/` — ~123K files (git clone with dependencies, re-cloneable)
- `lsp/` — ~9K files (LSP servers, re-downloadable)
- `profiles/` — ~12K files (critical — backed up)
- Rest — ~14K files (config, state, skills, sessions)

The script's local-ZIP-then-upload approach can **timeout** because Python's `zipfile` + `shutil.copytree` iterates every file sequentially. Results in **971-byte empty ZIPs** left on Google Drive (ZIP header only, no content).

**Detection:** List remote backups and flag any < 1 KB as failed:
```bash
rclone ls "YOUR_RCLONE_REMOTE:Hermes Backup" | awk '$1 < 1000 {print "FAILED: " $2 " (" $1 " bytes)"}'
```

**Workaround / faster alternative — use `rclone sync` directly:**
```bash
# Instead of the script, sync directly to Google Drive (skips ZIP bottleneck)
rclone sync /c/Users/YOUR_USERNAME/AppData/Local/hermes "YOUR_RCLONE_REMOTE:Hermes Backup/$(date +%F)/" \
  --exclude "hermes-agent/**" \
  --exclude "lsp/**" \
  --exclude "**/__pycache__/**" \
  --exclude "**/.git/**" \
  --exclude "**/node_modules/**" \
  --exclude "**/.codegraph/**"
```

### Failed Backup Cleanup

971-byte empty ZIPs accumulate when the script times out mid-ZIP. Clean them up:
```bash
rclone ls "YOUR_RCLONE_REMOTE:Hermes Backup" | \
  awk '$1 < 1000 {print $2}' | \
  while read f; do rclone deletefile "YOUR_RCLONE_REMOTE:Hermes Backup/$f"; done
```

---

## Backup Coverage

The backup ZIP includes:

| Item | Included? | Critical for plug-and-play? |
|------|-----------|---------------------------|
| config.yaml | ✅ | YES — MCP servers, providers, model config |
| .env | ✅ | YES — all API keys |
| auth.json | ✅ | YES — OAuth tokens for Gmail, rclone, etc. |
| profiles/ (all) | ✅ | YES — channel, finance, codingprofile, learning |
| skills/ | ✅ | YES — all skills, decide, references |
| memories/ | ✅ | YES — MEMORY.md, USER.md |
| scripts/ | ✅ | YES — backup/restore/sync scripts |
| plugins/ | ✅ | YES |
| state.db | ✅ | YES — all session history (426+ MB) |
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
# Cron job runs from workdir:
#   C:\\Users\\Attila\\AppData\\Local\\hermes
# It executes:
python scripts/run-hermes-backup.py
```

**Caveat:** The script routinely times out when the Hermes home exceeds ~160K files (state.db alone is 426+ MB). The ZIP-then-upload approach is the bottleneck. See "Potential Failure Modes" below for workarounds and faster alternatives.

The script:
1. Lists existing backups on Google Drive (`YOUR_RCLONE_REMOTE:Hermes Backup`)
2. Creates a ZIP directly from source (no staging copy)
3. Uses `ZIP_STORED` (no compression) for maximum speed
4. Uploads to Google Drive
5. Deletes old backups (keeps 5 most recent based on name sort order — does NOT detect failed 971-byte empty zips)

### B. Manual Backup

```bash
python /path/to/run-hermes-backup.py --name "Custom_Name.zip"
```

### C. Plug-and-Play Restore on a New Machine

```bash
# 1. Install Hermes on the new machine
# 2. Install rclone, configure YOUR_RCLONE_REMOTE remote
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

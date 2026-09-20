# Windows Backup to Linux Restoration Workflow

## Source Structure (External Drive)

```
/media/attila/SP PHD U3/MyOldOS/
├── 00_MANIFEST/
├── 01_HERMES/data/           ← Hermes state, skills, config
│   ├── config.yaml
│   ├── state.db
│   ├── profiles/
│   ├── skills/               ← Top-level skills (15 dirs)
│   ├── cron/
│   ├── memories/
│   └── sessions/
├── 02_OMNIROUTE/data/        ← OmniRoute DB (if backed up)
├── 03_AI_MODELS/
├── 04_VSCODE/
├── 05_PROJECTS/repos/
│   └── hermes-workflow/skills/  ← 266 custom skills
├── 06_DATABASES/hermes_dbs/
├── 08_CONFIG/
├── 09_CREDENTIALS_SECURE/
├── 10_GIT/
└── 13_RESTORE_SCRIPTS/
```

## Restoration Steps

### 1. Skills (Channel Profile)

```bash
# Restore custom skills from workflow repo
cp -r /media/attila/SP\ PHD\ U3/MyOldOS/05_PROJECTS/repos/hermes-workflow/skills/* \
      /home/attila/.hermes/profiles/channel/skills/
```

### 2. DECIDE.md + CAPABILITY_GRAPH.md

```bash
cp /media/attila/SP\ PHD\ U3/MyOldOS/01_HERMES/data/DECIDE.md /home/attila/.hermes/
cp /media/attila/SP\ PHD\ U3/MyOldOS/01_HERMES/data/CAPABILITY_GRAPH.md /home/attila/.hermes/
```

### 3. State Databases

```bash
# Stop gateway first
systemctl --user stop hermes-gateway

# Restore databases
cp /media/attila/SP\ PHD\ U3/MyOldOS/01_HERMES/data/state.db* /home/attila/.hermes/
cp /media/attila/SP\ PHD\ U3/MyOldOS/01_HERMES/data/response_store.db* /home/attila/.hermes/
cp /media/attila/SP\ PHD\ U3/MyOldOS/01_HERMES/data/kanban.db* /home/attila/.hermes/
cp /media/attila/SP\ PHD\ U3/MyOldOS/01_HERMES/data/projects.db /home/attila/.hermes/
cp /media/attila/SP\ PHD\ U3/MyOldOS/01_HERMES/data/verification_evidence.db* /home/attila/.hermes/

# Restart gateway
systemctl --user start hermes-gateway
```

### 4. OmniRoute (if DB backed up)

```bash
# OmniRoute DB location
cp /media/attila/SP\ PHD\ U3/MyOldOS/02_OMNIROUTE/data/storage.sqlite \
      /home/attila/.omniroute/
```

### 5. Credentials (selective, avoid overwriting fresh auth)

```bash
# GitHub CLI
cp /media/attila/SP\ PHD\ U3/MyOldOS/09_CREDENTIALS_SECURE/gh_auth/* \
      /home/attila/.config/gh/
```

## Verification

```bash
# Check skill count
find /home/attila/.hermes/profiles/channel/skills -maxdepth 1 -type d | wc -l

# Check databases
sqlite3 /home/attila/.hermes/state.db "SELECT COUNT(*) FROM sessions;"

# Check gateway
systemctl --user is-active hermes-gateway
curl -s http://localhost:20128/api/health
```

## Known Gaps

- OmniRoute DB was NOT backed up on Windows (only server.log + watchdog.cmd)
- Lending management system (.NET) project not on Linux
- PowerShell-dependent cron jobs stay disabled
- Pets (2) not restored — reinstall with `hermes pets`
- Some cron execution history stale (auto-regenerates)

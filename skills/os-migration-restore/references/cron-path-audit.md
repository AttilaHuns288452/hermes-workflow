# Cron Path Audit — Windows → Linux Migration

Cron jobs created on Windows embed absolute Windows paths in their `Workdir:` and `Script:` fields. On Linux these cause `FileNotFoundError: [Errno 2] No such file or directory: 'powershell'` or `C:\Users\…`. The cron scheduler does NOT translate them.

## How to find them

```bash
hermes cron list 2>&1 | grep -E "Workdir:|Script:" | grep -iE "C:\\\\Users|powershell|AppData"
```

Also inspect scripts directly:
```bash
grep -rl "C:\\\\Users\|powershell\|AppData" ~/.hermes/scripts/
```

## What breaks

| Symptom | Cause |
|---|---|
| `FileNotFoundError: powershell` | Script invokes `powershell` which doesn't exist on Linux |
| `FileNotFoundError: C:\Users\…` | Cron `Workdir:` or script hardcodes a Windows path |
| `Script not found` (path mangled) | Backslashes in script path parsed as escape sequences |

## Fix recipe

1. `hermes cron list` → identify the job ID
2. For each broken job, determine the Linux equivalent:
   - `C:\Users\Attila\AppData\Local\hermes` → `$HERMES_HOME` (`~/.hermes`)
   - `C:\Users\Attila\Documents\Projects\X` → `~/Documents/Projects/X`
   - `powershell -File X.ps1` → rewrite script as a Python or bash equivalent
3. Either `hermes cron edit <id>` (if the CLI supports it) or delete+recreate with corrected paths.
4. For scripts that wrap a Windows-only tool (PowerShell), port the logic to Python — the venv path changes too: `C:\…\.venv\Scripts\python.exe` → `/home/attila/.venv/bin/python` or the project's Linux venv.

## Real examples (2026-09-03 migration)

| Cron | Windows path | Linux fix |
|---|---|---|
| Sabiniano Lending Daily Backup | `powershell -File C:\…\daily-supabase-gdrive-backup.ps1` | Rewrite as Python using `subprocess` + `rclone` CLI |
| Hermes Daily Google Drive Backup | `Workdir: C:\Users\Attila\AppData\Local\hermes` | `Workdir: ~/.hermes` (or `$HERMES_HOME`) |
| paper_daily.py | `C:\Users\Attila\Documents\Projects\signal-bot` | `~/Documents/Projects/signal-bot` |
| post-deploy-browser-qa | Workdir `C:\Users\Attila\AppData\Local\hermes` | `~/.hermes` |

---
name: hermes-cron-jobs
description: Create, audit, and fix Hermes cron jobs. Covers the script-field semantics (file path, NOT inline command), model-drift self-skip behavior, health-check jobs for long-lived services, and full-library audits. Use when creating a cron job, when a cron job errors or silently skips, or when auditing the cron library.
---

# Hermes Cron Jobs

## Script field: file path, NOT inline command

The `script` param of `cronjob` is a **file path** (relative to `~/AppData/Local/hermes/scripts/`). Inline commands fail with:

```
Script not found: C:\Users\Attila\AppData\Local\hermes\scripts\python3 -c "
```

Fix: write the code to a real file first, then reference it by name.

```bash
# scripts/weekly-scan.py
```

```python
"""Docstring. Prune heavy dirs — rglob over a projects tree times out."""
import os, time
from pathlib import Path
SKIP = {"node_modules", ".git", "venv", ".venv", "__pycache__", "dist", "build", ".next", ".codegraph", "assets"}
cutoff = time.time() - 7 * 86400
recent = []
for root, dirs, files in os.walk(Path.home() / "Documents/Projects"):
    dirs[:] = [d for d in dirs if d not in SKIP]
    for f in files:
        if not (f.endswith(".py") or f.endswith(".js")):
            continue
        p = Path(root) / f
        try:
            if p.stat().st_mtime > cutoff:
                recent.append(str(p))
        except OSError:
            continue
print(f"Weekly scan — {len(recent)} files changed in last 7 days:")
for r in recent[:30]:
    print(f"  {r}")
```

Then: `cronjob action=update job_id=<id> script=weekly-scan.py`. Always run the script directly once (`python scripts/weekly-scan.py`) before wiring it — verify runtime is seconds, not minutes.

## Model drift: unpinned jobs self-skip

If the global `config.yaml` model/provider changes after a job was created, an unpinned job refuses to run:

```
RuntimeError: Skipped to prevent unintended spend: global inference config drifted since
this job was created (provider 'X' -> 'Y'; model 'A' -> 'B'), and this job is unpinned.
No inference call was made. To run on the new config, pin it explicitly:
cronjob action=update job_id=<id> provider=<provider> model=<model>
```

Fix: `cronjob action=update job_id=<id> model={model, provider}`. Jobs with `enabled_toolsets: [terminal]` or `no_agent: true` don't call inference and are immune. Audit signal: a job with `last_status: error` and this message in `cron/output/<job_id>/`.

## Gateway health jobs

For a "gateway alive" check cron, curl the port and report the code; 404 on `/` means the API is up (it's an API server). `gateway_state.json` can be STALE (says running, PID dead) — trust the curl, not the file.

## Library audit procedure

1. `cronjob action=list` — for each job note schedule, `last_status`, `next_run_at`.
2. Flag: `last_status: error` → read `cron/output/<job_id>/<latest>.md` for the Script Error / RuntimeError block.
3. Flag: `last_run_at: null` on a job created >1 day ago → it's new and simply hasn't fired yet; check `next_run_at` instead of treating as broken.
4. Script jobs: verify the script file exists and runs fast.
5. `no_agent: true` + script-only jobs are the cheapest form — prefer them for watchdogs/pollers that need no reasoning.

## Pitfalls

- rglob over a big tree (node_modules etc.) times out cron scripts — use os.walk with a SKIP set.
- `deliver: local` jobs write output to `cron/output/<job_id>/` — that's where error detail lives.
- Cron sessions can't ask questions — prompts must be self-contained.
- Cron-run sessions should not recursively schedule more cron jobs.

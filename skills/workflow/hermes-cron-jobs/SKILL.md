---
name: hermes-cron-jobs
description: Create, audit, and fix Hermes cron jobs. Covers the script-field semantics (file path, NOT inline command), model-drift self-skip behavior, health-check jobs for long-lived services, and full-library audits. Use when creating a cron job, when a cron job errors or silently skips, or when auditing the cron library.
---

# Hermes Cron Jobs

## Script field: file path, NOT inline command

The `script` param of `cronjob` is a **file path** (relative to the Hermes home `scripts/` dir — `~/.hermes/scripts/` on this box). Inline commands fail with:

```
Script not found: C:\Users\YOUR_USERNAME\AppData\Local\hermes\scripts\python3 -c "
```

Fix: write the code to a real file first, then reference it by name.

**Windows pitfall — `.sh` cron scripts run via the WSL shim.** Hermes runs `.sh`/`.bash` script jobs through `bash`, and on Windows that resolves to `wsl.exe` (not git-bash). If no WSL distro is installed, the job fails instantly with `WSL_E_DEFAULT_DISTRO_NOT_FOUND` — and with `deliver: local` the error is invisible (only `last_status: error` in `cronjob list`, output file in `~/AppData/Local/hermes/cron/output/<job_id>/`). Fix: use a `.py` wrapper that `subprocess.run`s the real script with `cwd` set (non-`.sh` scripts run via Python directly). Symptom check: `grep -i "WSL_E\|wsl.exe" ~/AppData/Local/hermes/cron/output/<job_id>/*.md`.

**`hermes cron edit --script` rejects absolute paths** (`Script path must be relative to ~/.hermes/scripts/`). When a job errors `Script not found: ...scripts/<name>` but the real script lives in a project (e.g. `~/Documents/Projects/signal-bot/paper_daily.sh`): copy it into `~/.hermes/scripts/` with the same filename — no job-config change needed. Copies are safe if the script is self-contained (cd's into its own project dir internally); verify with `bash -n` after copying.

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

Fix: pin the job's model/provider via the **CLI** — the `cronjob` tool has NO model/provider params (`cronjob action=update job_id=<id> model=...` fails with "No updates provided"):
```bash
hermes cron edit <job_id> --model deepseek-v4-flash --provider opencode-go
```
The same shape can move a job to a different provider entirely (e.g. after a 402). Jobs with `enabled_toolsets: [terminal]` or `no_agent: true` don't call inference and are immune to this self-skip — but not to provider preflight: a no-agent job pinned to a provider with missing or zero-credit credentials is blocked before its script runs (`Status: BLOCKED (configuration)`, nothing charged, in `cron/output/<job_id>/`). Re-pin no-agent jobs too when a provider dies. Audit signal: a job with `last_status: error` and this message in `cron/output/<job_id>/`. Verify a fix with `hermes cron run <job_id>` and read the fresh file in `cron/output/<job_id>/`.

`hermes cron run <job_id>` blocks in the foreground for as long as the run itself takes and can blow the terminal timeout while the job keeps executing in the gateway — do not re-run it on timeout. Poll `hermes cron runs <job_id>` instead (`running` → `completed`), and prove the model layer changed by reading the run's own session row rather than trusting `Updated job: <id>`:

```bash
sqlite3 ~/.hermes/state.db "select model, billing_provider from sessions where source='cron' order by rowid desc limit 3;"
```

Model ids are provider-scoped: the same weights are often a different id per provider, and an id one provider serves can 403 as PAYG-only on another. Re-pin `--provider` and `--model` together, and probe the pair with a 1-token request first. There is no bulk flag — loop the job ids through `hermes cron edit`, then re-parse `cron/jobs.json` and assert no job still names the retired model or provider.

## Provider balance failures (402/403/400 "insufficient credits") — sweep every pin

A provider that runs out of credit (or whose free tier is retired) fails jobs with `RuntimeError: HTTP 402 ... Insufficient Balance` or `... insufficient credits` — the jobs are fine, the provider isn't. The job that surfaced it is rarely the only victim: one dead provider usually poisons several jobs AND the profile configs. Sweep every surface that names it before declaring the fix done:

1. **Cron jobs, agent and no-agent alike** — read `cron/jobs.json` and list every job whose `provider`/`model` names the dead provider; re-pin each with `hermes cron edit <id> --provider <working> --model <m>` (the CLI is the only path — the `cronjob` tool has no model/provider params; there is no bulk edit, so loop the ids and re-read the file afterwards to confirm zero survivors). Use the target provider's own model-id format.
2. **Profile configs** (`~/.hermes/profiles/*/config.yaml`) — pins hide in four places: `model.provider`, `model.default`, `auxiliary.{vision,web_extract,compression}.{provider,model}`, and `fallback_providers[]`. Grep the provider name across every profile config; fixing only the `model:` block leaves vision/web-extract/compression calls failing later.
3. **Global `config.yaml`** `fallback_providers[]` — drop entries for the dead provider so the fallback ladder doesn't burn retries on dead endpoints. Leave its block under `providers:` alone; it becomes valid again if the user tops up.

Probe the replacement with a 1-token request against the new provider/model before re-pinning. Prefer a provider already proven working for delegation (see AGENTS.md delegation section) over the default route.

## Duplicate schedulers — the same job running twice

Hermes cron is not the only scheduler on the box. The user's own crontab can run the same script on a different schedule, and **Hermes tooling never looks at it**. Symptoms are data corruption, not errors: a ledger with triplicate rows, a report file rewritten twice a week, "why did this run 3 times today".

Always inventory both before auditing or adding a job:

```bash
crontab -l 2>/dev/null | grep -vE '^\s*#|^\s*$'          # the user's own crontab
hermes cron list --all                                    # Hermes-side jobs
```

Match by **script target**, not by job name — the two schedulers name the same work differently ("signal-bot weekly portfolio report" vs a bare `portfolio.sh` line). One job firing from both looks like a healthy `last_status: ok` on each side.

When you find a duplicate, decide which scheduler owns it and **disable rather than delete** the other (`# ` prefix in crontab, `hermes cron pause` on the Hermes side) so the reason survives: prefix the commented line with the reason and the evidence (`# DISABLED <why>: <metric that justified it>`). Re-enabling is then one edit, and nobody re-adds a duplicate because they could not tell why it was gone.

Related decision: a job whose runtime approaches the 3-minute cron interrupt belongs on the system crontab; short, cheap, reasoning-free pollers belong on the Hermes side where `no_agent` and output capture exist. Do not migrate a long job onto Hermes cron without checking its measured runtime first.

## `last_status: delivery_failed` — the job ran, the report did not

A job can execute perfectly and still read as failed. `delivery_failed` with `last_error: None` means the script exited 0 and only the notification target is broken:

```bash
hermes cron run <job_id>        # then read the job row
grep -o '"last_delivery_error":[^,]*' cron/jobs.json   # literal text, not python repr
```

Most common cause: `deliver: origin`, where `origin` captured a chat id from a session that no longer exists (`no gateway in this process owns its session`). Fix with `hermes cron edit <job_id> --deliver local` — `local` writes to `cron/output/<job_id>/` and never depends on a live chat. Compare against the jobs that do work: the healthy ones on this box are `local`.

Distinguish the two failure classes before debugging the script itself: `delivery_failed` = script fine, target wrong; `error` = read `cron/output/<job_id>/` for the script's own stderr.

## Long-running jobs (minutes, not seconds)

A job that takes longer than the agent interrupt window must not be an **agent**
job. An agent prompt that shells out to a 6-30 minute script dies mid-run with
`last_error: interrupted`, an ever-climbing `failure_streak`, and no output —
while the job still reads as scheduled. The agent wrapper adds nothing when the
script already does the work; it only adds a timeout.

**Convert to `no_agent: true` + a script.** The no-agent path has no agent turn
to interrupt. Sequence to encode in the script (it replaces the prompt's
instructions, which no longer get a chance to run):

1. snapshot any file the job may rewrite, so a bad write is revertible
2. run the work, capturing output
3. if a file changed and the platform has tests, run them and **revert on red**
4. print a short report — under `no_agent` the script's stdout IS the delivery

```bash
hermes cron create "0 10 * * 0" --name "X (weekly, script)" \
  --script run_x.py --no-agent --deliver local
hermes cron pause <old_agent_job_id>     # keep history, don't delete
```

**Stream, don't buffer.** A wrapper using `subprocess.run(capture_output=True)`
prints nothing until the child exits, so a 20-minute job is indistinguishable
from a hang. Stream line-by-line (`Popen` + iterate `stdout`) so progress is
visible and a stall is obvious. Note the CHILD's own stdout is block-buffered
when piped — `python -u` on the child fixes late-appearing progress.

**Bound the CPU with a cgroup, not with thread caps.** Long research jobs make
the desktop unusable when they saturate cores. Wrap the child:

```python
if quota:
    probe = subprocess.run(["systemd-run", "--user", "--scope", "--quiet",
                            "-p", f"CPUQuota={quota}", "/bin/true"],
                           capture_output=True, timeout=20)
    if probe.returncode == 0:
        args = ["systemd-run", "--user", "--scope", "--quiet",
                "-p", f"CPUQuota={quota}", "--", *args]
```

- `systemd-run --user --scope` needs a live user session; probe with `/bin/true`
  first and **fall back to a plain run** rather than skipping the job.
- **`Nice=` is NOT assignable on a transient `--scope`** (`Unknown assignment:
  Nice=10`). `CPUQuota` alone is the mechanism; niceness needs a real service unit.
- Verify the cap bites by measuring, not by reading the flag: a CPU burner doing
  6s of wall time consumes ~6s CPU uncapped and ~3s at `CPUQuota=50%`.
- Capping BLAS/OpenMP threads (via `sitecustomize.py` or `OMP_NUM_THREADS`) also
  lowers CPU, but it stretches wall clock — for a daily job that is usually the
  wrong tradeoff. Fix the WORK first (cache fetches, skip unused computation);
  treat thread caps as a separate, measured decision.

**Clear orphans before trusting a slow run.** Killing a wrapper does not kill
its children; cron-spawned worker scripts can run for hours after their parent
exited, and a handful of them will drive load average to 40+ on a 12-core box.
Before blaming a job's runtime: `ps -eo pid,pcpu,etime,cmd --sort=-pcpu | head`,
`uptime`, and `pgrep -af "<script>"`. A single job at 150% CPU is normal; load 40
with no visible hog means orphans or a game/app competing. Check `uptime` BEFORE
labelling the code slow.

## Gateway health jobs

For a "gateway alive" check cron, curl the port and report the code; 404 on `/` means the API is up (it's an API server). `gateway_state.json` can be STALE (says running, PID dead) — trust the curl, not the file.

## Library audit procedure

1. `cronjob action=list` — for each job note schedule, `last_status`, `next_run_at`.
2. Flag: `last_status: error` → read `cron/output/<job_id>/<latest>.md` for the Script Error / RuntimeError block.
3. Flag: `last_run_at: null` on a job created >1 day ago → it's new and simply hasn't fired yet; check `next_run_at` instead of treating as broken.
4. Script jobs: verify the script file exists and runs fast.
5. `no_agent: true` + script-only jobs are the cheapest form — prefer them for watchdogs/pollers that need no reasoning.
6. `hermes cron doctor` — lateness and catch-up warnings that `cron list` doesn't show.
7. `hermes cron incidents` — durable failure incidents with resolved/unresolved state.
8. Paused (`state: paused`) and disabled (`enabled: false`) jobs are audit items: resume a paused watchdog (`hermes cron resume <id>`) only after verifying the condition that paused it is gone; a disabled backup/export job is lost coverage someone may still be relying on — surface it prominently instead of assuming it was intentional.

## Pitfalls

- **No-agent `.py` cron scripts run on the generation venv python, not system python3** — and a dependency generation rebuild wipes manually pip-installed packages, so a script that ran clean yesterday dies `ModuleNotFoundError` today. Any script importing a third-party package must self-heal on `ImportError`: probe `shutil.which("uv")` and the current tools dir (never hardcode a versioned uv path — the versioned dir gets removed), install with `uv pip install --python <that venv python> <pkg>`, then retry. Keep the import cost out of the hot path.
- rglob over a big tree (node_modules etc.) times out cron scripts — use os.walk with a SKIP set.
- `deliver: local` jobs write output to `cron/output/<job_id>/` — that's where error detail lives.
- Cron sessions can't ask questions — prompts must be self-contained.
- Cron-run sessions should not recursively schedule more cron jobs.

---
name: debugging-spawned-processes
description: Debugging CLI tools and multi-process apps that behave differently when spawned from a process manager (Electron, Docker, CI) vs an interactive terminal. Covers TTY detection failures, env var path poisoning, port conflict handling in non-TTY mode, and orphaned child process cleanup.
---

# Debugging Spawned Processes

## When to Use

A CLI tool or multi-process app that:
- Works fine in an interactive terminal but **hangs, exits immediately, or "stops after a while"** when launched from:
  - An Electron app process manager (`child_process.spawn`, PowerShell `Start-Process`)
  - Docker / CI runners
  - Systemd, PM2, or any non-TTY context
- Spawns child processes (backend server + frontend dev server) that orphan or die early
- Has port conflict issues that only surface when launched via a manager

## Diagnosis Checklist

### 1. TTY Detection Check

The most common cause: the CLI uses `sys.stdin.isatty()` to decide whether to prompt interactively:

```python
if sys.stdin.isatty():
    choice = input("Port conflict. Change ports? [1/2]: ")
else:
    raise SystemExit("Port in use")  # ← kills process silently
```

**Test:** Run the exact command in a real terminal. If it works there but not from the process manager, it's a TTY issue.

### 2. Env Var Path Poisoning

When a tool uses a `*_HOME` env var, check if the config system **already appends subdirectories**:

```python
# DEEPTUTOR_HOME=/project/data
# settings = os.path.join(home, "data/user/settings")
# Result: /project/data/data/user/settings  ← double nesting!
```

**Fix:** Set `*_HOME` to the project root, not a subdirectory. Or don't set it at all.

### 3. Port Conflict in Non-TTY Mode

Tools that handle port conflicts via interactive prompts will silently die in headless contexts.

**Fix:** Kill stale processes before launching, or use a dedicated port range:
```bash
taskkill //F //PID <pid>
lsof -ti :8005 | xargs kill
```

### 4. Orphaned Child Processes

When the parent CLI process dies (from SystemExit or crash), child processes may continue:
```bash
# Find orphans
tasklist //FI "IMAGENAME eq node.exe"
tasklist //FI "IMAGENAME eq python.exe"

# Kill by port
netstat -ano | findstr :8005
taskkill //F //PID <pid>
```

**Windows/MSYS pitfall — `taskkill` itself fails or hangs.** In git-bash on Windows:
- `taskkill //F //PID <pid>` → `ERROR: Invalid argument/option - '//F'` (double-slash mangling)
- `taskkill /F /PID <pid>` → can hang indefinitely with no output

**Reliable kill from git-bash: PowerShell wins.**
```bash
powershell -Command "Stop-Process -Id <pid> -Force"   # works where taskkill hangs
```
This bites with orphaned `next dev` servers: Next.js sees the stale PID on port 3000 (`⚠ Port 3000 is in use by process <pid>`), refuses to start, and the orphan doesn't answer HTTP (`curl` → `000`). Kill via `Stop-Process`, confirm with `netstat -ano | grep ":3000 .*LISTENING"` returning nothing, then start fresh. Note Next falls back to port 3001 when 3000 looks occupied — always check which port the new server actually bound (`Ready in ... Local: http://localhost:<port>`).

### 5. Python Venv Path Leaking

When a parent process (Electron, process manager, bash with activated venv) spawns a child that uses its own Python venv, the parent's `PYTHONPATH` and `sys.path` leak into the child. The child imports the parent's packages instead of its own.

**Symptom:** `ModuleNotFoundError: No module named 'X'` or wrong version of X loaded, even though the child's venv has X installed. The traceback shows the parent's site-packages path.

**Diagnosis:**
```bash
# Check what sys.path the child actually sees
child-venv/python -c "import sys; print('\n'.join(sys.path))"
# If parent's site-packages appears before child's → leak confirmed
```

**Fix:** Clear PYTHONPATH in the launch command before running the child:
```powershell
# PowerShell launch script
$env:PYTHONPATH=''
poetry run python -m app.module serve
```

```bash
# Bash
PYTHONPATH="" python -m app.module serve
```

**Why it happens:** Poetry/venv activation doesn't clear inherited env vars. The parent's PYTHONPATH stays in the environment and Python prepends it to sys.path.

**Example:** AutoGPT (poetry venv) crashed with `ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'` when launched from the App Centerpiece Electron app. The Electron process inherited Hermes agent's venv PYTHONPATH. Fix: added `$env:PYTHONPATH=''` to the launch script in `apps.registry.json`. See `references/python-venv-isolation-fix.md` for full case study.

### 6. Runtime Detection via Process Ancestry (Windows)

Some CLIs (agent-runtime detectors, AMA runners, `ak`/agent-kanban) identify their
host by walking the **native Windows process tree** (a compiled `process-tree.node`
addon) from `process.ppid` upward and regex-matching each ancestor's command line
(e.g. `hermes_cli\.main`). Failure symptom: `Could not locate <runtime> process in
ancestry` even though the runtime is clearly running — typically when invoked from
git-bash, PowerShell, or an agent tool terminal.

**Key finding (tested):** the walk truncates at **script interpreters** —
`#!/bin/sh`, `#!/bin/bash`, and `#!/usr/bin/env node` wrappers appear as children
whose parent is unresolvable to the addon, so the chain dies there. Chains that DO
survive:
- `node ...` invoked directly (no script file) ✅
- `.cmd` files: the `cmd.exe` layer keeps the parent link ✅

**Fix:** make the wrapper delegate through `cmd.exe` so the chain stays intact:
```sh
#!/bin/sh
exec cmd //c "C:\\...\\tool.cmd" "$@"
```
Do NOT delete the shim expecting bash to fall back to `tool.cmd` — git-bash does
not fall back to `.cmd` for a bare command name (command becomes "not found").

**Probe:** dump the ancestry exactly as the addon sees it before concluding
anything about the chain (see `agent-kanban-ops` → `references/setup-windows-git-bash.md`
for the probe snippet).

## Fix: Bypass the CLI Wrapper

Run component processes directly instead of through the wrapper:

```bash
# Instead of:  deeptutor start
# Backend
cd /project && uvicorn module:app --host 0.0.0.0 --port 8005 &
# Frontend
cd /project/web && npx next dev -p 3785 &
```

## Common Patterns by Platform

| Platform | TTY behavior | Fix |
|----------|-------------|-----|
| Electron `child_process.spawn` | stdin piped (isatty=False) | Run component commands directly |
| PowerShell `Start-Process` | No stdin inherited | Use `-NoNewWindow` or separate commands |
| Docker | No TTY unless `-it` | Use `docker run -it` or override interactive flag |
| systemd | No TTY | Use `Type=simple` + `StandardInput=null` |
| CI (GitHub Actions) | No TTY | Bypass interactive wrappers |

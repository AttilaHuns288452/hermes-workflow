---
name: python-cli-troubleshooting
description: Troubleshoot Python CLI tools that hang, crash silently, or fail on startup — especially when individual components work but the orchestrated CLI wrapper does not. Covers env-var pollution, config path resolution, non-TTY port conflicts, import-time side effects, and Windows subprocess quirks.
---

# Python CLI Tool Troubleshooting

## Overview

Python CLI tools that orchestrate multiple subprocesses (backend + frontend servers) can fail silently — hanging with no output, crashing without a trace, or exiting before the user sees anything. This skill provides a structured approach to diagnosing and fixing these "invisible" failures.

The core insight: **when individual components work in isolation but the CLI wrapper does not, the problem is in the orchestration layer** — environment propagation, path resolution, or subprocess lifecycle.

## When to Use

- `myapp start` hangs with no output, but `myapp serve` works
- A Python CLI tool launches subprocesses that show no output
- The tool works in one terminal session but not another
- Port conflicts cause the tool to exit silently
- Changing environment variables (`DEEPTUTOR_HOME`, `PYTHONPATH`, etc.) causes weird behavior
- A process manager (Electron, systemd, supervisor) reports the app as "not running"
- Windows: PowerShell or cmd script launches Python but the window closes immediately

## Diagnostic Checklist

### 1. Component Isolation Test

Run the backend and frontend separately to identify which layer is failing:

```bash
# Backend alone
cd /project
python -m uvicorn app.main:app --host 127.0.0.1 --port XXXX

# Frontend alone (source install)
cd /project/web
npm run dev -- --port YYYY

# Or with the app's serve command
deeptutor serve --port XXXX --host 127.0.0.1
```

If both work independently → the CLI wrapper orchestration is the failing layer.

### 2. Trace Config/Settings File Resolution

Many Python tools resolve their config path by concatenating an env var (`DEEPTUTOR_HOME`, `APP_HOME`, etc.) with a relative path like `data/user/settings/system.json`. This is easy to get wrong:

```python
# Debug: print the actual resolved path
from deeptutor.services.config import load_launch_settings
from deeptutor.runtime.home import get_runtime_home

home = get_runtime_home(None)
print(f"runtime_home = {home}")

settings = load_launch_settings(home)
print(f"Settings path: {settings.system_json_path}")
print(f"File exists: {settings.system_json_path.exists()}")
```

**Common bug:** If `DEEPTUTOR_HOME=/project/data` but the code appends another `data/`, the path becomes `/project/data/data/user/settings/system.json` — DOUBLE nesting. The fix is to set `DEEPTUTOR_HOME` to the project root, not a subdirectory.

### 3. Check for Lingering Environment Variables

Terminal sessions share shell state across calls. A previous `export VAR=value` persists and can silently corrupt config:

```bash
# Check what's set
echo "$DEEPTUTOR_HOME"
env | grep DEEPTUTOR

# Clear it
unset DEEPTUTOR_HOME
```

**Signal:** A tool works after `unset` but fails with the env var set.

**Venv leakage variant:** On this machine, the Hermes venv's site-packages is always in sys.path. When running `poetry run` or `pipenv run` from a Hermes-activated shell, the target venv's modules can be shadowed by Hermes venv modules. Fix: `PYTHONPATH='' poetry run ...` or `$env:PYTHONPATH=''` in PowerShell scripts. See `references/autogpt-pydantic-core-venv-leakage.md`.

### 4. Check for Non-TTY Port Conflict Resolution

Many tools detect port conflicts interactively using `sys.stdin.isatty()`. When launched from a process manager (Electron app, systemd, Docker, CI), stdin is NOT a TTY, so the prompt raises `SystemExit` silently — the process dies before printing anything.

```bash
# Check if any process is listening on the target ports
netstat -ano | grep :PORT
# Windows alternative
wmic process where "CommandLine like '%:PORT%'" get ProcessId,CommandLine
```

**Fix:** Kill conflicting processes first, or update the settings file to use different ports that are definitely free.

### 5. Check for Import-Time Side Effects

When you run `myapp start`, Python imports the module. Some modules trigger side effects on import — creating directories, starting threads, reading config files, etc. These can:

- Create directories in the wrong location (based on a stale env var)
- Block on network I/O if a client connects during import
- Read config from a path that's been corrupted by previous runs

```bash
# Isolate the import to see what it does
timeout 30 python -c "from myapp.launcher import start; print('imported')"
```

If this hangs, the import itself is the problem (not the CLI entry point).

### 6. Windows-Specific Subprocess Gotchas

```python
# Common pattern on Windows
if os.name == "nt":
    kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
```

`CREATE_NEW_PROCESS_GROUP` on Windows creates a new console process group. This is fine for the subprocess itself but can cause:

- **The stdout pipe to buffer differently** than on Linux — line buffering (`bufsize=1`) may not work on Windows pipes
- **Subprocesses to live on after parent death** — orphan process group
- **Ctrl+C handling to behave differently** — signal groups vs console events

On Windows, use `subprocess.PIPE` with `text=True` and `encoding="utf-8"`. If a subprocess produces no output despite running successfully, suspect pipe buffering (use `PYTHONUNBUFFERED=1`).

### 7. CLI Entry Point Hangs But Direct Python Call Works

A distinctive failure mode: `mycli command` (installed executable) or `python -m mypackage.cli` hangs forever, but calling the core function directly from `python -c` works instantly.

**Root cause:** The CLI wrapper layer — the code between `main()` being called and the actual work starting. This can include:

- **Session claim/mutex logic** — the CLI tries to acquire an exclusive lock on a session database or file, and a previous crashed session left the lock stale. Common in tools with `_claim_active_session()` patterns.
- **Config resolution that blocks** — importing modules at startup that do network I/O (MCP server discovery, API key validation, model catalog fetch).
- **Signal handlers** — registering SIGINT/SIGTERM handlers that interfere when the process isn't in a real TTY.
- **Plugin/skill discovery** — scanning directories for plugins that contain an import which blocks (missing dependency, Windows path traversal on a broken symlink).
- **Compiled entry point (Windows)** — The installed `mycli.exe` is a PE binary (`MZ` header). The compiled stub → Python venv → script path behaves differently from `python -c` in working dir, env var propagation, and stdout buffering.

**How to diagnose:**

```bash
# 1. Confirm the split: direct call vs entry point
python -c "from pkg.core import main; main()"          # works?
python -m pkg.cli command                              # hangs?
mycli command                                          # hangs?

# 2. Trace with verbose imports to find the hang site
python -v -m pkg.cli command 2>&1 | tail -20
# The last import shown before timeout = near the hang site

# 3. Check if the compiled entry point is a PE binary
head -c 2 $(which mycli)    # "MZ" on Windows = compiled binary

# 4. Isolate the CLI wrapper with debug logging
export MYAPP_DEBUG=1
mycli command

# 5. Bypass the entry point entirely as a workaround
alias mycli='python -c "from pkg.core import main; main()"'
```

**Fix pattern:** Once located, the blocking call usually falls into one category:
- A synchronous server discovery call without timeout → wrap with `asyncio.wait_for(..., timeout=5)`
- A stale session database lock from a crashed process → add cleanup on startup
- A plugin sync that blocks on network → add `quiet=True` + timeout
- An import-time side effect (logging setup connecting to remote server) → defer to first-use

### prompt_toolkit + MSYS2/cygwin (git-bash) on Windows

A distinctive Windows-only failure mode: the CLI hangs at startup (no output, timeout) when run from **git-bash** or **MSYS2** but works from `cmd.exe` / Windows Terminal.

**Root cause:** `prompt_toolkit` detects `TERM=xterm-256color` (set by git-bash) and attempts to create a `Win32Output` via `kernel32.GetStdHandle()` / `GetConsoleScreenBufferInfo()`. Git-bash (MSYS2) does NOT provide a real Win32 console buffer — it's an `xterm` emulation layer on top of pipes. The call returns `NoConsoleScreenBufferError`, and if uncaught, the `Application.__init__()` blocks indefinitely.

**Diagnostic signal:** The CLI prints `"Initializing agent..."` then hangs with no further output for 60+ seconds and eventually times out. Running the same command from `cmd.exe` or Windows Terminal works instantly.

**Verify:**
```bash
echo $TERM     # "xterm-256color" in git-bash

python -c "
from ctypes import windll
stdout = windll.kernel32.GetStdHandle(-11)
info = windll.kernel32.GetConsoleMode(stdout, 0)
print('Has console:', bool(info))  # False in git-bash
"
```

**Fix** (priority order):

1. **`--quiet`/`-Q` flag** (for single queries) — Skips prompt_toolkit entirely, calls `agent.run_conversation()` directly. `hermes chat -q "..." -Q` works in git-bash.
2. **Run from native terminal** — `cmd.exe`, PowerShell, or Windows Terminal provide a real Win32 console. `hermes doctor` and interactive mode work there.
3. **`TERM=`** — Unsetting `TERM` is unreliable; prompt_toolkit may still detect MSYS2.
4. **`winpty`** — Works for interactive TTY but fails for piped/non-TTY (`stdin is not a tty`).

### Windows: Python Entry Point Quirks

Python CLI tools installed via pip create a `.exe` shim in `venv/Scripts/` (small PE binary from distlib). Differs from `python -m` / `python -c`:

- **stdout encoding:** PE shim may not set UTF-8 mode → UnicodeEncodeError on non-ASCII. Some tools call `configure_windows_stdio()` explicitly.
- **Process group:** Shim starts a new Windows job object → interferes with Ctrl+C + orphan cleanup.
- **Environment mutation:** Shim resolves venv Python, appends to PATH, but may not forward `PYTHONPATH`, `PYTHONUNBUFFERED`, or custom env vars.
- **Elevation:** Non-elevated terminal → shim triggers admin-check → different behavior.

**If `python -m pkg.main` works but `pkg` (.exe) hangs**, compare PATH env between the two:
```bash
python -c "import os; print(os.environ['PATH'])"  # vs when running the .exe
```

## Quick Reference

| Symptom | Most Likely Cause | Diagnostic |
|---------|------------------|------------|
| Hangs with no output, components work separately | CLI wrapper orchestration issue | Run components in isolation |
| Works in one terminal but not another | Stale env var | `unset VAR` and retry |
| Config is wrong despite correct settings file | Double path nesting | Print resolved path |
| Process dies when launched from manager | Non-TTY port conflict | Kill orphaned processes on target ports |
| Import hangs | Import-time side effect | `timeout 30 python -c "import module"` |
| Subprocess produces no output | Pipe buffering on Windows | Set `PYTHONUNBUFFERED=1` |
| Installed CLI hangs, `python -c` works | CLI wrapper layer (entry point) | Run `python -v -m pkg.cli` to find where it blocks |
| `poetry run` imports wrong venv's modules | Venv leakage via sys.path | `PYTHONPATH='' poetry run ...`; see `references/autogpt-pydantic-core-venv-leakage.md` |
| CLI hangs in git-bash but works in cmd.exe | prompt_toolkit + MSYS2/cygwin | Use `-Q` flag or run from Windows Terminal; `hermes doctor` slow at "connectivity checks" (26 parallel pings, one blocks) — not a bug |

## Concrete Examples

📎 [`references/deeptutor-startup-hang.md`](references/deeptutor-startup-hang.md) — Full reproduction recipe for the DeepTutor case that motivated this skill: env-var path multiplication, orphaned processes, non-TTY port conflict, and the fix sequence.

📎 [`references/hermes-cli-entrypoint-hang.md`](references/hermes-cli-entrypoint-hang.md) — Hermes Agent CLI hangs on `hermes chat -q` but direct `cli.main()` call works: debugging walkthrough for the CLI entry point vs direct Python API divergence on Windows.

📎 [`references/autogpt-pydantic-core-venv-leakage.md`](references/autogpt-pydantic-core-venv-leakage.md) — `poetry run` from Hermes-activated shell picks up Hermes venv's broken pydantic_core instead of the target venv. Fix: `$env:PYTHONPATH=''` before poetry run. Applies to any venv-in-venv leakage on this machine.

# DeepTutor Startup Hang — Reproduction & Fix

## Symptoms

- `deeptutor start` hangs with no output for 2+ minutes
- `deeptutor serve --port 8005` works fine independently
- Individual backend (uvicorn) and frontend (Next.js) work when started separately
- The App Centerpiece (Electron launcher) shows "Not Running"

## Root Cause

The `DEEPTUTOR_HOME` environment variable was set to the `data/` subdirectory, but the launcher code appends another `data/` internally:

```
DEEPTUTOR_HOME=/project/data
→ get_runtime_home() = /project/data
→ load_launch_settings() looks at /project/data/data/user/settings/system.json  ← WRONG!
→ Expected: /project/data/user/settings/system.json
```

The nested `data/data/` path either:
1. Doesn't exist (new repos) — the tool uses hardcoded defaults (ports 8001/3782)
2. Exists and has stale config (from previous runs) — overriding the intended config

## Fix Steps

### 1. Fix the environment variable

```powershell
# ❌ WRONG — causes double nesting
$env:DEEPTUTOR_HOME = 'C:\Path\To\Project\data'

# ✅ CORRECT — set to project root
$env:DEEPTUTOR_HOME = 'C:\Path\To\Project'
# Or don't set it at all (defaults to project root)
```

In the centerpiece `apps.registry.json`, do NOT set `DEEPTUTOR_HOME` in the launch script:

```json
"script": "Set-Location 'C:\\...\\DeepTutor'\n$env:PYTHONUTF8='1'\n& '.venv2\\Scripts\\python.exe' -m deeptutor_cli.main start"
```

### 2. Verify the settings path

```bash
cd /project && source .venv/Scripts/activate
timout 30 python -c "
import os
os.environ.pop('DEEPTUTOR_HOME', None)  # clear first
from deeptutor.services.config import load_launch_settings
from deeptutor.runtime.home import get_runtime_home
settings = load_launch_settings(get_runtime_home(None))
print(f'Backend port: {settings.backend_port}')
print(f'Frontend port: {settings.frontend_port}')
print(f'Path: {settings.system_json_path}')
"
```

### 3. Fix the settings

Write `data/user/settings/system.json` with custom ports:

```json
{
  "version": 1,
  "backend_port": 8005,
  "frontend_port": 3785,
  ...
}
```

### 4. Clean up stale nested directories

```bash
rm -rf /project/data/data
```

### 5. Kill orphaned processes

```powershell
netstat -ano | grep ":8005"    # Find PID
taskkill //F //PID <PID>       # Kill it
# Repeat for frontend port
```

## Verification

After fixing:
1. `deeptutor start` should produce output within 10-15 seconds
2. `curl http://127.0.0.1:8005/` returns `{"message":"Welcome to DeepTutor API"}`
3. `curl -sI http://127.0.0.1:3785/` returns HTTP 200
4. Centerpiece shows "Running" status

## Related Issues

- **Port conflict in non-TTY**: When the centerpiece process manager launches `deeptutor start`, stdin is not a TTY. If ports are occupied, `_resolve_port_conflicts()` raises `SystemExit` silently. Fix: clear ports first, or fix the ports in `system.json`.
- **Env var persistence**: `export DEEPTUTOR_HOME=data` in one terminal() call persists to all subsequent calls. Always `unset` or clear stale vars when switching between test configurations.

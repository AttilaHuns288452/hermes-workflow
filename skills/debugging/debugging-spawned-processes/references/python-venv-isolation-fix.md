# Python Venv Isolation Fix — AutoGPT / App Centerpiece

## Problem

AutoGPT (poetry venv) crashed when launched from the App Centerpiece Electron app:

```
ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'
```

The error pointed to the **Hermes agent venv's** site-packages, not AutoGPT's own venv.

## Root Cause

The Electron app's process manager spawns PowerShell, which inherits the current shell's environment. The Hermes agent venv was activated in that shell, so `PYTHONPATH` contained:

```
C:\Users\Attila\AppData\Local\hermes\hermes-agent\Lib\site-packages
```

AutoGPT's poetry venv has its own pydantic_core at:

```
C:\Users\Attila\AppData\Local\pypoetry\Cache\virtualenvs\autogpt-classic-F0I4XBFc-py3.12\Lib\site-packages\pydantic_core\_pydantic_core.cp312-win_amd64.pyd
```

But Python prepends the inherited `PYTHONPATH` to `sys.path`, so it found the Hermes venv's broken pydantic_core first.

## Verification

```bash
# Check sys.path in the child venv
"/c/Users/Attila/AppData/Local/pypoetry/Cache/virtualenvs/autogpt-classic-F0I4XBFc-py3.12/Scripts/python.exe" -c "import sys; print('\n'.join(sys.path))"

# Output showed Hermes venv BEFORE AutoGPT venv in sys.path
```

## Fix

Added `$env:PYTHONPATH=''` to the AutoGPT launch script in `apps.registry.json`:

```powershell
Set-Location 'C:\Users\Attila\Documents\Projects\AutoGPT\classic'
$env:PYTHONUTF8='1'
$env:PYTHONPATH=''
poetry run python -m autogpt.app.cli serve
```

## Prevention

When writing launch scripts for Python apps that use their own venv:

1. Always clear `PYTHONPATH` before activating/running the child venv
2. On PowerShell: `$env:PYTHONPATH=''`
3. On Bash: `PYTHONPATH="" command`
4. This is especially important when the parent process has its own Python environment active

## Related

- `debugging-spawned-processes` skill, section 5: Python Venv Path Leaking
- `config-state-debugging` skill for other env var state issues

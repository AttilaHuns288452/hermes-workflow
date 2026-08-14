# AutoGPT pydantic_core Venv Leakage

## Symptom

```
ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'
```

Running `poetry run python -m autogpt.app.cli serve` from a shell that has
Hermes venv activated. The AutoGPT poetry venv has a working
`_pydantic_core.cp312-win_amd64.pyd`, but Python imports from Hermes venv
instead.

## Root Cause

The shell's sys.path includes the Hermes venv's site-packages BEFORE the
poetry venv's site-packages. When `poetry run` executes, Python resolves
`pydantic_core` from the first matching path — Hermes venv — which has a
broken or incompatible `_pydantic_core` module.

```
sys.path (from poetry run python):
  0: C:\Users\YOUR_USERNAME\AppData\Local\hermes\hermes-agent          ← HERMES
  1: C:\Users\YOUR_USERNAME\AppData\Local\hermes\hermes-agent\venv\Lib\site-packages  ← HERMES
  ...
  6: C:\Users\YOUR_USERNAME\AppData\Local\pypoetry\Cache\virtualenvs\autogpt-classic-F0I4XBFc-py3.12
  7: ...\Lib\site-packages                                        ← AUTOGPT (too late)
```

## Fix

Clear PYTHONPATH before running poetry:

```powershell
# In the launch script (apps.registry.json)
$env:PYTHONUTF8='1'
$env:PYTHONPATH=''
poetry run python -m autogpt.app.cli serve
```

Or from bash:
```bash
PYTHONPATH="" PYTHONUTF8=1 poetry run python -m autogpt.app.cli serve
```

## Verification

```python
import sys
print([p for p in sys.path if 'hermes' in p.lower()])
# Should be empty after fix
```

## Applicability

Any `poetry run` / `pipenv run` / `venv` activation from a shell with
another venv active. The Hermes venv is the most common offender on this
machine because it's always in the shell environment.

## AutoGPT Notes

- Classic AutoGPT is backend-only (legacy project)
- Frontend lives in `autogpt_platform/frontend` (separate Next.js app)
- Server expects frontend at `classic/classic/frontend/build/web` — doesn't exist
- Use Agent Protocol API at `http://localhost:8000/docs` instead

# AutoGPT Setup Reference

## Repository

`https://github.com/Significant-Gravitas/AutoGPT`

Cloned to: `~/Documents/Projects/AutoGPT/`

## Two Paths

| Path | Requirements | Notes |
|------|-------------|-------|
| **Classic** (Python-only) | Python 3.12, Poetry | Full agent with CLI + HTTP serve mode |
| **Platform** | Docker Desktop | Blocked — Docker not installed on this Windows machine |

Use **Classic**.

## Setup Steps

### 1. Clone

```bash
git clone --depth 1 https://github.com/Significant-Gravitas/AutoGPT.git ~/Documents/Projects/AutoGPT
```

### 2. Install Poetry (if missing)

```bash
uv tool install poetry
```

### 3. Install dependencies

```bash
cd ~/Documents/Projects/AutoGPT/classic
poetry install
```

### 4. Create `.env`

Place at `~/Documents/Projects/AutoGPT/classic/.env`:

```ini
# AutoGPT Classic - Environment Configuration
OPENAI_API_KEY=sk-or-...        # OpenRouter API key
OPENAI_API_BASE_URL=https://openrouter.ai/api/v1

SMART_LLM=deepseek/deepseek-chat-v3-0324:free
FAST_LLM=deepseek/deepseek-chat-v3-0324:free
EMBEDDING_MODEL=text-embedding-3-small

RESTRICT_TO_WORKSPACE=True
FILE_STORAGE_BACKEND=local
LOG_LEVEL=INFO
AP_SERVER_PORT=8000
```

### 5. Known Patch — Pydantic Enum Validation

If `config.py` fails with `m.value` not iterable over `OpenAIModelName`, patch:

```python
# In original_autogpt/autogpt/app/config.py:
# Change:
if set((config.smart_llm, config.fast_llm)).intersection(OpenAIModelName):
# To:
if set((config.smart_llm, config.fast_llm)).intersection(m.value for m in OpenAIModelName):
```

This is because `OpenAIModelName` is a Pydantic v2+ enum — you need to iterate `.value` explicitly.

### 6. Custom Model Fallback in `multi.py`

`forge/forge/llm/providers/multi.py` has a `get_model_provider()` method. If the model name isn't in `CHAT_MODELS` (the case for OpenRouter models), it falls back to the OpenAI provider when `OPENAI_API_BASE_URL` is set. This already works — no patch needed.

## Running

### Serve mode (recommended for centerpiece)

```bash
cd ~/Documents/Projects/AutoGPT/classic
poetry run autogpt serve
```

Starts on `http://localhost:8000` with:
- Swagger UI: `http://localhost:8000/docs`
- Agent Protocol API: `/ap/v1/agent/tasks` (POST to create tasks)
- Heartbeat: `/ap/v1/heartbeat`

### Interactive mode

```bash
poetry run autogpt run --skip-news
```
Prompts for a task interactively. Use `--continuous -c` for autonomous loop.

## App Centerpiece Registry Entry

```json
{
  "id": "autogpt",
  "name": "AutoGPT",
  "description": "Autonomous AI agent server with Agent Protocol API",
  "cwd": "C:\\Users\\Attila\\Documents\\Projects\\AutoGPT\\classic",
  "launch": {
    "shell": "powershell",
    "script": "Set-Location 'C:\\Users\\Attila\\Documents\\Projects\\AutoGPT\\classic'\n$env:PYTHONUTF8='1'\n& (poetry env info --path)\\Scripts\\python.exe -m autogpt.app.cli serve",
    "windowStyle": "normal",
    "startupProbe": {
      "mode": "processMatch",
      "match": {
        "field": "commandLine",
        "value": "autogpt.app.cli serve"
      }
    }
  },
  "openTarget": {
    "type": "url",
    "value": "http://localhost:8000/docs"
  },
  "stop": {
    "mode": "processTreeMatch",
    "match": {
      "field": "commandLine",
      "value": "autogpt.app.cli serve"
    }
  },
  "notes": "Agent Protocol API on port 8000. Submit tasks via POST /ap/v1/agent/tasks."
}
```

**Key detail:** Use `(poetry env info --path)\\Scripts\\python.exe` in the registry script rather than `poetry run`. The `poetry run` pattern wraps the command through Poetry CLI which may not resolve paths correctly in the Electron process manager. Calling the venv Python directly is more reliable.

## Pitfalls

- **No official frontend for classic**: The modernization PR (Apr 2026) deliberately removed the frontend (`benchmark/frontend/` React app). The `classic/` directory on GitHub has no `frontend/` folder. The `agent_protocol_server.py` still has `frontend_path` check but it's dead code. If you want a UI, build a custom one that talks to the Agent Protocol API at `/ap/v1/agent/tasks`. The `autogpt_platform/frontend` is a different app (Next.js, port 8006, workflow builder — not compatible with classic backend).
- **PYTHONPATH leak from Hermes venv**: When launching AutoGPT from the centerpiece or any process that shares the shell with Hermes, the Hermes venv leaks into `PYTHONPATH`, causing `ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'`. Fix: set `$env:PYTHONPATH=''` (PowerShell) or `PYTHONPATH=""` (bash) before the launch command. The centerpiece registry entry for AutoGPT includes this fix.
- **Frontend warning**: `WARNING  Frontend not found. classic/frontend/build/web does not exist` — harmless if you have no frontend. If you built a custom frontend, place it at `classic/classic/frontend/build/web/index.html` (note the double `classic/` — the path resolves from `original_autogpt/autogpt/app/` going up 3 levels).
- **Port conflicts**: If port 8000 is occupied, set `AP_SERVER_PORT=8001` in `.env`.
- **`--skip-news`** is only valid for `run` command, not `serve`.
- **`poetry run autogpt --help`** may fail with path collision if the system `openai` package (from Hermes venv) conflicts with the project's pinned version. Always use `poetry run` from the classic directory with `unset PYTHONPATH`.

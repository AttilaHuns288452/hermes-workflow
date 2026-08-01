# OpenAI Base URL Patch Pattern

When setting up open-source AI projects that use the OpenAI Python SDK, the project almost always hardcodes the constructor:

```python
client = OpenAI(api_key="sk-...")
```

This **breaks** under local or self-hosted proxies (FreeLLMAPI, LiteLLM, vLLM, Ollama, LM Studio, etc.) because `OpenAI()` defaults to `https://api.openai.com/v1`.

## The Fix

A minimal, non-breaking patch that keeps the official OpenAI endpoint as the default while enabling local proxy use via `OPENAI_BASE_URL`:

### Step 1 — Add the env var to the config module

In the project's config/settings module (e.g. `config.py`), add:

```python
OPENAI_BASE_URL = (os.getenv("OPENAI_BASE_URL") or "").strip() or None
```

The `or None` is important — `OpenAI(base_url=None)` uses the default official endpoint, so the existing code path is preserved when no env var is set.

### Step 2 — Pass it to the OpenAI constructor

Find the `OpenAI(api_key=...)` call and add `base_url`:

```python
client = OpenAI(api_key=require_openai_key(), base_url=OPENAI_BASE_URL)
```

### Step 3 — Update `.env.example`

Add the new variable so it's discoverable:

```ini
OPENAI_BASE_URL=              # Optional: OpenAI-compatible proxy (e.g. http://localhost:3001/v1)
```

## What to Look For

Check these locations (in order):
1. **`shorts_generator/config.py`** or similar config module — look for `os.getenv("OPENAI_API_KEY"` as the anchor
2. **Local LLM backends** — `local/llm.py`, `providers/openai.py`, `client.py`, `api.py` — these are where the `OpenAI()` constructor lives
3. **`OpenAI(api_key=...)`** — grep for this pattern across the codebase

## Common Pitfalls

| Pitfall | Why | Fix |
|---------|-----|-----|
| `OpenAI(api_key=..., base_url=None)` | Passing `None` explicitly triggers OpenAI's default base_url internally — safe but redundant | `base_url=None` is fine; `base_url=OPENAI_BASE_URL` with `or None` is cleaner |
| `base_url="http://localhost:3001/v1"` hardcoded | Works for one proxy, breaks for all others | Always make it an env var with a documented default |
| Forgetting the trailing `/v1` | Different proxies expect different path suffixes | Use env var so the user provides the exact base URL their proxy exposes |
| Only patching one `OpenAI()` call when there are multiple | Some projects have separate client instances for different subsystems | `grep -rn "OpenAI(" src/` to find all occurrences |
| Not updating `.env.example` after patching | The env var exists but no one knows about it | Always update `.env.example` after adding a new env var |
| `OPENAI_BASE_URL` vs `OPENAI_API_BASE` vs `OPENAI_ENDPOINT` | Inconsistency across projects causes confusion | Standardize on `OPENAI_BASE_URL` — it matches what `litellm`, `langchain`, and `openai-python` all use |

## Why This Pattern Matters

The user's ecosystem runs **FreeLLMAPI** at `localhost:3001/v1` as the primary local proxy, aggregating 107+ free models from 16 providers. Almost every new AI project needs this patch to work in that environment. Patching it during setup (not later, not manually) is the right time.

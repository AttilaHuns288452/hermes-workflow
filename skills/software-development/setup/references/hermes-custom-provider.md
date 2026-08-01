# Wiring a Service as a Hermes Custom Provider

After setting up a local OpenAI-compatible API server (FreeLLMAPI, llama.cpp, vLLM, LM Studio, Ollama, etc.), wire it into Hermes so the agent uses it as the inference backend.

## Quick Reference

```yaml
# In ~/AppData/Local/hermes/config.yaml
model:
  provider: custom
  default: auto               # or specific model like "gemini-2.5-flash"
  base_url: http://localhost:3001/v1

providers:
  my-endpoint:
    base_url: http://localhost:3001/v1
    key_env: MY_API_KEY_ENV_VAR
    default_model: auto
    discover_models: true      # fetch models from GET /v1/models
```

## Step-by-step

### 1. Store the API key in `.env`

```bash
echo 'MY_API_KEY_ENV_VAR=sk-your-key-here' >> ~/.hermes/.env
```

Never put the key directly in `config.yaml` unless it's ephemeral — `.env` is automatically loaded by the Hermes runtime and kept out of version control.

**⚠️ Duplicate env var trap:** If `.env` accidentally has two lines with the same variable name (e.g. two `FREELMAPI_API_KEY=...`), the shell or Hermes runtime reads the **last** one, not the first. Always verify there's exactly one occurrence of each key:
```bash
grep -c "^MY_API_KEY_ENV_VAR=" ~/.hermes/.env  # should be 1
```

### 2. Set the model config

Use `hermes config set` with dot notation — it writes to the correct YAML keys and accepts nested values:

```bash
hermes config set model.provider custom
hermes config set model.default auto
hermes config set model.base_url "http://localhost:3001/v1"
```

### 3. Add the provider entry

```bash
hermes config set providers.my-endpoint.base_url "http://localhost:3001/v1"
hermes config set providers.my-endpoint.key_env "MY_API_KEY_ENV_VAR"
hermes config set providers.my-endpoint.default_model "auto"
hermes config set providers.my-endpoint.discover_models true
```

### 4. Verify

```bash
curl -s http://localhost:3001/v1/chat/completions \
  -H "Authorization: Bearer $(python -c "import os; print(os.environ.get('MY_API_KEY_ENV_VAR',''))")\
  -H "Content-Type: application/json" \
  -d '{"model":"auto","messages":[{"role":"user","content":"hi"}],"max_tokens":10}'
```

Then start a new `hermes chat` session—the config is picked up fresh on each session start.

## Alternative: Auth Credential Instead of `providers` Section

If your `config.yaml` doesn't have a `providers.*` section (e.g. it only has `mcp_servers:`), you can skip Step 3 entirely and store the API key via the Hermes auth system instead:

```bash
# Remove any stale credential first
hermes auth remove <provider-name> <index>   # e.g. hermes auth remove freellmapi 1

# Add the credential with the correct key
hermes auth add <provider-name> --type api-key --api-key "sk-your-key-here" --label "Description"

# Example for a custom endpoint at localhost:3001:
hermes auth add freellmapi --type api-key --api-key "freellmapi-2a3b4c5..." --label "FreeLLMAPI Key"
```

This registers the key in the `custom:<provider-name>` credential namespace. Hermes's `custom` provider type picks it up automatically when `model.provider=custom` and `model.base_url` are set.

The full config then needs only:
```bash
hermes config set model.provider custom
hermes config set model.base_url "http://localhost:3001/v1"
hermes config set model.default auto
```

No `providers.*` section, no `key_env` — the auth credential provides the API key directly.

## Config Schema (from Hermes source)

The `providers` dict entries support these fields (discovered from `_normalize_custom_provider_entry` in `hermes_cli/config.py`):

| Field | Description |
|---|---|
| `name` | Display name (defaults to the dict key) |
| `base_url` / `url` / `api` | API endpoint URL (required) |
| `api_key` | Inline API key (avoid — use `key_env` instead) |
| `key_env` / `api_key_env` | Env var name containing the API key |
| `model` / `default_model` | Default model to use |
| `models` | Dict of per-model configs (`{model_name: {context_length: N}}`) |
| `context_length` | Default context length for the provider |
| `rate_limit_delay` | Delay between requests for rate limiting |
| `request_timeout_seconds` | Per-request timeout |
| `stale_timeout_seconds` | Stale session timeout |
| `discover_models` | Boolean — fetch model list from `/v1/models` |
| `extra_body` | Dict of extra body params to include in every request |
| `api_mode` | API mode (`chat_completions`, `codex_responses`, etc.) |
| `transport` | Transport type |

## How Model Resolution Works

When `model.provider = "custom"`:

1. Hermes reads `model.base_url` and `model.default` (the model name)
2. It looks up the `providers` (or `custom_providers`) list for a matching `base_url`
3. The matching entry's `key_env` is used to resolve the API key from `.env`
4. The API key is seeded into the credential pool
5. All requests are sent to `{base_url}/chat/completions` with `model: {default}` (e.g., `"auto"`)

Source: `credential_pool.py` `seed_default_credentials()`, `auxiliary_client.py` `_resolve_task_provider_model()`

## Provider Discovery

With `discover_models: true`, Hermes calls `GET {base_url}/models` on startup and registers all returned models. If that endpoint is auth-gated and the key isn't resolved yet at discovery time, discovery returns 0 models — but chat completions still work because the `model.default` value (e.g. `"auto"`) is passed through as-is.

## auth-gated Servers

If the server requires auth for all endpoints (including `/v1/models`), the verification flow is:
1. Bootstrap credentials via the server's setup/login endpoints
2. Store the unified API key in `.env`
3. Test a chat completion (not just `/v1/models`)
4. A `401` on `/v1/models` is **not a failure** if chat completions work with the same key

## Key Reference

- `hermes config set <dot.key.path> <value>` — set any config value
- `hermes config show` — view current config
- `hermes config edit` — open in editor
- `~/.hermes/.env` — secret-bearing env vars loaded at runtime

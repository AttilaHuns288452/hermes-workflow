# OpenCode Configuration Patterns

## Custom Providers (OpenAI-Compatible Endpoints)

Add local or custom OpenAI-compatible endpoints (Ollama, FreeLLMAPI, llama.cpp, vLLM, etc.) via the `"provider"` key in `opencode.jsonc`.

### Ollama (local)

```json
{
  "provider": {
    "ollama": {
      "name": "Ollama Local",
      "api": "openai",
      "options": {
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "qwen3:4b": {
          "name": "Qwen3 4B",
          "limit": { "context": 32768, "output": 8192 }
        }
      }
    }
  }
}
```

- `"api": "openai"` — the only supported protocol adapter. Works with any OpenAI-compatible server.
- `options.baseURL` — full path including `/v1` suffix.
- `options.apiKey` — omit or leave empty for servers that don't require auth (Ollama default).
- `models` — optional per-model overrides. When omitted, OpenCode auto-discovers models via `GET /v1/models` on the base URL.

### FreeLLMAPI (localhost:3001)

```json
{
  "provider": {
    "freellmapi": {
      "name": "Free LLM API",
      "api": "openai",
      "options": {
        "baseURL": "http://localhost:3001/v1",
        "apiKey": "freellmapi-xxxxxxxxxxxx"
      }
    }
  }
}
```

Models are available as `freellmapi/<model-name>` in `opencode models` output.

## Skills Paths (External Directories)

Point OpenCode to external skill directories (e.g. from another agent framework) using `"skills"."paths"`:

```json
{
  "skills": {
    "paths": [
      "C:/Users/<user>/AppData/Local/hermes/skills/autonomous-ai-agents",
      "C:/Users/<user>/AppData/Local/hermes/skills/workflow"
    ]
  }
}
```

- Paths are absolute filesystem paths (forward slashes or double-backslashes on Windows).
- Each path should point to a **category directory** containing skill subdirectories with SKILL.md files.
- The default `skills/` directory is always checked; if absent OpenCode logs `Failed to change directory` but continues running.

## Auth File (Direct Edit)

Provider credentials live in `~/.local/share/opencode/auth.json`:

```json
{
  "openrouter": {
    "type": "api",
    "key": "sk-or-...xxxx"
  },
  "opencode": {
    "type": "api",
    "key": "sk-...xxxx"
  }
}
```

Each key is a **provider slug** (lowercase, no spaces, matching the provider name). Use this approach when `opencode providers login` fails (e.g. interactive pipe issues on Windows) or when bulk-adding keys. Verify with `opencode auth list`.

## Hermes-Side Local Provider (Ollama)

To make Ollama available in Hermes (not OpenCode), use `hermes config set` (direct file edit is blocked by the agent guard):

```bash
hermes config set providers.ollama.base_url http://localhost:11434/v1
hermes config set providers.ollama.discover_models true
hermes config set providers.ollama.default_model qwen3:4b
```

This queries `GET /v1/models` from Ollama and makes all models selectable via `hermes model`.

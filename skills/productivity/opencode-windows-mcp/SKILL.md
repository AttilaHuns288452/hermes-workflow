---
name: opencode-windows-mcp
description: "Windows-specific OpenCode MCP wiring quirks and fixes. Use when adding MCP servers to OpenCode on Windows, especially when opencode.jsonc rejects mcpServers or agentmemory connect is blocked."
version: 0.1.0
platforms: [windows]
---

# OpenCode Windows MCP Setup

## Problem

On Windows, `opencode mcp add <name>` may not complete a working config edit (it may only print help and fail), and the OpenCode JSONC schema rejects `"mcpServers"` and `"mcp_servers"` with:

```
Configuration is invalid
↳ Unrecognized key: mcpServers
```

This blocks automated agent wiring for tools like `agentmemory`.

## Fix

Use a top-level `"mcp"` key with each server as a direct child in `~/.config/opencode/opencode.jsonc`. The verified schema requires these fields:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `type` | `"local"` or `"remote"` | **Yes** | Must be `"local"` for stdio servers |
| `command` | `array[string]` | For `"local"` | Command + args as an array, e.g. `["npx", "-y", "@package/server"]` |
| `cwd` | `string` | No | Working directory for the process |
| `environment` | `object[string,string]` | No | Env vars — **NOT** `"env"` or `"args"` |
| `enabled` | `boolean` | No | Omit to default to true |
| `timeout` | `integer` (ms) | No | Request timeout |

Example for `agentmemory`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "agentmemory": {
      "type": "local",
      "command": ["npx", "-y", "@agentmemory/agentmemory", "mcp"],
      "environment": {
        "PATH": "C:\\Users\\Attila\\.local\\bin;C:\\Program Files\\nodejs;C:\\Users\\Attila\\AppData\\Roaming\\npm"
      }
    },
    "vscode": {
      "type": "local",
      "command": ["npx", "-y", "vscode-mcp-server"]
    },
    "codegraph": {
      "type": "local",
      "command": ["codegraph", "serve", "--mcp", "-p", "C:\\Users\\Attila\\Documents\\Projects"]
    }
  }
}
```

### Pitfalls

- The config key is `"mcp"` — NOT `"mcpServers"`, `"mcp_servers"`, or `"mcpServers"`. The schema accepts each server name directly under `"mcp"`.
- Use `"environment"` (not `"env"`) for environment variables.
- Use `"command"` as an **array**, not a string with separate `"args"` key.
- Include Node.js and local bin paths in `"environment"."PATH"` on Windows so `npx` and engine binaries resolve.
- Strip UTF-8 BOM from `opencode.jsonc` if present; otherwise JSON parsing may fail silently.
- After editing, verify with `opencode mcp list` — expect `✓ <server-name> connected`.

## MCP Server Overrides

Beside server definitions, `"mcp"` also accepts `{ "enabled": true }` or `{ "enabled": false }` as a value — this lets you enable/disable a server that was configured elsewhere (e.g. via `opencode mcp add`).

```json
{
  "mcp": {
    "existing-server": { "enabled": false }
  }
}
```

## Verification

- `opencode mcp list` should show the server as connected
- Restart OpenCode to load updated config
- If you see `No MCP servers configured`, the server name or config key does not match what OpenCode expects

## Sources

- Schema confirmed via `https://opencode.ai/config.json` (`$defs/McpLocalConfig`)
- Verified against OpenCode running on Windows (2026-07-03)

## Related Reference

See `references/opencode-config-patterns.md` for:
- Custom provider setup (Ollama, FreeLLMAPI, any OpenAI-compatible endpoint)
- `skills.paths` to external skill directories (e.g. Hermes skills)
- `auth.json` direct editing for API keys
- Hermes-side Ollama provider configuration
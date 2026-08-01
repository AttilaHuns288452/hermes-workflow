---
name: opencode-windows-mcp
description: "Windows-specific OpenCode MCP wiring quirks and fixes. Use when adding MCP servers to OpenCode on Windows, especially when opencode.jsonc rejects mcpServers or agentmemory connect is blocked."
version: 0.1.0
platforms: [windows]
---

# OpenCode Windows MCP Setup

## Problem

On Windows, `opencode mcp add <name>` may not complete a working config edit, and `opencode.jsonc` rejects `mcpServers` with:

```
Configuration is invalid
↳ Unrecognized key: mcpServers
```

This blocks automated agent wiring for tools like `agentmemory`.

## Fix

Use `mcp_servers` in `opencode.jsonc`. Example for `agentmemory`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp_servers": {
    "agentmemory": {
      "command": "npx",
      "args": ["-y", "@agentmemory/agentmemory", "mcp"],
      "env": {
        "PATH": "C:\\Users\\YOUR_USERNAME\\.local\\bin;C:\\Program Files\\nodejs;C:\\Users\\YOUR_USERNAME\\AppData\\Roaming\\npm"
      }
    }
  }
}
```

## Verification

- `opencode mcp list` should show the server
- Restart OpenCode to load updated config

## Sources

- Discovered in local OpenCode config backups: existing servers used `mcp_servers` with underscore
- Schema validation rejected `mcpServers` in `opencode.jsonc` on this Windows install
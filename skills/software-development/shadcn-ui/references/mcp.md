# shadcn MCP Server

Setup for the shadcn MCP server, which lets AI assistants search, browse, and install components from registries.

## Installation

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "shadcn": {
      "command": "npx",
      "args": ["-y", "@shadcn/mcp"]
    }
  }
}
```

For Hermes, this goes in `~/.hermes/config.yaml`:

```yaml
mcp:
  servers:
    shadcn:
      command: npx
      args: [-y, @shadcn/mcp]
```

Or per-project in `.hermes/config.yaml`.

## What It Does

The MCP server exposes tools that let the AI:
1. **Search** for components across registries
2. **Browse** component documentation and examples
3. **Install** components directly

## Tool Reference

| Tool | Description |
|------|-------------|
| `shadcn_list_registries` | List available component registries |
| `shadcn_search` | Search for components by query |
| `shadcn_get_docs` | Get documentation for a component |
| `shadcn_install` | Add a component to the project |

## Debugging

Check MCP server status:
```bash
npx -y @shadcn/mcp --help
```

Logs go to stderr, which Hermes captures in the MCP inspector.

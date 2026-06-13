# Windows OpenCode MCP Workaround

## Verified schema (this build)

Use a top-level `"mcp"` key in `~/.config/opencode/opencode.jsonc`:

```json
{
  "mcp": {
    "<server-name>": {
      "type": "local",
      "enabled": true,
      "command": ["npx", "-y", "@package/server"],
      "environment": {
        "PATH": "C:\\Users\\<user>\\.local\\bin;C:\\Program Files\\nodejs;C:\\Users\\<user>\\AppData\\Roaming\\npm"
      }
    }
  }
}
```

## Pitfalls

- This build rejects `"mcpServers"` and `"mcp_servers"`.
- Use `"environment"`, not `"env"`.
- Use `"command"` array, not separate command + args keys.
- Strip UTF-8 BOM from `opencode.jsonc` if present; otherwise JSON parsing fails.
- `opencode mcp add <name> ...` may print help and fail to edit config on Windows; edit the file directly.
- Verify with `opencode mcp list`.


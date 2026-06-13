# VS Code MCP Server — Configuration Notes

## Package Details

- **Package**: `vscode-mcp-server` (npm)
- **Status**: Deprecated (v0.2.0 shows "Package no longer supported") but functional
- **Install**: Via `npx -y vscode-mcp-server` (not globally installed)
- **CLI Commands**: `install`, `install-agents`, `update`, `start` (default), `get-goose-url`

## Hermes Config

```yaml
mcp_servers:
  vscode:
    command: "npx"
    args: ["-y", "vscode-mcp-server"]
    connect_timeout: 60
```

**Key point**: Use `npx -y` not a global binary. The `-y` flag auto-installs if missing.

## Exposed Tools (via MCP)

| Tool | Description |
|------|-------------|
| `open_project` | Open a folder in VS Code |
| `open_file` | Open a file in the editor |
| `create_diff` | Edit files via approved diffs |
| `execute_shell_command` | Run commands in VS Code's integrated terminal |
| `list_available_projects` | List registered projects |
| `check_extension_status` | Check the extension is alive |
| `get_extension_port` | Get the extension's port |
| `get_active_tabs` | Current open tabs |
| `get_context_tabs` | Tabs marked for AI context |

## Tool Naming in Hermes

Tools appear as `mcp_vscode_<tool_name>`, e.g.:
- `mcp_vscode_open_project`
- `mcp_vscode_open_file`
- `mcp_vscode_execute_shell_command`

## Notes

- Requires VS Code running with the MCP extension installed
- The server communicates with VS Code via a local port (websocket)
- `check_extension_status` and `get_extension_port` require `targetProjectPath`
- Best for: opening files, running terminal commands in VS Code context, reading active tabs
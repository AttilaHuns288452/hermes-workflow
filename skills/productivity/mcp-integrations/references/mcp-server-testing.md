# MCP Server Testing with JSON-RPC

When an MCP server is configured but not appearing in Hermes/OpenCode, the fastest diagnostic is piping a JSON-RPC init message directly to the server's command.

## One-shot init test

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}' \
  | python -m graphify.serve 2>/dev/null
```

A healthy server responds with a JSON object containing `"id":1,"result":{...}}`.

## Testing tools/list

Pip two JSON lines — the server processes each sequentially:

```bash
printf '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}\n{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' \
  | python -m obsidian_kg_mcp 2>/dev/null
```

Both lines should produce responses, confirming the server stays alive between requests.

## Known failure modes detected by this test

| Output | Root cause |
|--------|------------|
| Blank / no output | The command itself failed — missing package, wrong Python, PATH issue |
| `ModuleNotFoundError` | Python package not installed — `pip install <pkg>` |
| `AttributeError` / `ExceptionGroup` | MCP SDK API mismatch — the server was written for an older MCP SDK version. Rewrite using FastMCP (`mcp.server.fastmcp`) |
| Starts but no MCP response | Wrong subcommand (e.g. `npx pkg` instead of `npx pkg mcp`) or wrong args |
| `Error: Cannot find module` | npx package name wrong — verify with `npm view <name>` |

## npx package validation

```bash
# Confirm the package exists and has the expected version
npm view @agentmemory/agentmemory version
# This catches typos like agentmemory-mcp (wrong) vs @agentmemory/agentmemory (correct)
```

## cwd matters

Set the working directory to match what the Hermes config specifies:

```bash
cd /c/Users/Attila/.hermes/tools && python -m obsidian_kg_mcp
```

If the server reads relative paths or local config files, the wrong cwd produces silent file-not-found errors.

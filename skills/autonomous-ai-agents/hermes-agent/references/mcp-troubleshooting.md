# Hermes MCP Server Troubleshooting

## Common MCP Server Connection Issues

This document captures patterns for diagnosing and fixing MCP server failures that cause gateway instability, WebSocket stalls, and agent loop blocking.

## Symptoms
- `ws write slow (loop stalled >10s)` in gateway logs
- `WebSocketDisconnect` errors
- Agent context compression timing out
- MCP servers failing initial connection after 3 retries
- Errors like: `dictionary update sequence element #0 has length 1; 2 is required`

## Root Causes Found (June 2026)

### 1. AgentMemory MCP Server
```yaml
mcp_servers:
  agentmemory:
    args: '["-y", "@agentmemory/agentmemory", "mcp"]'
    command: npx
    connect_timeout: 60
    enabled: true
    env: '{"PATH": "..."}'
```
**Error:** `dictionary update sequence element #0 has length 1; 2 is required`
**Cause:** The `@agentmemory/agentmemory` package's MCP entry point has a config parsing bug
**Fix:** Disable in config.yaml
```yaml
mcp_servers:
  agentmemory:
    enabled: false  # disabled due to connection errors
    # ... rest of config preserved for reference
```

### 2. LLMQuant Data MCP Server
```yaml
mcp_servers:
  llmquant-data:
    args: '["-y", "@llmquant/data-mcp"]'
    command: npx
    connect_timeout: 60
    enabled: true
    env: '{"LLMQUANT_API_KEY": "lqd_data_..."}'
```
**Error:** Same dictionary parsing error
**Cause:** `@llmquant/data-mcp` package version mismatch or config format issue
**Fix:** Disable in config.yaml
```yaml
mcp_servers:
  llmquant-data:
    enabled: false  # disabled due to connection errors
    # ... rest of config preserved for reference
```

### 3. VSCode MCP Server
```yaml
mcp_servers:
  vscode:
    args: '["-y", "vscode-mcp-server"]'
    command: npx
    connect_timeout: 60
    enabled: true
    env: '{}'
```
**Error:** Connection timeout / failure after 3 attempts
**Cause:** `vscode-mcp-server` requires a running VS Code instance with the extension installed, or specific workspace context
**Fix:** Disable in config.yaml unless actively using
```yaml
mcp_servers:
  vscode:
    enabled: false  # disabled due to connection errors
    # ... rest of config preserved for reference
```

## Diagnostic Commands

```bash
# Check gateway logs for MCP connection failures
grep -i "mcp.*failed\|mcp.*error\|MCP server" ~/.hermes/logs/gateway.log | tail -20

# Check errors log for auxiliary client failures
grep -i "resolve_provider_client.*unknown\|auxiliary.*rate limit" ~/.hermes/logs/errors.log | tail -20

# Test individual MCP server manually
npx -y @agentmemory/agentmemory mcp
npx -y @llmquant/data-mcp
npx -y vscode-mcp-server
```

## Prevention Patterns

1. **Disable unused MCP servers** - Each enabled server adds connection overhead and failure surface
2. **Use `enabled: false` with comments** - Preserves config for re-enabling, documents why disabled
3. **Monitor gateway.log for `ws write slow`** - Early indicator of agent loop blocking
4. **Check auxiliary compression provider** - If using a free-tier provider (opencode-zen), rate limits will cascade into gateway stalls
5. **Prefer gateway-restart over config-edit** - MCP server changes need gateway restart: `hermes gateway restart` or `/restart` in chat

## Config Pattern for Problematic Servers

```yaml
mcp_servers:
  # Known problematic servers - keep config but disable
  agentmemory:
    enabled: false  # disabled due to connection errors - config parsing bug in @agentmemory/agentmemory
    args: '["-y", "@agentmemory/agentmemory", "mcp"]'
    command: npx
    connect_timeout: 60
    env: '{"PATH": "..."}'
  
  llmquant-data:
    enabled: false  # disabled due to connection errors - config format issue
    args: '["-y", "@llmquant/data-mcp"]'
    command: npx
    connect_timeout: 60
    env: '{"LLMQUANT_API_KEY": "..."}'
  
  vscode:
    enabled: false  # disabled due to connection errors - requires running VS Code
    args: '["-y", "vscode-mcp-server"]'
    command: npx
    connect_timeout: 60
    env: '{}'
  
  # Working servers (examples)
  codegraph:
    args: ["serve", "--mcp"]
    command: codegraph
    connect_timeout: 60
    enabled: true
    timeout: 120
  
  composio:
    connect_timeout: 60
    headers:
      x-consumer-api-key: "ck_..."
    timeout: 120
    url: https://connect.composio.dev/mcp
    enabled: true
```

## Related Issues

- **Auxiliary compression rate limits** - If `auxiliary.compression.provider` uses a free model (opencode-zen, deepseek-v4-flash-free), rate limits cause context compression to fail, blocking the agent loop and causing WebSocket timeouts. Fix: use `freellmapi` with `auto` model routing.
- **Credential pool exhaustion** - When all fallback providers exhausted, auxiliary tasks fail silently but leave the agent waiting.

## Quick Fix Checklist

When gateway shows `ws write slow` or frequent disconnects:

1. [ ] Check `auxiliary.compression.provider` - switch from free-tier to freellmapi
2. [ ] Check `mcp_servers` - disable any failing servers (agentmemory, llmquant-data, vscode common)
3. [ ] Restart gateway: `hermes gateway restart`
4. [ ] Verify: `grep -i "ws write slow" ~/.hermes/logs/gateway.log` should stop
5. [ ] Test: `hermes chat -q "test"` should complete without stall
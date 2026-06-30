# MCP Server Sharing Across Hermes Profiles

## Problem

Each Hermes profile can have its own `mcp_servers:` section in its config.
When a profile defines `mcp_servers:`, it **overrides** the root config —
the profile only gets the servers listed in its own config, not the root set.

This caused `channel`, `finance`, and `codingprofile` to only have 3 MCP servers
each (composio, open-design, opendesign), missing codegraph, graphify,
llmquant-data, obsidian-kg, agentmemory, and vscode.

## Solution

**Remove `mcp_servers:` from all profile configs.** Profiles that have no
`mcp_servers:` key automatically inherit the full set from the root config
at `AppData\Local\hermes\config.yaml`.

### Before (broken — 3 profiles, 3 servers each)

```yaml
# in profiles/finance/config.yaml
mcp_servers:
  composio: ...
  open-design: ...
  opendesign: ...
# ↳ profiles/finance MISSES codegraph, graphify, llmquant-data,
#   obsidian-kg, agentmemory, vscode
```

### After (fixed — all profiles inherit root's 8 servers)

```yaml
# in profiles/finance/config.yaml
# (no mcp_servers section at all)
# ↳ inherits ALL 8 from root:
#   codegraph, graphify, llmquant-data, obsidian-kg,
#   agentmemory, vscode, composio, open-design
```

## Verification

```bash
# Check root config has the full set:
grep -A 50 "mcp_servers:" ~/AppData/Local/hermes/config.yaml | head -60

# Confirm no profile config has its own mcp_servers:
grep -l "mcp_servers:" ~/AppData/Local/hermes/profiles/*/config.yaml
# Should return NOTHING — empty means all are clear
```

## Why This Works

Hermes merges config hierarchically:
1. Root `config.yaml` is loaded first (at `AppData/Local/hermes/config.yaml`)
2. Profile config is loaded as an overlay
3. Keys present in the profile config **replace** the root's version
4. Keys NOT present in the profile config are **inherited** from root

So removing `mcp_servers:` from the profile means the root's `mcp_servers:` shines through unchanged.

## What Else Can Be Shared This Way

The same technique applies to any root-level section that profiles tend to
duplicate:

| Config section | Shared? | Notes |
|---------------|---------|-------|
| `mcp_servers` | ✅ Fixed | Removed from all 3 profile configs |
| `.env` + `auth.json` | ✅ Fixed | Root copies propagated to profiles via `sync-hermes-credentials.py` |
| `skills/` | ✅ Inherited | Skills are read from root skills dir unless profile overrides |
| `plugins/` | ✅ Inherited | Same inheritance |
| `system_prompt` | ❌ Per-profile | Each profile has its own system prompt (intentional) |
| `allowed_tools` | ❌ Per-profile | Each profile can restrict tools |

## Affected Files

| File | Before | After |
|------|--------|-------|
| `profiles/channel/config.yaml` | 8 servers (6,190 chars) | 0 servers (3,270 chars) |
| `profiles/finance/config.yaml` | 3 servers (2,321 chars) | 0 servers (2,116 chars) |
| `profiles/codingprofile/config.yaml` | 3 servers (2,321 chars) | 0 servers (2,146 chars) |

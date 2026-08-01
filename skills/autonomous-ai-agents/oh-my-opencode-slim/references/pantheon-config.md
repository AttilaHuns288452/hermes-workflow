# Pantheon Agent Configuration — oh-my-opencode-slim v2.2.8

Verification from this session (July 2026) on Windows.

## Agent Models Actually Used

| Agent | Model | Purpose |
|-------|-------|---------|
| **Orchestrator** | `opencode-go/glm-5.2` | Plans work graph, dispatches specialists. Overseer only. |
| **Oracle** | `opencode/deepseek-v4-flash-free` | Code review, debugging |
| **Explorer** | `opencode/deepseek-v4-flash-free` | Codebase recon |
| **Librarian** | `opencode/deepseek-v4-flash-free` | API docs research |
| **Designer** | `opencode/deepseek-v4-flash-free` | UI/UX |
| **Fixer** | `opencode/deepseek-v4-flash-free` | Scoped patches |
| **Council** | config-driven | Multi-model consensus |
| **Observer** | `opencode/mimo-v2.5-free` | Vision (disabled by default) |

Free-tier equivalents if rate-limited:
- `deepseek-v4-flash-free` → `opencode-go/deepseek-v4-flash`
- `mimo-v2.5-free` → `opencode-go/mimo-v2.5`

## Plugin Path Config

Added to `~/.config/opencode/opencode.jsonc`:
```jsonc
{
  "plugins": {
    "paths": [
      "C:/Users/Attila/Documents/Projects/oh-my-opencode-slim"
    ]
  }
}
```

## Verification

```bash
# Pantheon swarm active — Orchestrator responds by default
opencode run '...'  # Output: > orchestrator · glm-5.2

# MCP servers still independent
opencode mcp list  # 9 servers: codegraph, vscode, llmquant-data, agentmemory, websearch, etc.
```

## File Layout

```
oh-my-opencode-slim/
├── dist/cli/index.js     # CLI entry (bin: oh-my-opencode-slim)
├── .agents/               # Core Pantheon agent definitions
├── .slim/                 # Slim-mode config overrides
├── skills-lock.json       # Bundled skill versions
├── oh-my-opencode-slim.schema.json  # Full config schema
└── src/                   # TypeScript source
```

## Sourced URLs

- Repo: https://github.com/alvinunreal/oh-my-opencode-slim
- AGENTS.md (root): Full Pantheon agent role descriptions

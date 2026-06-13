# CodeGraph Ecosystem Integration

## Overview
CodeGraph (`@colbymchenry/codegraph`, npm) is a real-time code knowledge graph
server providing 6 MCP tools (explore, search, callers, callees, impact, routes).
It complements Graphify (`graphifyy`, uv) which provides post-processing docs.

## Installation
```bash
npm install -g @colbymchenry/codegraph
codegraph install -y   # auto-detects Hermes Agent, Claude Code, Codex, Cursor
codegraph init .       # indexes current project (~30s for 3,596 files)
```

## Auto-Configuration
`codegraph install -y` automatically:
- Detects all supported agents (Hermes, Claude Code, Codex CLI, Cursor, OpenCode)
- Writes MCP server config for each
- For Hermes: updates `~/.hermes/config.yaml` with codegraph MCP entry
- No manual config editing needed

## MCP Tools Available After Install
| Tool | Purpose |
|------|---------|
| explore | Project symbols, definitions, structure at any granularity |
| search | FTS5 full-text search with ranking across indexed files |
| callers | Find who calls a function, cross-file |
| callees | Find what a function calls, cross-file |
| impact | Refactoring impact — everything touching a symbol path |
| routes | Auto-detect API routes (Express, FastAPI, Next.js, Django) |

## Comparison with Graphify
| Aspect | CodeGraph | Graphify |
|--------|-----------|----------|
| Type | Real-time MCP server | Post-processing CLI |
| Sync | Auto-file-watcher | Manual re-run |
| Output | JSON MCP responses | Obsidian notes + canvas + HTML |
| Languages | 22+ | Python/JS/TS/Go/Rust/Java |
| Best for | Live dev queries | Documentation obsidian export |
| Install | `npm i -g @colbymchenry/codegraph` | `uv tool install graphifyy` |

## Integration Pattern
Both tools index the same codebase independently — no conflict.
- CodeGraph: ask during development ("show callers of X", "find imports of Y")
- Graphify: run at documentation checkpoints ("export to obsidian", "run community detection")

## Windows Notes
- `codegraph init .` works from bash (git-bash) with native Windows paths
- The MCP server runs as a child process of Hermes — no Windows-specific config needed

## Related
- `graphify-integrate` SKILL.md — main code-graph skill
- `software-development/setup` — Phase 2.5 references both tools
- `software-development/repo-integration-reconciliation` — skill audit workflow

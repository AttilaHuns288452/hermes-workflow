# Graphify + Free Model Ecosystem Integration — Session Notes

**Date**: June 11, 2026
**Projects tested**: ecosystem-test (simple), task-manager-cli (complex)

---

## Graphify Installation + Gemini Semantic Extraction

```bash
# Core install
uv tool install graphifyy
uv tool install "graphifyy[mcp]"

# For Gemini semantic extraction (requires openai package for API compatibility)
uv tool install "graphifyy[gemini]" --force

# Verify
graphify --version  # 0.8.37
graphify-mcp --version  # 0.8.37
```

**Environment**: `GEMINI_API_KEY` must be set for semantic extraction of docs/papers/images.

---

## Test Results: AST vs AST+Gemini

| Project | Mode | Nodes | Edges | Communities | Obsidian Notes |
|---------|------|-------|-------|-------------|----------------|
| ecosystem-test | AST only | 8 | 3 | 5 | 13 |
| ecosystem-test | AST + Gemini | **16** | **11** | **6** | **22** |
| task-manager-cli | AST only | **60** | **95** | **14** | **74** |

**Key finding**: AST-only extraction on a 5-file clean architecture project produced 60 nodes/95 edges — rich structural signal without any LLM costs.

---

## Freebuff Integration Testing

### What Worked
- `npm install -g freebuff` → v0.0.106 installed
- `freebuff login` → GitHub OAuth completed
- `freebuff` in project directory → Connects, shows model selection UI (DeepSeek V4 Flash, MiMo 2.5)
- Session tracking: 1 of 5 sessions used, resets in ~15h

### What Didn't Work (Automation)
- Background PTY + `freebuff` → Captures raw ANSI escape sequences, not parseable
- No `--command` flag that works for headless task submission
- TUI is designed for interactive use only

**Workaround for testing**: Verify connection + model UI display manually, then kill. Don't attempt scripted task submission.

---

## Graphify as Secondary Brain — Model Selection Input

The code graph provides structural signals that should feed `free-ai-model-router`:

| Graph Signal | Interpretation | Model Preference |
|--------------|----------------|------------------|
| Single file, top-level statements, P/Invoke | Simple procedural, no abstraction | `deepseek-v4-flash-free`, `north-mini-code-free` |
| Models/Services/Commands separation, hub service | Clean architecture, moderate complexity | `deepseek-v4-flash-free` |
| Many async/await edges, concurrency patterns | Heavy async, reasoning needed | `nemotron-3-ultra-free`, DeepSeek V4 Pro |
| Agent patterns, multi-agent orchestration | Agentic workflow | `mimo-v2.5-free`, MiMo 2.5 Pro |
| High community count (>10), many cross-community edges | Complex system | Larger context models |

**Implementation**: Query `graphify-mcp` MCP server before model selection:
- `query_graph` — "What architectural patterns exist?"
- `get_node` — Details on central hub nodes
- `get_neighbors` — Dependencies of key services

---

## Obsidian Export + Knowledge Graph Integration

### Export Command
```bash
graphify export obsidian --dir "~/Documents/Obsidian Vault/Projects/<name>/graphify"
```

### Output Structure
- One `.md` per code symbol with `[[wikilinks]]`, YAML frontmatter, tags
- Community overview notes (`_COMMUNITY_<name>.md`) with Dataview queries
- `.obsidian/graph.json` — community coloring for Obsidian graph view
- `graph.canvas` — interactive canvas with community groupings

### Knowledge Graph Refresh
```bash
python ~/AppData/Local/hermes/skills/note-taking/obsidian-knowledge-graph/scripts/scan_vault.py \
  "~/Documents/Obsidian Vault" "~/Documents/Obsidian Vault/kg_output.json"

python ~/AppData/Local/hermes/skills/note-taking/obsidian/scripts/render_kg.py \
  "~/Documents/Obsidian Vault/kg_output.json" "~/Documents/Obsidian Vault/knowledge_graph.html"
```

### Growth Metrics
| After Test 1 (ecosystem-test) | After Test 2 (task-manager-cli) |
|-------------------------------|--------------------------------|
| 175 nodes, 407 edges | 266 nodes, 1,053 edges |
| 70 KB HTML | 217 KB HTML |

---

## Pitfalls & Workarounds

| Issue | Workaround |
|-------|------------|
| `GEMINI_API_KEY` invalid → 400 error | Ensure key has Generative AI API enabled in Google Cloud Console |
| `graphify .` needs API key for docs | Use `graphify update .` for AST-only re-extraction |
| Freebuff TUI not automatable | Test connection manually, don't script task submission |
| OpenCode server errors | Fall back to manual file creation + `dotnet build` |
| Large repos (>2000 files) slow | Use `--no-viz --no-cluster` flags |
| Windows path issues with `--dir` | Use forward slashes: `--dir "C:/Users/.../Obsidian Vault/..."` |

---

## MCP Server Registration (Per Project)

```yaml
# In ~/.hermes/config.yaml
mcp_servers:
  graphify-<project>:
    command: "python"
    args: ["-m", "graphify.serve"]
    cwd: "C:\\Users\\YOUR_USERNAME\\Documents\\Projects\\<project>"
    env:
      PATH: "C:\\Users\\YOUR_USERNAME\\.local\\bin;%PATH%"
    connect_timeout: 30
```

**Tools exposed**: `query_graph`, `get_node`, `get_neighbors`, `path`, `explain`

---

## Integration with /decide Workflow

Per `/decide` mandatory rules:
1. `session_memory` → context
2. **`graphify-integrate`** → build code graph, export to Obsidian, register MCP (SECONDARY BRAIN)
3. Primary domain skill (coding, research, etc.)
4. Complementary checks
5. Obsidian bundle + Graphify export + KG refresh

**Graphify runs on EVERY project/coding/analysis task** — not optional.

---

*Session notes for future reference when running Graphify on new projects.*
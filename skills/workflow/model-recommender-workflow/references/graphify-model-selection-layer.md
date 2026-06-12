# Model Recommender Workflow — Graphify Integration Layer

**Date**: June 11, 2026
**Trigger**: /decide made Graphify mandatory secondary brain; added as Layer 3 in pipeline

---

## Updated Pipeline Architecture

```
📊 Model Data (free-ai-tools)     → 45 providers, 550+ tools, free-coding-models CLI
🎯 Domain Skills (ECC)            → 261 skills, 64 agents, per-task skill loadouts
🔍 Code Graph (Graphify)          → AST code symbols, imports, calls, communities  ← NEW LAYER
🧠 Model Routing (free-ai-model-router) → Priority chains, verified fallbacks, live probing
   ├─ Hermes decide skill         → Routes to correct task type
   ├─ FreeLLMAPI (local)          → 110+ models, 16 providers at localhost:3001/v1
   └─ Obsidian                    → Documentation + Knowledge Graph
```

**Graphify runs immediately after session_memory and before model routing** — its code graph output feeds the model selection decision.

---

## Graphify as Model Selection Input

The code graph provides structural signals that map to model preferences:

| Graph Signal | Detected Pattern | Model Preference | Rationale |
|--------------|------------------|------------------|-----------|
| Single file, top-level, no cycles | Simple procedural | `deepseek-v4-flash-free`, `north-mini-code-free` | Fast coding, low context needed |
| Models/Services/Commands separation, hub service | Clean architecture | `deepseek-v4-flash-free` | Moderate complexity, standard patterns |
| High edge density, many async edges | Heavy concurrency | `nemotron-3-ultra-free`, DeepSeek V4 Pro | Reasoning for async complexity |
| Agent patterns, multi-agent orchestration | Agentic workflow | `mimo-v2.5-free`, MiMo 2.5 Pro | Agentic capability |
| Many communities (>10), cross-community edges | Complex system | Larger context models | Need broader understanding |
| Multi-language mix | Polyglot project | Per-module model selection | Different languages need different models |

---

## Live Test Results

### Test 1: System Dashboard (ecosystem-test)
```
Graphify: 8 nodes, 3 edges, 5 communities
Signal: Single C# file, top-level statements, P/Invoke, no complex patterns
Model routed: opencode/deepseek-v4-flash-free ✅
Verified: Built and ran successfully
```

### Test 2: Task Manager CLI (task-manager-cli)
```
Graphify: 60 nodes, 95 edges, 14 communities
Signal: Clean architecture (Models/Services/Commands), TaskService hub (highest degree), no circular deps
Model routed: opencode/deepseek-v4-flash-free ✅
Verified: All 6 commands functional, build 0 errors
```

---

## Implementation: Querying Graphify Before Model Selection

```bash
# 1. Build/refresh code graph (mandatory per /decide)
cd ~/Documents/Projects/<project>
graphify update .

# 2. Query MCP for architectural signals
# (Via Hermes MCP tools — graphify-mcp exposes: query_graph, get_node, get_neighbors, path, explain)

# Example queries to run before model selection:
# query_graph "What architectural patterns exist?"
# get_node "TaskService"  # hub service
# get_neighbors "TaskService"  # dependencies
# query_graph "Any async/concurrency patterns?"
# query_graph "Any agent/orchestration patterns?"
```

**Then feed results to model-recommender-workflow**:
```bash
python ~/Documents/Projects/free-ai-tools/scripts/model-recommender.py coding --ecc
# Now has Graphify context available via decide skill injection
```

---

## Fallback Chain — Graphify Informs Layer Selection

```
1. OpenCode bundled     → Graphify says "simple procedural"    → deepseek-v4-flash-free
2. Freebuff             → Graphify says "agentic patterns"     → MiMo 2.5 Pro / Kimi K2.6
3. FreeLLMAPI           → Graphify says "needs specific provider not in above" → 110+ models
4. OpenRouter :free     → All above exhausted                  → gpt-oss-120b:free
5. Paid safety net      → Last resort                          → claude-sonnet-4
```

**Key insight**: Graphify doesn't replace the fallback chain — it INFORMS which layer to try first and which model within that layer.

---

## Pitfalls & Learnings

| Pitfall | Learning |
|---------|----------|
| Running model recommender before Graphify | Model selection lacks code context — may pick wrong tier |
| Assuming AST-only graph is insufficient | 60 nodes/95 edges from 5 files = rich signal; semantic extraction is bonus |
| Not querying Graphify MCP | Missing hub detection, community boundaries, dependency cycles |
| Treating Graphify as optional | /decide now makes it mandatory — run on EVERY project task |

---

## Quick Verification Commands

```bash
# Full pipeline test (run on any new project)
cd ~/Documents/Projects/<new-project>
graphify update .                    # Build code graph (mandatory)
python ~/Documents/Projects/free-ai-tools/scripts/model-recommender.py coding --ecc  # Model selection with Graphify context
opencode run "test" --model opencode/deepseek-v4-flash-free  # Probe
dotnet build / npm build / etc.      # Build
graphify export obsidian --dir ...   # Export to Obsidian
python .../scan_vault.py ...         # Refresh KG
```

---

*Graphify is now the code-aware brain layer that sits between domain skills and model routing — making every model selection contextually grounded in actual project structure.*
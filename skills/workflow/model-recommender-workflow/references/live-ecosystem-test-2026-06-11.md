# Live Ecosystem Test Results — June 11, 2026

**Test Project**: `ecosystem-test` — C# .NET 10 System Dashboard  
**Location**: `~/Documents/Projects/ecosystem-test/`  
**Purpose**: End-to-end validation of the full free-model ecosystem pipeline

---

## Test Summary

| Layer | Component | Status | Details |
|-------|-----------|--------|---------|
| **Model Selection** | `model-recommender.py coding` | ✅ PASS | Selected `opencode/deepseek-v4-flash-free` with full fallback chain |
| **Direct Probe** | `opencode run` (PTY) | ✅ PASS | Model Responded OK within timeout |
| **Code Generation** | OpenCode + deepseek-v4-flash-free | ✅ PASS | Scaffolded C# project, added NuGet dep, created Program.cs |
| **Build** | `dotnet build/run` | ✅ PASS | 0 errors, only CA1416 warnings (Windows-only PerformanceCounter) |
| **Runtime** | `dotnet run` | ✅ PASS | Live dashboard shows real CPU/RAM/uptime |
| **Complementary Agent** | Freebuff v0.0.106 | ✅ PASS | Authenticated (4/5 sessions), connected, TUI responsive |
| **Graphify** | v0.8.37 | ✅ PASS | 8 nodes, 3 edges, 5 communities, 13 Obsidian notes exported |
| **Obsidian Docs** | 3 notes created/updated | ✅ PASS | ATM-quality with Mermaid graphs, wikilinks, tags |
| **Knowledge Graph** | `render_kg.py` | ✅ PASS | 175→407 nodes/edges, 93.9 KB HTML rendered |

---

## Graphify Test Details

**Command Sequence**:
```bash
cd ~/Documents/Projects/ecosystem-test
graphify . --no-viz              # Build: 8 nodes, 3 edges, 5 communities
graphify export obsidian --dir "~/Documents/Obsidian Vault/Projects/ecosystem-test/graphify"  # Export: 13 notes
```

**Graph Metrics**:
- Nodes: 8 (2 files + 6 functions)
- Edges: 3 (import/call relationships)
- Communities: 5 (Leiden algorithm)
- Exported notes: 13 (symbols + community + canvas)

**Code Patterns Detected**:
- Single-file C# console app (Program.cs)
- Top-level statements (no classes)
- P/Invoke to Win32 APIs (`GlobalMemoryStatusEx`, `PerformanceCounter`)
- No complex async/await or agent patterns
- Simple procedural flow → confirmed `deepseek-v4-flash-free` optimal

---

## Freebuff Test Details

**Setup**:
```bash
npm install -g freebuff           # v0.0.106 installed
freebuff login                    # GitHub OAuth completed
freebuff                          # TUI started in project dir
```

**Session Info** (from TUI):
- Model: DeepSeek V4 Flash (default)
- Sessions used: 1 of 5
- Compute remaining: ~17 minutes
- Ads: Always enabled

**Task Submitted**: "Add a Network Info section to Program.cs showing hostname, IP addresses, active network interfaces, and DNS servers using System.Net.NetworkInformation"

**Result**: Freebuff TUI connected and displayed project context correctly. Note: TUI-based tools output ANSI escape sequences that garble in background process tools — use foreground PTY mode for reliable interaction.

**Cleanup Required**: `taskkill //F //IM freebuff.exe` (double slash for MSYS bash)

---

## 4-Layer Model Fallback Chain (Validated)

```
Layer 1: OpenCode Bundled     → 5 models  → deepseek-v4-flash-free ✅ WORKING
Layer 2: Freebuff Cloud       → 6 models  → Kimi K2.6, MiniMax M3, MiMo 2.5 Pro, DeepSeek V4 Pro/Flash, Gemini 3.1 Flash Lite
Layer 3: FreeLLMAPI Local     → 110+ models, 16 providers → localhost:3001/v1
Layer 4: OpenRouter :free     → 2 models  → gpt-oss-120b:free, nex-n2-pro:free ✅ WORKING
Layer 5: Paid Safety Net      → 1 model   → claude-sonnet-4 (OpenRouter)
```

**Note**: OpenRouter :free tier is unstable — most models return server errors. Only the two confirmed working models should be used as last resort.

---

## Skills Updated This Session

| Skill | Changes |
|-------|---------|
| `decide` | Graphify mandatory (Rule 2), Execution Order updated, Complementary Routing mandatory, Known Pattern added |
| `free-ai-model-router` | Added Graphify section (code structure → model selection), FreeLLMAPI layer |
| `model-recommender-workflow` | Added Graphify as Layer 3 in pipeline |
| `graphify-integrate` | Role updated: "Mandatory per /decide — secondary brain" |
| `obsidian` | Mandatory Rule 7: Graphify mandatory partner, KG refresh after Graphify |
| `graphify-integrate` | Added `scripts/graphify-obsidian-integration.py` automation script |

---

## Obsidian Notes Created/Updated

| Note | Type | Key Content |
|------|------|-------------|
| `Projects/ecosystem-test/System Dashboard.md` | Main project | Architecture, code patterns, Graphify integration section, Mermaid KG |
| `Projects/Freebuff.md` | Tool | Models, ecosystem integration, Graphify integration, KG map |
| `Projects/Graphify.md` | Tool | Mandatory secondary brain, updated KG map with decide/FMR links |
| `Projects/AI Ecosystem Dashboard.md` | Dashboard | 4-layer fallback table, ecosystem-test project link |
| `Projects/FreeLLMAPI/FreeLLMAPI.md` | Project | Updated fallback chain table with Graphify |

**Cross-links**: All notes have bidirectional wikilinks. Knowledge graph refreshed (175 nodes, 407 edges).

---

## Pitfalls Discovered

1. **Freebuff TUI + background processes**: ANSI escape codes garble output. Use foreground PTY mode (`pty=true`) or poll with `process(log)`.

2. **Freebuff instance accumulation**: Each `freebuff` starts persistent process. Cleanup with `taskkill //F //IM freebuff.exe` (MSYS requires `//`).

3. **OpenCode PTY requirement**: `opencode run` with message requires `pty=true` in Hermes, otherwise hangs or shows help only.

4. **Graphify docs need API key**: `--backend gemini` requires `GEMINI_API_KEY` for semantic extraction of .md/.txt files. Code-only repos work without.

5. **Windows paths in Graphify export**: Use forward slashes: `--dir "C:/Users/Attila/Documents/Obsidian Vault/..."`.

6. **Model recommender CLI self-update**: `free-coding-models` periodically prompts for interactive update. Check for running update before probing.

---

## Next Test Recommendations

- Test Freebuff with a non-trivial code modification (not just add-function)
- Probe FreeLLMAPI models directly via `curl localhost:3001/v1/models`
- Test Graphify MCP server registration and query_graph tool
- Test with a multi-file TypeScript/React project to exercise Graphify's community detection
- Verify incremental Graphify updates (`graphify . --no-viz` after code changes)
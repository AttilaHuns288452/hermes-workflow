# Full Ecosystem Test Recipe

Run this after adding a new tool, model source, or provider to the free model ecosystem.
Verifies that model selection → code generation → build → complementary tool ←
documentation all work end-to-end.

## Prerequisites

- Free model ecosystem installed: free-ai-tools, OpenCode CLI, Freebuff (optional)
- Model recommender script: `~/Documents/Projects/free-ai-tools/scripts/model-recommender.py`
- Obsidian vault at `~/Documents/Obsidian Vault`
- .NET SDK (for C# projects) or Node.js (for JS/TS projects)

## Step 1 — Model Selection

Run the model recommender for the task type:

```bash
python ~/Documents/Projects/free-ai-tools/scripts/model-recommender.py coding
```

Expected: primary model + fallback chain printed. If `--probe` is available, probe live availability.

## Step 2 — Direct Model Probe

Verify the selected model responds:

```bash
opencode run "Respond with OK only" --model opencode/deepseek-v4-flash-free --timeout 30
```

Use **PTY mode** (`pty=true`) for OpenCode — it expects a pseudo-terminal.
If the model hangs, step down the fallback chain:
`mimo-v2.5` → `nemotron-3` → `north-mini-code` → `big-pickle`

## Step 3 — Code Generation

Generate a small but real project that exercises the model's capabilities.
Good test subjects:

- **C# .NET console app** — system dashboard (OS/CPU/RAM/uptime with ASCII art)
- **Node.js CLI** — file processing utility
- **Python script** — data transformation pipeline

```bash
opencode run "Create a C# console app... " --model opencode/deepseek-v4-flash-free
```

## Step 4 — Build & Runtime Verification

```bash
# C#
dotnet run --project "<project-path>"

# Node
node index.js

# Python
python script.py
```

Check for:
- Compilation errors (0 expected)
- Runtime warnings (expected ones like CA1416 are acceptable)
- Actual functional output (dashboard displays real data)

## Step 5 — Complementary Tool Test (if applicable)

If the ecosystem has a complementary tool (Freebuff, Codex, Claude Code):

```bash
# Check for leftover instances
taskkill //F //IM freebuff.exe

# Start in project directory
cd /path/to/project && freebuff
```

Submit a feature addition task (e.g. "Add a Network Info section").
> **Note**: TUI-based tools (Freebuff, etc.) output terminal escape sequences.
> Use foreground PTY mode, not background process management, for reliable interaction.

## Step 6 — Skill Updates

After adding a new tool to the ecosystem, update these skills:

| Skill | What to Add |
|-------|-------------|
| `free-ai-model-router` | New model source section + fallback chain position |
| `model-recommender-workflow` | Task-type mapping row with new option |
| `decide` | Complementary Setup Routing entry + Known Integration Patterns row |
| `update` | Complementary check table row |

## Step 7 — Obsidian Documentation

Create or update notes in the vault:

- **Main project note** — ATM Machine quality: overview, features, architecture,
  code patterns (with `write_file`), Mermaid knowledge graph, tags, wikilinks
- **Tool note** — New tool's capabilities, model list, integration with ecosystem
- **Ecosystem dashboard note** — Update the layer table and cross-links

Cross-link with existing notes: `[[OpenCode]]`, `[[Freebuff]]`,
`[[FreeLLMAPI]]`, `[[Projects/AI Ecosystem Dashboard]]`.

## Step 8 — Knowledge Graph Refresh

```bash
python ~/AppData/Local/hermes/skills/note-taking/obsidian/scripts/render_kg.py
```

Verify: `knowledge_graph.html` is regenerated with new notes visible.

## Expected Outcomes

| Layer | Tool/Step | Success Signal |
|-------|-----------|----------------|
| Model selection | model-recommender.py | Prints valid primary + fallback chain |
| Direct probe | opencode run | Returns response within timeout |
| Code gen | opencode run (PTY) | Files created, NuGet/pip packages added |
| Build | dotnet build/run | Compiles with 0 errors |
| Complementary | freebuff submit | Feature added to project |
| Documentation | Obsidian notes | 3+ notes created/updated with wikilinks |
| KG refresh | render_kg.py | `knowledge_graph.html` saved (no errors) |

## Pitfalls

- **Freebuff TUI process management**: Freebuff's full-screen TUI uses ANSI escape
  codes that garble when captured via background PTY process tools. Always use
  foreground PTY mode for interaction. If background mode is unavoidable, poll
  with `process(log)` to see the raw terminal state.
- **Freebuff instance accumulation**: Each `freebuff` invocation starts a persistent
  process. After testing, clean up with `taskkill //F //IM freebuff.exe`
  (note: MSYS bash requires double slashes).
- **OpenCode model probe**: `opencode run` with a message requires PTY mode in
  Hermes. Without PTY, it either hangs or shows only the help text.
- **Model recommender update**: The free-coding-models CLI (depended on by the
  model recommender) periodically self-updates and may prompt interactively.
  Check for an already-running update before probing.

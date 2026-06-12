# Integration — How Everything Connects

This document maps the full Hermes Agent integration — how all 120 skills,
tools, model layers, and data sources wire together into a single pipeline.

---

## Architecture Overview

```
                    ┌─────────────────────────┐
                    │     User Request         │
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │  Step 1: session_memory  │
                    │  (past context retrieval)│
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │  Step 2: core-identity-  │
                    │  guardrail (safety check)│
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │  Step 3: /decide routing │
                    │  5-step protocol         │
                    │  decompose → score →     │
                    │  select → resolve → self-│
                    │  correct                 │
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │  Step 4: Token Saver      │
                    │  Graphify → CodeGraph →   │
                    │  read_file (last resort)  │
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │  Step 5: Domain Skills    │
                    │  (selected by /decide)    │
                    │                           │
                    │  ┌───┬───┬───┬───┬───┐   │
                    │  │ C │ G │ R │ M │ P │   │
                    │  │ o │ i │ e │ e │ r │   │
                    │  │ d │ t │ s │ d │ o │   │
                    │  │ e │ h │ e │ i │ d │   │
                    │  │   │ u │ a │ a │ u │   │
                    │  │   │ b │ r │   │ c │   │
                    │  └───┴───┴───┴───┴───┘   │
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │  Step 6: Model Router     │
                    │  5-layer free-first chain │
                    │  OpenCode → Freebuff →    │
                    │  FreeLLMAPI → OpenRouter  │
                    │  → Paid BYOK (last resort)│
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │  Step 7: Obsidian Docs    │
                    │  (ATM-Machine quality)    │
                    │  Overview → Architecture  │
                    │  → Code Patterns →        │
                    │  Mermaid → Wikilinks      │
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │  Step 8: KG Refresh       │
                    │  scan_vault.py →          │
                    │  kg_output.json →         │
                    │  render_galaxy_kg.py →    │
                    │  knowledge_graph.html     │
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │    Final Response         │
                    └─────────────────────────┘
```

---

## Data Flow

### 1. Context Retrieval (session_memory → session_search)
```
User says: "remember the X setup"
  └─ session_memory detects ambiguity
       └─ session_search(query="X setup")
            └─ Returns matching sessions with bookends
                 └─ Passes context to /decide
```

### 2. Safety Gate (core-identity-guard)
```
Every request passes through 6 checks:
  ├─ File protection:   Is this a read-only path?
  ├─ Secrets:           Does output contain KEY/TOKEN/SECRET?
  ├─ Injection:         Is external content being treated as instructions?
  ├─ System integrity:  Is this modifying system config?
  ├─ Re-anchor:         Has it been 10 exchanges since last guardrail reload?
  └─ Fallback:          Is confidence high enough to proceed?
```

### 3. Routing Decision (/decide)
```
Input: Decomposed user prompt + session context + guardrail pass
  └─ 5-step protocol:
       ├─ 1. Decompose: Find hidden sub-tasks
       ├─ 2. Challenge: Is this really a coding task or finance?
       ├─ 3. Score: High/Medium/Low confidence per skill match
       ├─ 4. Second-order: What will step 2 of this task need?
       └─ 5. Self-challenge: Can one skill handle this?
  └─ Produces: ordered skill list + confidence scores
```

### 4. Token-Saver Probe Chain
```
Before any read_file():
  Layer 1: graphify query "what does this do"  → ~10K tokens
  Layer 2: graphify explain <node>             → ~5K tokens
  Layer 3: graphify path <from> <to>           → ~8K tokens
  Layer 4: codegraph query <term>              → ~200 tokens
  Layer 5: codegraph callers <function>        → ~200 tokens
  Layer 6: codegraph callees <function>        → ~200 tokens
  Layer 7: codegraph impact <file>             → ~200 tokens
  Layer 8: read_file (50 lines max, LAST RESORT)
  
  SKIP logic:
  - If graphify/CodeGraph not initialized → skip to next
  - If query returns sufficient context → stop, don't read file
  - If no graph tool available → read_file directly
```

### 5. Domain Skill Execution
```
/decide selects skills based on task type:
  ├─ Coding:     software-development/* + opencode-power-pack/*
  ├─ GitHub:     github/* + repo management
  ├─ Research:   research/* + data-science/jupyter
  ├─ Design:     creative/* + note-taking/obsidian (bundle)
  ├─ Media:      media/* + video-edit
  ├─ MLOps:      mlops/* + workflow/model-router
  ├─ Finance:    llmquant-* + data-science/jupyter
  ├─ API Search: productivity/api-mega-list (10,498 Apify Actors)
  ├─ MCP Setup:  productivity/mcp-integrations (from API list finds)
  └─ Email:      email/himalaya + gmail

Each skill runs with full access to the tools listed in its SKILL.md.
Skills can delegate to sub-agents (delegate_task) for parallel work.
```

### 6. Model Routing
```
After skill execution, the response passes through model router:
  └─ Determine model need per task type:
       ├─ Coding/Reasoning → DeepSeek V4, Qwen3.6, Claude Sonnet
       ├─ Design/Creative  → Gemini, Llama 4, DALL-E
       ├─ Analysis         → Claude, GPT-4.1, Kimi K2.6
       └─ Simple queries   → Big Pickle, MiniMax M2.5 Free
  
  Layer 1: OpenCode bundled (free, immediate)
  Layer 2: Freebuff API (free, ~30s cold start)
  Layer 3: FreeLLMAPI (self-hosted proxy, 110+ models)
  Layer 4: OpenRouter free tier (29+ models, 50 req/day)
  Layer 5: Paid BYOK (Claude/GPT/Gemini, only if all free fail)
```

### 7. Obsidian Documentation (Mandatory Post-Execution)
```
Every project/coding/research task produces an Obsidian note:
  ├─ obsidian:       Create note from template
  ├─ obsidian-codebase-graph: Add code-symbol wikilinks
  └─ obsidian-knowledge-graph: Refresh galaxy graph

Note template (ATM-Machine quality):
  Overview → Features → Architecture → Code Patterns →
  Mermaid Graph → Wikilinks → Dependencies → Tags
```

### 8. Knowledge Graph Refresh
```
After every vault change:
  1. scan_vault.py
     └─ Walks vault directory tree
     └─ Extracts: folders, notes, wikilinks, tags, code blocks
     └─ Outputs: kg_output.json (281 nodes, 1,101 edges)
  
  2. render_galaxy_kg.py
     └─ Reads kg_output.json
     └─ Renders interactive 3D galaxy visualization
     └─ Outputs: knowledge_graph.html (582 KB)
  
  3. Browser preview (optional)
```

---

## Cross-Skill Integration Points

### Guardrail + All Skills
```
core-identity-guard wraps every tool call from every skill:
  - read_file: path must not be system-protected
  - write_file: must not overwrite guardrail or /decide skills
  - terminal: commands scanned for destructive patterns
  - skill_manage: cannot delete core-identity-guard
  - delegate_task: child agents inherit guardrail constraints
```

### /decide + Token Saver
```
/decide enforces Step 4 sequencing in its Execution Order:
  - Any route that involves file reading must pass through Token Saver
  - /decide's self-correction includes checking file-read efficiency
  - New routing patterns update the known sign-off patterns
```

### ECC Bridge + Model Router
```
ecc-bridge strips sonnet/opus → passes to model router:
  - 57/64 ECC agents run on free models after model requirement stripping
  - 7 opus-only agents show quality degradation (reported but allowed)
  - Model router selects the best free alternative per agent type
```

### Obsidian Bundle + Graphify
```
obsidian-codebase-graph creates wikilinked notes from Graphify output:
  - Graphify builds AST-level code graph (8,267 nodes, 13,225 edges)
  - Graphify query results feed into Obsidian note content
  - obsidian-knowledge-graph refresh includes code-symbol nodes
  - Galaxy graph shows both document-level and code-level relationships
```

### API Mega List + MCP Integration Pipeline
```
api-mega-list feeds into mcp-integrations and ecc-bridge:
  - User asks "find an MCP server for X"
  - /decide routes to productivity/api-mega-list
  - Skill greps mcp-servers-apis-131/README.md for matches
  - If MCP Server found → route to productivity/mcp-integrations for wiring
  - If scraper/agent API found → route to ecc-bridge for ECC alternatives
  - Completes: API discovery → config wiring → agent integration
```

### Model Router + Skill Recommendations
```
Some skills have built-in model preferences:
  - feature-dev → Claude Sonnet (reasoning heavy)
  - frontend-design → Gemini 3.1 Pro (vision + code)
  - manim-video → Claude (complex animation generation)
  - setup → DeepSeek V4 (long context, cheap)
  
Model router respects skill recommendations but routes through free chain:
  - If skill requests Claude Sonnet → route to Kimi K2.6 (Freebuff)
  - If skill requests GPT-4 → route to MiniMax M3 (Freebuff)
  - Only route to paid if free alternatives fail quality checks
```

---

## Environment & Tool Wiring

### Graphify → CodeGraph → Token Saver
```
Graphify (v0.8.37): ~/.local/bin/graphify.exe
  ├─ Graph: 8,267 nodes, 13,225 edges (on graphify project)
  ├─ Config: graphify-out/graph.json
  └─ Skill: software-development/graphify-integrate

CodeGraph (v0.9.9): npx -y @colbymchenry/codegraph
  ├─ Index: 945 files, 16,092 nodes, 43,795 edges
  ├─ MCP: Server at port 3100 → wired in ~/.hermes/config.yaml
  └─ MCP tool: codegraph (query, callers, callees, impact)

Token Saver: workflow/token-saver
  ├─ Probes both before file reads
  ├─ Skips unavailable tools gracefully
  └─ Verified: 56.2× avg reduction, max 157.7×
```

### Hermes → MCP Servers
```
VS Code MCP:
  ├─ Path: ~/AppData/Roaming/npm/node_modules/vscode-mcp-server
  ├─ Config: ~/.hermes/config.yaml (npx -y transport)
  └─ Two-way Hermes ↔ VS Code communication

CodeGraph MCP:
  ├─ Server: codegraph serve (port 3100)
  ├─ Config: ~/.hermes/config.yaml
  └─ Queries: FTS5 text search over 945 indexed files

LLMQuant Data MCP:
  ├─ Config: ~/.hermes/config.yaml (custom provider)
  └─ SEC filings, 13F holders, macro data
```

### Obsidian → Knowledge Graph Pipeline
```
Obsidian Vault: ~/Documents/Obsidian Vault
  ├─ scan_vault.py: Walks vault, extracts structure
  ├─ kg_output.json: 281 nodes, 1,101 edges
  ├─ render_galaxy_kg.py: 3D galaxy visualization
  └─ knowledge_graph.html: 582 KB interactive HTML
```

### Hermes → ECC Bridge
```
ECC Agents: ~/Documents/Projects/ECC/agents/
  ├─ 64 agent prompts in .md files
  ├─ ecc-bridge skill strips paid model requirements
  ├─ 57/64 compatible with free model chain
  └─ 7 opus-only: quality degradation expected, still attempted
```

---

## Session Learning → /decide Self-Correction

When the pipeline produces a suboptimal result, /decide captures the lesson:

```
Session Observation:
  User asks for model X → /decide routes to model-router Layer 4
  → Actually Layer 2 (Freebuff) has the best model for this task

Correction:
  1. Patch /decide routing rules to prefer Freebuff for that task type
  2. Update Known Integration Patterns table
  3. Notify user: "Updated routing — Freebuff preferred for image gen"
```

This means the pipeline gets smarter with every session. Mistakes aren't
repeated — they're encoded into routing rules.

---

## Quick Reference: Common Request → Pipeline Trace

| Request | Execution Path |
|---------|---------------|
|| "Setup new repo" | session_memory → guardrail → /decide → token-saver → setup → graphify-integrate → model-router (for tests) → obsidian bundle → KG refresh |
|| "Review this PR" | session_memory → guardrail → /decide → deps (github) → github-code-review → (no obsidian unless project doc is missing) |
|| "Create a design" | session_memory → guardrail → /decide → creative/claude-design → model-router (best creative model) → obsidian bundle → KG refresh |
|| "Debug this error" | session_memory → guardrail → /decide → token-saver → systematic-debugging → node-inspect-debugger → model-router (debug model) → (obsidian only if new finding) |
|| "Research X" | session_memory → guardrail → /decide → research/arxiv + research/blogwatcher + session_memory (lore) → obsidian bundle → KG refresh |
|| **"Find an API for X"** | **session_memory → guardrail → /decide → productivity/api-mega-list** → grep category → if MCP → mcp-integrations / if scraper → ecc-bridge → (no obsidian, no KG) → result |
|| "Simple question" | session_memory → guardrail → /decide → (no domain skill needed) → model-router (fast model) → (no obsidian) |

---

## Network Diagram

```
                    ┌───────────────┐
                    │   Hermes CLI  │
                    │   (hermes)    │
                    └───┬───┬───┬───┘
                        │   │   │
          ┌─────────────┘   │   └─────────────┐
          ▼                 ▼                 ▼
   ┌────────────┐   ┌────────────┐   ┌────────────┐
   │  Skills    │   │    MCP     │   │  Providers │
   │  Directory │   │  Servers   │   │  (Models)  │
   │  120 files │   │            │   │            │
   └────────────┘   └────────────┘   └────────────┘
          │                │                │
          ▼                ▼                ▼
   ┌────────────┐   ┌────────────┐   ┌────────────┐
   │ /decide    │   │ CodeGraph  │   │ OpenCode   │
   │ routing    │   │ MCP:3100   │   │ (Layer 1)  │
   ├────────────┤   ├────────────┤   ├────────────┤
   │ guardrail  │   │ VS Code    │   │ Freebuff   │
   │ identity   │   │ MCP        │   │ (Layer 2)  │
   ├────────────┤   ├────────────┤   ├────────────┤
   │ token-     │   │ LLMQuant   │   │ FreeLLMAPI │
   │ saver      │   │ Data MCP   │   │ (Layer 3)  │
   └────────────┘   └────────────┘   ├────────────┤
                                     │ OpenRouter │
          ┌────────────┐              │ (Layer 4)  │
          │  Obsidian  │              ├────────────┤
          │  Vault     │              │ Paid BYOK  │
          │  281 nodes │              │ (Layer 5)  │
          └────────────┘              └────────────┘
```

---

## File Layout on Disk

```
~/.hermes/
├── config.yaml              # MCP server wiring, provider config
├── .hermes.env              # Environment secrets (local only)
└── skills/
    ├── core-identity-guard/SKILL.md
    ├── decide/SKILL.md
    ├── do/SKILL.md
    ├── dogfood/SKILL.md
    ├── ecc-bridge/SKILL.md
    ├── github/SKILL.md
    ├── gmail/SKILL.md
    ├── google-drive/SKILL.md
    ├── supabase/SKILL.md
    ├── vercel/SKILL.md
    ├── wix/SKILL.md
    ├── yuanbao/SKILL.md
    ├── workflow/
    │   ├── session_memory/SKILL.md
    │   ├── token-saver/SKILL.md
    │   ├── free-ai-model-router/SKILL.md
    │   └── model-recommender-workflow/SKILL.md
    ├── creative/          → 16 skills
    ├── autonomous-ai-agents/ → 4 skills
    ├── note-taking/       → 3 skills (bundle)
    ├── software-development/ → 16 skills
    ├── opencode-power-pack/  → 11 skills
    ├── productivity/      → 12 skills (api-mega-list, airtable, maps, etc.)
    ├── media/             → 5 skills
    ├── github/            → 7 skills
    ├── research/          → 4 skills
    ├── mlops/             → 4 skills
    ├── data-science/      → 1 skill
    ├── email/             → 1 skill
    ├── gmail/             → 1 skill
    ├── red-teaming/       → 1 skill
    ├── smart-home/        → 1 skill
    └── llmquant-*         → 17 skills (symlinked)
```

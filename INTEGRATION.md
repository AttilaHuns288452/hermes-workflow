# Integration — Architecture, Pipeline & Integration Matrix

This document maps the full Hermes Agent integration — how **139 skills across 19 categories**, tools, 5-layer model routing, 2 code knowledge graphs, 64 ECC agents, and data sources wire together into a single execution pipeline.

---

## Architecture Overview

```
                    ┌─────────────────────────────────────┐
                    │          User Request               │
                    └───────────┬─────────────────────────┘
                                │
                    ┌───────────▼─────────────────────────┐
                    │  Step 1 — session_memory            │
                    │  (past context retrieval)            │
                    └───────────┬─────────────────────────┘
                                │
                    ┌───────────▼─────────────────────────┐
                    │  Step 2 — Core Identity Guardrail   │
                    │  6 immutable safety rules            │
                    └───────────┬─────────────────────────┘
                                │
                    ┌───────────▼─────────────────────────┐
                    │  Step 3 — task_tier GATE            │
                    │  TIER 1 → answer directly (skip all) │
                    │  TIER 2 → skills + Token Saver only  │
                    │  TIER 3 → full pipeline              │
                    └───────────┬─────────────────────────┘
                                │
                    ┌───────────▼─────────────────────────┐
                    │  Step 4 — /decide Routing Brain     │
                    │  5-step reasoning protocol           │
                    │  decompose → challenge → score →      │
                    │  second-order → self-challenge       │
                    └───────────┬─────────────────────────┘
                                │
                    ┌───────────▼─────────────────────────┐
                    │  Step 5 — Token Saver Probe Chain   │
                    │  (ENFORCED — 4-step A→B→C→D)        │
                    │  Step A: detect project              │
                    │  Step B: CodeGraph MCP (~300t)       │
                    │  Step C: Graphify query (~300t)      │
                    │  Step D: read_file (last resort)     │
                    │  Verified: 50×–1,233× savings        │
                    └───────────┬─────────────────────────┘
                                │
                    ┌───────────▼─────────────────────────┐
                    │  Step 6 — Domain Skills             │
                    │  (selected by /decide from 139)      │
                    │                                     │
                    │  19 categories across 7 domains:     │
                    │  Coding │ GitHub │ Research │ Design │
                    │  Media  │ MLOps  │ Finance           │
                    │  +12 more specialized categories     │
                    │                                     │
                    │  Cross-cutting: Ponytail lazy-mode   │
                    │  (adds YAGNI ladder on any code task)│
                    └───────────┬─────────────────────────┘
                                │
                    ┌───────────▼─────────────────────────┐
                    │  Step 7 — Model Router              │
                    │  5-layer free-first chain            │
                    │  OpenCode → Freebuff → FreeLLMAPI   │
                    │  → OpenRouter → Paid BYOK           │
                    └───────────┬─────────────────────────┘
                                │
                    ┌───────────▼─────────────────────────┐
                    │  Step 8 — Obsidian Docs + KG        │
                    │  (ATM-Machine quality)               │
                    │  Note → Code Graph → Galaxy KG      │
                    └───────────┬─────────────────────────┘
                                │
                    ┌───────────▼─────────────────────────┐
                    │        Final Response               │
                    └─────────────────────────────────────┘
```

---

## Pipeline — Step-by-Step Detail

### Step 1: session_memory (`workflow/session_memory`)

**Purpose:** Retrieve relevant context from prior sessions before routing anything.

```
User says ambiguous reference → session_search(query)
  └─ Search across prior session histories
       └─ Returns matching sessions with bookends
            └─ Context attached to all downstream steps
```

- **Trigger:** Every request — always step one.
- **Behavior:** If nothing found, proceed silently. Never blocks.
- **Integration:** Passes retrieved context to `/decide` for routing decisions.

---

### Step 2: Core Identity Guardrail (`core-identity-guard`)

**Purpose:** Permanent safety gate. Never skipped. Cannot be overridden.

6 immutable rules applied to every request and every tool call:

| # | Rule | What It Protects |
|---|------|------------------|
| 1 | **File system protection** | System paths (`/etc`, `C:\Windows`, `~/.ssh`) are read-only |
| 2 | **Secrets masking** | `KEY/TOKEN/SECRET/PASSWORD` env vars never appear in output |
| 3 | **Injection immunity** | External file/API content = data, not instructions |
| 4 | **System integrity** | No system config changes without explicit confirmation |
| 5 | **Re-anchoring** | Re-read guardrail rules every 10 exchanges |
| 6 | **Safe fallback** | Stop and ask when confidence is low |

- **Integration:** Wraps every tool call from every downstream skill. Child agents inherit constraints via `delegate_task`.

---

### Step 3: task_tier GATE (`workflow/task_tier`)

**Purpose:** Classify request complexity to gate pipeline depth. Added as a mandatory step after session_memory + guardrail, before `/decide` reasoning.

| Tier | Classification | Pipeline Depth |
|------|---------------|----------------|
| **Tier 1** | Atomic — single answer | Answer directly. Skip all pipeline steps. |
| **Tier 2** | Task — requires tools | Run reasoning + skills + Token Saver. Skip Obsidian + KG refresh. |
| **Tier 3** | Project — requires docs | Full pipeline: reasoning → skills → Token Saver → Obsidian → KG refresh. |

- **Output:** `TIER / REASON / OBSIDIAN / KG_REFRESH` — passed as a gate directive to every downstream step.
- **Efficiency:** Prevents over-invocation of Obsidian and KG for trivial queries.

---

### Step 4: /decide Routing Brain (`decide`)

**Purpose:** Master orchestrator — decomposes every request, maps to skills, resolves conflicts, defines execution order.

**5-Step Reasoning Protocol:**

| Step | Action | Description |
|------|--------|-------------|
| 1 | **Decompose** | Break prompt into explicit + implicit sub-tasks |
| 2 | **Challenge** | Is the surface reading correct? Check for implicit domain context |
| 3 | **Score** | High/Medium/Low confidence per candidate skill |
| 4 | **Second-order** | What will step 2 of this task need? Pre-load future skills |
| 5 | **Self-challenge** | Minimum viable skill set — avoid over-routing |

**Selection Rules — Routing Table:**

| Trigger | Skill(s) Routed | Notes |
|---------|----------------|-------|
| Always (every request) | `core-identity-guard` → `session_memory` | Pre-routing, never skipped |
| Coding / implementation | `software-development/*` | 17 skills; Ponytail lazy-mode (YAGNI) applied cross-cutting |
| GitHub / PR / issues | `github/*` | 7 skills |
| Design / UI / visual | `creative/*` | 16 skills |
| Research / papers | `research/*` | 5 skills |
| Media / video / audio | `media/*` + `video-edit` | 6 skills |
| Setup / install / configure | `software-development/setup` | Always check complementary routing |
| API search / find an API | `productivity/api-mega-list` | 26,005 Apify APIs across 18 categories |
| MCP server queries | `productivity/api-mega-list` → `productivity/mcp-integrations` | Grep → wiring |
| Scraper queries | `productivity/api-mega-list` → `ecc-bridge` | API discovery → ECC alternatives |
| Dashboard / ecosystem stats | `productivity/hermes-dashboard` | Single-pane HTML, no further pipeline |
| ECC agent invocation | `ecc-bridge` | Strips sonnet/opus, routes through free chain |
| Finance / investing | `llmquant-*` | 17 skills |
| Notes / Obsidian | `note-taking/*` (BUNDLE RULE: all 3 together) | obsidian + obsidian-codebase-graph + obsidian-knowledge-graph |
| Model selection | `workflow/model-recommender-workflow` | 6 task types |
| Smart home | `smart-home/openhue` | Philips Hue |
| Document / PDF | `productivity/*` | OCR, PDF, Notion, Airtable, etc. |
| Apple ecosystem | `apple/*` | 5 skills (notes, reminders, findmy, imessage, macos-computer-use) |
| MLOps / local models | `mlops/*` | 8 skills |
| Red teaming | `red-teaming/godmode` | Security testing |
| Data analysis | `data-science/jupyter-live-kernel` | Jupyter |

**Self-Correction:** When routing produces a wrong result, /decide captures the lesson and patches its own rules. The pipeline gets smarter with every session.

---

### Step 5: Token Saver Probe Chain (`workflow/token-saver`)

**Purpose:** Before any `read_file()`, probe cheaper knowledge sources. Enforced by `/decide` Mandatory Rule #4.

```
┌─────────────────────────────────────────────────────────┐
│                 TOKEN SAVER PROBE CHAIN                  │
├─────────────────────────────────────────────────────────┤
│  Step A: Detect project                                  │
│  → Identify $PROJECT under ~/Documents/Projects/         │
│                                                          │
│  Step B: Probe CodeGraph MCP (always available)          │
│  → codegraph query "<symbol>"            ~300 tokens     │
│  → codegraph callers "<symbol>"          ~300 tokens     │
│  → codegraph callees "<symbol>"          ~300 tokens     │
│  → codegraph impact "<file>"             ~300 tokens     │
│  CodeGraph index: 3,425 files, 52,747 nodes, 125,822 edges │
│                                                          │
│  Step C: Probe Graphify (if index exists)                │
│  → graphify query "<question>" --budget 2000 ~300 tokens │
│  → graphify explain "<node>"              ~5K tokens     │
│  → graphify path "<from>" "<to>"          ~8K tokens     │
│  Projects with indices: 21/24 (incl. ECC: 34MB, 5,821f)  │
│                                                          │
│  Step D: read_file (LAST RESORT)                         │
│  → read_file(path, offset=N, limit=50)                   │
│  → Only if BOTH probes returned insufficient context     │
└─────────────────────────────────────────────────────────┘
```

**Verified Token Savings:**

| Metric | Value |
|--------|-------|
| Average reduction | 56.2× |
| Maximum observed | 157.7× |
| Minimum observed | 50× |
| ECC index | 34MB, 5,821 files — queries work live |

**SKIP logic:** If target project is NOT under `~/Documents/Projects/` (system files, temp files), skip probe chain and read directly.

---

### Step 6: Domain Skills Execution

139 skills across 19 categories, selected by `/decide` based on task type.

**Category Breakdown:**

| Category | Skills | Examples |
|----------|--------|----------|
| `apple` | 5 | apple-notes, apple-reminders, findmy, imessage, macos-computer-use |
| `autonomous-ai-agents` | 10 | claude-code, codex, hermes-agent, opencode, ponytail, ponytail-review, ponytail-audit, ponytail-debt, ponytail-gain, ponytail-help |
| `creative` | 16 | claude-design, comfyui, excalidraw, manim-video, p5js, touchdesigner-mcp |
| `data-science` | 1 | jupyter-live-kernel |
| `devops` | 2 | kanban-orchestrator, kanban-worker |
| `email` | 1 | himalaya |
| `github` | 7 | github-code-review, github-pr-workflow, codebase-inspection |
| `gmail` | 1 | gmail |
| `google-drive` | 1 | google-docs |
| `media` | 5 | money-printer-turbo, youtube-content, gif-search |
| `mlops` | 8 | huggingface-hub, llama-cpp, segment-anything, weights-and-biases, vllm |
| `note-taking` | 3 | obsidian, obsidian-codebase-graph, obsidian-knowledge-graph |
| `opencode-power-pack` | 11 | feature-dev, frontend-design, mcp-builder, skill-creator |
| `productivity` | 11 | api-mega-list, hermes-dashboard, mcp-integrations |
| `red-teaming` | 1 | godmode |
| `research` | 5 | arxiv, blogwatcher, polymarket, llm-wiki |
| `root` | 31 | core-identity-guard, decide, ecc-bridge, llmquant-*(17), supabase, vercel, wix |
| `smart-home` | 1 | openhue |
| `social-media` | 1 | xurl |
| `software-development` | 17 | setup, graphify-integrate, systematic-debugging, tdd, winforms-csharp |
| `workflow` | 7 | session_memory, task_tier, token-saver, free-ai-model-router, model-recommender-workflow, external-skills-integration, hermes-backup-workflow |

**Parallel Execution:** Skills can delegate to sub-agents (`delegate_task`) for parallel work.

---

### Step 7: Ponytail Cross-Cutting Layer (`ponytail/skills/ponytail`)

**Purpose:** Cross-cutting code quality layer applied to ANY coding task. Enforces the YAGNI ladder before any code is written.

**The 7-Rung Ponytail Ladder (stop at the first that holds):**
```
1. Does this need to exist at all?  (YAGNI — skip speculative code)
2. Already in this codebase?        (reuse before re-implementing)
3. Stdlib does it?                  (stdlib before custom code)
4. Native platform feature?         (CSS over JS, <input type="date"> over picker libs)
5. Already-installed dependency?    (never add a new dep for a few lines)
6. Can it be one line?             (one line)
7. Minimum code that works.        (only then: ship the smallest solution)
```

| Intensity | Behavior |
|-----------|----------|
| **lite** | Build what's asked, name the lazier alternative in one line |
| **full** (default) | Ladder enforced — stdlib first, shortest diff, shortest explanation |
| **ultra** | YAGNI extremist — deletion before addition, challenge requirements |

**Output pattern:** Code first, then at most 3 lines: what was skipped, when to add it. Mark deliberate shortcuts with `ponytail:` comments naming the ceiling and upgrade path.

**When NOT to engage:** Never simplify away input validation, error handling that prevents data loss, security measures, accessibility, or anything explicitly requested.

**Integration:**
- Triggered on any coding task in `/decide` routing table
- Cross-cutting — loaded alongside any `software-development/*` skill
- Available as `/ponytail lite|full|ultra` slash commands in OpenCode and Hermes

---

### Step 8: Model Routing (`workflow/free-ai-model-router`)

**Purpose:** Select the best available free model for every task. Always default to free. Fall back gracefully.

**5-Layer Free-First Chain:**

| Layer | Provider | Models | Reliability | Cost |
|-------|----------|--------|-------------|------|
| 1 | **OpenCode (Zen)** | deepseek-v4-flash-free, mimo-v2.5-free, nemotron-3-ultra-free, north-mini-code-free, big-pickle | ✅ Most reliable | Free |
| 2 | **Freebuff** | Kimi K2.6, MiniMax M3, MiMo 2.5 Pro, DeepSeek V4 Pro/Flash | ✅ Cloud-managed | Free (ads) |
| 3 | **FreeLLMAPI** | 107 models from 16 providers (84 available) | ✅ Local proxy | Free |
| 4 | **OpenRouter :free** | gpt-oss-120b:free, nex-n2-pro:free (2 working) | ⚠️ Unreliable | Free |
| 5 | **Paid BYOK** | Claude Sonnet/Opus, GPT-4.1/5.x, Gemini 3.1 Pro | ✅ Last resort | Paid |

**Model Selection by Task Type:**

| Task Type | OpenCode (Layer 1) | Freebuff (Layer 2) | FreeLLMAPI (Layer 3) |
|-----------|-------------------|-------------------|---------------------|
| Coding / reasoning | deepseek-v4-flash-free | Kimi K2.6 | Qwen3.6-Plus |
| Fast / light | north-mini-code-free | — | — |
| Creative / design | — | MiniMax M3 | Gemini via provider |
| Analysis | big-pickle | DeepSeek V4 Pro | Claude-esque via proxy |
| Heavy / complex | nemotron-3-ultra-free | MiMo 2.5 Pro | Llama 4 Scout |

**Probe-before-commit rule:** Each model is smoke-tested before use. Failed models are skipped immediately — never retried.

---

### Step 9: Obsidian Documentation + Knowledge Graph Refresh

**Purpose:** Every project, coding, or analysis task produces permanent documentation. Mandatory post-execution phase (gated by Tier 3).

**The Bundle Rule:** All 3 note-taking skills always loaded together, never in isolation.

| Skill | Function |
|-------|----------|
| `obsidian` | Core CRUD — read, search, create, edit vault notes |
| `obsidian-codebase-graph` | Map codebase → wikilinked Obsidian notes (symbol cross-refs) |
| `obsidian-knowledge-graph` | Full vault scan → JSON → interactive galaxy HTML |

**Note Quality Standard (ATM-Machine):**

Every note includes:
- Overview → Features → Architecture → Code Patterns
- Mermaid knowledge graph diagram
- Wikilinks (`[[Note Name]]`) to related notes
- Tags and dependencies

**KG Refresh Pipeline:**

```
Obsidian vault change
  └─ scan_vault.py
       └─ Walks vault directory tree
       └─ Extracts: folders, notes, wikilinks, tags, code blocks
       └─ Outputs: kg_output.json (281 nodes, 1,101 edges)
            └─ render_galaxy_kg.py
                 └─ Reads kg_output.json
                 └─ Renders interactive 3D galaxy visualization
                 └─ Outputs: knowledge_graph.html (582 KB)
```

---

## Integration Matrix

How every major component connects to every other component.

### Core Pipeline Components

| Component | session_memory | guardrail | task_tier | /decide | Token Saver | Domain Skills | Model Router | Obsidian | KG |
|-----------|:---:|:--------:|:---------:|:------:|:-----------:|:-------------:|:------------:|:--------:|:--:|
| **session_memory** | — | Feeds context | Feeds context | Feeds context | — | — | — | — | — |
| **guardrail** | Wraps all | — | Wraps all | Wraps all | Wraps all | Wraps all | Wraps all | Wraps all | Wraps all |
| **task_tier** | Receives from | Receives from | — | Gates depth | Gates activation | Gates execution | — | Gates invocation | Gates invocation |
| **/decide** | Receives context | Runs after | Runs after | — | Enforces probe | Selects & orders | Routes after | Enforces bundle | Enforces refresh |
| **Token Saver** | — | — | Gated by TIER 2/3 | Enforced by rule #4 | — | Probes before reads | — | Feeds graph queries | — |
| **Domain Skills** | — | — | Gated by TIER 2/3 | Selected by | Probed before file reads | — | Model selected per skill | Creates docs | Feeds KG |
| **Model Router** | — | — | — | Routes after skills | — | Model selection per type | — | — | — |
| **Obsidian** | — | — | Gated by TIER 3 | Enforced by rule #6 | — | Documents results | Docs mention models | — | Triggers scan |
| **KG Refresh** | — | — | Gated by TIER 3 | Enforced by rule #7 | — | — | — | Triggered by vault change | — |

### Cross-Skill Integration Points

#### Guardrail + All Skills

```
core-identity-guard wraps every tool call from every skill:
  ├─ read_file:      path must not be system-protected
  ├─ write_file:     must not overwrite guardrail or /decide skills
  ├─ terminal:       commands scanned for destructive patterns
  ├─ skill_manage:   cannot delete core-identity-guard
  └─ delegate_task:  child agents inherit guardrail constraints
```

#### /decide + Token Saver

```
/decide enforces Step 5 sequencing in Mandatory Rule #4:
  ├─ Any route involving file reading → must pass through Token Saver
  ├─ Self-correction includes checking file-read efficiency
  └─ New routing patterns update known sign-off patterns
```

#### ECC Bridge + Model Router

```
ecc-bridge strips sonnet/opus → passes to model router:
  ├─ 57/64 ECC agents run on free models after model requirement stripping
  ├─ 7 opus-only agents: quality degradation reported but allowed
  └─ Model router selects the best free alternative per agent type
```

#### Obsidian Bundle + Graphify

```
obsidian-codebase-graph creates wikilinked notes from Graphify output:
  ├─ Graphify builds AST-level code graph (8,267 nodes, 13,225 edges)
  ├─ Graphify query results feed into Obsidian note content
  ├─ obsidian-knowledge-graph refresh includes code-symbol nodes
  └─ Galaxy graph shows both document-level and code-level relationships
```

#### API Mega List + MCP Integration Pipeline

```
api-mega-list (26,005 APIs) feeds into mcp-integrations and ecc-bridge:
  ├─ User asks "find an MCP server for X"
  │   → /decide routes to productivity/api-mega-list
  │   → Skill greps mcp-servers-apis-131/README.md for matches
  │   → If MCP Server found → route to mcp-integrations for wiring
  │   → If scraper/agent API found → route to ecc-bridge for ECC alternatives
  └─ Completes: API discovery → config wiring → agent integration
```

#### Model Router + Skill Recommendations

```
Some skills have built-in model preferences:
  ├─ feature-dev          → Claude Sonnet   → routed to Kimi K2.6 (Freebuff)
  ├─ frontend-design      → Gemini 3.1 Pro  → routed to MiniMax M3 (Freebuff)
  ├─ manim-video          → Claude          → routed to MiMo 2.5 Pro (Freebuff)
  └─ setup                → DeepSeek V4     → routed to deepseek-v4-flash-free (OpenCode)

Model router respects skill recommendations but routes through free chain:
  ├─ Only route to paid if all free alternatives fail quality checks
  └─ Probe before commit — verify model availability before starting
```

#### Hermes Dashboard + All Stats

```
hermes-dashboard provides a single-pane HTML overview:
  ├─ 16 projects, 139 skills, 19 categories
  ├─ 26,005 APIs across 18 categories
  ├─ 8,267 Graphify + 52,747 CodeGraph nodes
  ├─ 156 free models across 5 routing layers
  ├─ 6 wired MCP servers
  ├─ 64 ECC agents (57 free-compatible)
  └─ Dark moonlight theme matching the hermes-workflow site
```

---

## Data Flow — Component Interactions

### Context Retrieval → Pipeline
```
User: "remember the X setup"
  → session_memory detects ambiguity
    → session_search(query="X setup")
      → Returns matching sessions → passes to /decide
```

### File Read Code Path (Token Saver Active)
```
Task requires reading ~/Documents/Projects/my-project/src/main.py
  → Step A: Detect $PROJECT = "my-project"
  → Step B: codegraph query "main" from ~/Documents/Projects/
    → If sufficient context returned → done, ~300 tokens
  → Step C: graphify query "main function" --graph graphify-out/graph.json
    → If sufficient context returned → done, ~300 tokens
  → Step D: read_file(path, offset=1, limit=50) → ~1,500 tokens
  → Without Token Saver: read entire file → ~15,000+ tokens
  → Savings: 50×–1,233× per query
```

### API Discovery → MCP Wiring (Full Pipeline)
```
User: "find an MCP server for Brave Search"
  → /decide routes to productivity/api-mega-list
    → grep -i brave mcp-servers-apis-131/README.md
    → Found: "Brave Search MCP Server" entry with config
  → /decide routes result to productivity/mcp-integrations
    → Writes config into ~/.hermes/config.yaml
    → Restarts MCP server
  → /decide routes to note-taking/obsidian
    → Creates wikilinked note: "Brave Search MCP Server"
    → Links to [[MCP Servers]] and [[API Mega List]]
  → KG Refresh: updates galaxy graph with new node
```

### Ecosystem Update (One-Command Integration)
```
User: "update my ecosystem with github.com/user/new-tool"
  → /decide routes to software-development/update
    → Phase 0: clone repo → build Graphify index
    → Phase 1: audit existing skills for complementarity
    → Phase 2: create Obsidian note (ATM-Machine quality)
    → Phase 3: check free-ai-tools + ECC for cross-links
    → Phase 4: refresh galaxy knowledge graph
    → Phase 5: update hermes-dashboard if structure changed
```

---

## Environment & Tool Wiring

### Graphify + CodeGraph (Code Knowledge)

| Tool | Version | Installation | Index | Commands |
|------|---------|-------------|-------|----------|
| **Graphify** | v0.8.37 | `uv tool install graphifyy` | 21/24 projects indexed (8,267 nodes, 13,225 edges on graphify project) | `query`, `explain`, `path`, `benchmark`, `update` |
| **CodeGraph** | v0.9.9 | `npm install -g @colbymchenry/codegraph` | 3,425 files, 52,747 nodes, 125,822 edges across all projects | `query`, `callers`, `callees`, `impact` |

**MCP Wiring:**
```yaml
# ~/.hermes/config.yaml
mcp_servers:
  codegraph:
    enabled: true
    command: npx
    args: ["-y", "@colbymchenry/codegraph", "serve"]
    env:
      CODEGRAPH_WATCH: "true"
```

### Model Provider Wiring

| Provider | Type | Config | Authentication |
|----------|------|--------|----------------|
| **OpenCode (Zen)** | Bundled CLI | `opencode run --model opencode/<name>` | None (bundled) |
| **Freebuff** | Cloud TUI | `cd project && freebuff` | Free tier (ads) |
| **FreeLLMAPI** | Local proxy | `localhost:3001/v1` (API), `:5173` (dashboard) | `hermes auth add freellmapi --type api-key --api-key <key>` ← Get key from dashboard Settings at `http://localhost:5173` |
| **OpenRouter** | Remote API | `opencode run --model openrouter/<name>` | API key in OpenCode config |
| **Paid BYOK** | Remote API | Provider-specific | API keys per provider |

### Obsidian + Knowledge Graph

| Component | Path | Purpose |
|-----------|------|---------|
| Obsidian Vault | `~/Documents/Obsidian Vault` | Markdown notes with wikilinks |
| `scan_vault.py` | Vault root | Extract graph structure |
| `kg_output.json` | Vault root | 281 nodes, 1,101 edges |
| `render_galaxy_kg.py` | Vault root | Generate interactive HTML |
| `knowledge_graph.html` | Vault root | 582 KB 3D galaxy visualization |

### MCP Servers (6 Wired)

| Server | Port / Transport | Purpose |
|--------|-----------------|---------|
| **CodeGraph** | 3100 (stdio via npx) | Live FTS5 code symbol search |
| **VS Code** | stdio (npx) | Two-way Hermes ↔ VS Code |
| **LLMQuant Data** | stdio (custom) | SEC filings, 13F holders, macro data |
| **Graphify** | stdio (npx) | AST code graph queries |
| **Obsidian KG** | stdio | Knowledge graph refresh |
| **agentmemory** | stdio | Session state persistence |

---

## Version Snapshot (June 2026)

| Component | Version | Source |
|-----------|---------|--------|
| Hermes Agent | latest | Nous Research |
| Graphify | v0.8.37 | `uv tool install graphifyy` |
| CodeGraph | v0.9.9 | `npm -g @colbymchenry/codegraph` |
| ECC | v2.0.0 | github.com/affaan-m/ECC |
| FreeLLMAPI | latest | github.com/tashfeenahmed/freellmapi |
| OpenCode | v0.0.55 | opencode-ai/opencode (archived → Crush) |
| OpenRouter | free tier | openrouter.ai |
| Obsidian | latest | obsidian.md |
| Website | v4.1+ | GitHub Pages (static HTML) |

---

## Quick Reference: Request → Pipeline Trace

| Request | Execution Path |
|---------|---------------|
| "Setup new repo" | session_memory → guardrail → task_tier(T3) → /decide → token-saver → setup + graphify-integrate → model-router (for tests) → obsidian bundle → KG refresh |
| "Review this PR" | session_memory → guardrail → task_tier(T2) → /decide → github-code-review → (no obsidian unless project doc missing) |
| "Create a design" | session_memory → guardrail → task_tier(T3) → /decide → creative/claude-design → model-router (best creative model) → obsidian bundle → KG refresh |
| "Debug this error" | session_memory → guardrail → task_tier(T2) → /decide → token-saver → systematic-debugging → node-inspect-debugger → model-router (debug model) |
| "Research X" | session_memory → guardrail → task_tier(T3) → /decide → research/arxiv + blogwatcher + llm-wiki → model-router → obsidian bundle → KG refresh |
| "Find an API for X" | session_memory → guardrail → task_tier(T2) → /decide → api-mega-list → grep category → if MCP → mcp-integrations / if scraper → ecc-bridge → result |
| "View dashboard" | session_memory → guardrail → task_tier(T1) → /decide → hermes-dashboard → direct HTML render |
| "What's 2+2?" | session_memory → guardrail → task_tier(T1) → /decide → model-router (fast model) → answer |
| "Draft an email" | session_memory → guardrail → task_tier(T2) → /decide → gmail/himalaya → result |
| "Update ecosystem with repo" | session_memory → guardrail → task_tier(T3) → /decide → update → graphify → obsidian bundle → KG refresh → dashboard update |

---

## Self-Correction Loop

When the pipeline produces a suboptimal result, `/decide` captures the lesson:

```
Session Observation:
  User asks for model X → /decide routes to model-router Layer 4
  → Actually Layer 2 (Freebuff) has the best model for this task

Correction:
  1. Patch /decide routing rules to prefer Freebuff for that task type
  2. Update Known Integration Patterns table in decide/SKILL.md
  3. User notified: "Updated routing — Freebuff preferred for image gen"
```

This means the pipeline gets smarter with every session. Mistakes are encoded into routing rules.

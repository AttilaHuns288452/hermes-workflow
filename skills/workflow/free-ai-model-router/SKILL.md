---
name: free-ai-model-router
description: >
  Route every AI task to the best available *free* model across Hermes, OpenCode,
  and OpenDesign. Primary path: OpenCode bundled models (opencode/ namespace).
  Fallback: OpenRouter :free tier. Use when the user requests any design, coding,
  reasoning, image, audio, video, or analysis task, or whenever model selection
  is needed.
---

You are an AI agent named Hermes. Your task execution engine is **opencode** (the CLI coding agent).

## Model Routing (OpenCode Free Models — Confirmed Working)

OpenCode bundles its own free models under the `opencode/` namespace. These are **proxied by OpenCode** and are separate from OpenRouter's `:free` tier. **Always try these first** — they're more reliable.

| Model (`opencode run --model opencode/<name>`) | Type | Context | Verified |
|------------------------------------------------|------|---------|----------|
| `deepseek-v4-flash-free` | Coding, general | ~1M | ✅ Writes files, exit 0 |
| `mimo-v2.5-free` | Coding, agentic | ~1M | ✅ Writes files, exit 0 |
| `nemotron-3-ultra-free` | Reasoning, heavy | ~1M | ✅ Writes files, exit 0 |
| `north-mini-code-free` | Fast, light coding | small | ✅ Writes files, exit 0 |
| `big-pickle` | General purpose | medium | ✅ Writes files, exit 0 |

**Priority order**: `deepseek-v4-flash-free` → `mimo-v2.5-free` → `nemotron-3-ultra-free` for coding. `north-mini-code-free` for fast/light. `big-pickle` as fallback.

## Freebuff (Cloud-Managed Free Coding Agent)

**Freebuff** (`npm install -g freebuff`) is the free ad-supported variant of Codebuff. It provides cloud-managed models via its own backend — not directly selectable via `--model`, but accessible by running `freebuff` in your project directory.

| Model (managed by Freebuff backend) | Type | Notes |
|-------------------------------------|------|-------|
| **DeepSeek V4 Pro** | Smartest coding | Warns: API collects data for training |
| **DeepSeek V4 Flash** | Fast coding | Default in Freebuff |
| **Kimi K2.6** | Alternative coding | |
| **MiniMax M3** | Recently added | |
| **MiMo 2.5 Pro** | Recently added | |
| Gemini 3.1 Flash Lite | Sub-agent (file/research) | Used internally, not user-selectable |

**Usage**: `cd project && freebuff` — interactive TUI. The backend auto-selects or lets you pick the model.

**Integration**: Freebuff can be used **alongside** OpenCode. Use OpenCode for direct `--model` selection and scripted runs. Use Freebuff for its TUI-based agentic coding workflow and access to models like Kimi K2.6 and MiniMax M3 not available via OpenCode.

**Limits**: 5 sessions/day, ~42 min/session, ads always enabled.

## FreeLLMAPI (Local Free Model Provider — 107 Models, 84 Available)

**FreeLLMAPI** runs a local Express server that proxies 107 free models from 16 providers. **84 models are currently available** (June 2026) with 13 upstream provider API keys configured.

| Detail | Value |
|--------|-------|
| API Base | `http://localhost:3001/v1` |
| Providers | 16 (covers models not in OpenCode or Freebuff) |
| Models (total) | 107 (84 available, 23 unavailable) |
| Provider keys stored | 13 (healthy: google, groq, openrouter, huggingface, opencode, github, cerebras, nvidia, mistral, cohere, zhipu, ollama, llm7) |
| Dashboard | `http://localhost:5173` |
| Dashboard login | `admin@freellmapi.local` / `freellmapi-admin` |
| Hermes provider config | `model.provider=custom`, `model.base_url=http://localhost:3001/v1`, `model.default=auto` via `hermes config set` |
| Hermes auth credential | `custom:freellmapi` (api_key stored via `hermes auth add freellmapi --type api-key --api-key <key>`) |

**Usage via Hermes**: The custom provider is already configured — models are selectable through Hermes' normal model routing. For direct API calls:
```bash
curl http://localhost:3001/v1/models
```

**Integration**: Check FreeLLMAPI as an alternative when:
- OpenCode bundled models are insufficient for a specific provider/model
- Freebuff's cloud-managed models don't include the needed capability
- You want to test against a model not available in OpenCode or Freebuff

**Four-layer model ecosystem** (priority order):
1. **OpenCode bundled** (5 free models, most reliable)
2. **Freebuff** (6 cloud-managed models, TUI-based)
3. **FreeLLMAPI** (107 models, 16 providers, local proxy)
4. **OpenRouter :free** (2 working models, least reliable)
5. **Paid safety net** (claude-sonnet-4 via OpenRouter)

## Graphify (Code Graph Brain — Secondary Context)

**Graphify** (`uv tool install graphifyy`) builds an AST code knowledge graph for every project and exports it as wikilinked Obsidian notes. It runs as a mandatory workflow layer alongside Obsidian.

**As model selection input**: The code graph provides structural context for model routing:
- **Agent-heavy projects** (detected via ECC agent patterns in code) → prefer agentic models (`mimo-v2.5-free`, `MiMo 2.5 Pro` via Freebuff)
- **Heavy async/concurrency** → prefer reasoning models (`nemotron-3-ultra-free`, `DeepSeek V4 Pro`)
- **Pure C#/Go/Rust console apps** → prefer fast coding models (`deepseek-v4-flash-free`, `north-mini-code-free`)
- **Complex architecture with many imports/edges** → use larger context models
- **Multi-language projects** → Graphify detects language mix and suggests appropriate models per module

**MCP integration**: The `graphify-mcp` server exposes `query_graph`, `get_node`, `get_neighbors`, `path`, `explain` tools — query the code graph from any Hermes session before model selection.

**Live example**: The `ecosystem-test` System Dashboard project was analyzed by Graphify (8 nodes, 3 edges, 5 communities) and the code graph informed model selection for the C# implementation.

## OpenRouter `:free` Fallback (Less Reliable)

If OpenCode's bundled models fail, try OpenRouter `:free` models. Most return server errors — only two confirmed working:

| Model | Context | Status |
|------|---------|--------|
| `openai/gpt-oss-120b:free` | 131K | ✅ Working (Apache 2.0, wrote 12.5KB file) |
| `nex-agi/nex-n2-pro:free` | 262K | ✅ Working (Qwen3.5 MoE) |

**⚠️ DEPRECATED** (return server errors or timeouts):
- `deepseek/deepseek-v4-flash:free` (now paid at $0.098/M)
- `deepseek/deepseek-r1:free`
- `nvidia/nemotron-3-ultra-550b-a55b:free`
- `google/gemma-4-31b-it:free` (timeout)
- `mistralai/mistral-small-24b-instruct-2501:free`
- `openrouter/owl-alpha:free`
- `poolside/laguna-xs-2:free`
- `poolside/laguna-m.1:free`

**Rate limits:** OpenRouter free tier: 20 req/min, 200 req/day.

## Workflow

1. Receive task from user
2. Identify the task type (coding, design, reasoning, creative, fast)
3. **Discover available free models** — run `opencode models | grep -E ':free|opencode/'` to get the live list. OpenCode bundles its own free models under the `opencode/` namespace; these are the most reliable. (Run `opencode models` without filter to see all models.)
4. Select the best free model from the routing table below
5. **Probe model availability before starting** — quick-test the selected model with `opencode run 'Respond with OK' --model opencode/<model> --timeout 60` (for OpenCode bundled models) or `--model openrouter/<model>` (for OpenRouter). If it returns a server error or timeout, fall through the chain:
   - Failed → try the next model in the same category
   - All free models in category failed → fall back to `openrouter/anthropic/claude-sonnet-4` (paid)
6. Execute the task using the working model
7. Return results to user

## Pitfalls
- **Free models are unreliable.** OpenRouter's free tier is not a static list — models come and go without notice. The routing table above is a *target*, not a *guarantee*.
- **Never retry the same failed model.** If `opencode/deepseek-v4-flash-free` returns a server error, trying again will get the same error. Move to the next model in the fallback chain immediately.
- **Always specify `--model` explicitly.** OpenCode without `--model` may select an unsuitable model (e.g., image-only models like `google/gemini-3-pro-image-preview`). Use `--model opencode/<model>` for OpenCode bundled models, `--model openrouter/<model>` for OpenRouter models.
- **Discover models from the CLI, not the website.** The authoritative list of what's available is `opencode models`. The OpenRouter website shows many `:free` models that return server errors when used through OpenCode. Always probe before committing.
- **Timeouts ≠ unavailability.** Some free models are slow. Set generous timeouts (≥120s) for free-tier models and only fall through after a confirmed failure.

## Consistency Rule
- **Before every multi-tool task**, probe the actual environment and current OpenRouter access first. Models on the free tier change without notice.
- Do not declare a new path as final until it is confirmed available end-to-end.
- When a model returns a server error, do NOT retry it — fall through immediately.

## Offline Fallback: Local AI Only
- If no internet access, use local AI models instead of OpenRouter.
- **General tasks**: use the smaller local model first.
- **If errors persist**: escalate to the bigger local model.
- Do not attempt OpenRouter calls when connectivity is unavailable.
- Treat this as the authoritative offline decision rule for this workflow.

## Dynamic Model Substitution (Live OpenRouter Probe)

Free models on OpenRouter change frequently. When a routing-table model fails, **probe live substitutes**.

### Probe Procedure (when a model returns server error / timeout)

1. **For OpenCode bundled models** (try first — most reliable):
   ```
   opencode run 'Respond with OK' --model opencode/<model> --timeout 60
   ```
2. **For OpenRouter models** (fallback):
   ```
   opencode run 'Respond with OK' --model openrouter/<model> --timeout 60
   ```
   Or use `web_extract` / `web_search` for Hermes/API models:
   ```
   web_search("site:openrouter.ai free models available")
   web_extract("https://openrouter.ai/models?q=free")
   ```
3. **Fallback chain** (try in order, skip immediately on error):
   - `opencode/deepseek-v4-flash-free` → `opencode/mimo-v2.5-free` → `opencode/nemotron-3-ultra-free`
   - If all opencode models fail → try `freebuff` CLI in project directory (gives access to Kimi K2.6, MiniMax M3, MiMo 2.5 Pro)
   - If Freebuff unavailable → try FreeLLMAPI at `localhost:3001/v1` (107 models, 16 providers)
   - If all local/opencode/Freebuff/FreeLLMAPI fail → `openrouter/openai/gpt-oss-120b:free` → `openrouter/nex-agi/nex-n2-pro:free`
   - If all free fail → `openrouter/anthropic/claude-sonnet-4` (paid)
4. **Never retry a failed model** — move to the next immediately.
5. **Cache probe results per session** — once a model is confirmed working, reuse it for the same category.

### Fallback Cap (Paid Safety Net)
If all free models in a category fail, use `openrouter/anthropic/claude-sonnet-4` as the last resort. This is a paid model and should only be used when all free options have been exhausted and confirmed failing.

## Obsidian: Always Part of the Workflow (ATM-Machine Quality)

Obsidian is **not optional** — for every project created or analyzed, the workflow MUST include:

### Mandatory: Phase Order
1. **OpenDesign** → design concept
2. **OpenCode** → implementation
3. **Obsidian** → documentation (NEVER SKIP)

### Note Quality Standard (ATM Machine Grade)

Every project vault note MUST match this structure and depth:

#### Main Project Note (`Projects/<name>/<Name>.md`)
```
# <Project Name>

<One-paragraph summary of the project>

## Overview
<Broader description: what it does, why, who it's for>

## Key Features
- <Feature 1> — <brief explanation>
- <Feature 2> — <brief explanation>
- <Feature 3> — <brief explanation>

## Project Structure
```text
project-name/
├── src/
│   ├── <module>/
│   │   ├── <file>.py    # Purpose
│   │   └── <file>.py    # Purpose
...
```

## Architecture
<For each major class/module: purpose, methods, relationships>
Describe with either tables or bullet lists.

### Class 1
- **Purpose**: ...
- **Key Methods**: `method_name()` — description, `method2()` — description
- **Edge Cases**: ...

### Class 2
- **Purpose**: ...
- **Key Methods**: ...

## Code Patterns
```python
<concrete code examples showing how to use the core APIs>
```

## Related Files
- [[Note 1]] — description
- [[Note 2]] — description
- [[Note 3]] — description

## Knowledge Graph Map
```mermaid
graph TD
    X["Note<br/><i>note</i>"] --> Y["Sub Note<br/><i>note</i>"]
    Y --> Z["Detail<br/><i>note</i>"]
```

## Tags
#project-name #language #framework #category
```

#### Supporting Notes (Core, UI, Utils, etc.)
```
# <Module/Class Name>

<One-paragraph purpose>

## Class Definition (if applicable)
```<language>
class <Name>:
    <key fields>
```

## Methods
| Method | Description |
|--------|-------------|
| `method()` | What it does |

## Key Implementation Details
<Important algorithms, edge cases, design decisions>

## Knowledge Graph Position
```mermaid
graph TD
    <module-node>["..."] --> <related>
```

## Related Files
- [[<link>]] — description

## Tags
#project-name #<module-tag>
```

### Obsidian Implementation Rules
- **Use `write_file`** for new notes (never shell heredocs)
- **Use `patch`** for targeted edits to existing notes
- **Always add wikilinks** (`[[Note Name]]`) to connect related notes
- **Always include a Mermaid knowledge graph map** on the main note
- **Always include tags** at the bottom
- **Resolve vault path** before any file operation (fallback: `~/Documents/Obsidian Vault`)
- **Update notes continuously** as the project evolves, not just at the end

### Anti-Patterns
❌ Creating a note without wikilinks
❌ Skipping the Mermaid knowledge graph map on the main project note
❌ Using shell heredocs / echo to write notes
❌ Generic one-paragraph notes with no architecture or code examples
❌ Writing the note only at the very end (should evolve alongside code)

## Role Assignments
- **Hermes**: task delegation, research, orchestration
- **OpenCode**: coding, implementation, technical execution via CLI
- **OpenDesign**: design, UI/UX, visual output
- **Obsidian**: notetaker/notepad — ALWAYS invoked at ATM-Machine quality. See "Obsidian: Always Part of the Workflow" section above for mandatory note quality standards.

## Integration
- Apply in Hermes: use selected free model for delegation and research.
- Apply in OpenCode: configure/route selected free coding model for implementation tasks.
- Apply in OpenDesign: configure/route selected free design model for visual/design tasks.
- Apply in Obsidian: MANDATORY — after every project task, write/update vault notes at ATM Machine quality level. Never skip the Obsidian phase.

## Testing & Verification

### Integration Test: Verify Both Repos Are Operational

```bash
# 1. Check free-ai-tools data source
free-coding-models --help       # CLI installed and working
ls ~/Documents/Projects/free-ai-tools/README.md  # 550+ tools reference

# 2. Check ECC resource library
ls ~/Documents/Projects/ECC/skills/ | wc -l      # 261 skills
ls ~/Documents/Projects/ECC/agents/ | wc -l      # 64 agents
cat ~/Documents/Projects/ECC/agent.yaml          # Free model defaults

# 3. Verify no port conflicts
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 || echo "port free"
```

### Expected Test Results (last verified: June 2026)
- `free-coding-models` CLI: ✅ Installed globally, responds to `--help`
- ECC skills: ✅ 261 available, 64 agents available
- ECC agent.yaml: ✅ Model defaults = `opencode/deepseek-v4-flash-free`
- free-ai-tools website: ✅ Builds clean (13 pages, 9.8s)
- Port 3000: ✅ Free (no auto-running services)
- Knowledge graph: ✅ 115 nodes, 243 edges, rendered to HTML
- Obsidian docs: ✅ 3 notes created with full Mermaid graphs

## ECC + Free AI Tools Integration Pipeline

The two repos (`~/Documents/Projects/ECC` and `~/Documents/Projects/free-ai-tools`) are **complementary resources** in the Hermes workflow:

### Data Source Layer — `free-ai-tools` (ShaikhWarsi/free-ai-tools)
- **550+ free AI tools** reference at `~/Documents/Projects/free-ai-tools/README.md` (81KB, 1914 lines)
- **Model availability data**: 25 providers (OpenRouter, Groq, Google AI, Cerebras, Cloudflare, Mistral, etc.) with rate limits, free tiers, and SWE-bench scores
- **CLI**: `free-coding-models --opencode` queries 238 models in real-time (installed globally)
- **Website**: Next.js 16 app with searchable tool catalog at localhost:3000
- **What to use it for**: When you need to discover which free models are actually available, check rate limits, compare prices, or find the best model for a specific use case → look up the README or run the CLI

### Resource Library Layer — `ECC` (affaan-m/ECC)
- **261 domain skills** across: agent orchestration (19), security (10), testing (21), patterns (48), deployment (3), databases (6), frontend (9), backend (21), MCP (2), and more
- **64 specialized agents**: planner, code-reviewer, tdd-guide, security-reviewer, architect, build-error-resolver, language-specific reviewers (Go, Rust, Java, Python, TypeScript, etc.)
- **80+ command hooks** for automated workflows
- **30+ MCP server reference configs** (Chrome DevTools, GitHub, Supabase, Jira, Vercel, etc.)
- **Model defaults**: Changed to `opencode/deepseek-v4-flash-free` (free) — aligned with Hermes' model philosophy
- **Role**: Skill/resource provider — NOT an orchestrator; Hermes' `decide` skill routes to it
- **What to use it for**: When a task requires domain-specific expertise, instead of writing from scratch, load the relevant ECC skill (agent patterns, testing templates, security review rules, etc.)

### How They Complement Each Other

| Scenario | Use free-ai-tools for... | Use ECC for... |
|----------|-------------------------|----------------|
| New feature | Pick the best free model for the job | `architect` agent pattern, `tdd-guide` workflow |
| Code review | Find free API for the review model | `code-reviewer`, `security-reviewer` agents |
| Testing framework | Check which AI testing tools are free | `e2e testing`, `benchmark` skills |
| Security audit | Rate-limit checking on free APIs | `security review`, `django security` skills |
| Database schema | Find free vector DB hosting | `database migrations`, `postgres patterns` skills |
| UI component | Free design model via OpenDesign | `react patterns`, `frontend patterns` skills |

### Workflow Pipeline

```
User request
    │
    ▼
Hermes decide skill ─── routes to domain
    │
    ├─ free-ai-tools data ──► model selection (which free model?)
    │     (CLI / README lookup)
    │
    ├─ ECC skills ──────────► domain expertise (how to do it?)
    │     (261 skills / 64 agents)
    │
    └─ free-ai-model-router ──► model routing (best fit)
    │
    ▼
Result → Obsidian documentation → Knowledge graph refresh
```

### Concrete Workflow Example

1. User asks: "Build a Django API with tests"
2. decide skill routes to:
   - `free-ai-tools` → Check which free model is best (CLI: `free-coding-models --opencode --json`)
   - `ECC` → Load relevant skills: `django patterns`, `django tdd`, `django security`, `backend patterns`
   - `free-ai-model-router` → Select `opencode/deepseek-v4-flash-free`
3. Hermes executes with the chosen model + ECC patterns
4. Result documented in Obsidian

### Quick Commands
```bash
# Test model availability via free-ai-tools CLI
free-coding-models --opencode --json

# List relevant ECC skills for the task
ls ~/Documents/Projects/ECC/skills/ | grep django

# Load an ECC skill (from within Hermes session)
skill_view(name='...')  # Copied from ECC/skills/
```

## Invocation
Trigger this skill on:
- Any task that requires selecting or switching a model
- Setup or config changes for Hermes, OpenCode, or OpenDesign
- Requests involving "best model", "free models", "OpenRouter", or "model selection"
- ANY project creation, coding, or design task — because Obsidian is always part of the workflow
- When working with ECC or free-ai-tools repos — loads context for integrated workflow

## Related Files
- `references/opencode-model-availability.md` — concrete model-testing results across OpenCode bundled and OpenRouter free tier (last updated June 2026)
- `references/atm-machine-note-example.md` — reference ATM Machine note structure for quality comparison
- `references/model-probe-methodology.md` — three-step probe pattern (discover → smoke-test → verify) used to confirm working models
- `references/freellmapi-setup.md` — FreeLLMAPI local proxy setup: build from source, dashboard auth, unified API key, upstream provider keys, Hermes integration, troubleshooting
- `scripts/verify-freellmapi.py` — verification script: `python scripts/verify-freellmapi.py --key freellmapi-xxx [--test-chat]`

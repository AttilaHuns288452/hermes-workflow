# Meta-Prompt Template

A complete reference for building a META_PROMPT.md — a self-contained
prompt that reproduces a full Hermes Agent ecosystem in a fresh session.

## Structure

The meta-prompt has six major sections:

1. **Header** — Title, instruction ("copy and paste this block"), date
2. **System Config Block** — code-fenced block with model/provider/guardrail/tools
3. **Custom Skills** — one subsection per custom/author-authored skill
4. **Pipeline** — numbered execution order with one-liners
5. **Model Chain** — table of fallback layers
6. **Key Config** — paths, MCP servers, version numbers

## Template

```markdown
# Meta Prompt — [User]'s Hermes Agent Setup

Copy and paste this entire block into a new Hermes Agent session to see
my complete skill ecosystem, model chain, guardrail, and workflow pipeline.
*Last updated: [YYYY-MM-DD]*

---

```
=== HERMES AGENT CONFIGURATION ===

Primary Model: [model name]
Provider: [provider name]
Active Profile: [profile name]

Guardrail:
  • core-identity-guard: ACTIVE (6 rules — file safety, secrets,
    injection immunity, system integrity, re-anchor, safe fallback)

Token Saver:
  • Probe chain: Graphify → CodeGraph → read_file (last resort)
  • Verified: 56.2× avg token reduction

Obsidian:
  • Vault: [vault path]
  • Bundle rule: obsidian + obsidian-codebase-graph + obsidian-knowledge-graph

Graphify:
  • Version: [x.y.z]
  • Corpus: [N]K words → ~[N]K tokens naive → ~[N]K probed

CodeGraph MCP:
  • Status: [active/inactive]
  • Indexed: [N] files, [N] nodes, [N] edges
```

---

## Pipeline (Execution Order)

Every request runs through this sequence, every time:

```
session_memory → guardrail → /decide → token-saver →
Graphify/CodeGraph → domain skills → model routing →
Obsidian docs → KG refresh
```

1. **📖 session_memory** — Pull prior context from past sessions. Never route blind.
2. **🛡️ Core Identity Guardrail** — 6 safety checks before anything else runs. Never skipped.
3. **🧠 /decide** — 5-step reasoning protocol: decompose → challenge → score → route → self-challenge.
4. **⚡ Token Saver** — Probe Graphify query/explain/path → CodeGraph query/callers/impact → read_file (last resort). 56× reduction.
5. **🧬 Graphify + CodeGraph** — Dual code knowledge: Graphify (AST graph, community detection) + CodeGraph (live MCP index).
6. **🎯 Domain Skills** — Execute via the skill(s) selected by /decide from the catalog below.
7. **🤖 Model Routing** — Probe each layer: [Layer 1] → [Layer 2] → [Layer 3] → [Layer 4] → [Layer 5].
8. **📝 Obsidian Docs** — ATM-Machine quality: Overview, Architecture, Mermaid graph, Code Patterns, wikilinks.
9. **🕸️ KG Refresh** — Re-scan vault, regenerate interactive galaxy graph. Compounding knowledge.

---

## Custom Skills

### 1. decide — The Routing Brain
**Path:** `~/.hermes/skills/decide/SKILL.md`
**Triggers:** always (every prompt)
**Behavior:** Decomposes every request, checks session_memory, loads guardrail + token-saver
**Self-healing:** Patches itself via skill_manage when routing is wrong

### 2. core-identity-guard — Permanent Safety Guardrail
**Path:** `~/.hermes/skills/core-identity-guard/SKILL.md`
**Triggers:** always (never skipped)
**6 rules:** File protection, secrets handling, injection immunity, system integrity, re-anchor every 10 exchanges, safe fallback
**Enforcement:** Blocks all tool calls until guard check passes

### 3. token-saver — Pre-Read Probe Chain
**Path:** `~/.hermes/skills/token-saver/SKILL.md`
**Triggers:** before every read_file() call
**Chain:** Graphify query → Graphify explain → Graphify path → CodeGraph query → CodeGraph callers/callees → CodeGraph impact → read_file (last resort)
**Verified:** 56.2× token reduction (max 157.7×)

### 4. model-router — 5-Layer Fallback Chain
**Path:** `~/.hermes/skills/model-router/SKILL.md`
**Triggers:** when model selection is needed or a request fails
**Layers:**
  1. OpenCode bundled (5 free models) — primary
  2. Freebuff cloud (6 models: DeepSeek, Kimi, MiniMax, MiMo, Gemini) — fallback
  3. FreeLLMAPI localhost:3001/v1 (110+ models, 16 providers) — wide selection
  4. OpenRouter free (29+ models) — research
  5. Paid BYOK — last resort

### 5. ecc-bridge — ECC Agent Adapter
**Path:** `~/.hermes/skills/ecc-bridge/SKILL.md`
**Behavior:** Strips sonnet/opus model requirements from ECC agents, routes 57/64 through the free model chain
**Key agents wired:** [list key ones]

### 6. obsidian-docs — Documentation Template
**Path:** `~/.hermes/skills/obsidian-docs/SKILL.md`
**Triggers:** after every project, coding, or analysis task
**Template:** Overview → Features → Project Structure → Architecture (Mermaid) → Code Patterns → Key Files → Dependencies → Wikilinks

---

## Model Chain
```
                        ┌─────────────────┐
                        │   TASK ENTERS   │
                        └────────┬────────┘
                                 │
                    ┌────────────▼────────────┐
                    │ Layer 1: OpenCode       │ ← 5 free models, primary
                    │   DeepSeek, Qwen, etc.  │
                    └────────────┬────────────┘
                                 │ fails?
                    ┌────────────▼────────────┐
                    │ Layer 2: Freebuff        │ ← 6 cloud models
                    │   Kimi K2.6, MiniMax M3, │
                    │   MiMo 2.5 Pro, Gemini   │
                    └────────────┬────────────┘
                                 │ fails?
                    ┌────────────▼────────────┐
                    │ Layer 3: FreeLLMAPI      │ ← 110+ on localhost:3001
                    │   16 providers, any model│
                    └────────────┬────────────┘
                                 │ fails?
                    ┌────────────▼────────────┐
                    │ Layer 4: OpenRouter free│ ← 29+ models
                    │   DeepSeek, Qwen, etc.  │
                    └────────────┬────────────┘
                                 │ fails?
                    ┌────────────▼────────────┐
                    │ Layer 5: Paid BYOK       │ ← Last resort
                    │   Your own API key      │
                    └─────────────────────────┘
```

| Layer | Provider | Count | Cost | Best For |
|-------|----------|-------|------|----------|
| 1 | OpenCode | 5 models | Free | Default tasks, coding |
| 2 | Freebuff | 6 models | Free | Creative, long context |
| 3 | FreeLLMAPI | 110+ models | Free | Any, broadest selection |
| 4 | OpenRouter | 29+ models | Free | Research, niche models |
| 5 | Paid BYOK | - | Cost | Premium quality |

**Selection logic:** Model Router probes each layer in order. If layer returns a valid completion, use it. If timeout or error, fall to next. Never skip to paid without trying all free layers.

---

## Key Config

- **Obsidian vault:** `[path]`
- **CodeGraph MCP:** [status — wired in ~/.hermes/config.yaml]
- **Graphify:** v[x.y.z] — [N] nodes, [N] edges, [N] communities
- **LLMQuant Data MCP:** [status]
- **VS Code MCP:** [status]
- **Profile:** [profile name]

---

## License

This Hermes Agent setup and its skill files are shared under
**Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**.
Free to use, share, and adapt — no commercial use.
```

## Usage

When building a meta-prompt for a user's actual setup:

1. **Populate all placeholders** (`[User]`, `[model name]`, `[vault path]`, etc.) — never leave brackets in the delivered file.
2. **Run the audit commands** from the `update` skill's Phase 1 to get real numbers.
3. **Custom skills section**: one entry per unique custom skill. Skip bundled/shipped skills.
4. **Model chain**: match the actual layers the user has configured. Modify the 5-layer default if their setup differs.
5. **Pipeline**: keep the numbered 9-step structure. It's the core reference.
6. **File output**: 350-420 lines is the sweet spot. Over 450 becomes unwieldy.

## Pitfalls

- **Stale numbers**: The meta-prompt is a snapshot. Add a date at the top and footnote.
- **Secrets exposure**: Never include actual API keys, model tokens, or local paths that reveal PII.
- **Over-customizing**: A meta-prompt that works for one session but breaks for another is worse than a generic one. Keep it structural and documented.
- **Graphify CLI differences**: Windows Graphify v0.8.37 doesn't have `export obsidian`. Don't reference it.

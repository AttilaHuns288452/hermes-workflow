# /decide Skill Evolution — Session Learnings

**Date**: June 11, 2026
**Major changes**: Graphify made mandatory "secondary brain", execution order updated, complementary setup routing expanded

---

## Key Rule Changes Made This Session

### 1. Graphify as Mandatory Secondary Brain (Rule 2)

**Before**: Obsidian bundle only (`obsidian` + `obsidian-codebase-graph` + `obsidian-knowledge-graph`)

**After**: Obsidian+Graphify bundle mandatory:
```
`obsidian` + `obsidian-codebase-graph` + `obsidian-knowledge-graph` + `graphify-integrate`
```

**Rationale**: Graphify provides AST-level code understanding that feeds ALL downstream skills:
- Model selection (free-ai-model-router)
- Code review and architecture decisions
- Refactoring and debugging
- Complementary tool integration

### 2. Graphify in Execution Order (New Position)

**Before**:
```
session_memory → reasoning → soul → primary domain → complementary → post-execution (Obsidian)
```

**After**:
```
session_memory → reasoning → soul → **Graphify (build/refresh code graph + MCP context)** → primary domain → complementary → post-execution (Obsidian + Graphify export + KG refresh)
```

**Graphify runs immediately after soul files, before primary domain skills** — it's the "secondary brain" that provides context for everything downstream.

### 3. Complementary Setup Routing — Graphify First Entry

**Before**: Graphify was one of several items in the table

**After**: Graphify is **FIRST and MANDATORY** for every project:
```
- Graphify (codebase knowledge graph) → MANDATORY for every project.
  Route to BOTH `setup` AND `graphify-integrate` AND the Obsidian bundle.
  Graphify is the secondary brain — provides AST-level code understanding
  that feeds model selection, code review, architecture decisions, etc.
```

### 4. Known Integration Patterns — Graphify as Secondary Brain

**Added new pattern**:
| Pattern | Trigger | Route to |
|---------|---------|----------|
| Graphify as secondary brain | Any project/coding/analysis task | Run `graphify-integrate` immediately after session_memory. Build code graph, export to Obsidian, register MCP. The code graph provides AST-level context for all downstream skills. |

### 5. Updated Existing Pattern — Graphify + Obsidian Bundle

**Before**: "User sets up Graphify (or any code-graph tool)"

**After**: "**MANDATORY for every project:** User sets up Graphify (or any code-graph tool) OR **any project task**"

---

## Verification: Two Test Projects Confirm Pipeline

### Test 1: System Dashboard (Simple)
- Graphify: 8 nodes, 3 edges, 5 communities → 13 Obsidian notes
- With Gemini semantic: 16 nodes, 11 edges, 6 communities → 22 notes
- Model selected: `opencode/deepseek-v4-flash-free` (confirmed by Graphify's simple procedural signal)

### Test 2: Task Manager CLI (Complex Clean Architecture)
- Graphify: 60 nodes, 95 edges, 14 communities → 74 Obsidian notes
- Architecture detected: Models/Services/Commands separation, TaskService as hub
- Model selected: `opencode/deepseek-v4-flash-free` (confirmed by Graphify's clean architecture signal)

---

## Updated Mandatory Rules Summary

| Rule | Description |
|------|-------------|
| 1 | session_memory always step one |
| 2 | **Graphify mandatory secondary brain** — runs on every project/coding/analysis task |
| 3 | **Obsidian+Graphify bundle mandatory** — docs + code graph required deliverables |
| 4 | After every Obsidian OR Graphify update → regenerate KG |
| 5 | Direct skill invocations → /decide still runs |
| 6 | Setup tasks → complementary integration check |

---

## Updated Execution Order

```
session_memory
    │
    ▼
reasoning (5-step protocol)
    │
    ▼
soul file(s)
    │
    ▼
**Graphify (build/refresh code graph + MCP context)** ← NEW
    │
    ▼
primary domain skill(s)
    │
    ▼
complementary check (setup tasks)
    │
    ▼
post-execution: Obsidian bundle + Graphify export + KG refresh
```

---

## Signals That Triggered These Changes

1. **User explicit instruction**: "remember to also put graphify as part of the workflow and use graphify as secondary context and brain with obsidian /decide"

2. **Empirical validation**: Two test projects showed Graphify's code graph provides actionable architectural signals (60 nodes/95 edges from 5 files) that directly inform model selection

3. **Ecosystem completeness**: The free model ecosystem now has a code-aware brain that complements note-level (Obsidian KG) and model-level (free-ai-model-router) intelligence

---

## Future Session Implications

When user says:
- "build X" → Graphify runs first, code graph feeds model selection
- "review code Y" → Graphify MCP queried for context before review
- "refactor Z" → Graphify communities guide refactoring boundaries
- "add feature to W" → Graphify hub nodes show impact radius

**No project task runs without Graphify context** — it's now the persistent secondary brain layer.

---

*Session learnings captured for /decide self-evolution per its own Session Evolution rules.*
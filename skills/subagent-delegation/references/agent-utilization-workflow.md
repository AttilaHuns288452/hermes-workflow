# Agent Utilization Workflow — End-to-End Pattern

Proven workflow from the budget tracker build session (2026-07-29).

## Full Pipeline

```
Orchestrator (deepseek-v4-pro): plan minimal spec
         ↓
21st.dev: get_inspiration("dark financial dashboard") → extract design tokens
         ↓
ECC code-reviewer (optional): audit architecture before build
         ↓
DeepSeek V4 Flash: build (delegate_task or opencode run)
         ↓
MiMo V2.5: visual QA (delegate_task with screenshot)
         ↓
Orchestrator: code-path trace + visual findings → report
```

## Concrete Example: Budget Tracker

1. **Orchestrator plan:** "Single HTML React CDN, 4 sections, glassmorphism"
2. **21st.dev design:** "Financial Dashboard" → tokens: #0f0f17 bg, #1e1e2a cards, #34D399 green, #F87171 red, Inter font, rounded inputs
3. **DeepSeek build:** delegate_task → index.html (309 lines)
4. **MiMo QA:** screenshot via PowerShell CopyFromScreen → delegate_task → found 3 critical bugs (below-fold, invisible button, contrast)
5. **Iterate:** DeepSeek added graphs + sample data → evolved to Vite React project → added nav + dashboard

## Key Decisions

- **Single HTML first, project later** — ponytail: build the lazy version first, upgrade only when user asks
- **No React Router** — state-based tab switching (rung 6: native over dep)
- **21st.dev ≠ code** — shadcn needs build system; use for design tokens only
- **ECC skipped for simple files** — single-file HTML doesn't need architecture review; MiMo finds visual bugs faster
- **PowerShell screenshot** — `CopyFromScreen` when cua-driver not installed; npx serve to bypass file:// CORS for fonts

## Pitfalls

- **cua-driver not installed** → fall back to PowerShell CopyFromScreen + npx serve
- **Firecrawl blocks localhost** → can't use for local QA; serve via npx and use PowerShell screenshot
- **LightRAG API volatile** → `ainsert(source_id=)` removed in 1.5.4 → switched to TF-IDF
- **Ollama LLM + LightRAG slow** → 295 files × LLM calls = >300s timeout → TF-IDF is 0.5s, zero API
- **React CDN <script> ordering** — Recharts must load after React; Babel must be last
- **Vite + Tailwind config** — use `@tailwindcss/vite` plugin, not Tailwind CLI; add to vite.config.js

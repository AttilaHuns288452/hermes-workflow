# Finance UI research round (2026-08-11)

Web research (Copilot Money, Muzli 50-best dashboards, Outcrowd fintech trends, template market) done to plan the next CashFlow OS UI round. User approved the full roadmap; 4 workstreams dispatched on kanban board `cfos-research-sprint` (tasks t_e81c0cb8 dashboard, t_f0f0ceae transactions, t_f7d2c3e3 mobile nav, t_5ab72d0d cashy).

## Patterns worth stealing (from the market leaders)

- **Copilot Money** (current gold standard): one-glance dashboard; every number has a trend arrow + context line ("vs last month"); accounts as a list with balances + sparklines; budgets as progress bars with % + over-budget red states; native mobile tab bar. Zero decorative chrome.
- **GlobalLink** (Muzli, Orbix Studio) — transaction/ledger table benchmark: spacious rows, color-coded status pills (Completed/Canceled/Pending), gradient balance header, effortless filters. Target for our transactions page.
- **Vaulto** — cinematic dark finance: deep charcoal surface LAYERING (card-on-card depth), multi-layer line chart, Sankey cash-flow diagram, net-cashflow heatmap.
- **Finexy** — SMB finance: multi-wallet balance cards + spending limits + recent-activity ledger (closest analog to Business mode).

## 2026 fintech trends (Outcrowd brief)

1. **Explainable AI** — AI must cite real numbers ("Spending up ₱2,300 — driven by Dining +₱1,100"), declined actions get explicit reasons + next steps.
2. **Agentic AI: recommendations → actions** — one-tap action chips from AI output.
3. **Data portability** — visible Export (CSV/JSON) + delete-account not buried.
4. **Progress over spinners** — real progress indicators + reassurance copy in onboarding.
5. **Regulation as UI** — statuses/explainers rendered in the interface (approval flows).

## Template landscape (same stack: shadcn + Tailwind v4)

| Template | Why | Cost |
|---|---|---|
| Shadcn UI Kit — FinanceView (`shadcnuikit.com/dashboard/finance`) | finance admin dashboard in our exact stack, dark+light | free preview, $69 |
| Bundui shadcn-dashboard-free (GitHub, MIT) | production shadcn dashboard + 5 pages | free |
| TailAdmin | 500+ Tailwind components to cherry-pick | free/open |
| 21st.dev components (`npx shadcn add`) | financial-dashboard, efferd-dashboard-2 (dense KPI grid), bento-dashboard | free-ish |

Inspiration galleries: Muzli 50 Best Dashboard 2026, Dribbble finance-dashboard, Mobbin finance category, Pinterest orbixstudio/dashboard-ui.

## Approved roadmap (mapped to existing code)

- **P0**: stat-card sparklines (extract the SVG polyline Sparkline from AIAssistant into shared `src/components/ui/sparkline.tsx`; feed from the 6-month chart data already loaded) + count-up on load (`.stat-enter` keyframe exists in globals.css; rAF hook respecting prefers-reduced-motion) · transaction status pills (unified token pill: `rounded-full border border-border bg-muted/50 px-2 py-0.5 text-[10px]`) · budget % bars with red over-budget state.
- **P1**: explainable Cashy — live month stats in context (income/expense/net + top-3 categories), `Source:` footnote rendering (`text-accent-bright` + Info icon), one-tap chips (Log expense → `/transactions?add=1`, View transactions) · CSV export client-side (serialize loaded rows, Blob download, headers date,type,category,description,amount,status).
- **P2**: mobile bottom tab bar (Home/Transactions/Business/Cashy/Settings, `pb-[env(safe-area-inset-bottom)]`, active state via usePathname; Cashy tab = `document.querySelector('.cashy-orb')?.click()` since it's always mounted) — then RAISE QuickFAB (`bottom-20`), orb default (`bottom-20`), toasts (`bottom-32 md:bottom-4`) above it, `pb-16` on the scroll container · bento dashboard grid (briefing full-width, stats 2/4-col, charts 2-col, budget/health 2-col — wrappers only, preserve all sections + empty states) · dark-mode card layering (color-mix surface elevation, additive, light mode untouched).

## Design guardrails re-affirmed during research

Keep (differentiators — generic fintech is sans-serif + green): serif display font, periwinkle `#5e6ad2` accent, flat minimal. Don't chase: gradients, glassmorphism, neon, 3D — the user's frozen design language.

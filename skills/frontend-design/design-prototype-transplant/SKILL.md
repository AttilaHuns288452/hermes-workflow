---
name: design-prototype-transplant
description: Apply a static HTML prototype's design (Open Design exports with DESIGN-HANDOFF.md/DESIGN-MANIFEST.json) to an existing app — token extraction, frozen DESIGN-SPEC.md, parallel agents on disjoint file sets, single build, review gate. Use when the user drops a folder of prototype HTML files and says "make the app look like this" or "apply this design to our project".
---

# Design Prototype Transplant

Transplant a static HTML prototype's visual system into an existing app WITHOUT rewriting the app. Proven on CashFlow OS (Next.js 16 + Tailwind v4 + shadcn) from a 4-screen Open Design export.

## When to Use
- User drops a folder of prototype HTML files (`dashboard.html`, `business-mode.html`, …) + `DESIGN-HANDOFF.md` + `DESIGN-MANIFEST.json`
- "Make it look like this prototype" / "apply this design" / "polish it more"

## Workflow

### 1. Extract tokens BEFORE writing code
Read the entry HTML's `<style>` block. Pull the frozen token table: bg, surface, fg, muted, border, accent, semantic colors (green/red/orange/purple), soft variants (`color-mix(in oklch, <c> 10%, transparent)`), font stacks (display serif / body sans / mono), clamp() type scale, radius, spacing scale, sidebar width.

Typical clean-finance prototype tokens:
```
--bg: #f8f9fb  --surface: #ffffff  --fg: #1a1d23  --muted: #6b7280
--border: #e5e7eb  --accent: #2563eb
--green: #16a34a  --red: #dc2626  --orange: #ea580c  --purple: #7c3aed
display: 'Iowan Old Style'/'Charter'/Georgia serif · body: system sans · meta: mono uppercase
```

### 2. Write docs/DESIGN-SPEC.md in the target repo (single source of truth)
Contents:
- Token table (light values; keep existing dark-mode vars)
- Typography rules: serif display h1, mono uppercase eyebrows/meta, tabular-nums for values
- Layout: sidebar width, active-nav = accent + accent-soft bg + 2px accent left border, radius 8/12px
- Per-screen mapping table: prototype file → target component/route
- "Polish beyond prototype" list: focus rings, hover lifts, no horizontal scroll 360→1920, consistent radius
- **Scope freeze line**: "logic, data fetching, server actions, loading/empty/error states UNTOUCHED — visual classes only"

### 3. Check the reference screenshot
If a PNG ships with the export, vision_analyze it — it may be an older spreadsheet/design version while the HTML files are the real target. The HTML `<style>` blocks are authoritative.

### 4. Dispatch parallel agents on DISJOINT file sets
Split by ownership so no two agents touch the same file:
- Agent 1: foundation — `globals.css` tokens + fonts + `AppShell`/layout/sidebar
- Agent 2: one feature dir (dashboard)
- Agent 3: other feature dirs (investments, transactions)

Each agent gets: spec path, prototype path, project rules (AGENTS.md), and **"run `npx tsc --noEmit` only — do NOT run `npm run build`"**.

### 5. ONE build at the end
Parallel builds on the same project corrupt each other (`.next` lock fights). Agents typecheck; the orchestrator builds once after all report back.

### 6. Track with kanban
Create one task per screen/area before dispatch (`hermes kanban create "..." --assignee orchestrator --project <slug>`), comment each task with which agent covers it. Update on completion.

### 7. Review gate (mandatory)
Check project AGENTS.md for a review requirement (e.g. CashFlow OS mandates ECC `code-reviewer` + `silent-failure-hunter` before merge). Dispatch after the build passes.

## Pitfalls
- **Design tokens in Tailwind v4**: map tokens to CSS variables + `@theme` — don't hardcode hex in components; dark mode must keep working.
- **yaml.dump 80-char wrap** corrupts long MCP URLs in spec-adjacent config work — use `width=999`.
- **Don't add font packages** when the prototype's display stack has a system fallback (Georgia/Charter) — `next/font` or a CSS import with fallback suffices.
- **Prototype HTML may be light-only**; keep existing dark variables intact and make light = prototype look.
- **Agents over-polish logic**: the scope-freeze line in the spec is what stops behavior changes sneaking into a "visual only" restyle.

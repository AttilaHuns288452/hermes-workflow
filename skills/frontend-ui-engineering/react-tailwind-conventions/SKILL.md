---
name: react-tailwind-conventions
description: Use when styling/restyling React UIs with inline Tailwind.
---

# React + Inline Tailwind Conventions (this user)

Use when building or restyling React (Vite + Tailwind v4) UIs — student-profile.app, playgrounds, dashboards. Encodes the user's explicit style corrections.

## Hard rules (user-corrected; do not drift)

1. **Plain utilities ONLY — no arbitrary values.** Never `[...]` values, `clamp()`, custom rgba/hex shadows (`shadow-[0_18px_40px_rgba(...)]`), or arbitrary hex gradients. "Style it simple like no clamp no [] in the styling inline." Use scale classes and accept close-enough:
   | Need | Use |
   |---|---|
   | `text-[clamp(2rem,3.5vw,3rem)]` | `text-4xl lg:text-5xl` |
   | `w-[min(1150px,100%)]` / 1200px container | `w-full max-w-6xl mx-auto` |
   | `rounded-[0.9rem]` | `rounded-xl` |
   | `text-[0.72rem]`, `text-[0.7rem]` | `text-xs` |
   | `tracking-[0.25em]` | `tracking-widest` |
   | `w-[120px] h-[120px]` avatar | `w-32 h-32` |
   | `shadow-[0_18px_40px_rgba(...)]` | `shadow-lg` / `shadow-xl` / `shadow-2xl` |
   | `bg-linear-to-br from-[#f8fbff] to-[#eef4ff]` | `bg-gradient-to-br from-blue-50 to-blue-100` |
   | `font-[Inter,...]` | drop it (preflight default) or `font-sans` |
   | `grid-cols-[repeat(auto-fit,minmax(240px,1fr))]` | `grid-cols-1 sm:grid-cols-2 lg:grid-cols-4` |
2. **Inline Tailwind in JSX only.** No per-component CSS files (App.css, etc.). `index.css` holds only `@import "tailwindcss";`. Body-level styles (font, background gradient, text color) go on the root div as utilities (`min-h-screen flex flex-col ...`); Tailwind preflight handles `margin: 0`.
3. **User-supplied component code is a spec.** When they paste a component verbatim, keep their JSX + class names 1:1. Only rewire data flow: replace local `useState` with parent props (`currentUser`, `onLogout`, `onOpenAuth`) so auth state stays single-sourced in App.jsx. No redesign, no added features. Note (don't silently build) anything their markup implies but the app lacks (e.g. `#hash` links that don't switch views).
4. **Auth-modal pattern**: extract the auth form into a modal component that receives `onClose`, `onRegister`, `onLogin`, `feedback` from App; navbar Login opens it; successful login closes modal + switches view; register success keeps it open with feedback. Overlay: `onClick={onClose}` + inner card `stopPropagation`, `role="dialog" aria-modal="true"`.
5. **Flat design — no AI slop** ("it looks vibecoded... remove ai slop", "no gradients and label with status"). Decorative AI tell-tales are banned unless explicitly requested:
   - No gradients anywhere: no gradient text (`bg-clip-text text-transparent`), no gradient buttons (`bg-gradient-to-r from-blue-600 to-sky-400`), no background gradients — solid tokens (`bg-blue-600 hover:bg-blue-700`).
   - No status badges / eyebrow pills with pulsing dots ("University student portal" + `animate-pulse` dot). No uppercase `tracking-widest` decorative labels as section headers.
   - No glow shadows (`shadow-lg shadow-blue-600/25`), no checkmark feature lists with green circles, no floating decorative cards/panels with `blur-2xl` glows.
   - No `span` where a `div` works ("don't use span use div").
   - Hardcode static values over computing them (school year, date, semester) — "hardcode this".
   - Flat layout: heading + one paragraph + one CTA button + plain info strip (label in small muted caps, value in bold). Verified against this exact pattern.
6. **Bare-minimum simplification ladder** (user pushed: "what's the use of authOpen... can it be simplified further"). When asked to simplify, in order:
   - Merge coupled states: if two states always change together, keep one (`view` + `currentUser` → `currentUser` only; `!currentUser` = landing).
   - Delete named handlers used once → inline arrows (`onLogout={() => setCurrentUser(null)}`). Keep named fn only when used 2+ places.
   - Honest names: `enterStudents` not `handleLogin` when there's no real auth. Comment state roles with `// ponytail:`.
   - Floor for this UX = 1 state (final, user-pushed further: "can authOpen just be removed"): merge the modal flag INTO the page state — one tri-state variable: `null` = landing, `'modal'` = auth modal open, user object = students. Page branch: `{currentUser?.fullName ? <main>…</main> : <LandingPage …/>}`; modal branch: `{currentUser === 'modal' && <AuthModal …/>}`. Every button is one `setCurrentUser(...)` call; no named handlers. **Pitfall:** components that read the state as a user (`Navbar` doing `Boolean(currentUser)` + `currentUser.fullName`) must switch to `Boolean(currentUser?.fullName)` so the `'modal'` sentinel doesn't render as logged-in ("Welcome undefined").
   - Drop validation/feedback/registeredUsers on request; uncontrolled inputs (no value/onChange) when values are unused.

## Dark mode via CSS-var semantic classes (Tailwind v4 @theme)
When a project registers tokens in `@theme` (globals.css: `--color-green: var(--green)`, `--color-green-soft: var(--green-soft)`, ...), use the generated classes directly — NO `dark:` variants, NO palette classes:
- `text-green` / `text-red` / `text-purple` / `text-accent` instead of `text-emerald-600 dark:text-emerald-400`
- soft chip/icon backgrounds: `bg-green-soft` (token = `color-mix(in oklch, var(--green) 10%, transparent)`), chart rings: `stroke-green`
- Dark mode swaps the `--green`/`--red`/`--purple` values in the `.dark` block, so one class covers both themes.
- Before inventing a class, grep globals.css for registered tokens and grep sibling components for the established pattern — a codebase usually has one (e.g. TransactionList already used `text-green`/`bg-green-soft` while DashboardPage was the outlier with palette+`dark:` classes).
- **Recharts accepts CSS-var strings** for fills/strokes: `fill="var(--green)"`, `stroke="var(--purple)"`, pie `COLORS = ["var(--accent)", "var(--green)", ...]` — SVG presentation attributes resolve var() in modern browsers (same mechanism as shadcn charts). Tooltip shadow: `boxShadow: "0 4px 12px color-mix(in oklch, var(--fg) 10%, transparent)"` instead of a hardcoded rgba.
- Frozen design specs may explicitly permit specific arbitrary values (`text-[11px]`, `tracking-[0.06em]` mono eyebrows are part of the CashFlow OS frozen language) — keep the frozen ones; the no-arbitrary rule means don't ADD new ones.

## Verify before reporting done

UI changes get browser-verified, not just built:
1. Start dev server background (`npm run dev`), wait for ready.
2. `agent-browser open http://localhost:5173`
3. `agent-browser click "nav button"` — **selectors are CSS-only; `:has-text()` fails with "Element not found"**. Use `nav button`, `form button[type=submit]`, `#username`.
4. `agent-browser screenshot /tmp/x.png` — positional path, no `--path`.
5. `vision_analyze` each screenshot (modal visible? login succeeded? view switched?). Deepseek chat model → vision_analyze routes to MiMo automatically.
6. Kill dev server process. Compile-check alone (`curl` transformed modules for 200) only proves no syntax errors.

## Pitfalls
- Fresh "not functioning" reports after a verified build are usually a stale dev server / browser cache — restart `npm run dev` and re-verify before touching code.
- **Orphaned servers serve OLD code.** A "killed" dev server's vite child can survive on the same port and serve a previous build — this was the true root cause of a "not functioning" report (phantom logged-in state). Diagnose: `netstat -ano | grep -E "517[3-5]" | grep LISTEN` (more than one listener = orphans), and confirm what's actually served with `curl -s http://localhost:5173/src/App.jsx | grep -c "<marker-from-new-code>"` (0 matches = stale server). Fix: `taskkill /PID <pid> /F` (SINGLE slash — `//PID` fails with "Invalid argument/option" in git-bash). Repeat kills left ports 5173/5174/5175 occupied this session.
- **agent-browser `open` does NOT reload an existing tab** — React state persists across `open` calls, so a tab from a previous test can show a stale logged-in state that looks like a bug. Force a real reload with `agent-browser press "Control+r"` before screenshotting, or navigate to a different port/URL.
- Old code style (from `.css`-file era) may reference dead classes (`.hero-panel` etc.) never used in JSX — they die with the CSS file, don't port them.
- Tailwind v4: `bg-gradient-to-*` legacy aliases still work; `bg-linear-to-*` is the v4 name. Both fine — but gradients with arbitrary hex are not (rule 1).

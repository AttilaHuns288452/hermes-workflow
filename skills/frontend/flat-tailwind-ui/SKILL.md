---
name: flat-tailwind-ui
description: Flat Tailwind UI — standard utilities only, no AI slop.
---

# Flat Minimal Tailwind UI (Attila's style)

Hard rules from repeated user corrections. Violating these gets "this looks vibecoded / AI slop" feedback.

## Style rules (non-negotiable)

1. **Standard Tailwind utilities only.** NO arbitrary values: no `text-[0.95rem]`, no `w-[120px]`, no `grid-cols-[...]`, no `shadow-[...]`, no `[clamp(...)]`, no `tracking-[0.28em]`. Use the default scale: `text-sm`, `w-32`, `grid-cols-4`, `shadow-lg`, `text-4xl lg:text-5xl`, `tracking-widest`.
2. **NO gradients.** No `bg-gradient-to-*`, no `bg-clip-text text-transparent` headline spans, no `bg-linear-to-br`. Flat colors: `bg-blue-50`, `bg-white`, `bg-slate-900`.
3. **NO badges/pills/status labels.** No eyebrow pills, no pulsing dots (`animate-pulse`), no uppercase `tracking-widest` kicker labels, no `Active` status chips, no checkmark feature lists. This is the "AI slop" he rejects by name.
4. **No glow shadows.** No `shadow-blue-600/25` colored shadows. Plain `shadow-sm`/`shadow-lg` at most.
5. **divs, not spans.** Use `<div>` for layout/label elements. He explicitly requested zero `<span>` on the landing page.
6. **Flat and quiet.** Rounded corners OK (`rounded-xl`, `rounded-full` buttons), single blue accent (`blue-600`), slate text colors. Boring bulletin board, not SaaS landing template.

## Logic rules

- **Strip to the minimum.** No validation, no auth, no stored users unless asked ("no validation like pure showing of pages").
- **One state = whole app** pattern he converged on:
  ```jsx
  const [page, setPage] = useState('landing')  // 'landing' | 'modal' | 'students'
  {page === 'students' ? <cards/> : <LandingPage/>}
  {page === 'modal' && <AuthModal onDone={() => setPage('students')} />}
  ```
  Every button is just `setPage(...)`. No named handlers when an inline arrow fits.
- **He supplies component code as spec** (e.g. navbar). Keep his JSX/markup 1:1; only rewire props to the app's state flow. Do NOT restructure his components.

## Verification (always after UI changes)

1. `npm run build` must pass.
2. **Stale-server trap:** on Windows, killed background dev servers leave orphaned `node` vite children on old ports serving OLD code — browser tests against them show phantom states. Before screenshotting: `netstat -ano | grep -E "517[3-5]" | grep LISTEN`, taskkill leftovers (`taskkill /PID <pid> /F`), and confirm served source is current: `curl -s http://localhost:<port>/src/App.jsx | grep -c "<marker>"`. See `references/vite-orphan-stale-server.md`.
3. agent-browser quirks: CSS-only selectors (no `:has-text()`), `open` does NOT reload the tab — use `press "Control+r"` for a fresh state; click `nav button` / `form button[type=submit]`.
4. Screenshot + vision_analyze the flow: landing → modal → submit → cards. Never report "done" on build alone.

## References

- `references/vite-orphan-stale-server.md` — Windows orphaned vite dev servers: symptoms, served-source check, cleanup.

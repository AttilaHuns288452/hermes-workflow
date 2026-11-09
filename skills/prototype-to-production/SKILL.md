---
name: prototype-to-production
description: Use when making a prototype's demo data and auth real.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [web-development, react, supabase, vercel, data-integrity, auth, mock-to-real, qa]
    related_skills: [production-audit, vercel-deployment, supabase, webapp-release-qa]
---

# Prototype → Production Data Integrity

A prototype ships with fabricated surfaces: demo logins that invent a user, seeded history, fake analytics, hard-coded product arrays, mock clients. Production must replace every one with a real source and fail HONESTLY when that source is unavailable. The governing rule: **never present fabricated, simulated, or seeded data as real.** A stale real value, or an honest empty/error state, beats a plausible fake every time.

## When to use
- Porting a UI prototype to real auth (Supabase/Firebase/etc.), a real API, or a real database.
- The user says "remove the demo/fake/seeded data", "use real data", "wire it to the backend", "make it real", or "it should not show made-up users/products".
- Auditing a just-ported app for leftover mock data before calling it done.

## Procedure
1. **Inventory every fabricated surface before editing:** mock clients, demo-auth fallbacks, seeded arrays/histories, hard-coded ids, invented stats. Grep for tell-tale markers (demo/mock/seed/fake/placeholder, invented person names, default `currentUser`, hard-coded product ids).
2. **Replace auth first** — it gates everything. Delete any demo/dev fallback that fabricates a logged-in identity from arbitrary credentials. If the real provider is unconfigured, sign-in must fail visibly; never synthesize a session.
3. **Wire real data + persistence through ONE seam** (a store/api module), not scattered fetches per component.
4. **Isolate test fixtures from the production bundle.** Fixture data used by unit tests/checks lives in a test-only module imported only by tests — never in a shared data file production also imports.
5. **Honest states everywhere:** real loading, empty, and error states. On API failure show an error; never fall back to a fixture.
6. **Prove nothing fake remains in the SHIPPED bundle:** grep the built output (not just src/) for fixture names/ids/markers. Then exercise the real flows end-to-end.

## Pitfalls
- **A demo-auth fallback that invents a user from any email/password** is the worst offender — the app looks "logged in" with zero real auth. Delete it; make unconfigured auth a visible error.
- **Seeded history/wishlist/reviews shown as the user's own** — a fresh account must start empty. Remove the seeding; render an empty state.
- **Fabricated analytics** (invented "top viewed", "weekly views", user counts) — compute from real data or omit. Never display a made-up metric.
- **Test fixtures leak into the production bundle** when they share a module with production code. Move them to a test-only import, then grep the built bundle for a fixture marker (an invented name/id) to prove they're gone.
- **`if (!data) return null` on a hero/header makes the whole section vanish** when data is empty or failed. Render the shell (headline, CTA) and degrade gracefully; only the data-bound part disappears.
- **A successful create/update that doesn't refresh the list** leaves the UI stale until reload. Refetch (or append) after the mutation resolves.
- **A CRUD control that toasts success but never persists** (Save/Delete/Edit mutates only frontend state) is fake CRUD — the UI lies about the write. Before shipping any management screen, confirm every mutation writes through the real persistence seam; a "deleted" toast with no backend call is the tell. If a surface has no real backend yet, make it read-only rather than shipping controls that don't stick.
- **Sentinel values for missing data (e.g. brand "Unknown") leak into derived UI** — filters, tags, and counts treat the sentinel as a real category. Filter it at every derivation point, not just the display.
- **The build won't catch a missing import in a rewritten component** — an undefined helper / `supabase` / `useEffect` compiles under Vite but crashes at runtime. After rewriting a component body, verify every referenced symbol is imported.
- **QA with fresh browser contexts bypasses the app's client-side cache**, so each run re-fetches from a quota-limited API and can exhaust the key. Test real-data integrations against fixtures/captured responses; use a small, controlled number of live calls and re-use cached results.
- **Loose substring/NaN checks false-positive on real data** (a real brand like "NANATECH" matches /NaN/i). Assert on structure, not loose substrings.

## See also
- `production-audit` (pre-launch readiness lens)
- `vercel-deployment`, `productivity/supabase` (the deploy + DB wiring this usually pairs with)
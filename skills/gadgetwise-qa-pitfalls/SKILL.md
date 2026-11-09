---
name: gadgetwise-qa-pitfalls
description: Use when Playwright-QA testing the GadgetWise React app.
---

# GadgetWise QA Pitfalls

GadgetWise is a HashRouter SPA on Vercel (`gadgetwise-react.vercel.app`) with a live Lazada marketplace backend (TMAPI via RapidAPI).

## HashRouter URLs
- Routes live in the HASH: `/#/login`, `/#/g/{id}`, `/#/admin`, `/#/u/{userId}`.
- Put cache-bust in the QUERY, never the hash: `https://host/?cb=123#/g/lazada-396958608`.
- WRONG: `/#/g/lazada-123&cb=1` (the `&cb=` pollutes the route param -> product reads "not found").

## Reviews live under the Reviews tab
- Product detail default tab = "Ownership Cost". The review list + "Write Review" trigger live under the **"Reviews (N)"** tab (`tab === "reviews"`, GadgetDetail.jsx). Inactive tab panels are UNMOUNTED — assert review cards only after clicking the tab. The tab's own label "Reviews (N)" is visible without clicking and is the cheapest live-count assert; it updates immediately after a successful post.
- Selector strings (one file, three labels): trigger button = **"Write Review"**, modal title = **"Write a review"**, submit = **"Post review"**. `name: /write a review/i` matches the modal title, not the trigger; the Reviews-tab button carries `role="tab"`-style naming so `getByRole('button', …)` can miss it — use `locator('button', { hasText: 'Reviews (' })`.
- Rating-only reviews are valid: the text body is optional (modal helper: "A rating on its own is fine. Words are optional."); a star-only review stores a null body and renders without one.
- Reviews AUTO-APPROVE on insert — there is no moderation queue for new reviews (admin Reviews tab handles later moderation actions only). Any copy claiming moderation is stale by default.
- Reviewer display name resolves LIVE from `public_profiles` on every load (no name snapshot on the review row). Valid E2E: rename the account display name, reload, assert the review card shows the new name; reviewer name links `#/u/{id}` public profile.
- On success the client refreshes the review list in-place — no reload needed to see your own review or the updated count.

## Live API rate limit
- Provider quota is per RapidAPI key (~50 requests/month on the basic tier). The app runs a failover pool (`LAZADA_API_KEYS` env, admin-configured DB key first) that switches keys only on 429/401/403, so budget QA requests across ~4 keys and prefer cached responses.
- Heavy QA exhausts a key: catalog shows "Couldn't load live products", detail shows a retry. This is an HONEST error state (no fake fallback) — do NOT treat it as a code bug. Verify product/review flows BEFORE burning quota on many requests.
- Feature E2E (reviews, profile, wishlist, compare) must target CATALOG gadgets (ids without `lazada-`), which render from local data. Marketplace detail (`lazada-*`) falls to "Could not load this listing" + a lone "Try again" button when the lookup is down or quota-exhausted, failing every feature assert for reasons unrelated to the feature.
- Product detail field for price is `image` (not `img`); product id in API = `productId`; toGadget sets `id = "lazada-{productId}"`.

## Admin console (real ops only)
- Admin tabs: Dashboard, Reports, Gadgets (READ-ONLY), Categories (READ-ONLY), Reviews (real moderation: status/edit/delete persist to Supabase), Users (real list).
- Marketplace listings are upstream-read-only; categories are structural config. No Add/Edit/Delete on Gadgets/Categories (fake CRUD was removed 2026-10-23).

## Live API + probe pitfalls
- Cache-bust correctly: URLs WITHOUT a query need `?cb=N`, URLs WITH a query need `&cb=N`. Appending `?cb` after an existing query corrupts the last param (e.g. `marketplace=ph?cb=1` -> 400 "invalid marketplace") and produces false failures.
- Lazada upstream `item_detail` answers 417 "Get item detail error" TRANSIENTLY: the same item_id returned 417 twice then 200 later. Never map 417 to "listing gone"/404; the app maps it to a retryable 502 `product_lookup_failed`.
- The catalog needs ~3s (6 category fetches) on a cold load; pages render an honest "Loading products…" card meanwhile. Assert cards only AFTER they appear, not at a fixed early sleep.
- Admin deep-link/reload: the route guard waits for session `ready` + the async `is_admin()` RPC (`adminChecked`) before rendering or redirecting. Test with `page.reload()` on /#/admin — an immediate click races the check.
- With real catalog data the Pareto chart (min-w 560px) and frontier list must stay inside their card; assert `document.documentElement.scrollWidth` AFTER data loads, not before.
- Product rows created during admin tests must be deleted through the Admin UI; review deletion opens a confirm Modal (click `[role="dialog"]`'s Delete), product deletion is immediate.

## Long-content / overflow traps (found 2026-10-23, live site)
- **Raw query echo overflows the page.** The catalog results line renders `matching “{q}”` (`src/pages/Catalog.jsx`, class `mt-3 text-sm text-ink3`) and LiveSearch renders `Searching Lazada for “{q}”` / `No live listings found for “{q}”` (`src/components/LiveSearch.jsx`, class `mt-3 text-sm text-ink2`). Neither has `overflow-wrap`, so a 200-char query or a long unbroken token makes `document.documentElement.scrollWidth` exceed the viewport and the page really scrolls sideways. Assert `scrollWidth` AND `window.scrollX` after a long query.
- **Catalog card titles clip mid-word.** The model link is `a.block.min-h-[2.75rem]` inside `article.card` (`overflow-hidden`, no `overflow-wrap`). Long Lazada model names get sliced at the card edge with no ellipsis — e.g. `…/11/12p`. Detect with Range `getClientRects()` vs the `<a>` box, not `scrollWidth` alone (the `<a>` can also wrap normally).
- **`main` creates a stacking context.** `main.flex-1` has `animation: fade-in ... both` (`.anim-fade-in` is applied via a page-level class), so any `position:fixed` toast rendered INSIDE `main` is trapped below a modal overlay even at `z-index:100` vs the overlay's `z-[90]`. A modal's toast dismiss button becomes unclickable.
- **Toasts are rendered per card.** `GadgetCard` calls `useToast()` itself, so the catalog mounts one `role="status" aria-live="polite"` host PER CARD (240 on /gadgets) instead of one app-level host.
- **Guest wishlist click shows a false success toast.** The toast fires before/independently of `requireAuth()`; the item is NOT added (aria-pressed stays false) but the toast says "Added to wishlist" while the sign-in modal opens.
- **`Modal` has no focus trap.** Despite `aria-modal="true"`, Tab leaves the dialog on the first press; focus stays on the trigger behind the overlay.

## Misc
- QA Chromium must set `TZ=Asia/Manila` for date-key asserts.
- Playwright from `~/.hermes/hermes-agent/node_modules/playwright` (system node, no venv).
- innerText misses input VALUES and reads text-transform-uppercased text; assert with /i regex.
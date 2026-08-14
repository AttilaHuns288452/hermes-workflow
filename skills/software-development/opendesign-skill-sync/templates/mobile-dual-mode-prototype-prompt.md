# Mobile dual-mode prototype prompt (known-good, 2026-08-09)

Copy and adapt for ANY customer/admin (or customer/staff) mobile prototype generated via
OpenDesign `start_run` OR the opencode-CLI fallback (`OPENCODE_SLIM_PRESET=flash-only`).
Delivered twice successfully: "Kape & Toasted" coffee shop, "SMILEWORKS" dental clinic.

## Structure rules that worked

1. **Modes**: prominent segmented toggle (Customer | Admin) in the sticky header.
2. **Mobile-first**: 375px base, single column; bottom nav bar for BOTH modes
   (top tabs on mobile = bad nav — user-flagged; always bottom nav, top bar only ≥640px).
3. **Single self-contained `index.html`**: inline CSS + JS, zero external deps (offline-capable).
4. **Seed realistic mock data in JS** (local business theme, ₱ prices, Filipino names).
5. **localStorage persistence** for cart/orders/appointments/status edits + a "Reset demo" button.
6. **Design tokens**: light theme, ONE accent (#5e6ad2 periwinkle for this user), flat styling
   (no gradients/pills clutter), rounded cards, inline SVG icons, 44px touch targets, a11y
   (aria-current, focus states, semantic HTML).
7. **Customer mode**: browse → detail → book/buy → confirm (with ref number) → my-account history.
8. **Admin mode**: dashboard (stat cards + pure-CSS/SVG chart + recent list) → records list with
   search/filter + status dropdown persisting → CRUD for the entity → customers/patients list.
9. Explicitly state both modes' bottom-nav items (4-5 each) — prevents the generator from
   inventing a top tab bar for admin.

## Prompt skeleton (fill the bracketed parts)

```
Create a mobile-first responsive website prototype for a [BUSINESS TYPE]
with TWO switchable modes for testing: CUSTOMER and ADMIN. A prominent mode toggle
lives in the top header (segmented control: Customer | Admin). Base layout targets
375px mobile (single column), scales up to tablet/desktop.

CUSTOMER MODE: [home/hero, browse/filter list, detail with options, cart-or-booking flow,
confirmation with ref number (PREFIX-YYYY-XXXX), account with history + status badges]

ADMIN MODE: [dashboard with N stat cards + weekly chart (pure CSS/SVG) + recent items,
records list (search, filter chips, expandable rows, status dropdown that persists),
CRUD with add/edit modal, secondary list]

Use realistic [LOCAL] mock data pre-seeded in JS. Persist everything in localStorage.
"Reset demo" button in the header. BOTH modes get a bottom navigation bar on mobile
with 4-5 icons ([customer items]; [admin items]); on desktop the nav becomes a top bar.
Design: clean modern light theme, one accent (#5e6ad2 periwinkle), flat simple styling
(no gradients, no pills), rounded cards, inline SVG icons. All in ONE self-contained
index.html (inline CSS + JS, zero external dependencies, works offline). Accessible:
semantic HTML, visible focus states, touch targets >= 44px.
```

Full reference prompt: `~/AppData/Local/hermes/scripts/od-prompt.txt` (shop) and
`od-prompt-dental.txt` (dental) — both validated end-to-end this session.

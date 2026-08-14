# Marketing Site: Landing + Feedback (built 2026-08-04)

Landing = `src/app/page.tsx` composing 12 sections from `src/components/marketing/landing/` (Reveal, Hero, SocialProof, Problem, Solution, Features, Showcase, AIAssistant, BusinessMode, Comparison, Testimonials, FAQ, FinalCTA). Feedback = `src/app/feedback/page.tsx` + `src/components/marketing/FeedbackForm.tsx`. Nav/footer = `src/components/marketing/MarketingNav.tsx` / `MarketingFooter.tsx` (links array at top of MarketingNav).

## Design system (Linear-inspired, per `opendesign/od-linear-app`)

- bg `#08090a`, panels `#0f1011`, elevated `#191a1b`; text `#f7f8f8` / `#d0d6e0` / `#8a8f98` / `#62666d` (faint, large-only); accent `#5e6ad2` (CTA bg) / `#7170ff` (links) / `#828fff` (hover); success `#27a644`; borders `rgba(255,255,255,0.05–0.08)`; cards `rgba(255,255,255,0.02–0.04)`; radius 6px buttons / 8px cards / 12px panels. No shadows for elevation — luminance stepping only. Display headlines: weight 500–590, NEGATIVE letter-spacing (-1.5px @72px, -1.05px @48px, -0.7px @32px). Mono eyebrows 11px uppercase tracked. Max weight 590.
- Landing page styles live in one `<style>{landingCss}</style>` block in `page.tsx` (`.lp-root`, `.lp-container`, `.lp-eyebrow`, `.lp-card`, `.lp-btn`, `.lp-reveal`, `.lp-fade-up`, orb keyframes) — the app's globals.css is the LIGHT app theme, untouched.

## Motion (zero deps, hand-rolled)

- `Reveal.tsx` ('use client'): IntersectionObserver threshold 0.15 fires once → `.is-in`; CSS transition opacity 0→1 + translateY(16px)→0, 600ms; stagger via `style={{ transitionDelay: i*60ms }}`.
- Hero `lp-fade-up` CSS animation with per-element `animationDelay` (80ms…1s).
- **no-JS fallback is mandatory (Firefox ignores `@media (scripting: none)`):** page.tsx renders `<noscript><style>{.lp-reveal{opacity:1;transform:none}.lp-fade-up,.lp-orb,.lp-eye,.lp-dot-pulse{animation:none!important}}</style></noscript>` + the media query + `@media (prefers-reduced-motion: reduce)` kill-block.
- Screenshot verification gotcha: agent-browser `screenshot --full` right after `open` captures BEFORE reveals fire → black middle. Correct sequence: `open` → `wait 2000` → `scroll down 1200` × 5-6 (triggers observers) → `eval "window.scrollTo(0,0)"` → `wait 800` → `screenshot --full out.png`. `screenshot` takes NO `--width/--height` flags; passing them creates a stray file named `--width` (remove: `git rm --cached -- --width`).

## Review-driven a11y/copy rules (from the ECC pass)

- Contrast: `#62666d` on `#08090a` ≈ 3.4:1 — FAILS AA for small text. Use `#8a8f98` (6.2:1) everywhere small. (sed: `s/#62666d/#8a8f98/g` across landing + nav/footer.)
- FAQ: closed answers need `aria-hidden={!open}` + `inert={!open}` on the animated wrapper (grid-rows 0fr→1fr is visual-only; SRs otherwise read all answers).
- Showcase tabs: `role=tablist` (aria-label) / `role=tab` + `aria-selected` + `aria-controls` / `role=tabpanel` with matching id.
- Decorative SVGs (`<svg>` sparklines/polylines): `aria-hidden="true"`. Lucide icons are auto-hidden.
- Hamburger: `aria-expanded={open}` + `aria-controls="mobile-menu"` on the button, id on the menu div.
- Testimonials: currently placeholder quotes (Miguel R., Alyssa T., Reyes family) — flagged with a ponytail comment; swap for real `feedback` table rows (kind='testimonial', approved=true) before Product Hunt.
- Copy honesty: BYOK strip says "bring-your-own-key is on the way; built-in provider works now" — do NOT claim features that don't exist yet.

## Feedback form (insert-only RLS pattern)

- `feedback` table (migration 014): id, name, email, role, kind (`testimonial|feature|bug|general`), message, approved BOOL default false, created_at. RLS: ONE policy `"public submit feedback" ON feedback FOR INSERT WITH CHECK (true)` — no SELECT/UPDATE/DELETE policies, so the API is write-only; owner reads via SQL Editor and flips `approved`.
- Client: `createClient()` from `@/lib/supabase/client` (browser anon key) → `supabase.from('feedback').insert({...})`. Kind selector toggles a "What do you do?" role field for testimonials. Success state replaces the form; inline error on failure; submitting guard.
- Verify: `curl -X POST $URL/rest/v1/feedback -H "apikey: $KEY" -d '{...}'` → 201. Then `DELETE FROM feedback WHERE name='probe'` (owner-side; insert-only RLS means the app itself can't delete).

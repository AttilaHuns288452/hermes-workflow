# Premium Audit Checklist — 12-Point Site Evaluation

Use when auditing an EXISTING site for premium feel. Run this before proposing changes — it produces a concrete punch list, not vague "make it nicer" advice.

## How to Run

1. Load `high-end-visual-design` + `baseline-ui` skills
2. Read the target site's HTML/CSS
3. Check each item below — mark PASS or VIOLATION with the specific line/CSS rule
4. Output a table: # | What's Wrong | Which Skill Flags It | Fix
5. Group fixes into tiers: Quick wins (CSS only) → Structural (HTML+CSS) → Polish

## Tier 1 — Quick Wins (CSS only)

| # | Check | Fail Condition | Fix |
|---|-------|---------------|-----|
| 1 | Font | Inter, Roboto, Arial, Open Sans, Helvetica | Swap to Geist. Google Fonts link + `--font` var |
| 2 | Reduced motion | No `@media(prefers-reduced-motion:reduce)` | Add blanket override for all animations/transitions |
| 3 | Text wrapping | No `text-wrap` on headings/body | `text-wrap:balance` on h1-h3, `text-wrap:pretty` on paragraphs |
| 4 | Viewport height | `min-height:Nvh` or `height:100vh` | Change to `dvh` units (prevents iOS Safari jump) |
| 5 | Transition timing | `ease`, `ease-in-out`, `linear` in CSS | Replace with `cubic-bezier(0.32,0.72,0,1)`. Preserve `ease-out` in keyframes |
| 6 | Section padding | `< 6rem (96px)` desktop | Bump to `6rem` desktop, keep `2rem` mobile |

## Tier 2 — Structural (HTML+CSS)

| # | Check | Fail Condition | Fix |
|---|-------|---------------|-----|
| 7 | Nav style | Edge-to-edge sticky `position:sticky;top:0` | Floating pill: `position:fixed;top:1rem;left:50%;transform:translateX(-50%);border-radius:100px;max-width:calc(100% - 2rem)` |
| 8 | Card depth | Flat — single border, no inset shadow | Double-bezel via `box-shadow:inset 0 1px 1px rgba(255,255,255,.04)` (no HTML change) |
| 9 | CTA buttons | Arrow `→` naked next to text | Button-in-button: `<span class="btn-icon">` wrapper, `width:24px;height:24px;border-radius:50%;background:rgba(255,255,255,.15)` |
| 10 | Mobile nav | Links just toggle `display:flex` | Staggered reveal: `navItemIn` keyframe + `nth-child(N)` delays at 50ms increments |
| 11 | Gradient text | Multicolor (3+ hue) gradient on text | Single-hue or solid. Keep gradients only on structural elements (progress bars, dividers) |

## Tier 3 — Polish

| # | Check | Fail Condition | Fix |
|---|-------|---------------|-----|
| 12a | Button hover | Only color/bg change | Magnetic: `scale(1.02)` hover, `scale(.98)` active, inner icon `translate(2px,-1px) scale(1.05)` |
| 12b | Eyebrow tags | Plain text or missing | Pill: `display:inline-block;padding:.2rem .6rem;border-radius:100px;background:rgba(accent,.08);border:1px solid rgba(accent,.15)` |
| 12c | Glow affordances | `box-shadow:0 0 0 1px rgba(color,.1)` or mousemove radial gradient | Replace with elevation: `box-shadow:0 12px 40px rgba(0,0,0,.15)` + `translateY(-3px)`. Remove mousemove JS |

## Delegation Pattern

For large sites (1000+ lines), delegate the implementation to a subagent:
- Write the punch list as the `context` field with exact find-replace pairs
- Be specific: "replace THIS exact CSS rule with THAT exact CSS rule"
- **Pitfall:** subagents time out at 600s. For 12+ fixes, split into 2 delegations or handle the last few yourself
- **Verify after delegation:** `grep -c` each pattern to confirm the subagent actually changed what it claimed

## Verification Commands

```bash
grep -c "ease-in-out" index.html        # should be 0
grep -c "cubic-bezier(0.32" index.html  # should be > 5
grep -c "prefers-reduced-motion" index.html  # should be 1
grep -c "text-wrap:balance" index.html  # should be > 3
grep -c "dvh" index.html               # should be 1+
grep -c "inset 0 1px" index.html       # should be > 3 (double-bezel)
grep -c "btn-icon" index.html          # should be > 0 (button-in-button)
grep -c "navItemIn" index.html         # should be > 0 (staggered nav)
```

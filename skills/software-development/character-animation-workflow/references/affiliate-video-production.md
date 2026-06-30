# Affiliate Video Production — GTA-Style Product Promotion

## Overview

Affiliate product videos use the same character-animation pipeline but for **product promotion** rather than story/explainer. The character acts as a presenter/endorser, and the scene centers on a product card + pricing + CTA.

**Pipeline:** `character-animation` (same as finance education videos)  
**Format:** 15–30s TikTok/Shorts — hook → product → price → CTA  
**Style:** GTA game HUD repurposed for product stats (Energy bar, Strength bar, Savings counter)  

## Template Structure

### Layout Zones

```
┌──────────────────────────────────────────┐
│  HUD TOP BAR: stat bars, branding logo   │  Top 80px
│  STAT NAME    ████████░░░  +XX%          │
├──────────────────────────────────────────┤
│                                          │
│         ALERTS (stock, sold, etc.)       │  Align left
│                                          │
│    ┌────────────────────────────┐        │
│    │     ★ BADGE ★              │        │
│    │                            │        │  Center 380px
│    │     [PRODUCT IMAGE]        │        │  wide card
│    │                            │        │
│    │   PRODUCT NAME             │        │
│    │   ~~₱OLD~~  ₱NEW  -XX%    │        │
│    │                            │        │
│    │  TAG1  TAG2  TAG3  TAG4   │        │
│    └────────────────────────────┘        │
│                                          │
│                                          │
│    ┌─────────────────────────┐           │
│    │  🛒 SHOP NOW → PLATFORM │  ← pulsing│
│    └─────────────────────────┘           │
└──────────────────────────────────────────┘
```

### Key Components

1. **HUD Stats** — Repurpose stat bars for product-specific metrics:
   - `ENERGY` bar → product efficacy
   - `STRENGTH` bar → user satisfaction
   - `RECOVERY` bar → review rating
   - Show positive deltas (+17%, +20%) to create urgency

2. **Product Card** — Centered, gold-accented panel with:
   - Best-seller badge (top center)
   - Product image (180×180, drop-shadowed)
   - Product name + sub-name
   - Pricing: old price (strikethrough) + new price (green) + discount badge
   - Benefits tags (4 tags max, staggered animation)
   - Spec line (weight, servings, flavor)

3. **Alerts** — GTA-style floating text on the left side:
   - Sold count ("2.3K SOLD")
   - Shipping info ("FREE SHIPPING")
   - Urgency signal ("LIMITED STOCK")

4. **Savings Counter** — Top-right, like GTA money display:
   - Shows "SAVE" label + savings amount in green

5. **CTA Button** — Bottom center, pulsing animation:
   - "🛒 SHOP NOW → [PLATFORM NAME]"
   - Gold gradient, white border, shadow glow
   - `pulse` CSS animation (1.5s ease-in-out infinite)

6. **Brand Logo** — Top-right minimap area:
   - Product brand name in large bold text
   - Sub-brand in smaller text below

## Animation Sequence (GSAP Timeline)

| Time | Event | Animation |
|------|-------|-----------|
| 0–1s | HUD fills | Stat bars animate from 0% to target width |
| 1–3s | Notification | Notification box slides in from right |
| 3–4s | Product card | Pops in with `back.out(1.7)` easing |
| 5–8s | Benefits | Tags stagger in from right, 0.15s apart |
| 9–10s | Savings pulse | Savings counter scales 1.2x → 1x → 1.2x |
| 10–15s | Hold + CTA | CTA button pulses continuously |

## Character Integration

Choose the character that best matches the product:

| Product Type | Best Character | Reason |
|-------------|---------------|--------|
| Fitness / supplements | **Bogart Bugs** (risk-taker/energy) | Gym bro energy, purple aesthetic fits fitness |
| Finance / investing | **Kuya Piso** (the host) | Trusted authority, neutral endorser |
| Shopping / lifestyle | **Gardo Gastos** (spender) | The "deserve ko 'to" impulse buyer |
| Savings / tools | **Ian Ipon** (saver) | Practical, analytical |
| Luxury / high-end | **Boss Bilyon** (success) | Status symbol, aspirational |
| Small business / local | **Ate Tindera** (hustler) | Sari-sari store, community trust |

For the video, the character can appear either:
- **Full-body on the left** as a presenter (pointing at product card)
- **As a floating bust in the corner** reacting (raise eyebrow, nod, smile)
- **Off-screen** — character not visible, only voiceover + product card

The simplest approach for fast production: **product card + HUD only, no character on screen**. The character brand speaks through the channel identity.

## Pricing Display Format

```
price-old: strikethrough gray (₱699)
price-new: bright green with text-shadow glow (₱374)
price-badge: red pill with white text (-46%)
```

- Always show the discount percentage
- Show the absolute savings amount separately in the HUD savings counter
- Use Philippine Peso (₱) for local relevance
- Keep prices accurate — verify from the source product page

## Affiliate CTA Patterns

| Platform | CTA Text | Notes |
|----------|----------|-------|
| Lazada | `🛒 SHOP NOW → LAZADA` | Lazada affiliate program |
| Shopee | `🛒 SHOP NOW → SHOPEE` | Shopee affiliate program |
| Amazon | `🛒 CHECK AMAZON PRICE` | Amazon Associates |
| Generic | `🔗 LINK IN DESCRIPTION` | Works for any platform |

The CTA button uses a pulsing gold gradient — it's the only element with continuous animation after the initial sequence ends.

## Legal Requirement: Affiliate Disclosure

- **Placement**: In video description, NOT inside the video itself (keeps the video clean for TikTok's algorithm)
- **Text**: `"Disclaimer: This video contains affiliate links. I may earn a commission at no extra cost to you."`
- **TikTok**: Add `#ad` or `#affiliate` in caption
- **YouTube**: Check "Contains paid promotion" in advanced settings

On-screen text like "AFFILIATE" or "SPONSORED" is not required for TikTok/Shorts in the Philippines but is good practice. Add a small `AFFILIATE` tag in the corner if you want to be extra transparent.

## Character Verification Pitfall

After generating batch character SVGs, verify with vision_analyze. A known trap: the vision model may **misidentify body contours as accessories**. For example, a character's neckline/collar was read as "wire-rimmed glasses" because the dark stroke around the neck was positioned near the face.

**Fix**: Before accepting a vision_analyze reading, check the actual SVG source to confirm accessories. If a character is described as having something they shouldn't (glasses, hat, prop), the silhouette needs more differentiation — adjust body color, skin tone, or clothing outline width.

## Verification Checklist

- [ ] Product pricing is accurate (check source page)
- [ ] Discount percentage matches (new vs old price)
- [ ] Affiliate link works and is in description
- [ ] Disclosure is present in description
- [ ] Video length is 15–30s (TikTok/Shorts sweet spot)
- [ ] HUD bars animate correctly
- [ ] Product card animates without clipping
- [ ] CTA button pulses and is readable
- [ ] No character accessories misidentified in visual QA
- [ ] ffprobe confirms 720p+, 30fps, H.264

## Production Cost

- **~15 min per video** (template reuse)
- **$0.00 API cost** (all SVG + HTML, no external calls)
- **~451KB MP4** (15s, 720p, good for mobile upload)

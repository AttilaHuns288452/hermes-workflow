# Character Cast Production — Batch SVG Characters for Faceless Channels

## Alternative: Single Mascot

This document covers batch multi-character production. For a **single recurring mascot** (one character = channel face), see `references/single-mascot-design.md` instead. The single-mascot approach uses the same body skeleton but emphasizes premium aesthetics, signature items, and channel-name alignment over cast variety.

## Strategy

For a faceless YouTube/TikTok channel with recurring characters, **batch-produce all characters upfront** from a single body skeleton. This enables:

- **~15-20 min per video** (just swap colors + pick character)
- **Consistent visual identity** across all content
- **Scaling to 6+ characters** without redoing rig work
- **Programmatic SVG generation** from a JSON definition file

## Cast Design Principles

### The 6 Archetypes for a Pinoy Finance Channel

| Archetype | Character | Vibe | Color |
|-----------|-----------|------|-------|
| **The Host** (narrator) | Kuya Piso | Wise tropa, explains both sides | Orange hoodie + cap |
| **The Spender** (liability) | Gardo Gastos | Impulse buyer, "deserve ko 'to" | Red jersey + chain |
| **The Builder** (asset) | Ian Ipon | Saver/investor, "investment yan" | Green polo + glasses |
| **The Goal** (success) | Boss Bilyon | Already rich, calm | Gold barong + watch |
| **The Hustler** (micro-entrepreneur) | Ate Tindera | Sari-sari store, daily grind | Orange dress + apron |
| **The Risk-Taker** (gambler) | Bogart Bugs | Crypto, sugal, "100x sureball" | Purple hoodie + beanie |

### Differentiation Strategy (without rebuilding the rig)

1. **Body color** — change `body_color` per character
2. **Skin tone** — vary skin color for visual diversity
3. **Clothing type** — hoodie vs jersey vs polo vs barong vs dress
4. **Headwear** — cap vs beanie vs headscarf vs none vs shades
5. **Props** — credit card, calculator, money stack, dice, etc.
6. **Eyebrow shape** — raised/cocked/determined/relaxed per personality
7. **Mouth shape** — warm smile vs smug grin vs determined line vs manic grin

## Programmatic SVG Generation

### Pattern: JSON Definition → Python Generator → SVG Files

```
characters/
  cast_definitions.json     # All character data in one file
  gen_svgs.py               # Single script generates all SVGs
  kuya_piso.svg             # Output (one per character)
  gardo_gastos.svg
  ian_ipon.svg
  ...
```

### `cast_definitions.json` Structure

```json
{
  "character_id": {
    "name": "Display Name",
    "role": "Description of archetype",
    "skin": "#hex",
    "body_color": "#hex",
    "clothes": "string for template routing",
    "palette": {
      "hoodie": "#hex",
      "cap": "#hex",
      "pants": "#hex",
      "chain": "#hex",
      ...
    },
    "props": ["prop_id", ...]
  }
}
```

### `gen_svgs.py` Pattern

- Single Python script reads `cast_definitions.json`
- SVG generation function `gen_svg(cid, char_data)` builds SVG string
- Template logic: `if 'hoodie' in clothes` / `if 'jersey' in clothes` etc.
- Same body skeleton (shadow → legs → left arm → body section → right arm → head → props)
- Each clothing type renders different SVG elements for that body section
- Props are SVG groups positioned per hand
- Output one `.svg` file per character

### Clothing Template Routing

```python
if 'hoodie' in clothes:
    # Draw hoodie body + pocket + drawstrings
elif 'jersey' in clothes:
    # Draw jersey body + number + neckline
elif 'polo' in clothes:
    # Draw polo body + collar + buttons
elif 'barong' in clothes:
    # Draw barong body + embroidery lines
elif 'dress' in clothes:
    # Draw dress body + flare + apron + scarf
```

### Prop Library

Define prop SVGs as static groups positioned at hand locations:
- credit_card → right hand (24x16 rect + chip + strip)
- calculator → right hand (20x30 rect + display)
- money_stack → right hand (3 stacked rects)
- dice → right hand (16x16 red square + dots)
- lotto_ticket → left hand (18x24 ticket + numbers)
- chart → left hand (22x16 line chart)
- coffee → left hand (12x14 cup + handle + liquid)
- basket → left hand (woven basket + items)
- coins → right hand (stacked circles)
- shopping_bag → left hand (bag with $-tag)

## Verification

After generating SVGs, verify visually:

```python
from playwright.sync_api import sync_playwright
# Create an HTML grid showing all characters side-by-side
html = '<html><body style="display:flex;flex-wrap:wrap;background:#111">'
for cid in characters:
    svg = open(f'{cid}.svg').read()
    html += f'<div style="flex:1;min-width:200px"><div>{svg}</div>...</div>'
# Screenshot and analyze with vision_analyze
```

Check:
- [ ] Each character has a distinct silhouette
- [ ] Colors differentiate clearly
- [ ] Props are visible and positioned at hands
- [ ] Expressions match the personality (eyebrows + mouth)
- [ ] Same body skeleton scale/proportions

**⚠️ Vision model verification pitfall**: When analyzing cast screenshots with `vision_analyze`, the model may **misidentify body contours as accessories**. For example, a character's neckline/collar stroke was read as "wire-rimmed glasses" — the dark outline stroke near the face was interpreted as eyewear.

To prevent false readings:
- If `vision_analyze` says a character has an accessory they shouldn't (glasses, hat, facial hair), verify against the SVG source file — don't take the vision output at face value.
- Characters with similar body colors + skin tones are most at risk. Increase differentiation by adjusting color palette in `cast_definitions.json` before accepting the design as final.
- The `vision_analyze` result is advisory; the SVG source is truth.

## Extending Cast for Affiliate Content

The same character cast used for finance education can be **repurposed for affiliate product videos** without re-rigging. Match the product to the character's archetype (see `references/affiliate-video-production.md` for the full production template):

| Product Type | Best Character | Why |
|-------------|---------------|-----|
| Fitness / supplements | Bogart Bugs | Energy / risk-taker vibe |
| Finance / investing | Kuya Piso | Trusted authority |
| Shopping / lifestyle | Gardo Gastos | Impulse buyer appeal |
| Savings / tools | Ian Ipon | Practical, analytical |
| Luxury / high-end | Boss Bilyon | Aspirational status |
| Small business / local | Ate Tindera | Community trust |

For affiliate videos, the character can be:
- **On-screen** presenting the product (full-body + pointing gesture)
- **Reaction overlay** in corner (head only, eyebrow raise + smile)
- **Off-screen entirely** — product card + HUD only, character name carries the brand

## Production Workflow

1. Define cast in `cast_definitions.json` (5 min)
2. Run `gen_svgs.py` (instant)
3. Verify with Playwright screenshot + vision_analyze (2 min)
4. Adjust any colors/props and regenerate
5. For each video: pick characters, write scene plan, compile action timeline, render
6. Each character shares the same pose library (idle, blink, point, celebrate, etc.)
7. To add a new character: add to JSON, run generator — no rig rebuilding

## Cost

- **Zero API cost** — all SVG generation is local Python
- **~$0.04 per video** (just Flux/FAL backgrounds if needed)
- **No recurring character cost** — characters cached as SVG files

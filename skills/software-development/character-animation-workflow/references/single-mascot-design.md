# Single Mascot Character Design — Premium Aesthetic

## Overview

When the channel needs ONE consistent face (not a cast), the character must be:
- **Instantly recognizable** — silhouette, colors, signature items
- **Versatile across content types** — explainer, story, react, affiliate
- **Simple to animate** — 5-6 poses max, same rig every video
- **Premium-feeling** — suits the authority of a finance/personal-growth channel

## The "Mr Finance Guy" Case Study

### User Requirement
- "Good looking character with shades"
- "Good elegant fashion"
- Consistent face for faceless channel
- Channel name = character name

### Design Decisions

| Feature | Decision | Rationale |
|---------|----------|-----------|
| **Outerwear** | Navy blazer | Signals professionalism, authority — dark colors = trust in finance |
| **Shirt** | Crisp white | High contrast against dark blazer, clean look on camera |
| **Tie** | Red (tie or bow tie) | Power accent, draws eye to face, splits shirt from blazer |
| **Sunglasses** | Aviator style | Cool without being aggressive, associated with success icons |
| **Gesture** | Pointing hand | Primary pose for educator/host — "pay attention, this matters" |
| **Watch** | Gold-tone | Subtle wealth signal, visible when hand points or rests |
| **Pocket square** | White | Detail that says "I pay attention to details" |
| **Shoes** | Black, polished | Completes the silhouette from head to toe |
| **Hair** | Dark, side-parted, groomed | Professional, mature, not distracting |

### Color Palette

```css
/* Mr Finance Guy palette */
blazer:    #1a2744    /* deep navy */
shirt:     #ffffff    /* crisp white */
tie:       #c0392b    /* power red */
shades:    #1a1a2e    /* almost black with blue tint */
skin:      #e8c99b    /* warm tan */
hair:      #2d1b0e    /* dark brown */
gold:      #d4af37    /* luxury accent */
pants:     #2c3e50    /* matches blazer */
shoes:     #1a1a1a    /* black */
```

### SVG Structure

The character shares the same body skeleton as the batch-cast template but with these fixes to prevent vision-model misinterpretation:

```svg
<!-- Layer order (bottom to top) -->
<shadow>        <!-- ellipse at feet, rgba(0,0,0,0.15) -->
<legs>          <!-- rects, darker than blazer -->
<shoes>         <!-- ellipses, black -->
<torso>         <!-- blazer body path -->
<lapels>        <!-- left + right, different shade -->
<shirt>         <!-- white triangle under collar -->
<tie>           <!-- red triangle + knot -->
<pocket_square> <!-- white triangle at chest -->
<left_arm>      <!-- curved stroke at side -->
<left_hand>     <!-- skin circle -->
<right_arm>     <!-- curved stroke, pointing up and forward -->
<right_hand>    <!-- pointing gesture group -->
<watch>         <!-- gold rect on left wrist -->
<neck>          <!-- skin rect -->
<head>          <!-- skin ellipse -->
<hair>          <!-- full hair path covering top of head -->
<ears>          <!-- skin ellipses -->
<eyebrows>      <!-- confident curve strokes -->
<sunglasses>    <!-- two lens paths + frame outline + bridge + reflection -->
<mouth>         <!-- smirk stroke -->
<nose>          <!-- subtle line strokes -->
<chin>          <!-- subtle jawline stroke -->
```

**Critical dimensions**: 500×700 viewBox. Character stands on bottom at y=680 (shoes at y=638), head center at (250, 145) radius 65×75.

### Sunglasses Design (Aviator Style)

The aviator sunglasses are the character's signature. SVG implementation:

```svg
<!-- LEFT LENS -->
<path d="M210 130 Q210 120 220 117 L245 117 Q250 117 250 125 L250 155 Q250 165 240 167 L220 167 Q210 165 210 155 Z"
      fill="#1a1a2e" opacity="0.95"/>

<!-- RIGHT LENS -->
<path d="M250 125 Q250 117 255 117 L280 117 Q290 120 290 130 L290 155 Q290 165 280 167 L260 167 Q250 165 250 155 Z"
      fill="#1a1a2e" opacity="0.95"/>

<!-- BRIDGE -->
<path d="M248 128 Q250 122 252 128" stroke="#1a1a2e" stroke-width="2.5" fill="none"/>

<!-- LENS REFLECTION (adds realism) -->
<path d="M218 130 Q218 122 226 120 L238 120" stroke="rgba(255,255,255,0.15)" stroke-width="1.5" fill="none"/>
```

Key details:
- Lens shapes are asymmetrical (aviators taper outward at bottom)
- Bridge curves slightly upward (fits nose)
- Reflections are subtle white strokes (prevents "dead eyes" look)
- Outer frame stroke anchors the glasses on the face

### Vision Verification

When checking the rendered character with `vision_analyze`, be aware of these common misinterpretations:

| What the model may say | Likely SVG cause | Fix |
|------------------------|-----------------|-----|
| "Wearing a headset/mic" | Sunglasses arm path extending toward ear | Verify arm path is thin (stroke-width:2.5) and reaches ear, not beyond |
| "Holding a tablet/book" | Pointing hand + arm path read as holding an object | Verify hand group is positioned at end of arm, not in middle |
| "Wire-rimmed glasses" (on a character without glasses) | Neck collar stroke near face boundary | Adjust neck width or collar stroke width |
| "Glowing object" | Gold watch reflected in background | Verify watch is small (<30px) and positioned at wrist, not floating |

If the model misidentifies accessories: first verify against the SVG source, then adjust SVG colors/dimensions for better visual differentiation. The SVG source is truth.

### Pose Library (Explainer Format)

For a single mascot doing finance education, build these 6 poses:

| Pose | SVG Changes | Use Case |
|------|------------|----------|
| **Host stand** | Both arms at sides, slight smile | Opening/closing |
| **Pointing** | Right arm extends forward, index finger out | "Ito ang importante" |
| **Explaining** | Both arms slightly raised, palms open | Teaching a concept |
| **Confident lean** | One hand in pocket, head tilted slightly | Presenting good news |
| **Thinking** | Right hand to chin, head tilted up | "Isipin mo..." |
| **Reacting/shocked** | Both hands up, eyebrows raised | "Ano?! Hindi pwedeng ganun!" |

Each pose changes only: arm paths, hand positions, eyebrow angle, mouth shape. Head and body remain the same SVG elements with different transform attributes.

### Content Format Matching

| Content Format | Recommended Pose | HUD Elements |
|---------------|-----------------|--------------|
| **Finance fact** (15s) | Host stand → transition to pointing at text card | Knowledge bar, money counter, stat display |
| **Explainer** (30-45s) | Host stand → explaining → pointing → thinking → back to host | Subject label, progress bar, key stat on right |
| **Story** (45-60s) | Reacting → explaining → confident lean → reacting → host close | Scene title, character name, location indicator |
| **Affiliate review** (15-20s) | Host stand → pointing at product → confident close | Product card center, stat bars left, price top-right |

### Channel Brand Integration

When the character's name IS the channel name:

- **Profile picture**: Character bust on dark gradient background + channel name below
- **Video opener**: +3 frame hold of character in host pose before first sentence
- **Color consistency**: Use the character's palette for ALL channel graphics (thumbnails, banner, logo)
- **Voice**: The character's personality in the script should match their visual — a suited character speaks with authority, not "pare chong bro" slang
- **Thumbnails**: Character in expressive pose + bold text overlay using brand colors

### Production Time

- **First character build** (SVG + verification): ~20 min
- **Scene template with 3 cuts** (stand → explain → point): ~15 min
- **Per-video production** (pick poses, write script, render): ~10-15 min
- **Animating with GSAP** (character + HUD): add ~10 min for timeline if not using template

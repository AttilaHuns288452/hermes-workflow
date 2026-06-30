# Game-Style Remotion Composition Template

For @onlymrbones / GTA / brainrot TikTok style — 23+ fast cuts at 2-4s each.

## Composition Builder Script Pattern

Build the composition JSON programmatically so timing recalibration is a single variable change:

```python
import json, os

def scene(name, scene_type, start, end, **kw):
    s = {'id': name, 'in_seconds': start, 'out_seconds': end, 'type': scene_type}
    s.update(kw)
    return s

def overlay(name, otype, start, end, **kw):
    s = {'type': otype, 'in_seconds': start, 'out_seconds': end}
    s.update(kw)
    return s

TARGET = 78.0  # match fast audio duration
fps = 30
scenes = []
overlays = []

# Build acts here (see below)

comp = {
    'render_runtime': 'remotion',
    'renderer_family': 'explainer-data',
    'fps': fps,
    'durationInFrames': int(TARGET * fps),
    'cuts': scenes,
    'overlays': overlays,
    'captions': [],
    'audio': {
        'narration': {'src': 'assets/audio/narration_fast.mp3'},
        'music': {'src': 'assets/music/background.mp3', 'volume': 0.06,
                   'fadeInSeconds': 2, 'fadeOutSeconds': 3, 'loop': True}
    }
}

with open('renders/remotion_props_game.json', 'w') as f:
    json.dump(comp, f, indent=2)
```

## Standard Game-Style Act Structure (80s at 30fps = 2400 frames)

### Act 1: Hook (0–11s, 3 cuts)
| Cut | Type | Time | Content |
|-----|------|------|---------|
| s1 | hero_title | 0–3.5s | "TWO LIVES" / "One Choice Changes Everything" |
| s2 | comparison | 3.5–7s | Same Salary $45K, no difference yet |
| s3 | hero_title | 7–11s | "FIRST DECISION" / "The fork in the road" |

### Act 2: Person A — Assets (11–32s, 7 cuts)
| Cut | Type | Time | Content |
|-----|------|------|---------|
| s4 | hero_title | 11–14s | "PERSON A" green theme, "Chooses Assets" |
| s5 | callout (tip) | 14–17.5s | ✅ "$500/month into Index Funds" |
| s6 | progress_bar | 17.5–21s | Green health bar 85% "INVESTING DISCIPLINE" |
| s7 | callout (warning) | 21–23.5s | ⚠️ Dropshipping FAILED |
| s8 | callout (warning) | 23.5–26s | ⚠️ YouTube FAILED (12 views) |
| s9 | callout (warning) | 26–28.5s | ⚠️ Crypto went completely red |
| s10 | callout (tip) | 28.5–31.5s | ✅ "KEPT INVESTING through every failure" |

### Act 3: Person B — Liabilities (32–52s, 6 cuts)
| Cut | Type | Time | Content |
|-----|------|------|---------|
| s11 | hero_title | 31.5–35s | "PERSON B" red theme, "Chooses Liabilities" |
| s12 | callout (warning) | 35–38s | 💀 Car lease $500/month |
| s13 | callout (warning) | 38–41s | 💀 Starbucks $200/month |
| s14 | callout (warning) | 41–44s | 💀 Dining out $300/month |
| s15 | callout (warning) | 44–46.5s | 💀 Latest iPhone $150/month |
| s16 | progress_bar | 46.5–51.5s | Red health bar 5% "MONEY DRAINING" |

### Act 4: Climax (52–71s, 4 cuts)
| Cut | Type | Time | Content |
|-----|------|------|---------|
| s17 | hero_title | 51.5–54.5s | "30 YEARS LATER" |
| s18 | bar_chart | 54.5–61s | Net Worth: $1.1M vs $50K |
| s19 | stat_card | 61–66s | "$1.1M" green, "500/mo at 10%" |
| s20 | stat_card | 66–71s | "$50K" red, "Car? Long gone" |

### Act 5: Lesson + CTA (71–80s, 3 cuts)
| Cut | Type | Time | Content |
|-----|------|------|---------|
| s21 | comparison | 71–74.5s | "ASSETS → GROW" vs "LIABILITIES → VANISH" |
| s22 | callout (tip) | 74.5–78.5s | 🎯 "Both risked. One on growth. One on vanish." |
| s23 | hero_title | 78.5–81s | "CHOOSE" / "Your risk wisely" |

## Kinetic Overlays (6 shown, more if desired)

Place `stat_reveal` overlays that pop up during key scenes:

```python
overlays = [
    overlay('hook-num1', 'stat_reveal', 1.5, 3.5, text='$1M+', subtitle='One will get this', position='bottom-right'),
    overlay('hook-num2', 'stat_reveal', 2.5, 4.5, text='$0', subtitle='Other? Nothing', position='bottom-right', accentColor='#EF4444'),
    overlay('invest-500', 'stat_reveal', 14.5, 17, text='$500', subtitle='/month invested', position='bottom-right', accentColor='#10B981'),
    overlay('spend-500', 'stat_reveal', 35.5, 37.5, text='$500', subtitle='/month wasted', position='bottom-right', accentColor='#EF4444'),
    overlay('result-a-big', 'stat_reveal', 63, 65.5, text='$1.1M', subtitle='Compounded 10%', position='center', accentColor='#10B981'),
    overlay('result-b-big', 'stat_reveal', 68, 70.5, text='$50K', subtitle='All wasted', position='center', accentColor='#EF4444'),
]
```

## Timing Calibration Workflow

1. **Speed up TTS** → `atempo=1.3` produces ~80s from 105s
2. **Check duration with ffprobe** → `ffprobe -v quiet -print_format json -show_format narration_fast.mp3`
3. **Set `TARGET`** in builder script to audio duration minus 1–3s for margin
4. **Set `durationInFrames`** = `int(TARGET * fps)`
5. **Ensure last scene** ends at or before `TARGET` seconds
6. **Render test segment** around the farthest-near frame before full render to verify no crashes

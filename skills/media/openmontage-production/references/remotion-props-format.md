# Remotion Explainer Props Format — For `.remotion_props.json`

This documents the **actual JSON schema** that the `Explainer.tsx` React component reads when rendering the `explainer-data` / `explainer-teacher` composition. Use this when building the `.remotion_props.json` file directly (Option A in `references/explainer-remotion-format.md` rather than going through the `video_compose` tool pipeline.

## Cut Interface (Explainer.tsx line 192)

```typescript
interface Cut {
  id: string;
  source: string;
  in_seconds: number;       // ← NOT start_seconds
  out_seconds: number;      // ← NOT end_seconds
  layer?: string;
  type?: string;            // Scene renderer type
  text?: string;
  stat?: string;
  subtitle?: string;
  callout_type?: "info" | "warning" | "tip" | "quote";
  title?: string;
  animation?: string;       // Image animation: "zoom-in", "ken-burns", "parallax", etc.
  source_in_seconds?: number;  // Video source trim offset
  overlays?: Overlay[];
  // Comparison props
  leftLabel?: string;  rightLabel?: string;
  leftValue?: string;  rightValue?: string;
  // Chart props
  chartData?: any[];
  chartSeries?: any[];
  chartColors?: string[];
  chartAnimation?: string;
  donut?: boolean;
  centerLabel?: string;
  // generated_content for text_card scenes
  generated_content?: any;
}
```

## Available Cut Types (type field)

| type | Component | Purpose | Props |
|------|-----------|---------|-------|
| Empty / `undefined` | `ImageScene` | Static image via `source` path | `source`, `animation` |
| `"generated"` | `ImageScene` | Same as empty — image with animation | `source`, `animation`, `overlays` |
| `"text_card"` | `TextCard` | Text overlay with `generated_content` | `generated_content`, `text` |
| `"stat_card"` | `StatCard` | Animated stat reveal | `stat`, `text` |
| `"callout"` | `CalloutBox` | Info/warning/tip/quote callout | `callout_type`, `text` |
| `"comparison"` | `ComparisonCard` | Side-by-side comparison | `leftLabel`, `rightLabel`, `leftValue`, `rightValue` |
| `"bar_chart"` | `BarChart` | Animated bar chart | `chartData`, `chartSeries`, `chartColors` |
| `"line_chart"` | `LineChart` | Animated line chart | `chartData`, `chartSeries`, `chartColors`, `chartAnimation` |
| `"pie_chart"` | `PieChart` | Pie/donut chart | `chartData`, `chartSeries`, `donut`, `centerLabel` |
| `"kpi_grid"` | `KPIGrid` | Grid of KPI cards | `chartData`, `chartSeries` |
| `"progress"` | `ProgressBar` | Progress bar animation | `stat`, `text` |
| `"section_title"` | `SectionTitle` | Text section header | `text`, `subtitle` |
| `"stat_reveal"` | `StatReveal` | Big stat reveal with count-up | `stat`, `subtitle` |

## Available Animation Types (animation field for image cuts)

| Value | Effect | Implementation |
|-------|--------|----------------|
| `"zoom-in"` | Start 1.0, zoom to 1.18 | Simple scale ramp |
| `"zoom-out"` | Start 1.18, zoom to 1.0 | Reverse scale ramp |
| `"pan-left"` | Pan right→left at 1.15x | translateX 40→-40 |
| `"pan-right"` | Pan left→right at 1.15x | translateX -40→40 |
| `"ken-burns"` | Cinematic zoom 1.0→1.22 + diagonal drift (0→-25px) | Classic slow Ken Burns |
| `"ken-burns-slow-zoom"` | Same as ken-burns | Alias |
| `"parallax"` | Subtle vertical drift 15→-15px at 1.1x | Parallax effect |
| `"static"` or `"none"` | No animation | Just display |

## Available Transition Names

Used as `transition_in` / `transition_out` in cuts:

| Value | Effect |
|-------|--------|
| `"fade_from_black"` | Start from black, fade in |
| `"fade_to_black"` | Fade out to black |
| `"dissolve"` / `"crossfade"` / `"fade"` | Opacity crossfade |

## Audio Format

The Explainer reads audio from a **nested** object, not flat fields:

```typescript
interface AudioConfig {
  narration?: {
    src: string;       // file:/// or relative (staticFile) path
    volume?: number;   // default 1.0
  };
  music?: {
    src: string;
    volume?: number;          // default 0.1
    offsetSeconds?: number;   // delay before music starts (default 0)
    fadeInSeconds?: number;   // fade-in duration (default 2)
    fadeOutSeconds?: number;  // fade-out duration (default 3)
    loop?: boolean;           // loop the track (default false)
  };
}
```

**Complete audio object example:**
```json
{
  "audio": {
    "narration": {
      "src": "file:///$HOME/OpenMontage/projects/my-video/assets/audio/narration.mp3",
      "volume": 1.0
    },
    "music": {
      "src": "file:///$HOME/OpenMontage/projects/my-video/assets/music/background.mp3",
      "volume": 0.1,
      "offsetSeconds": 0,
      "fadeInSeconds": 2,
      "fadeOutSeconds": 3,
      "loop": false
    }
  }
}
```

## 🚨 Caption Format — Milliseconds, NOT Seconds

The `WordCaption` interface in `CaptionOverlay.tsx` expects `startMs` and `endMs` in **milliseconds**:

```typescript
export interface WordCaption {
  word: string;
  startMs: number;  // milliseconds, NOT seconds
  endMs: number;    // milliseconds, NOT seconds
}
```

### ❌ The Bug That Wastes Render Attempts

ElevenLabs TTS transcript JSON outputs word timestamps in **seconds** (`start: 0.5, end: 0.8`). Passing these directly as the `captions` array causes `CaptionOverlay.buildPages()` to read `startMs = undefined`, producing `NaN` in the `<Sequence>` `from` frame calculation. This manifests as the **misleading error**:

```
TypeError: The "from" prop of a sequence must be finite, but got NaN.
```

### ✅ Correct: Convert Seconds → Milliseconds

```python
import json

with open("assets/audio/narration_full_transcript.json") as f:
    transcript = json.load(f)

# ElevenLabs transcript structure depends on TTS output format:
# Option A: List of segments with nested "words" arrays
# Option B: Dict with "words" or "segments" top-level keys

captions = []

if isinstance(transcript, list) and "words" in transcript[0]:
    # Each segment has a "words" array
    for seg in transcript:
        for w in seg.get("words", []):
            captions.append({
                "word": w.get("word", ""),
                "startMs": round(w.get("start", 0) * 1000),   # ← SECONDS TO MS
                "endMs": round(w.get("end", 0) * 1000)         # ← SECONDS TO MS
            })
elif isinstance(transcript, dict):
    source = transcript.get("words", transcript.get("segments", []))
    for item in source:
        if "words" in item:
            for w in item["words"]:
                captions.append({
                    "word": w.get("word", ""),
                    "startMs": round(w.get("start", 0) * 1000),
                    "endMs": round(w.get("end", 0) * 1000)
                })
        else:
            captions.append({
                "word": item.get("word", item.get("text", "")),
                "startMs": round(item.get("start", 0) * 1000),
                "endMs": round(item.get("end", 0) * 1000)
            })

# Correct output: {"word": "hello", "startMs": 500, "endMs": 800} ✓
```

✅ Correct example word object:
```json
{"word": "hello", "startMs": 500, "endMs": 800}
```

❌ Wrong (seconds — causes NaN error):
```json
{"word": "hello", "start": 0.5, "end": 0.8}
```

## Theme Config (optional)

Controls visual styling of the Explainer. If omitted, default dark theme is used:
```json
{
  "themeConfig": {
    "backgroundColor": "#0F172A",
    "primaryColor": "#22C55E",
    "secondaryColor": "#EF4444",
    "accentColor": "#3B82F6",
    "textColor": "#FFFFFF",
    "captionHighlightColor": "#FDE047",
    "captionBackgroundColor": "rgba(0,0,0,0.6)",
    "headingFont": "Arial, sans-serif",
    "bodyFont": "Arial, sans-serif"
  }
}
```

## Complete Example — Working `.remotion_props.json`

```json
{
  "cuts": [
    {
      "id": "cut-1",
      "type": "text_card",
      "in_seconds": 0,
      "out_seconds": 5.5,
      "generated_content": {
        "type": "split_screen",
        "left_side": {"label": "JUAN", "glow_color": "green"},
        "right_side": {"label": "MARIA", "glow_color": "red"},
        "bottom_text": "SAME AGE. SAME SALARY. TWO DIFFERENT LIVES."
      }
    },
    {
      "id": "cut-2",
      "type": "generated",
      "in_seconds": 5.5,
      "out_seconds": 20,
      "source": "file:///$HOME/.../scene-2-juan.png",
      "animation": "ken-burns",
      "overlays": [
        {"text": "JUAN — Failed Hustles",
         "x": "w*0.05", "y": "h*0.05",
         "color": "green", "font_size": 24}
      ]
    },
    {
      "id": "cut-5",
      "type": "line_chart",
      "in_seconds": 46,
      "out_seconds": 65,
      "text": "Compounding Risk",
      "chartData": [
        {"age": 25, "juan": 100, "maria": 100},
        {"age": 40, "juan": 50000, "maria": 0}
      ],
      "chartSeries": [
        {"key": "juan", "label": "Juan", "color": "green"},
        {"key": "maria", "label": "Maria", "color": "red"}
      ]
    }
  ],
  "captions": [
    {"word": "Two", "startMs": 100, "endMs": 300},
    {"word": "lives.", "startMs": 300, "endMs": 600}
  ],
  "audio": {
    "narration": {
      "src": "file:///C:/.../narration.mp3",
      "volume": 1.0
    },
    "music": {
      "src": "file:///C:/.../background.mp3",
      "volume": 0.1,
      "fadeInSeconds": 2,
      "fadeOutSeconds": 3
    }
  },
  "themeConfig": {
    "backgroundColor": "#0F172A",
    "primaryColor": "#22C55E",
    "secondaryColor": "#EF4444",
    "accentColor": "#3B82F6",
    "textColor": "#FFFFFF",
    "captionHighlightColor": "#FDE047",
    "captionBackgroundColor": "rgba(0,0,0,0.6)"
  }
}
```

## Common Pitfalls

1. **`in_seconds`/`out_seconds` vs `start_seconds`/`end_seconds`**: The edit_decisions schema uses `start_seconds`/`end_seconds`. The Remotion Explainer **only reads `in_seconds`/`out_seconds`**. Using `start_seconds` → `NaN` in Sequence → `"from prop must be finite"` error. ALWAYS use `in_seconds`/`out_seconds` in the `.remotion_props.json`.

2. **`audio.narration.src` not `audio.narration_path`**: The edit_decisions schema uses flat fields (`narration_path`). Remotion expects nested objects (`audio.narration.src`). Direct render props MUST use the nested format.

3. **`file:///` paths break the Remotion renderer**: The `resolveAsset()` function in Explainer.tsx can construct `file:///` URIs for absolute paths (like `C:\Users\...\narration.mp3`), but the **Remotion renderer cannot download `file:///` URIs** — it throws `Error: Can only download URLs starting with http:// or https://`. This only happens during rendering, not in Studio preview. **Fix**: Copy assets to `public/{project-name}/` and use bare relative paths without `./` prefix:
   - ✅ `"src": "bad-debt-vs-good-debt/audio/narration.mp3"` — works with `staticFile()`
   - ✅ `resolveAsset()` calls `staticFile(clean)` for non-URL, non-absolute paths
   - ❌ `"src": "./bad-debt-vs-good-debt/audio/narration.mp3"` — `staticFile()` rejects with `does not support relative paths`
   - ❌ `"src": "file:///C:/Users/.../narration.mp3"` — renderer can't download

4. **Text card cuts need `generated_content`**: A `text_card` cut with no `generated_content` renders a blank card. Always provide at least a basic `generated_content` object.

5. **Image cuts with `animation: "ken-burns"` need no `generated_content`**: The two are mutually exclusive per cut — `generated_content` is for text_card scenes, `animation` is for image scenes.

6. **Formatting `generated_content.subtitle`: Use `\n`** — For multi-line text in `end_screen.main_text` or subtitle fields, use `\n` as the line separator (JSON escape `\\n`).

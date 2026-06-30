# Remotion Explainer "explainer-data" Format — edit_decisions Schema

## Overview

When `render_runtime: "remotion"` and `renderer_family: "explainer-data"`, the `video_compose.render()` operation reads `edit_decisions`, converts it to `.remotion_props.json`, and invokes the `Explainer` composition in `remotion-composer/src/`. The JSON schema is **strictly validated** by OpenMontage governance — missing fields block the render at pre-compose validation.

## ⚠️ Critical: edit_decisions vs. Remotion Props Field Name Mismatch

The `edit_decisions` schema (what you pass to `video_compose`) uses **different field names** than what the actual `Explainer` React component (`Explainer.tsx`) expects. The `video_compose._remotion_render()` method does **NOT** convert between these two formats — it copies fields verbatim and only converts `source` paths to `file:///` URIs.

Using the edit_decisions field names (`start_seconds`, `end_seconds`, `narration_path`, etc.) causes:
1. **`TypeError: The "from" prop of a sequence must be finite, but got NaN.`** — because `cut.in_seconds` is `undefined` (the component reads `in_seconds`/`out_seconds`, not `start_seconds`/`end_seconds`). This is the most common & misleading error.
2. **No narration or music audio** — because the component reads `audio.narration.src` and `audio.music.src`, not `narration_path`/`background_music_path`
3. **Wasted render attempts** — the "from prop NaN" error is a red herring; the fix is field names, not timing values

### The Fix: Two Options

**Option A — Direct Remotion render (recommended for now):** Bypass `video_compose.render()` entirely. Build the props JSON yourself matching the `Cut` interface exactly (see `references/remotion-props-format.md`), then call `npx remotion render` directly. On Windows use `--props=<path>` (equals sign).

**Option B — edit_decisions pipeline:** Use the edit_decisions schema below with `video_compose.render()`, but only if/when the tool's `_remotion_render()` method has been patched to convert field names. Until then, Option A is more reliable.

## Required Root Fields (for edit_decisions)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `render_runtime` | string | **YES** | Must be `"remotion"` |
| `renderer_family` | string | **YES** | Must be `"explainer-data"` |
| `delivery_promise` | object | **YES** | Render contract (see below) |
| `metadata` | object | **YES** | Proposal metadata |
| `subtitles` | object | **YES** | Subtitle/caption config |
| `audio` | object | **YES** | Narration + music paths |
| `cuts` | array | **YES** | Scene definitions (≥1) |

### `delivery_promise`

⚠️ `promise_type` must be a valid `PromiseType` enum value (from `lib/delivery_promise.py`): `"motion_led"`, `"data_explainer"`, `"source_led"`, `"teacher_explainer"`, `"screen_demo"`, `"avatar_presenter"`, `"hybrid"`, `"localization"`. Do NOT use `"render"` — that will fail `pre_compose_validation`.

```json
{
  "promise_type": "data_explainer",
  "runtime": "remotion",
  "output_profile": "youtube_landscape",
  "resolution": "1920x1080",
  "fps": 30,
  "total_duration_seconds": 82.66
}
```

### `metadata`

```json
{
  "proposal_render_runtime": "remotion",
  "total_duration_seconds": 82.66,
  "resolution": "1920x1080",
  "fps": 30,
  "profile": "youtube_landscape"
}
```

### `subtitles`

```json
{
  "enabled": true,
  "source": null,
  "style": {
    "font": "Arial",
    "font_size": 32,
    "primary_color": "&HFFFFFF",
    "outline_color": "&H000000",
    "outline_width": 3,
    "margin_v": 120,
    "alignment": 2,
    "burn_in": true
  }
}
```

`style` is a **sub-object**, not flat fields. Colors use `&H` prefixed hex values (ASS subtitle convention).

### `audio`

```json
{
  "narration_path": "C:/path/to/narration.mp3",
  "narration_duration_seconds": 82.66,
  "background_music_path": "C:/path/to/music.mp3",
  "music_duration_seconds": 87.7,
  "music_volume": 0.12,
  "ducking": {
    "enabled": true,
    "attack_ms": 200,
    "release_ms": 500,
    "reduction_db": 12
  }
}
```

⚠️ Reminder: These fields (`narration_path`, `background_music_path`) are the **edit_decisions** format. The actual Remotion Explainer expects `audio.narration.src` and `audio.music.src`. The `video_compose` tool does NOT convert between these. If rendering via `video_compose.render()` fails with missing audio, switch to the direct Remotion props format.

Paths: Use **absolute Windows paths with forward slashes** (`C:/Users/...`).

### ⚠️ Caption Word Object Format (Hidden NaN Bug)

The Remotion Explainer expects caption words with `startMs`/`endMs` in **milliseconds**, not `start`/`end` in seconds. This is the most common cause of `TypeError: The "from" prop of a sequence must be finite, but got NaN` after the field-name fixes above.

**Always convert ElevenLabs transcript timestamps from seconds to milliseconds** before embedding in props. See `references/remotion-props-format.md` for the conversion code and the full explanation.

### `proposal_metadata`

```json
{
  "render_runtime": "remotion",
  "renderer_family": "remotion"
}
```

Note: `proposal_metadata.renderer_family` says `"remotion"`, not `"explainer-data"` — these track the same concept at different levels.

## Cuts Array

### Common Fields (all cut types)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | **YES** | Unique, e.g. `"cut-1"` |
| `scene_id` | string | **YES** | Maps to scene plan |
| `type` | string | **YES** | `"text_card"` or `"generated"` |
| `start_seconds` | number | **YES** | Cut start time (edit_decisions format) |
| `end_seconds` | number | **YES** | Cut end time (edit_decisions format) |
| `duration_seconds` | number | **YES** | `end - start` |
| `source` | string\|null | **YES** | Image path or `null` |
| `generated_content` | object\|null | **YES** | Visual description |
| `transition_in` | string | Optional | e.g. `"fade_from_black"`, `"crossfade"` |
| `transition_out` | string | Optional | e.g. `"dissolve"`, `"fade_to_black"` |
| `narration_segment` | string | Optional | Maps to narration sections |
| `effect` | string | Optional | `"ken_burns"` for still images |
| `ken_burns` | object | Conditional | Required with `effect: "ken_burns"` |

### `type: "text_card"` — generated_content sub-types

#### `split_screen`
```json
{"type": "split_screen", "background": "black",
 "left_side": {"label": "NAME", "glow_color": "green", "silhouette": "solid_circle"},
 "right_side": {"label": "NAME", "glow_color": "red", "silhouette": "solid_circle"},
 "bottom_text": "Subtitle"}
```

#### `diverging_paths`
```json
{"type": "diverging_paths", "background": "gradient_green_dark",
 "left_path": {"label": "RISK ON ASSETS", "color": "green", "items": ["Item1"]},
 "right_path": {"label": "RISK ON LIABILITIES", "color": "red"},
 "stat_card": {"pop_seconds": 45, "left": "GROWING", "right": "DEPRECIATED"}}
```

#### `stat_card_stagger`
```json
{"type": "stat_card_stagger", "hero_stat": "HEADLINE", "hero_subtitle": "Sub",
 "core_lesson": "Message",
 "stagger_lines": [{"text": "Line", "icon": "check_mark", "delay_seconds": 1}],
 "background": "gradient_dark"}
```

#### `end_screen`
```json
{"type": "end_screen", "main_text": "RISK ON ASSETS\nNOT ON LIABILITIES",
 "subtitle": "Subtitle", "footer": "CTA", "background": "dark_gradient", "accent_color": "green"}
```

#### `comparison_grid`
```json
{"type": "comparison_grid", "background": "dark_gradient",
 "rows": [{"label": "A", "color": "green", "value": "Growing"}, {"label": "B", "color": "red", "value": "Depreciated"}]}
```

### `type: "generated"` — with external image

```json
{"id": "cut-2", "scene_id": "scene-2", "type": "generated",
 "start_seconds": 4.4, "end_seconds": 16.32, "duration_seconds": 11.92,
 "source": "C:/path/to/image.png",
 "effect": "ken_burns",
 "ken_burns": {"zoom_start": 1.0, "zoom_end": 1.08, "pan": "subtle_right"},
 "generated_content": { ... },
 "transition_in": "crossfade", "transition_out": "dissolve",
 "narration_segment": "s2"}
```

Source paths resolve through the asset manifest. Use absolute paths with forward slashes.

## Transition Names

- `"fade_from_black"`, `"fade_to_black"` — Fade from/to black
- `"crossfade"`, `"dissolve"`, `"fade"` — Dissolve transitions

## Asset Manifest Format

Required alongside edit_decisions for the `render` operation:

```json
{
  "version": "1.0",
  "assets": [
    {"id": "narration", "type": "audio", "subtype": "narration",
     "path": "C:/path/to/narration.mp3", "source_tool": "elevenlabs_tts",
     "duration_seconds": 82.66},
    {"id": "img-character", "type": "image", "path": "C:/path/to/image.png",
     "source_tool": "flux_image"},
    {"id": "music-bg", "type": "audio", "subtype": "music",
     "path": "C:/path/to/music.mp3", "source_tool": "pixabay_music",
     "duration_seconds": 87.7}
  ],
  "total_cost_usd": 0.39
}
```

## Windows `npx remotion render` Quoting Issue

`--props <path>` (space) fails on Windows cmd.exe. Use `--props=<path>` (equals sign):
```bash
npx remotion render src/index.tsx Explainer output.mp4 \
  --props=C:/full/path/to/.remotion_props.json --width 1920 --height 1080
```

## Debugging Pattern

When Explainer fails, isolate step by step:
1. Text card only, no audio → validates schema + timing
2. Multiple text cards → validates sequencing
3. Text cards + captions → validates overlay
4. Text cards + audio → validates audio channel
5. Single image via image cut → validates image loading
6. Full composition

Use `--concurrency 1` to avoid parallel error spam.

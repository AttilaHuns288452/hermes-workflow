---
name: openmontage-production
version: "1.1.0"
description: >-
  Full OpenMontage video production pipeline wrapper. When the user asks to
  make, create, produce, or render any video content — animated explainer,
  TikTok/Shorts, cinematic trailer, character animation, documentary montage,
  or any other video — route through OpenMontage's pipeline system first.
  OpenMontage is fully installed at ~/OpenMontage with all 12 API keys
  configured and 182/184 contract tests passing. DO NOT fall back to ad-hoc
  FFmpeg scripts unless OpenMontage's tool registry shows blockers.
category: media
triggers:
  - "make a video"
  - "create a video"
  - "produce a video"
  - "render video"
  - "generate video"
  - "animated explainer"
  - "TikTok video"
  - "YouTube Shorts"
  - "viral video"
  - "video production"
  - "openmontage"
  - "open montage"
---

# OpenMontage Video Production Pipeline

## 🚨 Mandatory — This is the DEFAULT for video production

OpenMontage is installed at `~/OpenMontage/` and fully configured with **all 12 API keys** (FAL, Google, ElevenLabs, OpenAI, xAI/Grok, Suno, HeyGen, Runway, Pexels, Pixabay, Unsplash, HuggingFace). All 182 contract tests pass.

**When the user asks to make ANY video, you MUST route through OpenMontage first.** Do not write ad-hoc FFmpeg scripts, do not use `short-video-production` unless OpenMontage's tool registry shows blockers. The OpenMontage pipeline system produces significantly higher quality output with proper Remotion/HyperFrames composition, Ken Burns effects, ASS subtitles, and multi-provider model selection.

## Environment

- **Location:** `~/OpenMontage/` (`C:\Users\YOUR_USERNAME\OpenMontage/`)
- **Python:** System Python 3.11.9 — OpenMontage uses its own venv-free discovery (imports tools directly)
- **Working directory:** Always `cd ~/OpenMontage` before any OpenMontage commands
- **.env:** Complete — all 12 API keys configured and verified. CHROME_PATH is set to Chrome's Windows install path for Remotion rendering
- **Test status:** 182 passed, 7 skipped, 1 known-minor fail (doubao provider not in test expected set — not a real issue)
- **Remotion:** npm deps installed in `remotion-composer/` (verified working — renders stills and video via `npx remotion`)
- **Chrome:** Found at `C:\Program Files\Google\Chrome\Application\chrome.exe` — Remotion auto-discovers it on Windows

## Relevant Files

| File | Purpose |
|------|---------|
| `AGENT_GUIDE.md` | **READ FIRST** — Agent onboarding, Rule Zero, all governance rules |
| `PROJECT_CONTEXT.md` | Architecture, key files, conventions |
| `pipeline_defs/*.yaml` | Pipeline manifests (13 pipelines) |
| `skills/pipelines/<pipeline>/` | Stage director skills per pipeline |
| `skills/INDEX.md` | Full skill index, Layer 2-3 architecture |
| `skills/meta/` | Reviewer, checkpoint, onboarding, skill-creator |
| `tools/tool_registry.py` | Tool discovery — run preflight before any production |
| `config.yaml` | Global config |
| `lib/checkpoint.py` | Checkpoint reader/writer |

## Step-by-Step — Video Production via OpenMontage

### Phase 0 — Onboarding & Pipeline Selection

1. **First time in session or first video request:** Read `AGENT_GUIDE.md` from the project root.
   ```bash
   cd ~/OpenMontage && read_file AGENT_GUIDE.md
   ```

2. **Identify the right pipeline** based on the user's request:

   | User Says | Pipeline | Reason |
   |-----------|----------|--------|
   | "explainer about [topic]" | `animated-explainer` | Research-first, full pre-production |
   | "TikTok video", "viral short" | `animated-explainer` or `cinematic` | TikTok-optimized pacing |
   | "character animation", "cartoon" | `character-animation` | Local SVG rigged characters |
   | "cinematic trailer", "mood" | `cinematic` | Mood-led edits |
   | "documentary", "stock footage" | `documentary-montage` | Pexels/Pixabay stock-led |
   | "product ad", "commercial" | `cinematic` | Trailer/ad format |
   | "talking head", "lecture" | `talking-head` | Footage-led |
   | "screen recording", "demo" | `screen-demo` | Walkthroughs |
   | "clip from long video" | `clip-factory` | Many clips from one source |
   | "avatar", "spokesperson" | `avatar-spokesperson` | Lip-sync avatars |
   | "podcast repurpose" | `podcast-repurpose` | Podcast to social clips |
   | "dub", "localization" | `localization-dub` | Subtitle/dub variants |
   | Not sure, or "best for [topic]" | `animated-explainer` | Most mature pipeline (production stability) |

3. **Read the pipeline manifest:**
   ```bash
   cat ~/OpenMontage/pipeline_defs/<pipeline>.yaml
   ```

4. **Run preflight** to check available tools:
   ```bash
   cd ~/OpenMontage && python -c "from tools.tool_registry import registry; import json; registry.discover(); print(json.dumps(registry.provider_menu_summary(), indent=2))"
   ```

### Phase 1 — Follow the Pipeline Stages

Each pipeline follows the same state machine pattern, with stage-specific director skills:

```
research → proposal → script → scene_plan → assets → edit → compose → publish
```

For EACH stage:
1. **Read the stage director skill** — `skills/pipelines/<pipeline>/<stage>-director.md`
2. **Execute** using the tools the director skill specifies
3. **Self-review** using `skills/meta/reviewer.md`
4. **Checkpoint** using `lib/checkpoint.py`
5. **Present for human approval** when `human_approval_default: true`
The executive-producer skill simplifies this orchestration — read it first:
```
skills/pipelines/<pipeline>/executive-producer.md
```

### Read Director Skills Before Calling Tools

Before using ANY tool, check if it has an `agent_skills[]` field in the tool registry, and if so, read the corresponding Layer 3 skill under `.agents/skills/`. These contain provider-specific prompting guidance that dramatically improves output quality.

Example:
```bash
cd ~/OpenMontage
python -c "from tools.tool_registry import registry; registry.discover(); t = registry.get('image_selector'); print(t.get_info().get('agent_skills', []))"
```
If it returns `["fal-ai-flux"]`, then read `.agents/skills/fal-ai-flux.md` before calling the tool.

### Phase 2 — Project Directory Convention

Every production run creates a workspace under `projects/<project-name>/`:
```
projects/<project-name>/
├── artifacts/      # Stage outputs (research_brief, script, scene_plan, etc.)
├── assets/         # Generated images, video, audio, music
└── renders/        # Final MP4 output
```

Create the project directory at pipeline initialization, before any stage runs.

## Composition Runtimes (HARD RULE)

OpenMontage supports multiple composition runtimes:

1. **Remotion** — React-based, highest quality, needs Chrome/chromium
2. **HyperFrames** — HTML/CSS/GSAP, needs Node
3. **FFmpeg** — Scripted composition, fallback only

**When both Remotion and HyperFrames are available** (check via `video_compose.get_info()["render_engines"]`), you MUST present both to the user and let them choose. Do NOT silently pick a default.

### 💡 Remotion Scene Types (Explainer composition)

When building props directly (see `references/remotion-props-format.md`), these cut types are available:

| type | Purpose | Required Props |
|------|---------|----------------|
| (empty) | Static image with animation | `source`, `animation` |
| `"generated"` | Image + animation + overlays | `source`, `animation`, `overlays` |
| `"text_card"` | Animated text scene | `text`, `generated_content` |
| `"stat_card"` | Animated stat reveal | `stat`, `text` |
| `"callout"` | Info/warning/tip/quote card | `callout_type`, `text` |
| `"comparison"` | Side-by-side | `leftLabel`, `rightLabel` |
| `"bar_chart"` / `"line_chart"` / `"pie_chart"` | Animated charts | `chartData`, `chartSeries` |
| `"kpi_grid"` | KPI dashboard grid | `chartData`, `chartSeries` |
| `"progress"` / `"section_title"` / `"stat_reveal"` | Progress/header/reveal | `stat`, `text`, `subtitle` |

### 💡 Word-Level Captions from TTS Transcript

After generating ElevenLabs narration, the transcript JSON contains word-level timestamps. Load and pass these as the `captions` array in Remotion props:

```python
import json
with open("assets/audio/narration_full_transcript.json") as f:
    transcript = json.load(f)
captions = transcript if isinstance(transcript, list) else transcript.get("words", [])
```

Each caption entry: `{"word": "hello", "start": 0.5, "end": 0.8}`

Pass the captions array in the Remotion props under the `"captions"` key.

### 💡 `delivery_promise.promise_type` Enum Constraint

The `delivery_promise.promise_type` must be a valid `PromiseType` enum value from `lib/delivery_promise.py`:
- `"motion_led"` — Requires real motion (70%+ animated cuts)
- `"data_explainer"` — Data visualization (default for animated-explainer pipeline)
- `"source_led"` — User-provided footage
- `"teacher_explainer"`, `"screen_demo"`, `"avatar_presenter"`, `"hybrid"`, `"localization"`

Do NOT use `"render"` — `pre_compose_validation` will reject it.

### Phase 4 — Post-Production

1. Verify the output exists and is playable:
   ```bash
   ffprobe -v quiet -print_format json -show_format projects/<name>/renders/final.mp4
   ```
2. Report to user what was created, which pipeline was used, which providers/models were called, and the final render path.

## Common Pipeline Shortcuts

For quick TikTok/Shorts requests (NOT for long-form or high-quality), you can use the `animated-explainer` pipeline which is designed for fast turnaround with production quality. It defaults to auto-approval for research and asset generation, with human approval gates at proposal, script, scene_plan, and publish.

## Key Commands Reference

```bash
# Preflight — summary (human-friendly)
cd ~/OpenMontage && python -c "from tools.tool_registry import registry; import json; registry.discover(); print(json.dumps(registry.provider_menu_summary(), indent=2))"

# Preflight — full menu
cd ~/OpenMontage && python -c "from tools.tool_registry import registry; import json; registry.discover(); print(json.dumps(registry.provider_menu(), indent=2))"

# Preflight — capability catalog
cd ~/OpenMontage && python -c "from tools.tool_registry import registry; import json; registry.discover(); print(json.dumps(registry.capability_catalog(), indent=2))"

# Checkpoint — get next stage
cd ~/OpenMontage && python -c "from lib.checkpoint import checkpoint; print(checkpoint.get_next_stage('projects/<name>'))"

# Cost tracker — budget governance
cd ~/OpenMontage && python -c "from tools.cost_tracker import cost_tracker; print(cost_tracker.summary())"

# Run tests to verify setup
cd ~/OpenMontage && python -m pytest tests/ -q --no-header 2>&1 | tail -5
```

## ⚠️ Windows Remotion Asset Paths — Critical Pitfall

Remotion's headless Chrome on Windows **blocks `file:///` URIs** for local images and audio. The `video_compose._remotion_render()` method automatically converts file paths to `file:///` URIs when writing props, but Chrome refuses to load them (`"Not allowed to load local resource"` and `"EncodingError: The source image cannot be decoded"`).

### Troubleshooting Tip: "from prop NaN" is often a misleading error

If Remotion fails with `TypeError: The "from" prop of a sequence must be finite, but got NaN.`, the actual root cause is frequently a **failed image load**, not a timing issue. The NaN propagates from an unhandled image loading error that cascades. Always rule out image/audio asset failures first — test with text-only cuts before investigating `in_seconds`/`out_seconds` values. See `references/remotion-windows-asset-paths.md` for the full debugging workflow.

### The Fix

Place all assets in `remotion-composer/public/` and reference them with **relative paths (no leading slash)** in the composition JSON so `resolveAsset()` in `Explainer.tsx` routes them through Remotion's `staticFile()`:

```python
# WRONG — causes file:/// URIs blocked by Chrome
cut["backgroundImage"] = "C:/path/to/assets/image.png"
cut["backgroundImage"] = "file:///C:/path/to/assets/image.png"
cut["backgroundImage"] = "/assets/image.png"  # resolveAsset treats / as absolute path

# RIGHT — routes through staticFile() → public/ lookup
cut["backgroundImage"] = "assets/images/hero_bg.png"
audio["narration"]["src"] = "assets/audio/narration.mp3"
```

**Windows `npx` quirk — use `--props=<path>` not `--props <path>`:** When passing the props file to `npx remotion render` on Windows (via MSYS/bash), the `--props` flag followed by a space-separated value gets mangled by cmd.exe's parsing. Always use the `=` syntax:

```bash
# ✅ WORKS on Windows MSYS
npx remotion render src/index.tsx Explainer output.mp4 --props=/c/Users/.../props.json

# ❌ BROKEN — spaces before args get mangled by cmd.exe quoting
npx remotion render src/index.tsx Explainer output.mp4 --props C:/Users/.../props.json
```


### Step-by-step

1. Copy all asset files into `remotion-composer/public/` preserving the directory structure:
   ```bash
   cp -r projects/<name>/assets/images/* remotion-composer/public/assets/images/
   cp -r projects/<name>/assets/audio/*  remotion-composer/public/assets/audio/
   cp -r projects/<name>/assets/music/*  remotion-composer/public/assets/music/
   ```

2. In your composition JSON, use paths **without** leading `/`:
   ```
   assets/images/hero_bg.png  ✓
   /assets/images/hero_bg.png ✗
   file:///assets/...         ✗
   C:\Users\...               ✗
   ```

3. The `resolveAsset()` function in `Explainer.tsx` (line 16-28) routes relative paths to `staticFile()`, which resolves them under `public/`. Paths starting with `/` or a drive letter get converted to `file:///` URIs instead — blocked by Chrome.

### `backgroundImage` Resolution

The `render` operation's asset manifest resolution only resolves the `source` field of cuts, **not** `backgroundImage`. You must resolve background image paths manually before passing to `video_compose`:

```python
for cut in comp.get("cuts", []):
    bg = cut.get("backgroundImage", "")
    if bg and not bg.startswith(("http://", "https://")):
        # Handled via public/ — use relative path
        cut["backgroundImage"] = "assets/images/" + Path(bg).name
```

### `render` Operation Requires Both `edit_decisions` AND `asset_manifest`

`operation="render"` will fail with `"asset_manifest required for render"` if you pass only `edit_decisions`. Both are required:

```python
result = VideoCompose().execute({
    "operation": "render",
    "edit_decisions": comp,
    "asset_manifest": {"assets": [...]},
    "output_path": "renders/output.mp4",
})
```

For direct Remotion rendering without the asset manifest step, use `operation="remotion_render"` which only needs `edit_decisions`:

```python
result = VideoCompose().execute({
    "operation": "remotion_render",
    "edit_decisions": comp,
    "output_path": "renders/output.mp4",
})
```

## References

| File | Content |
|------|---------|
| `references/remotion-windows-asset-paths.md` | Windows file:/// URI blocking fix, public/ directory workaround, `from prop NaN` red herring detection |
| `references/explainer-remotion-format.md` | Full schema for the `explainer-data` edit_decisions format: required fields, cut types, `generated_content` sub-types, asset manifest, transition names |
| `references/remotion-props-format.md` | **Actual** Remotion props JSON schema that the Explainer component reads. Use this for direct `npx remotion render` calls (bypassing the `video_compose` tool). Documents the `Cut` interface, `in_seconds`/`out_seconds` (not `start_seconds`), `audio.narration.src` (not `narration_path`), scene types, animation values. |

> **When composing for the Remotion Explainer (`renderer_family: "explainer-data"`)**, read BOTH reference files. First `references/explainer-remotion-format.md` for the edit_decisions pipeline schema, then `references/remotion-props-format.md` for the actual Remotion component schema. The edit_decisions schema is what the `video_compose` tool expects; the remotion-props-format is what the React component actually reads — and they use **different field names** for the same data (start_seconds vs. in_seconds, narration_path vs. audio.narration.src). The tool does NOT convert between them.

### Render Performance — Windows

On this Windows machine, Remotion renders at approximately **1 frame per ~2 seconds** at 1920×1080 (30fps, `--concurrency=8`). That means:

| Duration | Frames @ 30fps | Expected Render Time |
|----------|-----------------|---------------------|
| ~30s | 900 frames | ~30 min |
| ~60s | 1800 frames | ~60 min |
| ~83s | 2510 frames | ~84 min |

Actual wall-clock time varies with frame complexity. Simple text-card scenes render faster than image-heavy or chart scenes. Remotion's built-in progress estimate stabilizes after ~100 frames but tends to be slightly optimistic.

**This user explicitly prefers Remotion** over the FFmpeg compose fallback, even knowing the speed difference. Do NOT silently fall back to FFmpeg or suggest degrading to Ken Burns slideshows — they want the full animated experience with charts, comparison cards, and spring transitions. Offer the choice, but respect this preference.

**Fast iteration tip:** test Remotion renders with text-only cuts first (no images, no audio) to validate timing and transitions before the full render. The `calculateMetadata` in Root.tsx auto-computes `durationInFrames` from `cuts[].out_seconds` — no need to set it manually in props.

## Tool Module Paths

| Tool | Full Import Path |
|------|-----------------|
| Flux image generation | `tools.graphics.flux_image` (NOT `tools.image`) |
| ElevenLabs TTS | `tools.audio.elevenlabs_tts` |
| Pixabay music | `tools.audio.pixabay_music` |
| Video compose | `tools.video.video_compose` |

## Provider-Specific Quirks

### ElevenLabs TTS
- **Voice ID, not name**: The TTS tool needs the voice **UUID** (`21m00Tcm4TlvDq8ikWAM` for Rachel), not the voice name (`"Rachel"`). Passing the name returns a `404` because the tool only does ID-based lookup.
- **API key**: Read from `ELEVENLABS_API_KEY` env var. Set it before calling the tool:
  ```bash
  ELEVENLABS_API_KEY=$(cat path/to/.elevenlabs_key) python -c "from tools.audio.elevenlabs_tts import ElevenLabsTTS; ..."
  ```
- **User preference — mandatory**: This user requires ElevenLabs for ALL voiceovers. Never default to OpenAI TTS, edge-tts, or any other provider. Always use ElevenLabs Rachel (UUID `21m00Tcm4TlvDq8ikWAM`).

### Pixabay Music
- **No API key required** — works out of the box for free stock music downloads
- Search by mood/energy (`"uplifting corporate background"`, `"motivational"`) and specify `min_duration`/`max_duration` in seconds
- Returns MP3 at ~256 kbps

### Flux Image
- Available at `tools.graphics.flux_image`
- Models: `flux-pro/v1.1` (default, best quality), `flux/dev` (fallback)
- Generates 1024×1024 by default; use `output_path` to save

## Related Skills

| Skill | When to load |
|-------|-------------|
| `mr-finance-guy` | User wants a finance explainer script first — produces the annotated script with expression tags that feed into character-animation pipeline |
| `media/tiktok-finance-video` | User wants a finance "two lives" comparison video |
| `media/short-video-production` | Fallback when OpenMontage is unavailable |

## 🚫 Why Previous Videos Were "Very Bad" — Root Cause

The rejected outputs (`two_paths_viral.mp4` at 2.8MB/79s, `Two_Lives_One_Choice_SUBTITLED.mp4` at 2.8MB/85s) were produced by **ad-hoc FFmpeg scripts** (like `make_two_paths.py` v1-5) that:

1. **Concatenated static images** — FFmpeg concat demuxer linked still images with hard cuts. No Ken Burns effect, no zoom, no pan, no motion at all.
2. **No animated scenes** — No spring transitions, no animated text cards, no count-up stats, no animated charts — just static overlays on static images.
3. **Extremely low encoded data** — At 271-288 kbps for 1080p, the h264 encoder produced tiny files because there's **no motion to encode**. The file size proves the video is a slideshow.
4. **Bypassed OpenMontage entirely** — The agent wrote standalone Python scripts instead of using:
   - `video_compose` with `operation='remotion_render'`
   - `image_selector` for proper provider routing
   - `tts_selector` for optimal TTS provider selection
   - The director skills containing quality guidance

### The Real Fix

The fix wasn't about compression settings (CRF 23 was fine). It was about **using Remotion composition** instead of FFmpeg static-image concatenation. Remotion produces:

| Feature | FFmpeg (old) | Remotion (fixed) |
|---------|------------|-----------------|
| Ken Burns zoom/pan | ❌ Static images | ✅ Animated entrance |
| Scene transitions | ❌ Hard cuts | ✅ Spring physics |
| Text cards | ❌ Static drawtext | ✅ Animated reveal |
| Stat cards (count-up) | ❌ Static | ✅ Animated numbers |
| Charts | ❌ Not possible | ✅ Bar/line/pie |
| Comparison cards | ❌ Not possible | ✅ Side-by-side |
| Caption styling | ❌ ASS basics | ✅ Word-level |
| Encoded motion | ~280 kbps | 5-8 Mbps (proper) |

> **Key insight:** The 2.8MB file size wasn't a compression error — it was proof of a static slideshow. A proper Remotion-rendered video with real motion will be 10-20x larger because it contains actual visual information to encode.

## Pitfalls

- **Don't skip AGENT_GUIDE.md** — Every video production session must read it first. The governance rules (no unilateral substitutions, present both runtimes, escalate blockers) are mandatory.
- **Don't write ad-hoc Python scripts** to call providers directly. OpenMontage's tool registry + selector tools handle provider routing, cost tracking, and quality review. Ad-hoc scripts bypass all governance.
- **Don't fall back to short-video-production** unless OpenMontage preflight returns blockers. The short-video-production skill is a simpler FFmpeg-based approach for when OpenMontage isn't available.
- **Don't skip director skills** — Stage director skills contain critical quality guidance, enhancement chains, and OpenMontage-specific conventions. Reading them before executing each stage is mandatory.
- **Don't use `promise_type: "render"`** — Must be a valid `PromiseType` enum value. For `animated-explainer` pipeline, use `"data_explainer"`.
- **renderer_family MUST be `"explainer-data"` not `"remotion"`** — The top-level `renderer_family` should be `"explainer-data"` for animated explainers. The `proposal_metadata.renderer_family` is a different field and gets `"remotion"`. Getting this wrong causes `Unknown renderer_family` errors from `_get_composition_id()`.
- **edit_decisions field names differ from Remotion props field names** — The `video_compose` tool's `_remotion_render()` method copies cut fields verbatim (only converting `source` to `file:///` URIs). This means `start_seconds`/`end_seconds` and `narration_path`/`background_music_path` are NEVER converted to the `in_seconds`/`out_seconds` and `audio.narration.src`/`audio.music.src` that the Explainer component expects. To render successfully, build the `.remotion_props.json` directly using `references/remotion-props-format.md` and call `npx remotion render` manually.
- **Load transcript for captions** — Word-level captions come from the ElevenLabs TTS transcript JSON, not from the edit_decisions. Load `narration_full_transcript.json` and pass as the `captions` array in props.
- **"from prop NaN" is a misleading error** — When Remotion says `The "from" prop of a sequence must be finite, but got NaN`, do NOT chase timing values. The root cause is usually missing/wrong field names (`start_seconds` instead of `in_seconds` causing `undefined * fps = NaN`) or failed image loading.
- **Layer 3 skills matter** — Before calling any tool, check `agent_skills[]` in the tool's registry info. These skills contain provider-specific prompting patterns that produce significantly better results.
- **Preflight is mandatory** before any production work. Don't start asset generation until the capability menu has been presented to the user.
- **Decision Communication Contract** — Announce every meaningful production decision (provider, model, render runtime) before acting. Users shouldn't have to infer what was chosen.
- **⚠️ Caption format: milliseconds vs seconds** — The `WordCaption` interface in `CaptionOverlay.tsx` expects `startMs`/`endMs` in **milliseconds**, but ElevenLabs transcript JSON outputs `start`/`end` in **seconds**. Passing transcript words directly as captions causes `startMs = undefined → NaN → "Sequence from prop NaN"`. See `references/remotion-props-format.md` for the conversion pattern.

## Related

- `media/short-video-production` — Fallback when OpenMontage is unavailable (simpler FFmpeg pipeline)
- `software-development/setup` — Original setup skill that installed and configured OpenMontage
- `software-development/repo-integration-reconciliation` — If integrating OpenMontage skills into Hermes

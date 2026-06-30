---
name: character-animation-workflow
description: >-
  Full end-to-end workflow for producing character-animation videos in OpenMontage.
  Covers pipeline selection, preflight, stage-by-stage execution (research → proposal
  → script → character_design → rig_plan → scene_plan → assets → edit → compose →
  publish), tool chain order, and user interaction patterns. NOT for text-over-image
  slideshows — use this for @onlymrbones-style GTA character skits, mascot explainers,
  and any video with animated characters acting out a story.
license: MIT
---

# Character Animation Workflow

## When to Use

Use this skill when the user asks for an animated video with **characters that act**:
- @onlymrbones GTA-style character skits
- Financial comparison videos with 2 characters acting out choices
- Mascot explainers with character actions
- Any video where the core ask is "animated characters doing things," not "text over images"

**Do NOT use** this skill for text-card slideshows, pure data visualization, or cinematic trailer edits. Those belong in the `animation` or `animated-explainer` pipelines.

## Anti-Pattern: Don't Force Character Animation Through Explainer

The **Explainer** pipeline (`animated-explainer`) renders **text cards over images with spring animations**. It looks like a slideshow. NEVER use it for character animation or @onlymrbones-style kinetic videos, no matter how many cuts or overlays you add. The user will notice and call it a slideshow.

The **character-animation** pipeline uses **SVG-rigged characters** (jointed parts, pose libraries, action timelines) that perform real motion and acting.

## Step 1: Preflight — Discover Capabilities

Before starting ANY pipeline work, discover the tool registry:
```python
from tools.tool_registry import registry
registry.discover()
```

**IMPORTANT: `registry.discover()` may hang** — on this machine `pkgutil.walk_packages` imports every tool module under `tools/`, and some modules make network calls or block on import. If it hangs for more than 30 seconds, import the specific tools you need directly instead of using `registry.discover()`:
```python
from tools.character.character_animation import CharacterSpecGenerator, SvgRigBuilder, PoseLibraryBuilder, CharacterRigRenderer, CharacterAnimationReviewer, ActionTimelineCompiler
from tools.video.video_compose import VideoCompose
from tools.video.hyperframes_compose import HyperFramesCompose
```

Check these specifically:
- `"character_animation"` capability — must be 6/6 configured
- `"remotion"` — should be available (default render runtime)
- `"hyperframes"` — optional, present both if available
- `"image_generation"` — for backgrounds and character art
- `"tts"` — for narration
- `"music_generation"` — for background music
- `"video_post"` — for FFmpeg processing

Preflight output is your truth source for what tools exist on this machine. Save the summary in a note for the session.

## Step 2: Pipeline Selection — Read the Manifest

The pipeline manifest is at `pipeline_defs/character-animation.yaml`. Always read it fully.

Key fields to extract:
- Stages (10 stages listed in order)
- Required skills per stage
- Checkpoint / human_approval requirements
- Compatible playbooks
- Budget default and max wall time

**Runtime selection** (from `pipeline_defs/character-animation.yaml`):
- When both Remotion AND HyperFrames are available, the proposal MUST present both to the user before locking `render_runtime`. Read `skills/meta/animation-runtime-selector.md`.
- When only Remotion is available (no HyperFrames), Remotion is the default.

## Step 3: Read the Executive Producer Skill

The EP skill at `skills/pipelines/character-animation/executive-producer.md` is the orchestration blueprint. Read it before executing any stage.

## Step 4: Stage-by-Stage Execution

Execute in strict order. Each stage reads the pipeline manifest's stage definition for checkpoint and approval rules.

### Stage 1 — Research
**Skill**: `skills/pipelines/character-animation/research-director.md`
**Produces**: `research_brief`
**Process**:
1. Identify what the reference uses (rigged animation, frame-by-frame, video gen, stills, mixed)
2. Research 3-5 relevant examples or techniques
3. Separate reproducible from manual/illustration/expensive
4. Record reusable animation primitives (walk cycle, blink, head turn, reach, etc.)
5. Output: character_animation_fit, reference_motion_type, required_character_actions,
   rig_complexity, manual_asset_risks, local_runtime_candidates

### Stage 2 — Proposal
**Skill**: `skills/pipelines/character-animation/proposal-director.md`
**Produces**: `proposal_packet` + `decision_log`
**Human Approval**: REQUIRED (checkpoint with `human_approval_default: true`)
**Must include per concept**: characters/roles, visual style, action complexity, rig reuse strategy, sample plan, audio architecture, music plan, render runtime options, cost estimate, honest limitation note
**Sample-first rule**: Propose a 10-15s sample before full asset generation (1 character, 1 expression change, 1 body action, 1 camera treatment, 1 audio cue)

### Stage 3 — Script
**Skill**: `skills/pipelines/character-animation/script-director.md`
**Produces**: `script` structured as action beats (not only narration)
**Human Approval**: REQUIRED

### Stage 4 — Character Design
**Tool**: `character_spec_generator` (CharacterSpecGenerator)
**Produces**: `character_design`
**Input**: characters array with:
- id, display_name, role, body_type, style
- required_emotions (neutral, happy, surprised, sad, etc.)
- required_actions (idle, blink, look, point, celebrate, panic, etc.)
- required_views (front, side, etc.)
- props, constraints
**Human Approval**: REQUIRED

Key: Each character needs a DISTINCT silhouette, role, and emotional range. Character count realistic for local rigging (2-3 usually max).

### Stage 5 — Rig Plan + Pose Library

**Tool 1**: `svg_rig_builder` (SvgRigBuilder)
**Input**: character_design
**Produces**: `rig_plan` with:
- parts: body, head, eyes, pupils, mouth, arms, legs (+ wings/tail if needed)
- joints: pivots, rotation ranges, scale ranges
- layers: ordered rendering
- required_poses: derived from actions

**Tool 2**: `pose_library_builder` (PoseLibraryBuilder)
**Input**: rig_plan
**Produces**: `pose_library` with:
- poses: idle, blink, look_left, look_right, surprised, plus custom per actions
- mouth_shapes: closed, small_o, wide, smile
- action_cycles: walk, breathe
**Human Approval**: not required by default (checkpoint only)

Read `skills/agents/skills/character-rigging/SKILL.md` before using the rig builder.

### Character Model Decision: Mascot vs Cast

**FIRST decision** before any design work: does this channel need a single recurring mascot or a multi-character cast?

| Signal | Choose Single Mascot | Choose Multi-Character Cast |
|--------|---------------------|---------------------------|
| Channel name matches character | ✅ "Mr Finance Guy", "Kuya Money" | ❌ "The Money Show" |
| Content is explainer / host-led | ✅ Character teaches to camera | ❌ Drama between characters |
| The user says "consistent face" | ✅ One recognizable brand | ❌ Ensemble storytelling |
| Comparison format needed | ✅ Character acts both sides via gestures | ✅ Each character represents one side |
| Production speed priority | ✅ One rig, faster production | More content variety in exchange for more rig work |

**User signal pattern**: If the user initially approves a cast then pivots to wanting ONE character ("i need a character to be consistent that will be the face of the channel"), capture that immediately — you were on the cast path and they want the mascot path. The single-mascot model wins for: channel-as-personality branding, profile picture consistency, faster production, and simpler viewer recognition.

### Single Mascot Design Principles

When building ONE recurring mascot for a faceless channel:

1. **Name = Channel name** — The character IS the channel. Mr Finance Guy, Kuya Piso, etc. Every video reinforces both.
2. **Signature items** — 2-3 permanent accessories that make the character instantly recognizable: sunglasses (the #1 most recognizable), a signature outfit color, a consistent prop (watch, hat, coffee cup).
3. **Premium aesthetic** — When the user says "good elegant fashion," use: tailored suit/blazer, crisp shirt, gold accents, dress shoes, structured hair. This signals authority and success for finance content.
4. **One pose per scene** — The character doesn't need full walk cycles. For explainers: host stand, point, explain with both hands, thinking chin-rub, react-surprised. 5-6 poses max.
5. **Color consistency** — Lock the character's palette in the channel brand kit. Never change the signature appearance between videos.
6. **The shades shortcut** — Sunglasses are the single most effective way to make a character look "cool" and reduce facial animation complexity by 40% (no blink timing, no eye tracking). If the user says "shades," say yes immediately.

For the actual batch generation pipeline when building a cast instead, use **batch SVG generation** from a shared body skeleton:

1. Define all characters in a single `cast_definitions.json` file (colors, clothes, props, expressions)
2. Write one Python `gen_svgs.py` that reads the JSON and outputs one `.svg` per character
3. Each character shares the same body skeleton (shadow, legs, body, arms, head)
4. Differentiation via: body color, skin tone, clothing template, headwear, props, eyebrow/mouth shapes
5. All characters share the same pose library — no per-character rig rebuilding

See `references/character-cast-production.md` for the full strategy, archetype templates (Pinoy finance channel), clothing template routing patterns, prop library, and verification workflow.

### Stage 6 — Scene Plan
**Skill**: `skills/pipelines/character-animation/scene-director.md`
**Produces**: `scene_plan`
**Input**: script, character_design, rig_plan, pose_library
**Each scene needs**: characters present, actions, camera/framing, background, effects
**Human Approval**: REQUIRED

### Stage 7 — Assets
**Tool**: `character_rig_renderer` (CharacterRigRenderer)
**Produces**: `asset_manifest`
**Also**: image generation for backgrounds, TTS for narration, music selection
**Read Layer 3 skills** for every generation/rendering tool used
**Human Approval**: depends on manifest (checkpoint)

### Stage 8 — Edit
**Tool**: `action_timeline_compiler` (ActionTimelineCompiler)
**Input**: scene_plan, character_ids, fps
**Produces**: action_timeline with timed actions per scene:
- Each scene: start_seconds, end_seconds, camera, background, effects
- Each action: at_seconds, duration_seconds, character_id, action_type, pose, easing
**Also produces**: edit_decisions
**Human Approval**: not required by default

### Stage 9 — Compose
**Tool**: `character_rig_renderer` (for browser preview + render package)
**Tool**: `video_compose` (for final MP4 render)
**Produces**: render_report, character_qa_report, final_review
**QA**: Read `skills/agents/skills/character-animation-qa/SKILL.md` for review protocol
**Check**: frame sampling, console errors, character visibility, motion deltas, ffprobe
**Human Approval**: not required by default

**CRITICAL: HyperFrames template output pitfall** — `character_rig_renderer.execute()` outputs a HyperFrames-style HTML composition using `<template>` tags. This format only renders correctly when consumed by the HyperFrames runtime (which processes `<template data-composition-id>`). In a plain browser or Playwright capture, `<template>` elements are NOT rendered — the page shows source code, not the character.

**If HyperFrames is NOT available** (check `render_engines` in `video_compose.get_info()`):
  - The `<template>`-based output from `character_rig_renderer` is NOT renderable as video.
  - **Workaround**: Create a standalone HTML page that inlines the SVG character + GSAP animation without using `<template>` tags. Extract the SVG markup from the template's inner HTML. Write GSAP timeline calls that animate the SVG parts directly (gsap.to/q() with selectors). Then capture via Playwright (see below).
  - Do NOT try to use `video_compose` with `render_runtime="hyperframes"` when HyperFrames is unavailable — it routes to a broken pipeline.
  - Remotion cannot natively render arbitrary SVG+GSAP animation pages. The video capture must be done through Playwright screenshot/recording.

**Playwright capture approaches** (when HyperFrames is unavailable and you are using a standalone HTML):

  **Option A: Record video (simpler, real-time)** — Use `browser.new_context(record_video_dir=...)`:
  ```python
  from playwright.sync_api import sync_playwright
  context = browser.new_context(
      viewport={"width": 1280, "height": 720},
      record_video_dir=video_dir,
      record_video_size={"width": 1280, "height": 720}
  )
  page = context.new_page()
  page.goto(html_url, wait_until="networkidle")
  page.wait_for_timeout(animation_duration_s * 1000)
  context.close()  # MUST close before accessing page.video
  browser.close()
  # Convert .webm to .mp4:
  ffmpeg -y -i input.webm -c:v libx264 -pix_fmt yuv420p output.mp4
  ```
  *Caveats*: Real-time (12s animation = 12s+ capture). Framerate depends on browser compositor (~25fps). page.video.path() is None until context.close().

  **Option B: Frame-by-frame capture (deterministic)** — requires `window.goToFrame(N)`:
  ```python
  page.goto(url, wait_until="domcontentloaded")  # NOT networkidle (CDN may hang)
  page.wait_for_timeout(2000)
  for frame in range(total_frames):
      page.evaluate(f"goToFrame({frame})")
      page.wait_for_timeout(5)
      page.screenshot(path=f"frame_{frame:06d}.png")
  ffmpeg -y -framerate 30 -i frame_%06d.png -c:v libx264 -crf 18 output.mp4
  ```
  See `references/playwright-frame-capture.md` for the full implementation.

  **Playwright CDN Pitfall**: The `wait_until="networkidle"` option hangs forever if CDN resources (GSAP from jsdelivr, Google Fonts) are unreachable. Always inline GSAP, use `domcontentloaded`, or set a timeout.
  
  ### Stage 10 — Publish
**Skill**: `skills/pipelines/character-animation/publish-director.md`
**Produces**: publish_log
**Human Approval**: REQUIRED

## Pre-Flight Pipeline Check (MANDATORY)

Before executing ANY video production task, verify your pipeline choice:

1. Open the project's `pipeline_defs/` directory and list available pipelines.
2. Confirm the pipeline name in your plan matches the user's stated need.
3. If the user wants **characters that act** (GTA skits, mascots, comparison characters), the pipeline MUST be `character-animation` — NOT `animated-explainer`.
4. If the user has previously complained about "slideshows" or "static videos", the #1 root cause is an Explainer/FFmpeg pipeline being used for character work. **Do not try to "fix" the Explainer pipeline — switch to the correct one.**

**The default-mode trap**: Agents frequently default to the Explainer/animated-explainer pipeline because it is the most-tested and first-to-mind. Even after a user complains it is a slideshow, agents often try to *fix* the render (asset paths, captions, overlays) rather than switching pipelines. This wastes sessions — in one case **multiple sessions** were spent trying to polish the Explainer pipeline before the obvious fix (pipeline switch) was made. If the user wants character animation, the pipeline choice is non-negotiable from the start.

**Key diagnostic signal**: A user saying "why is my videos just a good slideshow not animated story or something" is a COMPLAINT about the wrong pipeline, not a request for better Explainer polish. The fix is to switch to `character-animation`, not to improve text cards.

## Common Pitfalls

1. **Using the wrong pipeline**: Explainer pipeline (text cards) CANNOT do character animation. Use character-animation pipeline. If the user wants animated characters, this is non-negotiable. This is the #1 source of user frustration — MULTIPLE sessions were wasted on the wrong pipeline before this was caught.
2. **Blaming the user for pipeline mistakes**: If the output is wrong, check YOUR pipeline choice first before asking the user what they want. "Why is it a slideshow" should be answered by pipeline audit, not questioning the user.
3. **Skipping preflight**: Always discover capabilities first. Character_animation tools may not be fully configured.
4. **Skipping the sample**: The proposal MUST include a 10-15s sample plan. Get it approved before full asset generation.
5. **Not reading stage skills**: Each director skill has specific process, output guidance, and quality bars. Read them during that stage, not upfront.
6. **Bypassing user approvals**: Pipeline stages with `human_approval_default: true` require user sign-off. Frustrating the user with wrong output is worse than asking for approval.
7. **Character appearance consistency**: SVG parts need consistent art style across all poses. Invest in prompt engineering for the base character, then vary poses programmatically.
8. **@onlymrbones style specifically**: They want GTA-style 2D cartoon characters with game UI elements (health bars, alerts, stat overlays). The Explainer components can provide the UI overlays, but the character acting must come from the svg_rig pipeline. Use Remotion for composition, not HyperFrames.
9. **HyperFrames template not rendering**: `character_rig_renderer` outputs `<template>` tags (HyperFrames format). These DO NOT render in a plain browser — the page appears to show source code. If HyperFrames is unavailable, create a standalone HTML page that inlines the SVG directly (no `<template>` wrapper) and captures via Playwright.
10. **Playwright CDN hang** — Loading GSAP from a CDN with `wait_until=networkidle` may hang the browser indefinitely in headless mode. Options: (a) inline GSAP in the HTML, (b) use `wait_until=domcontentloaded`, or (c) set an explicit timeout.
11. **Character cast verification** — After generating batch SVGs for a cast, verify visually before committing: load all SVGs side-by-side in a Playwright page, screenshot, and analyze with vision_analyze. Check distinct silhouettes, color differentiation, visible props, and expression matches. A frame where vision_analyze confuses characters (e.g., says character A has glasses when they shouldn't) signals colors/silhouettes aren't distinct enough.
12. **Blind-model video review** — If your model lacks vision and cannot analyze video frames directly, build a static frame-comparison page: extract frames at 5s intervals from both the reference and your output via `ffmpeg -ss $t -i input.mp4 -vframes 1 frame.jpg`, serve them via `python -m http.server`, and open the side-by-side page in the browser. Let the USER look at the comparison and describe issues — you cannot assess visual quality without vision.
13. **PIL compositing vs SVG rigs** — The `replicate_video.py` approach (PIL/Pillow scene composition from character PNGs + prop images) is a fast-track for replicating comparison-format videos when assets already exist. It is NOT a replacement for the SVG-rigged character-animation pipeline (which does fluid motion). Use PIL compositing for batch-produced 9:16 finance shorts where the style is locked; use SVG rigs for character-driven storytelling with real animation.

## Verification

Before declaring done:
- [ ] ffprobe confirms technical specs (duration, resolution, fps, audio)
- [ ] Character QA report is pass (not revise or fail)
- [ ] Final review covers frame sampling, visual spotcheck, audio spotcheck, promise preservation
- [ ] User has approved the final output

## Support Files

This skill ships with supporting files under the skill directory:

| File | Purpose |
|------|---------|
| `references/affiliate-video-production.md` | GTA-style product video template for affiliate marketing: product card, pricing display, HUD stats, CTA patterns, character matching, disclosure requirements |
| `references/playwright-frame-capture.md` | Playwright + ffmpeg render pipeline: code, decisions, performance data |
| `references/slideshow-diagnosis.md` | Root-cause checklist when user says "it's a slideshow" — pipeline audit, asset path fix, quick triage |
| `references/character-cast-production.md` | Batch SVG generation from JSON definition: cast strategy, archetypes, clothing routing, props, verification |
| `scripts/build_animation.py` | Template for generating the animation HTML from scene plan + SVGs |
| `templates/` | (Optional) Starter templates for scene plans, rig configs |

Check `references/` for detailed guides before running Stage 9 (Compose).  
| `references/single-mascot-design.md` | Premium single-character design for faceless channels (Mr Finance Guy aesthetic, pose library, vision verification traps) |
| `references/pil-ffmpeg-compositing.md` | Fast-track PIL+FFmpeg replication path using pre-rendered character PNGs and prop grids — skip SVG rigging when assets already exist |
| `references/mr-finance-guy-replication.md` | Mr Finance Guy video replication pipeline: 10-scene structure, layout preferences, toolchain, and user-approved scene composition for finance education shorts |
| `references/blind-video-comparison.md` | Frame-comparison workflow for reviewing generated video vs reference when the agent model lacks vision — extract frames, serve via HTTP, let user compare |
Use `scripts/` patterns rather than re-inventing the build pipeline.

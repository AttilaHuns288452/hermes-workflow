# Repo Pipeline Workflow Protocol

When a GitHub repo has its own agent-driven pipeline system (AGENT_GUIDE.md, pipeline manifests, stage director skills, tool registry), follow this protocol instead of writing ad-hoc scripts.

## Detection Signals

Check for these files after cloning:
- `AGENT_GUIDE.md` — agent contract and operating guide
- `PROJECT_CONTEXT.md` — architecture and conventions
- `pipeline_defs/*.yaml` — pipeline stage definitions
- `skills/pipelines/<name>/` — stage director skills
- `tools/tool_registry.py` — capability discovery
- CLAUDE.md / AGENTS.md that reference a pipeline system

## Protocol

### 1. Read the Agent Guide First

Always read `AGENT_GUIDE.md` or `PROJECT_CONTEXT.md` before running anything. These contain the repo's "Rule Zero" — the non-negotiable workflow rules.

### 2. Run Preflight

Discover what tools are actually available:
```python
from tools.tool_registry import registry
registry.discover()
envelope = registry.support_envelope()  # available tools summary
catalog = registry.capability_catalog() # all tools by category
```

### 3. Pick the Right Pipeline Manifest

Match the user's request to a pipeline in `pipeline_defs/`:
- `animated-explainer` — AI-generated explainer videos (best for narrative/tutorial content)
- `talking-head` — footage-based presenter videos
- `screen-demo` — screen recording demos
- `clip-factory` — short-form batch extraction
- `hybrid` — source-plus-support hybrid

### 4. Execute Stage by Stage

For each stage in the pipeline manifest:
1. **Read the director skill** first: `skills/pipelines/<pipeline>/<stage>-director.md`
2. **Follow the skill's process** — these contain tool-specific guidance, quality bars, and pitfalls
3. **Produce the required artifact** (validated against `schemas/artifacts/`)
4. **Self-review** against the manifest's `success_criteria` and `review_focus`

### 5. Don't Skip the Human Approval Gates

Many pipelines have approval gates at critical stages (proposal, script). Present choices with cost estimates and wait for explicit approval before proceeding.

### 6. Use the Proper Compose Tools

Don't write raw FFmpeg scripts. Use the repo's compose tools:
- `video_compose` — routes to FFmpeg/Remotion/HyperFrames based on `edit_decisions.render_runtime`
- `audio_mixer` — handles narration/music mixing
- `subtitle_gen` — generates proper subtitle files
- `video_stitch` — multi-clip assembly

## OpenMontage Example Walkthrough

Repository: `calesthio/OpenMontage`

### Architecture
- **Instruction-driven** — the AI agent IS the intelligence. Python exists only for tools and persistence.
- **3 knowledge layers**: Layer 1 (tool registry), Layer 2 (skill docs), Layer 3 (external API guides)
- **Pipeline stages**: idea → research → proposal → script → scene_plan → assets → edit → compose → publish

### Standard Pipeline: `animated-explainer`

| Stage | Skill | Produces | Cost |
|:------|:------|:---------|:----:|
| research | `research-director` | `research_brief.json` | $0 (web search only) |
| proposal | `proposal-director` | `proposal_packet.json` | $0 (needs user approval) |
| script | `script-director` | `script.json` | $0 |
| scene_plan | `scene-director` | `scene_plan.json` | $0 |
| assets | `asset-director` | `asset_manifest.json` | ~$0.20-0.50 |
| edit | `edit-director` | `edit_decisions.json` | $0 |
| compose | `compose-director` | `render_report.json` | $0 (local) |
| publish | `publish-director` | `publish_log.json` | $0 |

### Tool Registry API Patterns (from real usage)

The registry uses object-based access, not dict access. Common patterns:

```python
from tools.tool_registry import registry
registry.discover()

# Get all tools by capability (returns objects, not dicts)
tts_tools = registry.get_by_capability('tts')
for t in tts_tools:
    print(t.name, t.status)          # ✅ .name and .status — not ["name"]

# Get capability catalog (returns list of dicts)
cc = registry.capability_catalog()
for cap, tools in cc.items():
    for t in tools:
        print(t['name'], t['status'])  # dict access works here

# Get support envelope (limited summary)
env = registry.support_envelope()

# NO get_by_name method — use get_by_capability + filter, or iterate list_all
# registry.get_by_name('video_compose')  # ❌ AttributeError
vc_list = registry.get_by_capability('video_post')
vc = next((t for t in vc_list if t.name == 'video_compose'), None)

# Check render engine availability
from tools.video.video_compose import VideoCompose
info = VideoCompose().get_info()
info['render_engines']  # {'ffmpeg': bool, 'remotion': bool, 'hyperframes': bool}

# Check specific subtool availability (from capability catalog entries)
for t in cc.get('subtitle', []):
    if 'remotion' in t.get('name', ''):
        print(f"Remotion caption burn: {t.get('status')}")
```

### Composition Options

The `video_compose` tool supports multiple render engines:
- **FFmpeg** — Ken Burns pan-and-zoom on static images. Functional but limited.
- **Remotion** — React-based animated scene components (text cards, stat cards, comparison cards, charts, spring transitions). Much higher quality, professional motion graphics feel. Requires Node.js.
- **HyperFrames** — HTML/GSAP kinetic typography and custom motion. Requires `npx` and HyperFrames CLI.

Check availability via:
```python
from tools.video.video_compose import VideoCompose
info = VideoCompose().get_info()
info['render_engines']  # {'ffmpeg': bool, 'remotion': bool, 'hyperframes': bool}
```

### Runtime Selection Protocol (Mandatory in Proposal Stage)

The `proposal-director` requires you to present BOTH runtimes to the user before selecting one:

1. Query `video_compose.get_info()["render_engines"]` — check if `remotion` and `hyperframes` are `True`
2. Present both to the user with brief analysis:
   - **Remotion** — one line on fit (React scene stack: text_card, stat_card, bar_chart, line_chart, comparison_card, etc.), one line on tradeoff
   - **HyperFrames** — one line on fit (HTML/GSAP motion, registry blocks, kinetic typography), one line on tradeoff
   - **FFmpeg** — fallback when neither is available
3. Recommend one with rationale tied to the brief's `delivery_promise`, `visual_approach`, and whether word-level caption burn is required (that forces Remotion)
4. Wait for explicit user approval before writing `render_runtime` into the proposal
5. Log the decision in `decision_log` with both runtimes in `options_considered`

**Fit cheat-sheet:**
- Existing React scene stack (text_card, stat_card, bar_chart, comparison, callout, etc.) → recommend **Remotion**
- Kinetic typography, custom HTML motion, registry-block-driven scenes → recommend **HyperFrames**
- Word-level/karaoke captions required → **Remotion only** (HyperFrames caption parity deferred)
- Static images only, no animations → **FFmpeg** (simpler setup)

### Mandatory Sample Protocol

After the user approves a concept (before entering the script stage), produce a 10-15 second sample:
1. The opening hook (first 5-7 seconds) + one representative middle scene
2. Actual TTS voice, actual visual style, music bed snippet
3. Present with: "Here's a preview. Does this feel right?"
4. Iterate until approved, then proceed to full production

This is required for reference-driven productions but also useful for catching direction mismatches early on any production.

### Scene Plan: 5-Aspect Checklist (Mandatory per Scene)

Every scene in the scene plan artifact must specify all five aspects. For Remotion-native scenes, "Camera" can be marked N/A explicitly (not silently omitted):

1. **Subject** — type + key visual attributes; for diagrams, the foregrounded data element (node, bar, KPI being highlighted)
2. **Subject Motion** — actions in temporal order; for animated diagrams, the order nodes/edges/values appear or change
3. **Scene** — overlays (separately!) + POV + setting + time of day + scene dynamics. For Remotion scenes, "setting" maps to background treatment + theme
4. **Spatial Framing** — shot size + position-in-frame + depth (FG/MG/BG) + camera-height-relative; for static Remotion scenes, document the layout grid + which element occupies the visual center
5. **Camera** — playback speed → lens → height → angle → focus → steadiness → movement. Mark N/A for native-Remotion scenes; specify fully for `generated`/`broll` scenes

**Overlays callout:** Overlays (titles, subtitles, HUD, watermarks, lower-thirds, section titles, stat chips) are NOT part of the scene's foreground/midground/background depth axis. List them separately in scene metadata. Never describe an overlay as "in the foreground."

### Script Word Budget Calibration

| Pace | Words/Minute | Use When |
|:-----|:-----------:|:---------|
| Conversational | ~150 wpm | Default for most explainers |
| Contemplative | ~120 wpm | Complex topics needing processing time |
| Energetic | ~180 wpm | Short-form, TikTok/Reels |
| Technical | ~130 wpm | Code walkthroughs, deep-dives |

**Practical calibration:** 227 words @ 147 WPM ≈ 93 seconds. A comparison script with hook → setup → teen → adult → old → climax → landing (7 sections) typically lands at ~190-230 words for a 75-93s video. Each scene's narration should leave 0.5-1s of silence between transitions for visual breathing room.

### Executive Producer (EP) Pattern

Some pipelines have an EP pattern where one skill orchestrates all stages serially:
- The EP loads each director skill, injects cross-stage context (budget remaining, style anchors, prior artifacts)
- The EP performs cross-stage checks (narration duration vs scene duration, budget spent vs budget remaining)
- The EP can send work BACK to a prior stage if downstream findings invalidate upstream work
- Max 3 revisions per stage, max 3 total send-backs (anti-loop protection)

### Common Pitfalls

- **Skipping the pipeline**: Writing ad-hoc FFmpeg/Python scripts instead of following the pipeline produces lower quality output and wastes the repo's built-in capabilities
- **Not reading director skills**: Each director skill contains specific guidance about tool usage, quality bars, and formatting that produces dramatically better output
- **Forgetting preflight**: Always run `registry.discover()` first to know what's available before designing a production plan
- **Bypassing approval gates**: The proposal stage exists precisely to get user approval before spending money. Don't skip it.
- **Raw FFmpeg when Remotion is available**: If Remotion is available (render_engines.remotion=true), design for animated component scenes — stat cards, comparison cards, spring transitions — rather than AI images with Ken Burns pan
- **Not presenting both runtimes**: When both Remotion and HyperFrames are available, silently defaulting to one is a critical reviewer finding. Always present both.
- **Registry object confusion**: Registry tools are objects with `.name` and `.status`, not dicts with `["name"]` and `["status"]`. The `capability_catalog()` returns dicts, but `get_by_capability()` returns objects. Accessing them wrong raises `TypeError: 'ToolName' object is not subscriptable`.
- **Silently omitting the 5-aspect scene checklist**: Every scene in the scene plan must explicitly state Subject, Subject Motion, Scene, Spatial Framing, and Camera. Silent omission is the most common failure mode.

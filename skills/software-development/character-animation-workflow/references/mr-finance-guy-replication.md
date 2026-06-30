# Mr Finance Guy — Video Replication Pipeline

## When to Use

Replicate an existing approved video's format for a new topic in the Mr Finance Guy finance-education series. Used when the user says "replicate this video for a different topic."

## Reference Video Structure

The approved videos follow a **Hook → Bridge → Rounds → Kicker → Closing** structure, ~71s total, 10 scenes:

| # | Scene | Duration | Content |
|---|-------|----------|---------|
| 1 | intro | 4s | Both labels, character center, "A vs B. What's the difference?" |
| 2-4 | side_A_1-3 | 10+8+6s | A-side content (negative/worse option), character left pointing left, images right |
| 5 | transition | 4s | Bridge statement: "A protects today. But for tomorrow you need B." |
| 6-8 | side_B_1-3 | 10+8+8s | B-side content (positive/better option), character right pointing right, images left |
| 9 | kicker | 8s | Side-by-side comparison, character center, summary bullets |
| 10 | closing | 5s | CTA, character center, "Follow for more." |

## Script Writing Rules

- **~150-170 words total** across all 10 scenes
- Keep each narration segment tight (one key idea per scene)
- Narration text drives both the TTS audio AND the on-screen text overlay
- Simple English, conversational tone (Filipino audience, but English-only delivery)
- Each scene's spoken line becomes the bottom narration bar text

## Layout — User-Confirmed Preferences

### Scene Composition

```
┌──────────────────────────────┐
│        LABEL HEADER          │  ← SAVING or INVESTING (color-coded)
│     ─── underline ───        │
│                              │
│   ┌──────┐     ┌─────────┐   │
│   │ IMAGE │     │         │   │
│   │ CARD  │     │ CHAR    │   │
│   │       │     │ ACTER   │   │
│   └──────┘     └─────────┘   │
│                              │
│  ┌────────────────────────┐  │
│  │ Narration text overlay │  │  ← semi-transparent black bar
│  └────────────────────────┘  │
└──────────────────────────────┘
```

**Critical rules (user enforced by iteration v1→v2→v3→v4):**

1. **Character BESIDE images** — DO NOT place character on one side and images on the other with dead space between. They must form a grouped composition.
2. **1-2 images max per scene** — Never use a 3×2 grid of 6 tiny cards. Use 1-2 larger cards (280-300px wide).
3. **Character size** — ~48-52% of screen height. Not too small (rejected at 42%).
4. **Character position from TOP** — Anchor at `char_y = 230` (fixed pixel from top edge), NOT from bottom (`H - char_h - 140`). Positioning from bottom puts the character's head at 45%+ down the screen, wasting the upper half.
5. **Pose points TOWARD the image** — Critical: if images are on the RIGHT, character must use `explain_right` (points right toward them). If images are on the LEFT, use `explain_left`. A character pointing AWAY from the content looks broken.
6. **Narration text overlay** — Always show the spoken words at the bottom (H-75) in a semi-transparent black bar (`fill=(0,0,0,140)`). Text should match the TTS script verbatim.
7. **Label header** — Color-coded label at top with underline (same as reference).
8. **Existing props only** — `load_prop()` silently returns `None` for missing images. Before rendering, list props with `ls props/` and only reference filenames that exist. Common working props: `coins`, `uptrend`, `investingsaving`, `receipt`, `working`, `businessloan`, `rentalproperty`, `mortage`, `studentloan`, `smallbusiness`, `creditcard2`, `thinking`.

### Layout Variant (Saving vs Investing example)

- **Side A (e.g. Saving, blue #1E64DC)**: Character LEFT at W×0.30 with `explain_right` pose (points RIGHT at images), image card(s) on the RIGHT at W-40-card_w
- **Side B (e.g. Investing, green #28B43C)**: Character RIGHT at W×0.70 with `explain_left` pose (points LEFT at images), image card(s) on the LEFT at ~30px
- **Single image**: 320×300 card, large prop (180×180 inside)
- **Two images**: 280×250 cards stacked vertically with 15px gap

## Toolchain

```
Python PIL/Pillow       — scene generation (ImageDraw, ImageFont, Image)
ElevenLabs TTS          — narration audio (Rachel voice 21m00Tcm4TlvDq8ikWAM)
FFmpeg                  — compose segments, add audio, add background music
```

### Key Paths

```
Character poses: ~/Downloads/Channel/Character_models_poses/bg_removed/ (18 PNGs)
Props:            ~/OpenMontage/projects/mr-finance-guy/<topic>/props/ (copy from bad-debt)
Background music: ~/OpenMontage/projects/mr-finance-guy/bad-debt-vs-good-debt/audio/bg_music.wav
Output:           ~/OpenMontage/projects/mr-finance-guy/<topic>/output/
Approved:         ~/Downloads/Channel/approved videos for production/
```

### Script Template

Copy `replicate_video_v3.py` from a completed project. Adapt:
1. Change scene definitions (label, color, props, narration text)
2. Change TTS script in `generate_tts.py`
3. Run: `python replicate_video_v3.py` → `python generate_tts.py` → `python compose_final_v3.py`

## Pitfalls

- **Missing `import shutil`** in replicate scripts — causes NameError at copy step
- **Props not found** — copy from existing replica project first: `cp <bad-debt>/replica/props/* <new>/props/`
- **Narration bar too high** — keep at H-75 to avoid overlapping character
- **Character too small** — user rejected <42% height. Use 48-52%.
- **Grid layout rejected** — user explicitly rejected 3×2 grid of 6 cards. Max 2 images.
- **Character too far from center** — keep at W×0.28-0.42 for left, W×0.58-0.72 for right. Never W×0.2 or W×0.8.

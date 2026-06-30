---
name: tiktok-finance-video
version: "1.0"
description: >-
  Produce viral TikTok finance shorts using the "two lives comparison" storytelling format.
  Full pipeline: script → PIL image scenes → edge-tts narration → FFmpeg composition.
  Trigger when user wants: finance TikTok, comparison video, two-person money story,
  viral finance short, "two lives one choice" format, risk vs comfort video.
---

# TikTok Finance Video Production

## Core Concept

Produce comparison-based finance storytelling videos for TikTok. The signature format:
two characters start equal, make different financial choices, diverge over time.
One takes risks (investing, courses, side hustles, trading) — fails repeatedly but compounds skills/wealth.
The other consumes/plays it safe — comfortable but fragile.
Message: "Risk on assets vs risk on liabilities" — not "save vs spend."

## User Preferences

- Filipino, Taglish audience in mind (but English narration default)
- Monetization-focused: every video should drive toward affiliate/product monetization
- Hates verbose fluff — get to the video, don't narrate the pipeline
- Wants end-to-end execution: "don't stop until the video is done"
- Prefers options before committing (3 angle concepts)
- Loves visual polish — clean dark theme with accent colors
- **ElevenLabs TTS mandatory for all voiceovers.** Never default to OpenAI TTS, edge-tts, or any other TTS provider. Always use ElevenLabs Rachel voice (UUID `21m00Tcm4TlvDq8ikWAM`). API key at `~/Documents/Projects/MoneyPrinterTurbo/.elevenlabs_key`; set `ELEVENLABS_API_KEY` env var before calling the tool.

## Storytelling Rules

1. **Focus on the risk-taker's journey** — the comparison character provides contrast but the hero is the one who risks
2. **Show failure as part of the journey** — multiple failed attempts, not instant success
3. **Compound learning** — every failure teaches something; skills stay forever
4. **Visual wealth divergence** — use charts, numbers, comparison bars to show the gap growing
5. **Emotional arc**: Hook → Setup → Struggle → Breakthrough → Payoff → CTA

---

## Related Skills

- **`character-animation-workflow`** — **Preferred pipeline for character-driven comparison videos.** OpenMontage's `character-animation` pipeline produces SVG-rigged characters with GSAP animation, action timelines, and GTA-style HUD overlays — replacing the static PIL scenes and FFmpeg composition described in this skill. Use `tiktok-finance-video` for format-specific guidance (script structure, storytelling rules, user preferences) and `character-animation-workflow` for the technical pipeline.
- `media/short-video-production` — Fallback FFmpeg pipeline

### Technical Pipeline

### Stack (Windows-compatible)
- **Characters**: SVG-rigged characters via `character-animation` pipeline (preferred) or Python PIL/Pillow (fallback)
- **Narration**: ElevenLabs only (Rachel voice, UUID `21m00Tcm4TlvDq8ikWAM`). NEVER use edge-tts, OpenAI TTS, or any other provider.
- **Composition**: Remotion (preferred) or FFmpeg (H.264, AAC, 1080×1920 vertical 9:16) as fallback
- **Subtitles**: Burned in via FFmpeg `subtitles` filter

### Output Specs
| Property | Value |
|----------|-------|
| Resolution | 1080×1920 (9:16 vertical) |
| Duration | 60-90s (TikTok sweet spot) |
| FPS | 30 |
| Video codec | H.264 (libx264) |
| Audio codec | AAC, 24kHz |
| Container | MP4 |
| Subtitles | Burned-in, white text + black outline, bottom-positioned |

### Scene Structure (8 scenes for ~85s)

| # | Scene | Duration | Visual Type |
|---|-------|----------|-------------|
| 1 | Hook/Title | 8s | Title card + character silhouettes + VS divider |
| 2 | Childhood | 10s | Split-screen: learning vs playing |
| 3 | Teenage Divergence | 12s | Split-screen: courses/books vs toys/gadgets |
| 4 | Young Adult Risks | 15s | Timeline of failures + growth chart |
| 5 | Comfort Zone | 8s | Dashboard stats + warning box |
| 6 | Middle Age | 12s | Wealth comparison bars ($850K vs $120K) |
| 7 | Old Age | 10s | Freedom vs survival split |
| 8 | CTA | 10s | Bold message + hashtags |

### Color Palette
- Background: `#1a1b26` (dark navy)
- Blue (saver/neutral): `#7aa5ff`
- Red (spender/warning): `#ff9e9e`
- Green (growth/success): `#5cca8c`
- Yellow (accent): `#ffd700`

### Production Steps

1. **Generate scenes** — Python PIL script creating all 8 PNGs
2. **Generate narration** — edge-tts per scene, save as MP3
3. **Adjust audio timing** — speed up/slow down to match video duration
4. **Compose video** — FFmpeg concat images → video, merge audio
5. **Burn subtitles** — SRT file → burned-in text overlay
6. **Verify** — ffprobe final output

### Key FFmpeg Patterns

**Image sequence to video:**
```bash
ffmpeg -y \
  -loop 1 -t 8 -i scene_01.png \
  -loop 1 -t 10 -i scene_02.png \
  ... \
  -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps=30[v0]; ... [v0][v1]...concat=n=8:v=1:a=0[outv]" \
  -map "[outv]" -c:v libx264 -pix_fmt yuv420p -r 30 -t 85 output.mp4
```

**TTS per section (write text to file first to avoid shell escaping):**
```bash
echo "text here" > temp.txt
edge-tts -v en-US-GuyNeural --rate="-15%" --write-media output.mp3 -f temp.txt
```

**Speed-adjust audio:**
```bash
ffmpeg -y -i narration.mp3 -filter:a "atempo=1.87" -vn adjusted.mp3
```

**Burn subtitles:**
```bash
ffmpeg -y -i video.mp4 -vf "subtitles=subtitles.srt:force_style='FontName=Arial,FontSize=28,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Alignment=2,MarginV=80'" -c:a copy output.mp4
```

### Windows Gotchas
- `python3` = Windows Store stub → use `python` (real Python 3.11)
- `edge-tts` CLI syntax: `-t TEXT -v VOICE --write-media FILE` (not `--text`)
- For long text, write to file first then use `-f FILE` to avoid shell escaping issues
- FFmpeg subtitles filter: use relative path or escape `:` and `\` properly
- `textbbox` is on `ImageDraw` not `Image` — use `draw.textbbox()` not `img.textbbox()`

### Narration Voice\n- **Default: ElevenLabs Rachel** (UUID `21m00Tcm4TlvDq8ikWAM`) — warm, natural female voice\n- **Alternative:** ElevenLabs other voices if the format needs a different tone\n- **Mandatory:** ElevenLabs is the ONLY TTS provider for this user. Never use edge-tts, OpenAI TTS, or any other provider for voiceover.\n- **API key location:** `~/Documents/Projects/MoneyPrinterTurbo/.elevenlabs_key`\n- **Rate:** Do not speed-change ElevenLabs narration — generate at native speed and calibrate the video to match the delivered audio.

### Subtitle Style
- Font: Arial
- Size: 28
- Color: White (#FFFFFF)
- Outline: Black, 2px
- Position: Bottom center (Alignment=2, MarginV=80)
- Max ~40 chars per line, 2 lines max

## Kinetic / Game-Style Remotion Techniques

When the user requests an **@onlymrbones / GTA / brainrot / animated-film** style (super-fast cuts, game UI elements, kinetic text), switch from standard comparison cards to game-style components with rapid pacing:

### Narration Speed-Up for Brainrot Pacing

Standard narration at ~150 wpm (105s for 237 words) is too slow. Speed up to 1.3x for the rapid-fire feel:

```bash
ffmpeg -y -i narration_full.mp3 -filter:a "atempo=1.3" -vn narration_fast.mp3
```

A 237-word script at 1.3x → ~80s = ~2400 frames at 30fps.

### Scene Structure: 23+ Fast Cuts

Break the narrative into **2–4 second micro-scenes** instead of 8–15s. Typical structure:

| Act | Cuts | Duration | Style |
|-----|------|----------|-------|
| Hook | 3 cuts (3.5s each) | 10s | HeroTitle + Comparison + HeroTitle |
| Person A (Assets) | 7 cuts (2.5–3.5s) | 21s | HeroTitle → Callout (tip) → ProgressBar → Callout (warning ×3) → Callout (tip) |
| Person B (Liabilities) | 6 cuts (3–5s) | 21s | HeroTitle → Callout (warning ×4) → ProgressBar |
| Climax | 4 cuts (3–6.5s) | 18s | HeroTitle → BarChart → StatCard ×2 |
| Lesson + CTA | 3 cuts (2.5–4s) | 10s | Comparison → Callout (tip) → HeroTitle |
| **Total** | **23 cuts** | **~80s** | |

### Game-Style Visual Elements

Use the Remotion Explainer components with game-like styling:

| Desired Effect | Remotion Component | Key Props |
|---------------|-------------------|-----------|
| **MISSION FAILED** alert | `callout` with `type="warning"` | `title='💀 MESSAGE'`, `borderColor='#EF4444'`, `backgroundColor='#2e0a0a'`, `textColor='#F8FAFC'`, `containerBackgroundColor='rgba(0,0,0,0)'` |
| **MISSION PASSED** / success | `callout` with `type="tip"` | `title='✅ MESSAGE'`, `borderColor='#10B981'`, `backgroundColor='#0a2e1a'` |
| **Health bar** (financial health) | `progress_bar` | `progress=0.85`, `progressColor='#10B981'` (green = full), `progressColor='#EF4444'` (red = drained) |
| **Kinetic number pop-up** | `overlay` with `stat_reveal` | Place at `position='bottom-right'` or `position='center'`, set `accentColor` to match theme |
| **Head-to-head comparison** | `comparison` | `leftLabel='ASSETS'`, `rightLabel='LIABILITIES'`, two `StatReveal` overlays on top |
| **Big reveal number** | `stat_card` | Use for climax stats ($1.1M / $50K), different `color` for each |
| **Title card with impact** | `hero_title` | `animation='scale-in'` or `animation='zoom-in'` for extra energy |

### Example Composition Pattern

```python
scene('s-hook', 'hero_title', 0, 3.5, text='TWO LIVES', heroSubtitle='One Choice', backgroundImage='assets/images/hero_bg.png')
scene('s-invest-alert', 'callout', 18, 22, title='✅ INVESTING', text='$500/month', type='tip', borderColor='#10B981', ...)
scene('s-money-progress', 'progress_bar', 46.5, 51.5, title='💸 DRAINING', progress=0.05, progressColor='#EF4444', ...)

# Add kinetic overlays:
overlays = [
    overlay('num-pop', 'stat_reveal', 63, 66, text='$1.1M', subtitle='Compounded 10%', position='center', accentColor='#10B981'),
]
```

### Remotion Asset Handling on Windows (Critical)

Remotion's headless Chrome **blocks `file://` URIs** for local images and audio — you cannot use absolute filesystem paths. The correct approach:

1. **Copy all assets** to Remotion's `public/` directory before rendering:
   ```bash
   cp project/assets/images/*.png remotion-composer/public/assets/images/
   cp project/assets/audio/*.mp3 remotion-composer/public/assets/audio/
   ```

2. **Use relative asset paths** (no leading `/`):
   - ✅ `assets/images/hero_bg.png` — resolved via Remotion's `staticFile()`
   - ❌ `/assets/images/hero_bg.png` — converted to `file:///` by `resolveAsset()` → blocked by Chrome
   - ❌ `C:/.../hero_bg.png` — absolute path → blocked
   - ❌ `file:///...` — blocked by Chromium security policy

3. **Why no leading slash**: The `resolveAsset()` function in `Explainer.tsx` checks `src.startsWith("/")` and converts such paths to `file:///` URIs. Pass paths that don't start with `/` so they go through `staticFile()` instead.

### Background Images

For game-style production, generate dedicated background images for each visual mood:

| Mood | Image Prompt Seed | Tone |
|------|------------------|------|
| Success/Wealth | "Green gold glowing success screen, cinematic, wealth, dark background" | Green-gold gradient |
| Failure/Danger | "Dramatic red failure screen, dark dramatic, mission failed aesthetic" | Red glow |
| Fork/Choice | "Road fork with two paths, one gold/wealth, one darkness, GTA style, dramatic lighting" | Cinematic split |
| Consumer/Spending | "Consumer lifestyle clutter, shopping bags, receipts, dark dramatic red tones" | Red-toned chaos |
| Growth/Wealth | "Glowing money and numbers, stock market green chart up, cinematic dark, golden particles" | Gold-green glow |

## Pitfalls

1. **TTS too long** — edge-tts at normal rate produces ~150 WPM. For 85s video, script should be ~1275 words max. Use atempo to fit.
2. **PIL textbbox** — `draw.textbbox()` works, `image.textbbox()` doesn't. Always use the draw object.
3. **FFmpeg concat** — concat demuxer needs the last file listed twice. Or use filter_complex for explicit control.
4. **Memory limit** — User memory is 1375 chars. Consolidate overlapping entries with `replace`.
5. **Don't stop mid-pipeline** — User wants the final video. Generate ALL scenes, ALL audio, compose, subtitle, verify. Never stop at "plan" stage.
6. **Remotion Chrome blocks `file://`** — On Windows, Remotion's headless Chrome refuses to load local files via `file://` URIs. Always copy assets to `remotion-composer/public/` and reference them with relative paths that DON'T start with `/`. Setting `--disable-web-security` is NOT recommended — use the `public/` directory + `staticFile()` path instead.
7. **`resolveAsset()` path quirk** — The Explainer's `resolveAsset()` function checks `clean.startsWith("/")` and converts such paths to `file:///` URIs. Paths without leading `/` go through `staticFile()` instead. Always strip the leading `/` from relative asset paths.
8. **atempo > 2.0 needs two filters** — FFmpeg's `atempo` filter caps at 2.0. To go faster (e.g. 3x), chain two: `[0:a]atempo=1.5,atempo=2.0` (1.5×2=3). But 1.3x is plenty for brainrot pacing.
9. **Remotion Chrome OOM on long renders** — Large 1080×1920 renders (2000+ frames) can crash Chrome with out-of-memory at the default 6–8 concurrency. Fix: `--concurrency=4` halves memory pressure. Drop to 2 on machines with <16GB RAM. A crashed render produces no output file (zero bytes, not partial) and exit code 1.
10. **Composition JSON timing must match audio duration** — If the fast narration is 80.8s, the composition's `durationInFrames` should be at most `ceil(80.8 * fps)`. Scenes extending beyond the audio file create dead silence for the final few seconds. Always **verify audio duration first**:
    ```bash
    ffprobe -v quiet -print_format json -show_format narration_fast.mp3 | python -c "import json,sys; print(f'{float(json.load(sys.stdin)[\"format\"][\"duration\"]):.1f}s')"
    ```
    Then calibrate composition total frames = `ceil(duration_seconds * fps)`.

## Monetization Hooks

Embed naturally in script:
- "Link in bio for my investing course"
- "Want to learn trading? Check [affiliate]"
- "I use [broker] for my investments — link in description"
- Hashtags: #Finance #Investing #FinancialFreedom #SideHustle #Trading

## References

- See `references/pil-scene-patterns.md` for reusable PIL drawing patterns
- See `references/script-template.md` for the two-lives script structure template
- See `references/game-style-composition.md` for @onlymrbones kinetic game-style composition structure, overlay patterns, and timing calibration workflow

---
name: mr-finance-guy
description: >-
  Channel production skill for "Mr. Finance Guy" — a short-form finance content
  brand. Use this skill whenever the user asks to write, format, or produce a
  finance script, TikTok reel, YouTube Short, Instagram Reel, or comparison
  video. Triggers on: "script", "reel", "short", "tiktok", "youtube short",
  "what's the difference", "finance content", "mr finance guy", "write a finance
  video", "compare X and Y for video", "video analysis", "twelve labs",
  "twelvelabs", "analyze my video". Also triggered when the user provides a
  reference video for replication. Always load this skill before any short-form
  finance video work — even if the user doesn't name the channel explicitly.
---

# Mr. Finance Guy — Channel Production Skill

## About This Skill

This skill is the single source of truth for producing **Mr. Finance Guy** short-form
content (TikTok, YouTube Shorts, Instagram Reels). It covers:

- **Content strategy** — hooks, structure, retention optimization
- **Character** — visual lock, pose/expression palette, voice
- **Scripts** — "What's the Difference" format, timing, QC
- **Production pipeline** — TTS, Python PIL + FFmpeg, or Remotion asset management
- **Video analysis** — Twelve Labs integration for frame-level QC
- **Reusable workflow** — generate scripts from any finance topic

---

# Part 1 — Channel Identity

## Target Audience

| Segment | Why |
|---------|-----|
| Beginners | Never invested before, intimidated by finance |
| Students | Small budgets, big curiosity, mobile-native |
| Young professionals | First real income, need structure fast |
| Money-curious | Interested in personal finance, investing, wealth |

## Tone

| Attribute | Standard |
|-----------|----------|
| Clear | 8th-grade words. Jargon explained in one line. |
| Confident | No hedging ("kind of", "sort of", "maybe"). State facts. |
| Educational | Teaches without lecturing. Shows, doesn't tell. |
| Modern | Relatable references. No boomer finance tropes. |
| Minimalist | One idea per sentence. One sentence per beat. |

**Never** sound like a textbook, never sound robotic.

---

# Part 2 — Video Structure

## 4-Part Flow

| Part | Duration | Purpose |
|------|----------|---------|
| **Hook** | 0–3s | Attention-grabbing statement. No intro. No greeting. |
| **Explain** | ~70% | Break concept into steps. One idea per sentence. |
| **Compare** | interleaved | Good vs Bad, Wrong vs Right, Risk vs Reward |
| **End** | ~5s | One memorable takeaway. Satisfying, not abrupt. |

### Hook Rules
- **Never** introduce the topic ("Today we're talking about...")
- **Never** greet the audience ("Hey guys, welcome back")
- Must create curiosity in ≤3 seconds
- Examples: *"Most people save money the wrong way."* / *"This investing mistake costs people years."*

### Explain Rules
- One idea per sentence.
- Each sentence introduces something new — no repetition.
- Build logically: what → why → how → example.

### Compare Rules
- Visual comparisons double retention.
- Always interleave comparison: left (bad/risk/short-term) vs right (good/reward/long-term).
- Label both sides clearly with on-screen text.

### End Rules
- The ending must feel **satisfying**, not abrupt.
- Answer the question the hook created.
- Leave the viewer with something they'll remember.

---

# Part 3 — Narration Rules

## Sentence Style

| Rule | Example ✅ | Example ❌ |
|------|-----------|-----------|
| Short sentences | "Save first. Spend later." | "You should always make it a priority to save a portion of your income before spending on discretionary items." |
| One idea at a time | "This is bad debt. It charges 25% interest." | "Bad debt is credit that charges high interest rates and can trap you in a cycle of payments." |
| No filler | "Most people save wrong." | "Have you ever wondered if you're actually saving your money the right way?" |
| No long intros | "Saving vs investing." | "In today's video we're going to break down the key differences between saving and investing." |
| No unnecessary adjectives | "The market dropped 20%." | "The market experienced a massive, unprecedented 20% decline." |

## Pacing

- **120–160 words per minute** (TikTok: 140–160, YouTube: 120–140)
- Keep momentum — every 5 seconds should contain at least one memorable insight
- If a sentence doesn't improve understanding or retention, remove it

## Don'ts
- ❌ Filler openers: *"Have you ever wondered…"* / *"In today's video…"*
- ❌ Hedging: *"kind of"*, *"sort of"*, *"you might want to"*
- ❌ Corporate language: *"leverage"*, *"synergies"*, *"unlock"*, *"empower"*
- ❌ Weak closings: *"So that's the difference!"* / *"Thanks for watching!"*
- ❌ No moralizing — state the contrast, let it land

---

# Part 4 — Visual Rules

## Mr. Finance Guy Visual Identity

## Character — Mr. Finance Guy

### Visual lock (never change these)

| Feature | Spec |
|---------|------|
| Head | Large, round — dominant anchor |
| Hair | Clean black side-part, sharp |
| Glasses | Black rectangular frames, thick outlines |
| Eyes | Expressive — primary emotion carrier |
| Suit | Sharp black business suit, slim |
| Shirt / tie | White shirt, solid black tie |
| Style | Stickman-inspired, thick outlines, flat color, subtle shading, transparent bg |

Face, hair, glasses, proportions, and clothing are **locked across all frames**.
Only pose and eye expression change.

### Expression palette

| Tag | Eyes | Pose | Use when |
|-----|------|------|----------|
| `[neutral]` | open, level | upright, arms at sides | narration, setup |
| `[explaining]` | focused, slightly wide | one arm up, index finger raised | definitions, comparisons |
| `[shocked]` | very wide, brow raised | both hands out, lean back | surprising stat |
| `[confident]` | half-lidded, slight smirk | arms crossed or hand in pocket | punchlines, kicker |
| `[cautious]` | narrow, one brow up | palm forward | warnings, bad debt, risk |
| `[approving]` | curved upward | thumbs up or open palms | good outcomes, green side |

## Scene Visual Rules (Twelve Labs-Verified)

### Reference Layout (verified via Twelve Labs Pegasus 1.2 analysis of reference video)

### Background
- **Solid WHITE background** — pure #FFFFFF, NO gradients, NO textures
- The character and cards are the focus against the clean white backdrop
- No complex backgrounds, no patterns, no busy colors

### Character on Screen
- **Position: LEFT side of frame** (~3-5% from left edge), **VERTICALLY CENTERED** (starts ~22% from top, just below cards and icons)
- **Size: ~48-55% of vertical height** — use 55% for thin-stickman sprites (aspect ~0.67), 48% for larger sprites (aspect ~0.75)
- Black stickman-inspired character with thick outlines
- Character wears: black suit, white shirt, black tie, black glasses
- **Critical**: The character MUST NOT overlap with narration text. Position character centered in the middle zone and narration text at the very BOTTOM of the frame (below the character's feet).
- **Critical**: When character sprites are pure black outlines on transparent (no skin tones), always apply MaxFilter dilation to thicken lines — see Pitfall 3 Fix B. Without this, thin lines are invisible at mobile scale.

### Cards at Top Center (~10% from top)
Two large horizontally-aligned cards at the top of the frame:
- **Left card** ("Active Income" / bad side): **White background (#FFFFFF), black text, NO visible border** (or subtle light gray border)
- **Right card** ("Passive Income" / good side): **Green background (#00AA66), white text, NO border**
- Each card takes **~40% of screen width**, with ~5% gap between them
- Card height: ~12% of frame height
- Text: Bold sans-serif, ~40% of card height

### On-Screen Narration Text
- **Position: VERY BOTTOM of frame** (60px margin from bottom edge, BELOW the character's feet)
- Color: **Black**, optionally on a white semi-transparent rectangle for readability (fill=(255,255,255,230))
- Font: Bold (Impact 44px), word-wrapped to 85% of screen width
- **Critical**: Narration text MUST be positioned below the character so it doesn't block the character's body. If there's overlap, move text down or character up.

### Speech Bubble (Hook Scene Only)
- Positioned at center of frame, slightly below top third (~30% from top)
- Contains "? ?" in bold font
- White fill with black outline (3px)
- Small triangular tail pointing downward

### Graphics & Icons
- **Gold coin icon (#D4AF37)** with "$" symbol — positioned near passive income card
- **Green up arrow (#00AA66)** — positioned top-right corner or near growth indicators
- **Blue chart icon (#007BFF)** — bar chart, positioned bottom-left or near passive examples
- All icons are simple flat designs, no thick outlines needed
- Icons are ~60-80px in size

### Supporting Visuals (Icons + Concept Box)
Every scene MUST have supporting visual elements to illustrate the concepts being narrated. Two layers:

**Layer 1: Icons under each card** (~y=394, centered below card)
- Each scene has a left-icon and right-icon assignment
- Supported icon types: `bank`, `chart_up`, `coin`, `piggy`, `star`, `growth`, `shield`, `calendar`, `clock`, `question`
- Icons are drawn with PIL shapes (no external image files needed)
- Icon size: 55px diameter

**Layer 2: Concept box** (right side, between cards and character)
- Floating box at RIGHT_X (573), y=384, w=454, h=180
- Contains two icons with an arrow between them
- Box fill color: light blue tint when left/good side highlighted, white otherwise
- Icons in the box change per scene to match the current comparison
- The arrow creates a visual comparison: left-arrow-right

### Scene-to-Icon Mapping (Verified Pattern)
Each scene gets specific icons matching its narration. Example from saving-vs-investing:

| Scene | Left Icon | Right Icon | Concept Box |
|-------|-----------|------------|-------------|
| SAVING / INVESTING | bank | chart_up | question + coin |
| BANK / ASSETS | bank | chart_up | bank + coin |
| CASH / STOCKS | piggy | chart_up | coin + piggy |
| 1% PA / 9% PA | bank | growth | piggy + calendar |
| PASSBOOK / REITs | coin | chart_up | bank + calendar |
| 72 YRS / 8 YRS | calendar | clock | piggy + calendar |
| SECURE / GROW | shield | star | shield + coin |
| BUFFER / FUTURE | coin | growth | shield + coin |
| 3 MONTHS / REST | calendar | chart_up | bank + calendar |
| SURVIVE / THRIVE | shield | star | shield + coin |

**Pattern rule**: Left-side (bad/risk/safe) icons: `bank`, `shield`, `calendar`, `piggy`, `coin`. Right-side (good/growth) icons: `chart_up`, `growth`, `star`, `clock`.

### Draw Icon Reference
See `references/supporting-icons-system.md` for the complete draw_icon() function code with all icon types.

### Color Palette (Complete — v7 Verified)
| Color | Hex | Usage |
|-------|-----|-------|
| White | #FFFFFF | Background |
| Off-White | #F5F5F5 | Left card fill (visible against white!) |
| Black | #000000 | Text, narration |
| Light Green | #33BB77 | Passive card background (was too dark) |
| Dark Green | #28A064 | Passive card border |
| Gold | #D4AF37 | Coin icon |
| Blue | #007BFF | Chart icon |
| Blue Accent | #1E90FF | Active card accent bar |
| Card Border | #DCDCDC | Subtle card outline |

### Proportions Grid (1080×1920 — v9 Verified by Twelve Labs)
The v9 layout fixes three user-reported issues: character too low, text blocking character, missing supporting visuals.
```
CARD ROW:       y=115 (6%), h=269 (14%), CARD_W=454 (42%), LEFT_X=54 (5%), RIGHT_X=573 (5%+42%+6%=53%)
ICON ROW:       y=394 (20%), icons centered below each card, ~55px each, drawn with PIL draw_icon()
CHARACTER:      LEFT x=32 (3%), y=422 (22%), h=922 (48%), bottom=1344 (70%) — VERTICALLY CENTERED
CONCEPT BOX:    x=573 (RIGHT_X), y=384 (20%), w=454 (CARD_W), h=180, icons + arrow between
NARRATION:      y=H - total_h - 60 (very bottom, 60px margin), max 85% W, Impact 44px
BOTTOM SAFETY:  60px margin — nothing drawn below y=1860
```
### Layout Zones (y-axis)
| Zone | y-range | Purpose |
|------|---------|---------|
| Cards | 115–384 | Two cards with dynamic scene-matched labels |
| Icons | 384–459 | Supporting icons under each card |
| Concept Visuals | 384–564 | Floating concept box with two icons + arrow (right side) |
| Character | 422–1344 | Character on left side — centered vertically |
| Narration Text | 1860–1860+total_h | Text at very bottom, below character |
| Bottom margin | 1860–1920 | Keep clear (60px safety zone) |

### Character Positioning (Centered)
- **Fixed value**: `char_y = int(H * 0.22)` = 422px from top
- **Fixed value**: `char_target_h = int(H * 0.48)` = 922px (start at y=422, end at y=1344)
- **Width cap**: 55% of frame width (594px) — wider than before, needed because sprites are portrait (aspect ~0.67-0.75)
- **Dilation**: Always apply MaxFilter(9) kernel when sprites are pure black outlines — see Pitfall 3 Fix B

### Card Text (Dynamic Per Scene)
- **Card text changes every scene** to match narration topic (see Pitfall 6 for example progression)
- Font: Impact Bold, 40% of card height (~108px for 269px card)
- Style: Left card = BLUE text when highlighted (#007BFF), BLACK otherwise; Right card = GREEN text when highlighted (#33BB77), BLACK otherwise
- **Speech bubble**: center x=540, y=538 (28% top), 200×120px
- **Narration text**: Impact 44px, centered, y=1402 (73% bottom), max 85% width
- **Icons**: 80-100px, placed near cards (coin at right card, chart near character)

### Editing Rules

### Animation — Critical Rule
**Every 1–2 seconds, something must move:**
| Technique | Example |
|-----------|---------|
| Zoom | Camera slow-zoom in on character for emphasis |
| Icon | Coin spins, arrow animates upward, chart draws |
| Transition | Cross-dissolve, slide, or wipe between scenes |
| Highlighted word | Key number or word pulses or changes color in on-screen text |
| Character animation | Pose change, expression shift, arm movement |
| Camera | Slow pan across cards, dolly in on character |

**Never allow static visuals for more than 2 seconds.** A still image with zero motion loses viewer attention.

---

# Part 5 — Editing Rules

| Rule | Why |
|------|-----|
| Cut pauses | Remove all dead air between sentences |
| Keep momentum | Nothing slows down. Every cut delivers new info or visual change |
| Deliver value fast | Skip setup. Start with the takeaway |
| Insight every 5s | Every 5-second interval must contain one memorable, quotable fact |
| Remove weak scenes | If it doesn't improve understanding or retention, delete it |

---

# Part 6 — Retention Optimization

> **Assume every viewer wants to leave after 3 seconds.**

- **Continuously create curiosity.** Every line should make them wonder what's next.
- **Answer one question while creating another.** Give them a fact, then raise the stakes.
- **Reveal important information early.** Don't save the best insight for the end — they'll be gone.
- **Never save the cliffhanger for the very last line.** Spread peaks across the script.

---

# Part 7 — Reusable Workflow (10 Steps)

Whenever a new finance topic is provided:

1. **Identify** the single biggest takeaway
2. **Generate 3 possible hooks** — test each for curiosity gap
3. **Create a high-retention script** using the 4-part flow (Hook → Explain → Compare → End)
4. **Divide the script into scenes** — one scene per beat
5. **Describe the visuals for every scene** — character pose, props, cards, on-screen text
6. **Suggest animations** — what moves, how, and when (with timing)
7. **Suggest on-screen text** — labels, numbers, callouts
8. **Suggest icons and graphics** — coin, chart, arrow, percentage badge, etc.
9. **Suggest sound effects** if appropriate — coin drop, swoosh, ding, click
10. **Review the final video** for retention improvements — is every 5s interval strong?

---

# Part 8 — Script Format: "What's the Difference"

### Structure
```
[HOOK]    Cold open, two-sided reveal       ≤5 sec on screen
[BRIDGE]  One-line stakes statement
[ROUNDS]  3–6 head-to-head comparison beats
[KICKER]  Reframe + quotable closing line
[CTA]     Optional, 1 line max
```

### Hook (mandatory format)
```
"This is [X]."     ← left / red card
"This is [Y]."     ← right / green card
"What's the difference?"
[beat]
[bridge — stakes in ≤15 words]
```
- X = negative/risky concept. Y = positive/empowering concept.
- Always cold open. No intro narration.

### Round format
```
[X] is ___. [1–2 sentences.]
[Y] is ___. [mirror structure, parallel rhythm.]
```
- Symmetric — same sentence count per side.
- One dimension per round only (see pick-list below).
- Max 6 rounds. Optimal 4–5.

### Round dimensions

| # | Dimension | Focus question |
|---|-----------|----------------|
| 1 | Definition | What is it, fundamentally? |
| 2 | Real examples | What does it look like in daily life? |
| 3 | The number | Rate, cost, or return — be specific. |
| 4 | The mindset | What thinking pattern creates it? |
| 5 | The long game | Where does this path lead in 5–10 years? |
| 6 | The test | How do you spot it in the wild? |

### Kicker format
```
[Reframe — names the real principle behind both sides.]
[Contrast line 1 — short.]
[Contrast line 2 — mirror of line 1.]
[The question — one quotable line they'll screenshot.]
```
End on a question the viewer now has the answer to. Not a CTA.

### CTA
`"Follow for more."` — one line maximum, or omit entirely.
Never: *"smash that like button"* / *"comment below."*

---

# Part 9 — Script Output Format

Every script begins with YAML front-matter:

```yaml
---
series: "What's the Difference"
topic: "[X] vs [Y]"
character: Mr. Finance Guy
platform: [TikTok / YouTube Shorts / Instagram Reels]
target_length: [45s / 60s / 90s]
estimated_words: [number]
rounds: [number]
visual_cues: yes
---
```

Then the script body with inline expression tags:

```
[SPLIT SCREEN]
[neutral]
"This is bad debt."

[cautious]
"This is good debt."
...
```

### Visual cue tags

| Tag | Meaning |
|-----|---------|
| `[SPLIT SCREEN]` | Left = X card (red tint), Right = Y card (green tint) |
| `[FULL BODY]` | Default — narration and transitions |
| `[CLOSE-UP]` | Face only — punchline or kicker delivery |
| `[expression]` | Any tag from the expression palette |

---

# Part 10 — Timing Guide

| Length | Words | Rounds | Pace |
|--------|-------|--------|------|
| 30s | 60–75 | 2–3 | Punchy |
| 45s | 90–110 | 3–4 | Steady |
| 60s | 130–155 | 4–5 | Steady |
| 90s | 190–225 | 5–6 | Measured |

Word budget: Hook+bridge ~10% · Each round ~15–18% · Kicker ~12–15% · CTA ≤5 words.

---

# Part 11 — Platform Rules

| Platform | Hook | Kicker | End Card |
|----------|------|--------|----------|
| **TikTok** | ≤3 sec, no delay | Close-up, full stop | No end card |
| **YouTube Shorts** | Can run 1–2 sec longer | 2–3 lines | Optional end card OK |
| **Instagram Reels** | Mirror TikTok rules | Post caption restates kicker | No end card |

---

# Part 12 — QC Checklist

Before outputting any script, verify:

- [ ] Cold open — no filler opener ("Have you ever wondered…")
- [ ] Hook creates curiosity in ≤3 words or one statement
- [ ] Bridge ≤15 words
- [ ] Rounds symmetric (same sentence count each side)
- [ ] One dimension per round
- [ ] Numbers specific (rate/amount, not "high interest")
- [ ] Kicker stands alone as a quotable line
- [ ] Word count matches target length
- [ ] Expression tags annotated on every spoken line
- [ ] YAML front-matter complete
- [ ] Every 5-second interval has at least one memorable insight
- [ ] No static period > 2 seconds (animation plan exists)

---

# Part 13 — Production Pipeline

The channel has two production pipelines. Use the **Python PIL** approach for rapid prototyping (<10 scenes). Use the **Remotion** approach for complex productions with animations, transitions, and word-level captions.

## Pipeline A — Python PIL + FFmpeg (Rapid Prototyping)

See `references/python-pil-video-pipeline.md` for the complete workflow, including:
- ElevenLabs TTS generation with per-segment MP3s
- PIL scene rendering matching the reference layout
- FFmpeg per-scene clip + concat composition
- Audio merge and final output

### Key differences from Remotion
| Aspect | Python PIL | Remotion |
|--------|-----------|----------|
| Setup time | ~5 min | ~30 min (npm install, etc.) |
| Render speed | ~30s per video | ~12-15 min per video |
| Animations | Static frames only | Full CSS/React animations |
| Captions | No word-level captions | Word-level highlight |
| Complexity | Simple script | Full React project |

## Pipeline B — Remotion (Production)

## Stage B1 — ElevenLabs TTS Narration

| Setting | Value |
|---------|-------|
| Voice | Rachel (`21m00Tcm4TlvDq8ikWAM`) |
| Model | `eleven_multilingual_v2` |
| Stability | 0.5 |
| Similarity boost | 0.75 |
| Key location | `~/Documents/Projects/MoneyPrinterTurbo/.elevenlabs_key` |

### Endpoint for audio + captions together
```python
POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps
{
  "text": "...",
  "model_id": "eleven_multilingual_v2",
  "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
}
```

Returns `audio_base64` + `alignment.characters` / `alignment.character_start_times_seconds` / `alignment.character_end_times_seconds`.

### Convert character timestamps to word captions:
Group successive characters between spaces. For each word: `start` = first character's `character_start_times_seconds`, `end` = last character's `character_end_times_seconds`. Convert to milliseconds:
```python
{"word": w, "startMs": round(start * 1000), "endMs": round(end * 1000)}
```

See `references/elevenlabs-tts-captions.md` for the full TTS + word-timestamp pipeline.

## Stage B2 — Build `.remotion_props.json`

The Remotion Explainer (`~/OpenMontage/remotion-composer/src/Explainer.tsx`) reads this JSON schema:

| Key | Type | Notes |
|-----|------|-------|
| `cuts` | Cut[] | Ordered scene array (see Cut types below) |
| `captions` | WordCaption[] | `{word, startMs, endMs}` — milliseconds! |
| `audio.narration.src` | string | Path to MP3 inside `public/` |
| `themeConfig` | object | See Theme section |

### Cut types for finance comparisons

| type | Props | Good for |
|------|-------|----------|
| `text_card` | `generated_content` with `type: "split_screen"` | Hook with BAD vs GOOD labels |
| `comparison` | `leftLabel, leftValue, rightLabel, rightValue` | Rounds (definition, examples, numbers) |
| `callout` | `callout_type`, `text` | Quotes, mindset beats |
| `stat_card` | `stat`, `text` | Single big number reveals |

### File path convention (⚠️ critical)
- ❌ Do NOT use `file:///C:/...` paths — Remotion renderer cannot download them
- ❌ Do NOT use `./` prefix — `staticFile()` rejects relative paths
- ✅ Copy assets to `~/OpenMontage/remotion-composer/public/{project-name}/audio/`
- ✅ Use bare relative paths: `"src": "bad-debt-vs-good-debt/audio/narration.mp3"`
- ✅ The `resolveAsset()` function calls `staticFile(clean)` for non-URL, non-absolute paths

## Stage B3 — Render

```bash
cd ~/OpenMontage/remotion-composer
npx remotion render src/index.tsx Explainer out/{output-name}.mp4 \
  --props=remotion_props.json
```

Defaults: 1920×1080 @ 30fps, H.264. A 65-second render takes ~12–15 min.

## Stage B4 — Deliver

The rendered MP4 lands at `~/OpenMontage/remotion-composer/out/{name}.mp4`.

---

# Part 14 — Character Assets

All 18 Mr. Finance Guy character sprites with transparent backgrounds live at:
```
C:\Users\YOUR_USERNAME\Downloads\Channel\Character_models_poses\bg_removed\
```

See `references/character-sprites.md` for the full expression-to-filename map.
See `references/elevenlabs-tts-captions.md` for the TTS + word-timestamp capture pipeline.

---

# Part 15 — Topic Bank

## Financial concepts
- bad debt vs good debt
- assets vs liabilities
- saving vs investing
- income vs cash flow
- net worth vs salary
- ETF vs mutual fund
- dollar-cost averaging vs lump sum
- stock vs bond
- diversification vs concentration
- bull market vs bear market
- active income vs passive income
- fixed salary vs freelance income
- traditional IRA vs Roth IRA
- term life vs whole life insurance
- renting vs buying a home
- credit card vs debit card

## Behavioral finance
- fear vs greed
- risk tolerance vs risk capacity
- impulse buy vs planned purchase
- budget vs spending plan
- delayed gratification vs instant reward
- scarcity mindset vs abundance mindset
- lifestyle inflation vs lifestyle deflation
- FOMO investing vs patience investing

## Philippines-specific
- PAG-IBIG MP2 vs UITF
- SSS pension vs VUL
- palengke vendor credit vs bank loan
- BIR registered vs unregistered
- OFW remit vs invest
- co-op membership vs bank savings
- 5-6 loan shark vs formal lending
- digital bank vs traditional bank (PH context)

## Modern finance
- crypto vs stocks
- DeFi vs traditional banking
- robo-advisor vs human advisor
- passive index fund vs active managed fund
- fiat vs cryptocurrency
- SPAC vs traditional IPO
- REIT vs direct real estate

## Career & money
- salary negotiation vs job hop
- employee vs freelancer
- side hustle vs passive income
- upskilling vs degreed career
- networking vs applying cold
- contractor vs full-time tax planning

## Business
- startup vs small business
- service business vs product business
- B2B vs B2C
- franchise vs build from scratch
- dropshipping vs inventory-based
- solo vs team

## Economy & macro
- inflation vs deflation
- recession vs depression
- fiscal policy vs monetary policy
- supply vs demand shocks
- soft landing vs hard landing
- fixed rate vs variable rate mortgage
- growth stock vs value stock

## New additions (can expand)
- Artificial Intelligence in Finance
- Fintech vs Traditional Banking
- Green Investing vs ESG
- Generational Wealth vs Earned Wealth
- Financial Independence vs Early Retirement
- Emergency Fund vs Investment Fund
- Dollar vs Peso (forex basics)
- High Yield Savings vs Money Market

---

# Part 16 — Twelve Labs Video Analysis Integration (Verified Working)

Twelve Labs (https://twelvelabs.io) provides a video understanding API that can analyze
Mr. Finance Guy videos at the frame level using the Pegasus 1.2 model. **Verified working
with the Mr. Finance Guy channel.**

## API Key

```
Key: tlk_3GPGSWK0PX0GY82Y8NS8H0564ZBD
Base URL: https://api.twelvelabs.io/v1.3
```

## Integration Workflow

### Step 1: Create a Dedicated Index
```bash
curl -X POST -H "x-api-key: $KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "index_name": "Mr. Finance Guy Channel",
    "addons": ["thumbnail"],
    "models": [
      {"model_name": "pegasus1.2", "model_options": ["visual", "audio"]}
    ]
  }' \
  "https://api.twelvelabs.io/v1.3/indexes"
```
Returns `{"_id": "..."}` — the index ID. Pegasus 1.2 is used for text generation/analysis.
For semantic search, use `marengo3.0` instead.

### Step 2: Upload a Video
```bash
curl -X POST -H "x-api-key: $KEY" \
  -F "index_id=INDEX_ID" \
  -F "video_file=@/path/to/video.mp4" \
  "https://api.twelvelabs.io/v1.3/tasks"
```
Returns task ID and video ID. Uploaded synchronously for files ≤200MB.

### Step 3: Wait for Indexing
```bash
curl -H "x-api-key: $KEY" \
  "https://api.twelvelabs.io/v1.3/tasks/TASK_ID"
```
Status goes: `uploading` → `indexing` → `ready`. Duration depends on video length.

### Step 4: Analyze with Pegasus
```bash
curl -X POST -H "x-api-key: $KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "VIDEO_ID",
    "prompt": "Describe what you see in detail..."
  }' \
  "https://api.twelvelabs.io/v1.3/analyze"
```
Returns streaming text with scene descriptions. Prompt can be up to 2,000 tokens.

## Analysis Prompts That Work (Verified)

### Frame Layout QC
```
I need exact frame layout analysis. For every scene in this video, describe:
1) Character position — left or right? % of height? vertical centering?
2) Cards and labels — position, size, color, border style, text
3) On-screen text — exact text, font size, position, color
4) Background — exact color or gradient
5) Colors used — specific colors
6) Icons and their position
```

### Full Transcription with Timestamps
```
Transcribe every single word spoken in this video with timestamps.
List each sentence with its start and end time in seconds.
Format: [start-end] sentence.
```

### Scene Structure Analysis
```
Segment this video into scenes. For each scene tell me:
1) Start and end time
2) What the character is doing
3) What text is shown on screen
4) What the narrator says
```

## Limitations
- **Pegasus 1.2 indexes do NOT support semantic search** (only Marengo does)
- Search endpoint returns error `"index_not_supported_for_search"` on Pegasus indexes
- For search, create a separate Marengo 3.0 index
- Rate limits: 60 requests/min, 36,000 seconds of video/hour

## Verified Analysis Results — "Active Income vs Passive Income" Reference

### Layout Specs (from actual Pegasus 1.2 analysis)
- **Background**: Solid white, no gradients, no textures
- **Character**: Left side, ~30% of vertical height, centered vertically
- **Active Income card**: White bg (#FFFFFF), black text, 40% width, no visible border
- **Passive Income card**: Green bg (#00AA66), white text, 40% width, no visible border
- **Cards position**: Top of frame, ~10% from top edge, horizontally centered with ~5% gap
- **Narration text**: Lower third (70% from top), centered, black text
- **Speech bubble**: Center, slightly below top third, "? ?" in bold
- **Icons**: Gold coin (#D4AF37), green arrow (#00AA66), blue chart (#007BFF)
- **Color palette**: White #FFFFFF, Black #000000, Green #00AA66, Gold #D4AF37, Blue #007BFF

### Full Narration Script (extracted by Pegasus)
```
[00-10] This is active income. This is passive income. What's the difference?
        One stops the moment you stop. The other pays you while you sleep.
[11-20] Active income is money you earn by trading time. You work an hour.
        You get paid for an hour. You stop working. The money stops.
[21-31] Passive income is money that earns without your direct time.
        You build it or buy it once. Then it pays you over and over.
[31-41] Active income looks like your monthly salary, your freelance project rate,
        your daily wage at a sorry-sorry store.
[41-51] Passive income looks like rent from a condo unit, dividends from stocks,
        a YouTube channel earning ad revenue while you're asleep.
[51-01:01] Active income has a ceiling. 24 hours in a day. You can only sell so
           many hours. Hit the ceiling. Income flatlines.
[01:01-01:12] Passive income has no ceiling. One rental becomes two. One channel
              becomes a portfolio. The more you build, the more it compounds.
[01:12-01:22] Active income thinking: How much do I make per hour? Passive income
              thinking: How much does my money make per hour?
[01:22-01:32] Most people only have active income. That's not wrong. It's your
              foundation. But if your income stops when you stop, don't own your time.
[01:32-01:33] Follow for more.
```

## Fallback if API Unavailable
If Twelve Labs is unavailable, fall back to:
1. `vision_analyze()` tool on extracted frames (if model supports vision)
2. Manual frame extraction + PIL analysis (color, edge, density comparison)
3. FFmpeg scene detection + faster-whisper transcription

---

# Part 17 — Video Replication Workflow (Concrete Steps)

## When given a reference video AND a new topic

### Phase 1 — Analyze the Reference

1. **Check key exists**: Ensure Twelve Labs API key is available at `https://api.twelvelabs.io/v1.3`.
2. **Check the reference video**: `ffprobe -v quiet -show_entries format=duration -of csv=p=0 ref.mp4`
3. **Create a dedicated Pegasus 1.2 index** if one doesn't exist (see Part 16 for curl commands)
4. **Upload the reference video** with `-F "video_file=@/path/to/video.mp4"`
5. **Wait for indexing** (poll `/v1.3/tasks/TASK_ID` until status=ready)
6. **Analyze the frame layout** using Pegasus with a detailed prompt about character position, cards, text, background color
7. **Extract the full narration** with timestamps using a "Transcribe every single word" prompt

### Phase 2 — Write the New Script

8. **Write the "What's the Difference" script** for the new topic using Parts 2, 3, 8, 9
9. **Verify** the word count matches target duration (Part 10)
10. **Annotate** every spoken line with expression tags (Part 4)

### Phase 3 — Generate TTS and Determine Timings

11. **Generate ElevenLabs TTS** for each scene's narration text (see `references/elevenlabs-tts-captions.md`)
12. **Get per-segment duration**: `ffprobe -v quiet -show_entries format=duration -of csv=p=0 segment_01.mp3`
13. **Round scene durations** to the nearest 0.5s or 1s (avoids sync drift)

### Phase 4 — Render Scenes (Python PIL)

14. **Create a render script** following `references/python-pil-video-pipeline.md`
15. **Assign each scene unique card labels** — card text MUST change per scene to match narration, not stay static. See the dynamic card text progression in Pitfall 6 for the pattern.
16. **Use the v9 proportions grid** from Part 4 — character centered at y=422 (22%), icons under cards at y=394, concept box on right, text at very bottom (H - text_h - 60px)
17. **Include supporting visuals** — icons under each card (55px) + concept box with two icons + arrow. Map icons to scene content using the "Scene-to-Icon Mapping" table in Part 4.
18. **Apply character dilation** — when character sprites are pure black outlines, apply ImageFilter.MaxFilter(9) to thicken outlines (Pitfall 3 Fix B)
19. **Save each scene** as PNG in a `backgrounds_v9/` directory

### Phase 5 — Compose the Video

20. **Generate per-scene video clips** using ffmpeg `-loop 1` approach (NOT concat demuxer with stills — see Pitfall 7)
21. **Concat clips** with `ffmpeg -f concat -c copy`
22. **Merge TTS audio segments** with `ffmpeg -f concat` or filter_complex concat
23. **Combine video + audio** with `ffmpeg -shortest`
24. **Verify output**: must show 1080×1920, 30fps, h264 + aac

### Phase 6 — QC

23. **Upload the generated video** to Twelve Labs for comparison
24. **Analyze** with the same prompt used on the reference
25. **Compare** layout specs — cards at top? Character left? White bg?
26. **Fix discrepancies** and re-render
27. **Delivery**: save to `~/Downloads/Channel/approved videos for production/` with topic name

---

# Integration with /decide

The `/decide` skill already routes to this skill when it detects:
```
Writing finance scripts / "What's the Difference" / Mr. Finance Guy /
TikTok finance / reel / short / compare X and Y for video
```

This skill also triggers on:
- Video analysis requests (with or without Twelve Labs API)
- Frame quality audits
- Reference video replication
- Any channel management task for Mr. Finance Guy

**When loaded by /decide**, this skill produces:
- A complete script with YAML frontmatter
- Scene-by-scene visual descriptions
- Animation and on-screen text suggestions
- Production-ready assets
- Twelve Labs analysis integration (when API key is available)

---

## Processing Instructions

When this skill is loaded:

1. **First check** if the user provides a specific topic or reference video
2. **If topic only**: Run the 10-step reusable workflow (Part 7)
3. **If reference video**: Run the video replication workflow (Part 17)
4. **If analysis requested**: Use Twelve Labs or fallback methods (Part 16)
5. **Always** produce complete scripts with YAML frontmatter
6. **Always** verify visual rules and QC checklist before delivering

## Common Rendering Pitfalls (Found via Twelve Labs QC)

These were discovered by analyzing generated videos against the reference using Twelve Labs Pegasus 1.2 + pixel-level thumbnail comparison. Check these BEFORE telling the user a video is ready.

### Pitfall 1: Invisible White Card on White Background (CRITICAL)
**The Left card (bad side) is white-filled on a white background.** Without border or shadow the card shape disappears — only the text is visible, making the top of the frame look empty.

**Symptoms**: Pegasus reports `"Cards at the top: Not present"`. OCR reads garbled text (e.g. `"Income"` → `"Incasso"`). Pixel check shows >98% white in left card area.

**Fix** (pick one):
- Use **#EEEEEE** light gray fill for the left card instead of pure white
- Add a 1-2px visible border (gray or blue accent)
- Add a subtle drop shadow (3px offset, 5px blur, 20% opacity black)
- Make card text bold/large enough to provide visual structure independently

### Pitfall 2: Card Text Too Small / Wrong Font
**Top-area text needs to be bold and large enough to read at mobile scale (320px thumbnail).** At thumbnail width, each letter is only ~6-8px — too small to distinguish shapes.

**Fix**: Use Impact or Arial Bold at minimum 80px (for 1080-wide frame). Card text should fill ~40% of card height (~92px for a 230px card).

### Pitfall 3: Pure Black Character = Featureless Blob
**A pure black stickman silhouette has no visible detail at video scale — it reads as a flat blob.** The reference character has visible skin-toned face and hands (~210,120,30) that distinguish head from suit.

**Symptoms**: Pixel analysis shows only (0,0,0) and (240,240,240) in character area. No skin-tone range present.

**Fix A (preferred)**: Ensure character sprites have skin-toned face/hands. Verify transparent PNGs are NOT all-black silhouettes at full transparency.

**Fix B (when sprites are pure black outlines)**: Thicken the character outlines using `ImageFilter.MaxFilter` dilation. This makes thin lines visible at mobile scale without needing skin tones:

```python
from PIL import Image, ImageFilter

char_img = Image.open(pose).convert("RGBA")
char_resized = char_img.resize((w, h), Image.LANCZOS)

_, _, _, a = char_resized.split()
outline_mask = a.point(lambda x: 255 if x > 30 else 0)
thicken_px = 4
dilated = outline_mask.filter(ImageFilter.MaxFilter(thicken_px * 2 + 1))

thick_shadow = Image.composite(
    Image.new('RGBA', char_resized.size, (0, 0, 0, 200)),
    Image.new('RGBA', char_resized.size, (0, 0, 0, 0)),
    dilated
)
img.paste(thick_shadow, (char_x, char_y), thick_shadow)
img.paste(char_resized, (char_x, char_y), char_resized)
```

Pegasus 1.2 describes this output as: "thick outline ensures high contrast and clarity against the white background, making it easily distinguishable and memorable."

### Pitfall 6: Static Card Labels Across All Scenes
**Using the same two card labels (e.g. "SAVING" / "INVESTING") for every scene makes the top of the frame feel repetitive and wastes the opportunity to reinforce each scene's specific message.** The user expects the card text to evolve with the narration.

**Fix**: Give each scene its own pair of card labels that match the specific comparison being made in that scene's narration. Example progression for a saving-vs-investing video:

| Scene | Left Card | Right Card | Narration Topic |
|-------|-----------|------------|-----------------|
| Hook | SAVING | INVESTING | Establish the two sides |
| Where | BANK | ASSETS | Where the money goes |
| What | CASH | STOCKS | What you buy |
| Returns | 1% PA | 9% PA | The rate difference |
| Examples | PASSBOOK | REITs | Real world examples |
| The Number | 72 YRS | 8 YRS | Doubling time comparison |
| Mindset | SECURE | GROW | Core philosophy |
| Purpose | BUFFER | FUTURE | Role in your life |
| The Test | 3 MONTHS | REST | Decision framework |
| Kicker | SURVIVE | THRIVE | Memorable reframe |
| CTA | FOLLOW | FOR MORE | End card |

**Verified**: Pegasus 1.2 detects the changing labels and confirms "the text shifts" between scenes.

### Pitfall 7: Concat-Demuxer Still-Image Videos Index Slowly on TwelveLabs
**Using `ffmpeg -f concat` directly on still image files produces a 1fps video that takes 20+ minutes to index on Pegasus 1.2, often timing out.** The per-scene clip method (30fps clips) indexes in under 1 minute.

**Fix**: Use the per-scene clip approach (already documented in Pitfall 5). Videos with 30fps real clip encoding index in ~30-60s on TwelveLabs Pegasus 1.2 regardless of file size.

### Pitfall 4: Green Card Too Dark
**The reference right card uses a lighter green ~(60,180,90).** Darker green like #00AA66 = (0,170,102) is too saturated against white background.

**Fix**: Use green closer to (60,180,90) — about #3CB45A.

### Pitfall 8: Missing Supporting Visuals Per Scene
**Using only cards and character without scene-specific icons or visual elements leaves the middle of the frame empty and makes the video feel text-heavy.** The user will complain about "no supporting images for what the character is saying."

**Symptoms**: Pegasus reports only "cards at top and character on left" without mentioning icons, concept boxes, or visual contrasts. Frame layout feels empty.

**Fix**: Always assign scene-specific icons under each card AND a concept visualization box with two icons + arrow. Every scene should have at least 3-4 visible elements: cards, icons under cards, concept box, character. See "Supporting Visuals (Icons + Concept Box)" in Part 4 for the icon types and mapping.

### Pitfall 9: Character Positioned Too Low (Text Overlaps)
**If the character is positioned at the bottom of the frame (below 50% of frame height), the narration text in the lower third will overlap with the character's upper body.**

**Symptoms**: User says "the character is so below and text captions block it." Pegasus confirms the text is in the middle of the character's body area.

**Fix**: Center the character vertically in the middle zone (y=422, 22% from top for a 48% tall character). Position narration text at the VERY BOTTOM of the frame (H - text_height - 60px). The character and text should have zero vertical overlap. See the v9 Proportions Grid for exact values.

### Pitfall 5: FFmpeg Concat 1fps Glitch
**Using the concat demuxer with `duration` lines on still images produces a 1fps output file.**

**Fix**: Use the per-scene clip approach instead:
```bash
# CORRECT
ffmpeg -y -loop 1 -i scene.png -c:v libx264 -t 7 -r 30 -pix_fmt yuv420p scene_clip.mp4
# then concat clips
ffmpeg -f concat -safe 0 -i clips.txt -c copy final.mp4
```

**Wrong** (creates 1fps output):
```bash
echo "file 'scene.png'\nduration 7.0" > concat.txt  # 1fps output!
```

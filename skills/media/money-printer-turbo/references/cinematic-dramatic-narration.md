# Cinematic / Dramatic Narration — Voice Selection & Script Craft

> How to pick voices and write scripts for the "skeleton AI" / dramatic narrator style.
> Companion to `money-printer-turbo` — used when the user asks for "cool calm voice" or "more cinematic / dramatic."

---

## Voice Selection (Edge TTS)

The "skeleton AI" / dramatic narrator style requires a **deep, calm, authoritative** male voice. **Pacing direction depends on the psychological goal:**

| Voice Name | Tone | Best For | Style Score |
|---|---|---|---|
| **`en-US-ChristopherNeural`** | Deep, calm, authoritative | **Skeleton AI / sophisticated / dramatic** | ★★★★★ |
| `en-US-GuyNeural` | Deep, standard news anchor | General storytelling (less dramatic) | ★★★★ |
| `en-US-RogerNeural` | Warm, deep | Inspiring / motivational stories | ★★★★ |
| `en-US-SteffanNeural` | Storytelling, slightly breathy | Emotional / psychological stories | ★★★ |
| `en-US-AndrewNeural` | Balanced, approachable | Light storytelling, not dark | ★★★ |
| `en-GB-ThomasNeural` | Deep British, authoritative | Royal / historic / prestige narration | ★★★★ |
| `en-GB-RyanNeural` | Calm British, relaxed | Gentle storytelling | ★★★ |
| `en-US-BrianNeural` | Balanced male, versatile | All-purpose, lacks character | ★★ |

**Winner for Skeleton AI / Sophisticated style:** `en-US-ChristopherNeural` + **slightly faster** rate (+5-8%) for natural authoritative pacing — NOT slow (0.80).

---

## Voice Rate Adjustment — CRITICAL UPDATE

Voice rate is a **VideoParams** field, NOT directly exposed via CLI.

| Speed | Effect | When to Use |
|---|---|---|
| `1.0` (default) | Normal conversation | Standard informational |
| `0.80–0.85` | Slow, deliberate, dramatic | **OLD: Skeleton AI / movie trailer** — user hates the "crisps" artifacts from this |
| `0.75` | Very slow, hypnotic | Creepy / suspense — avoid unless requested |
| `0.90` | Slightly calmer | Professional / authoritative |
| `1.05–1.08` | **Slightly faster, natural authoritative** | **NEW: Sophisticated financial / behavioral finance style** |
| `1.10–1.20` | Fast, energetic | Hype / motivation |

**Sophisticated storytelling sweet spot:** `voice_rate=1.05–1.08` (+5-8%). ChristopherNeural at +5% = natural measured authority without drag.

> **Why the change:** User explicitly rejected the 0.80 rate ("dragged, unnatural pauses") and the resulting audio artifacts ("crisps"). The +5-8% rate produces clean audio with natural Socrates-like pacing.

---

## Retention Psychology Framework (Behavioral Finance Content)

**Zero cheap hooks. Zero amateur tactics.** Use these evidence-based frameworks:

| Framework | Principle | Implementation |
|---|---|---|
| **Information Gap (Loewenstein)** | Curiosity from knowledge gap | Open with a question: *"What if the wealthiest person you know... isn't the one with the highest salary?"* |
| **Identity Signaling** | Viewer self-identifies as insider | *"They don't talk about money. They talk about ownership."* → positions viewer as "one who gets it" |
| **Authority + Specificity** | Concrete numbers = credibility | Name **Kiyosaki**, cite **$500k lawyer vs $80k plumber** |
| **Loss Aversion (Kahneman/Tversky)** | Losses weigh 2x gains | Frame house/car as *liabilities* draining wealth — loss frame > gain frame |
| **Agency Restoration** | Viewer regains control | *"Every dollar votes for who you're becoming"* — gives control back |
| **Identity Question Close** | Self-reflection loop | *"Does this make me an owner... or a renter?"* + *"What did you choose today?"* |

---

## Sophisticated Script Structure — 18-Segment Visual-Audio Lock

**Each segment = 1 video clip, trimmed to exact narration duration.** Total: ~85-90s (TikTok sweet spot).

```
SEGMENT MAP (TIMESTAMP → DURATION → PSYCHOLOGY → VISUAL CUE)

0:00   4.5s  Information Gap    "What if wealthiest ≠ highest salary?"         → Wealthy couple walking
0:05   4.0s  Pattern Reveal     "Quiet pattern: generational wealth"           → Family portrait
0:09   3.5s  Identity Signal    "Don't talk money. Talk ownership."            → Business owner / keys
0:12   4.0s  Authority Concrete "Lawyer $500k leases BMW"                      → Luxury car / lease
0:16   4.5s  Identity Contrast  "Plumber $80k owns building"                   → Commercial building
0:21   4.5s  Long-Term Payoff   "20yrs: plumber's grandkids inherit building"  → Grandfather / keys
0:25   3.5s  Loss Frame         "Lawyer's grandkids inherit lease payments"    → Bills / stress
0:28   3.5s  Reframe            "Not income. What you DO with income."         → Decision moment
0:32   3.0s  Authority Named    "Kiyosaki said it 30yrs ago"                   → Book / authority
0:35   5.5s  Core Lesson        "Rich acquire assets, middle=liabilities"      → Asset vs liability
0:40   4.0s  Specific Examples  "House=liability. 401k=asset."                 → House / account
0:44   4.0s  More Examples      "Rental=asset. Financed car=liability."        → Rental / car
0:48   2.5s  Conspiracy Hook    "That's not an accident."                      → Shadow / document
0:53   4.5s  Identity Reframe   "Every dollar votes for who you're becoming"   → Voting metaphor
0:56   3.0s  Pattern Interrupt  "Question isn't 'can I afford?'"               → Credit card pause
0:59   4.5s  Identity Question  "Does this make me owner or renter?"           → Fork in road
1:03   4.0s  Social Norming     "Most choose renter daily, unknowingly"        → Sleepwalking
1:07   3.0s  Perfect Loop Close "What did YOU choose today?"                   → Mirror / direct cam
```

**Total: ~89s | 18 segments | Each clip trimmed to exact duration**

---

## Precise Visual-Audio Lock (Filter Complex Method)

**Replaces the concat.txt + manual merge approach.** Single-pass ffmpeg with exact trim per segment:

```python
# build_retention.py pattern — precise visual-audio mapping
segments = [
    ("What if the wealthiest...", 4.5, ["wealth contrast"]),
    ("Quiet pattern...", 4.0, ["family legacy"]),
    # ... 16 more (text, target_duration, keyword_hints)
]

# For each segment:
# 1. Pick best cached video by duration match (abs(vdur - target) minimized)
# 2. Build ffmpeg filter_complex with trim=0:{target} per segment
# 3. Single filter chain: trim → scale → pad → fps → concat
# 4. Overlay audio with -t {audio_duration}

# Result: 1080x1920@30fps, perfect sync, no generation loss
```

**Advantages over old concat method:**
- Zero "crisps" artifacts (single re-encode)
- Each visual locked to exact narration segment
- 5-10x faster than MoviePy
- Works with mixed-resolution cached videos

---

## Cinematic Script Craft — Anti-Patterns to AVOID

| Anti-Pattern | Why It Fails | Use Instead |
|---|---|---|
| "STOP scrolling" | Amateur, triggers skip reflex | Question-based curiosity gap |
| "Wait for it..." | Cheap retention bait | Information gap that pays off |
| Exaggerated pauses (0.75 rate) | "Crisps" artifacts, unnatural | Natural +5-8% pacing |
| Generic "Here's why..." | No identity hook | Specific authority + numbers |
| "Comment below" CTAs | Low engagement | Self-reflection question that loops to rewatch |

---

## Full Parameter Control (Python Approach)

```python
# sophisticated_video.py — Full parameter control
from app.models.schema import VideoParams
from app.services import task as tm
from app.utils import utils

params = VideoParams(
    video_subject="Financial Literacy - Asset vs Liability",
    video_script="""What if the wealthiest person you know... isn't the one with the highest salary?

[beat]

There's a quiet pattern among people who build generational wealth. 

They don't talk about money. They talk about ownership.

[beat]

A lawyer making five hundred thousand a year leases a BMW. 
A plumber making eighty thousand owns the building his shop sits in.
... (full script)""",
    video_terms=[
        "wealthy couple walking", "family legacy", "business owner keys",
        "luxury car lease", "commercial building", "grandfather teaching",
        "bills stress", "decision moment", "financial book", "assets liabilities",
        "house investment", "rental property", "car payment", "shadow document",
        "voting metaphor", "credit card", "fork in road", "sleepwalking", "mirror"
    ],
    video_source="pexels",
    voice_name="en-US-ChristopherNeural",
    voice_rate=1.05,   # Slightly faster for sophisticated pacing
    subtitle_enabled=False,
    video_aspect="9:16",
    video_count=1,
)

task_id = utils.get_uuid()
result = tm.start(task_id=task_id, params=params, stop_at="video")
```

**Or use the direct ffmpeg filter_complex approach** (see `scripts/build_sophisticated.py` in templates) for disk-efficient, artifact-free assembly.

---

## Windows Pitfalls — Updated

| Issue | Old Workaround | Better Approach |
|---|---|---|
| BrokenPipeError | Manual concat after failure | Pre-build with filter_complex (never hits MoviePy) |
| Whisper 3GB download | Disable subtitles | Keep `subtitle_provider=""` in config.toml |
| LLM hangs (FreeLLMAPI down) | Provide --video-script + --video-terms | **Always** bypass LLM for production — script + terms manually |
| Disk space (temp clips) | Delete old tasks | Filter_complex uses cached videos directly — zero temp clips |
| Long video timeout | Increase terminal timeout | Filter_complex completes in <30s for 90s video |

---

## Related Skills
- `money-printer-turbo` (this skill)
- `tk` — TikTok content strategy references in `references/tiktok-ai-storytelling.md`
- `media/video-edit` — Edit existing video
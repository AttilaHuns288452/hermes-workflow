# TikTok AI Storytelling — Content Pipeline

> For use with MoneyPrinterTurbo. Covers the complete pipeline: niche → script → video → monetization for AI-generated storytelling accounts.

---

## Niche Profile: AI Storytelling / Reddit Stories

| Factor | Value |
|--------|-------|
| **CPM** | $2–8 / 1k views |
| **AI automation** | Very High (nearly fully automated) |
| **Competition** | Low-Medium |
| **Monetization** | Creator Rewards, brand deals, merch, affiliates |
| **Posting cadence** | 1–3x daily, 1+ minute videos |
| **AI disclosure** | Mandatory — unlabeled AI content gets −73% reach |

---

## Niche Expansion: Financial Literacy Storytelling (HIGH CPM)

**Superior to horror/creepy for monetization.** Uses narrative structure with behavioral finance themes.

### Content Types

1. **Two Paths Comparison** — "Two kids, same age, same town. One saves, one spends. Here's how it ended."
2. **Asset vs Liability Frame** — Kiyosaki's framework applied to life decisions
3. **"I Wish I Knew This at 20"** — Hindsight financial lessons with specific numbers
4. **Failure-to-Success Stories** — Side hustles that failed but taught valuable lessons
5. **Generational Wealth Explainers** — How small early decisions compound over 40 years
6. **Identity-Based Wealth** — "Owner vs Renter" identity framing (highest retention)

### CPM Advantage

| Niche | CPM | Audience Intent |
|-------|-----|-----------------|
| **Financial storytelling** | **$4–10** / 1k views | High purchase intent |
| Horror/creepy stories | $2–5 / 1k views | Entertainment |
| True crime | $1–3 / 1k views | Volume-based |

### Retention Psychology — NO AMATEUR HOOKS

**Banned phrases:** "STOP scrolling", "Wait for it", "You won't believe", "Here's why"

**Use instead — Evidence-Based Frameworks:**

| Framework | Opening Line Example | Psychology |
|---|---|---|
| **Information Gap** | "What if the wealthiest person you know... isn't the one with the highest salary?" | Loewenstein — curiosity from knowledge gap |
| **Identity Signal** | "There's a quiet pattern among people who build generational wealth." | Viewer self-identifies as insider |
| **Authority + Specificity** | "A lawyer making $500k leases a BMW. A plumber making $80k owns the building." | Concrete numbers = credibility |
| **Loss Frame** | "Your house? Liability. Your 401k match? Asset." | Kahneman/Tversky — losses weigh 2x gains |
| **Agency Restoration** | "Every dollar you spend... votes for the person you're becoming." | Viewer regains control |
| **Perfect Loop Close** | "What did you choose today?" | Self-reflection → rewatch |

---

## Sophisticated Script Template — 18 Segments (~89s)

**Each segment maps to ONE visual clip, trimmed to exact narration duration.**

```
[HOOK — Information Gap] 0:00-0:05
"What if the wealthiest person you know... isn't the one with the highest salary?"

[PATTERN REVEAL] 0:05-0:09
"There's a quiet pattern among people who build generational wealth."

[IDENTITY SIGNAL] 0:09-0:12
"They don't talk about money. They talk about ownership."

[AUTHORITY + SPECIFICITY A] 0:12-0:16
"A lawyer making five hundred thousand a year leases a BMW."

[IDENTITY CONTRAST] 0:16-0:21
"A plumber making eighty thousand owns the building his shop sits in."

[LONG-TERM PAYOFF] 0:21-0:25
"Twenty years later... the plumber's grandchildren inherit the building."

[LOSS FRAME] 0:25-0:29
"The lawyer's grandchildren inherit the lease payments."

[REFRAME] 0:29-0:32
"This isn't about income. It's about what you DO with income."

[NAMED AUTHORITY] 0:32-0:35
"Robert Kiyosaki said it thirty years ago."

[CORE LESSON] 0:35-0:40
"Rich people acquire assets. The middle class acquires liabilities they THINK are assets."

[CONCRETE EXAMPLES] 0:40-0:44
"Your house? Liability. Your 401k match? Asset."

[MORE EXAMPLES] 0:44-0:48
"That rental property? Asset. The car you finance? Liability."

[CONSPIRACY HOOK] 0:48-0:51
"Here is what nobody tells you:"

[AGENCY RESTORATION] 0:51-0:55
"Every dollar you spend... votes for the person you are becoming."

[PATTERN INTERRUPT] 0:55-0:59
"The question is not can I afford this?"

[IDENTITY QUESTION] 0:59-1:03
"The question is... does this make me an owner... or a renter?"

[SOCIAL NORMING] 1:03-1:07
"Most people choose renter. Every single day. Without realizing it."

[PERFECT LOOP CLOSE] 1:07-1:10
"What did you choose today?"
```

---

## Precise Visual Terms — 18 Keywords for Pexels Search

Use these EXACT terms (one per segment) for `video_terms` parameter:

```
wealthy couple walking
family legacy portrait
business owner keys
luxury car lease
commercial building deed
grandfather teaching grandchildren
financial stress bills
decision crossroads
financial authority book
assets vs liabilities diagram
house investment account
rental property keys
car payment finance
shadow document mystery
voting ballot metaphor
credit card pause
fork in road choice
mirror reflection direct camera
```

**Pro tip:** The 18 terms map 1:1 to the 18 script segments. The filter_complex build script picks cached videos by duration match to each term.

---

## MoneyPrinterTurbo Production Commands

### Full Video with Custom Script + Terms (Bypasses LLM — RECOMMENDED)

```bash
cd ~/Documents/Projects/MoneyPrinterTurbo
source .venv/Scripts/activate

# Use Python script for full parameter control (voice_rate, precise visual mapping)
python build_sophisticated.py
```

### CLI Version (if LLM is working)

```bash
python cli.py \
  --video-subject "Financial Literacy - Asset vs Liability" \
  --video-script "What if the wealthiest person you know... isn't the one with the highest salary? [full script]" \
  --video-terms "wealthy couple walking, family legacy portrait, business owner keys, luxury car lease, commercial building deed, grandfather teaching grandchildren, financial stress bills, decision crossroads, financial authority book, assets vs liabilities diagram, house investment account, rental property keys, car payment finance, shadow document mystery, voting ballot metaphor, credit card pause, fork in road choice, mirror reflection direct camera" \
  --voice-name "en-US-ChristopherNeural" \
  --voice-rate 1.05 \
  --video-aspect "9:16" \
  --no-subtitle-enabled \
  --stop-at video
```

**Note:** CLI doesn't expose `--voice-rate`. Use the Python approach for production.

### Voice Generation Only (Test Voice First)

```bash
# Test Edge TTS voice + rate
edge-tts --voice en-US-ChristopherNeural --rate +5% --text "Your test text" --write-media test.mp3
```

---

## The 30-Video Rule (Unchanged)

> **Post 30 videos before you evaluate anything.** TikTok's algorithm needs 2–3 weeks to learn your audience.

**Launch checklist for Financial Storytelling account:**
- [ ] Produce **10-video buffer** before posting first
- [ ] Each video uses **different psychological framework** (rotate: Info Gap, Identity, Loss Aversion, Authority, Agency)
- [ ] **1080x1920@30fps** — native TikTok spec
- [ ] **AI label** on every post (caption + TikTok toggle)
- [ ] Hook in first 0-3s — **no "STOP scrolling"**
- [ ] Pattern interrupt every 4-5s (visual change locked to narration beat)
- [ ] Caption with **specific numbers** (e.g., "$500k lawyer vs $80k plumber")
- [ ] Respond to every comment (first hour critical)
- [ ] Cross-post to YouTube Shorts / Reels

---

## Monetization Milestones (Financial Niche)

| Followers | Revenue Stream | Est. Earnings |
|---|---|---|
| 0–1,000 | Volume test | $0 |
| 1,000–10,000 | Affiliate (brokerage, books, courses) | $50–500/mo |
| **10,000** | **TikTok Creator Rewards** | $200–2k/mo |
| 10,000–50,000 | Brand deals (fintech, banking, investing apps) | $500–5k/post |
| 50,000+ | Digital products (courses, templates, community) | $5k–50k/mo |

**Financial niche advantage:** Brands pay 3-5x more for financially literate audiences vs entertainment.

---

## Related Skills
- `money-printer-turbo` (this skill)
- `cinematic-dramatic-narration` — Voice selection, script craft, filter_complex build in `references/cinematic-dramatic-narration.md`
- `media/video-edit` — Edit existing video
---
name: ai-marketing-skills
description: Open-source AI marketing and sales automation skills — growth experiments, sales pipeline, content ops, outbound, SEO, finance ops, revenue intelligence, podcast ops, team ops, and more. Battle-tested on real pipelines. Use for ANY marketing, sales, content, SEO, or growth automation task.
tags: [marketing, sales, content, seo, growth, outbound, finance-ops, revenue, podcast, team-ops, automation]
platforms: [linux, macos, windows]
---

# AI Marketing Skills — Hermes Integration

## Overview

[AI Marketing Skills](https://github.com/ericosiu/ai-marketing-skills) provide production-ready, battle-tested marketing and sales automation workflows. 15+ categories, each with Python scripts, SKILL.md files, and requirements.txt — all MIT licensed, 2.6k stars.

**Repo:** `~/Documents/Projects/ai-marketing-skills/`

## Category Reference

### 🧪 Growth Engine
Real marketing experiments with statistical rigor (Mann-Whitney U, Bootstrap CI). Creates experiments, scores results, auto-promotes winners to a living playbook.
```bash
cd ~/Documents/Projects/ai-marketing-skills/growth-engine
python experiment-engine.py create --hypothesis "..." --variable format --variants '["thread","single"]' --metric impressions
```
**Files:** `experiment-engine.py`, `autogrowth-weekly-scorecard.py`, `pacing-alert.py`

### 💰 Sales Pipeline
Complete visitor → pipeline automation: RB2B routing, intent scoring, company dedup, deal resurrection, trigger prospecting, self-learning ICP.
```bash
cd ~/Documents/Projects/ai-marketing-skills/sales-pipeline
python rb2b_instantly_router.py
```
**Files:** `rb2b_instantly_router.py`, `deal_resurrector.py`, `icp_learning_analyzer.py`, `rb2b_suppression_pipeline.py`, `rb2b_webhook_ingest.py`

### 📝 Content Ops
90+ quality scoring with expert panel (9 personas), editorial brain, quote mining from podcasts/RSS.
```bash
cd ~/Documents/Projects/ai-marketing-skills/content-ops
# Uses SKILL.md for LLM-guided workflows — runs as agent prompt + optional Python scripts
```

### 📤 Outbound Engine
Cold email automation: ICP → sequence writing → infrastructure audit → capacity planning.
```bash
cd ~/Documents/Projects/ai-marketing-skills/outbound-engine
```

### 🔍 SEO Ops
Keyword intelligence, content gap analysis, GSC optimization, trend detection, content attack briefs.
```bash
cd ~/Documents/Projects/ai-marketing-skills/seo-ops
```

### 💵 Finance Ops
AI CFO: executive briefings from QuickBooks exports (P&L, Balance Sheet, Cash Flow), burn rate, runway, cost estimates, scenario modeling.
```bash
cd ~/Documents/Projects/ai-marketing-skills/finance-ops
python cfo-briefing.py
```

### 📊 Revenue Intelligence
Sales call insight extraction (Gong-style), content-to-revenue attribution, multi-source client reporting.

### 🎯 Conversion Ops
CRO audits, landing page scoring, survey segmentation → lead magnet generation.
```bash
cd ~/Documents/Projects/ai-marketing-skills/conversion-ops
```

### 🎙️ Podcast Ops
Podcast-to-Everything: one episode → clips, threads, LinkedIn articles, newsletters, quote cards, blog outlines, scripts.

### 👥 Team Ops
"Elon Algorithm" performance audits, meeting-to-action item extraction.

### 📋 Sales Playbook
Value-based pricing framework: pre-call briefings, tiered packaging, post-call analysis, pattern library.

### 🔬 Autoresearch
Karpathy-style content optimization: 50+ variant generation, 5-expert panel scoring, evolution through rounds. (Philosophically related to `karpathy-guidelines` skill — complement, not replacement.)

### 🖼️ Deck Generator
AI slide decks with Imagen 4.0 + Google Slides API. (Complementary to `creative/claude-design` — deck-generator for production decks, claude-design for prototypes.)

### 🎬 YouTube Competitive Analysis
Outlier detection and packaging pattern extraction from competitor YouTube channels.

### 🐦 X Long-Form + Humanizer
Founder-voice X articles with 24-pattern AI slop detector + ASCII diagrams. (Complementary to creative/ascii-art.)

### 🔄 Closed-Loop Analytics Upgrade
Upgrades any marketing skill to judge output by platform analytics instead of vibes.

### 🛡️ Security & PII
PII Sanitizer: scans code/data for sensitive info. Pre-commit hook blocks PII leaks.

### 📹 Video Pipelines
- `short-form-pipeline`: Extract viral clips (TikTok/Reels/Shorts) from long-form YouTube
- `video-clip-pipeline`: Long-form → highlight clips pipeline
- `video-caption-generator`: Transcribe Drive videos → social captions + YouTube titles

(Complementary to `media/money-printer-turbo` — different pipelines for different content needs.)

### 📋 Eval
Universal AI output evaluation: 13 criterion types, multi-turn/single-turn, threshold gating.

### 🧩 Utilities
- `clone-site`: Clone any website → pixel-perfect Next.js replica (complementary to `creative/sketch`)
- `lead-dossier`: Multi-source account research + cascade enrichment
- `content-eval`: Content idea generation + expert panel scoring

## Conflict Resolution With Existing Skills

| Existing Hermes Skill | AI Marketing Skill | Relationship |
|---|---|---|
| `karpathy-guidelines` | `autoresearch` | **Complementary.** Both inspired by Karpathy. Autoresearch is content optimization loops; karpathy-guidelines are coding behavior rules. Different domains. |
| `creative/claude-design` | `deck-generator` | **Complementary.** Deck-generator = production slide decks via Imagen+Slides API. Claude-design = HTML prototypes. Different outputs. |
| `creative/sketch` / `creative/popular-web-designs` | `clone-site` | **Complementary.** Clone-site = full Next.js replica of existing sites. Sketch = throwaway HTML mockups. Different use cases. |
| `media/money-printer-turbo` | video pipelines | **Complementary.** Different pipeline purposes (AI short videos vs marketing clip extraction). |
| `creative/ascii-art` | X Long-Form + Humanizer | **Complementary.** Different formats (pure ASCII art vs writing with diagram support). |

All AI Marketing skills are **new domain additions** — no Hermes skill is replaced.

## Workflow

When the user asks for marketing/sales/growth tasks:
1. Identify the category (growth, sales, content, SEO, finance, etc.)
2. Load this skill
3. Route to the specific category directory
4. Use the SKILL.md in that directory for workflow guidance
5. Run Python scripts when needed (e.g., experiment-engine.py for growth experiments)

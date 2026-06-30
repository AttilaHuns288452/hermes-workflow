# Token-Saver Enforcement in /decide — Evolution

## Session 2026-06-12 — First Enforcement
The token-saver probe chain was documented in `Mandatory Rule #4` as "ACTIVE — enforced" for the first time. Prior to this session it existed only as passive prose in the token-saver skill.

## Session 2026-06-23 — Restructured for Real Enforcement
The decide skill was completely rewritten to solve a critical problem: **the rules were documented as "enforced" but the agent never followed them.**

### What Changed
1. **Enforcement rules moved to the top** — Rule 1 (Token Saver), Rule 2 (OpenMontage), Rule 3 (CodeGraph/Graphify), Rule 4 (task_tier) are now the literal first thing you read after the frontmatter.
2. **"Mandatory Rule #4/5" numbering removed** — replaced with simpler Rule 1-4 naming.
3. **Aspirational content separated** — "ENFORCED RULES" (🔴 must follow) vs "Aspirational Guidelines" (🟡 use judgment). Previously everything was mixed together.
4. **Self-Audit step added** — Before finishing any session, a checklist verifies Rule 1-3 were followed.
5. **Stale counts fixed** — "14/19 projects" → "21/24 projects" (reality had outgrown the docs).
6. **Philosophical content moved down** — Reasoning Protocol (steps 1-5) moved below the enforcement rules.

### Why Prior Enforcement Failed
- The agent never had a **self-check** mechanism — it could read the rules and still not follow them
- The enforcement rules were buried in a 318-line document among routing tables and philosophy
- There was no consequence for skipping the probe chain (no one checked)
- The OpenMontage rule existed but the agent consistently defaulted to ad-hoc FFmpeg scripts
- "ACTIVE enforcement" was aspirational text, not operational behavior

### How This Is Different
- The agent now has a **self-audit checklist** that runs before finishing each session
- The enforcement rules are the **first content** in the skill file
- Every violation is now a **conscious choice** to skip the rules, not an accidental oversight
- The self-audit creates accountability — if the checklist is unchecked, the agent must fix it

### Current Token Saver State (as of 2026-06-23)
- **CodeGraph** (v0.9.9): 945 files, 16,092 nodes, 43,795 edges — always available
- **Graphify** (v0.8.37): 21/24 projects indexed (all except Hermes Skills, hermes-dashboard, unit-converter which have no code)
- **ECC index**: 34MB across 5,821 files — queries work in ~300 tokens
- **Savings**: 50× to 1,233× per query
- **Projects with indices**: ai-marketing-skills, AI-Youtube-Shorts-Generator, anime-waifu-quiz, API-mega-list, atm-crypto-bank, atm-machine, buildable-plugin-skills, countdown-timer, ECC, ecosystem-test, free-ai-tools, freebuff-test, freelance-rate-calculator, freellmapi, free-llm-api, graphify, hermes-workflow, hw-new, MoneyPrinterTurbo, MoneyPrinterV2, task-manager-cli

# External Source Map — 2026-09 import (system_prompts_leaks)

> Per-source analysis required by the import process: purpose, technique, Hermes compatibility, duplication, risks, usefulness rating. Corpus: `~/Documents/SkillReferences/system_prompts_leaks/` (430 prompt files; shallow clone of github.com/asgeirtj/system_prompts_leaks, 2026-09-11).

## Method

1. Inventory by directory → prioritize small, non-archive, coding/agent-ops files (large chatbot prompts like the 330KB Claude Code captures were sampled for structure only — Hermes must NOT import monolithic always-loaded prompts).
2. For each prioritized source: extract the underlying technique, check against existing Hermes capability, rate, integrate or reject.

## Sources analyzed

| # | Source (path in repo) | Original purpose | Technique extracted | Hermes-compatible? | Duplicates existing? | Risks | Rating | Integrated where |
|---|---|---|---|---|---|---|---|---|
| 1 | `Anthropic/claude-code/agents/Explore.md` | Read-only code-search subagent | Verbatim read-only contract; breadth levels (quick/medium/very-thorough); parallel grep/read; "reads excerpts, not whole files" limitation stated in whenToUse | Yes — matches delegate_task read-only roles | Overlaps subagent-delegation → composed, not replaced | Low; importing verbatim would duplicate | HIGH | P1 in `agent-patterns`; decide #3 |
| 2 | `Anthropic/claude-code/agents/Plan.md` | Read-only planning subagent | Read-only plan contract; required output = critical-files list | Yes | Composes with writing-plans | Low | HIGH | P1/P3 |
| 3 | `Anthropic/claude-code/agents/general-purpose.md` | General subagent | "Don't re-delegate your whole assignment"; report-concise-essentials; never create files proactively | Yes | Complements | Low | MED | P10 |
| 4 | `OpenAI/Codex/plan_mode.md` | Conversational planning mode | Two kinds of unknowns (discoverable vs preference); decision-complete plans; non-mutating exploration allowed during planning; clarifying-questions only when material | Yes — strong fit with writing-plans + ask-user pattern | Gaps in writing-plans (unknown-handling, decision-completeness) | Medium: plan-mode mode-locking NOT imported (Hermes has no plan-mode state machine) | HIGH | P2/P3; decide #4 |
| 5 | `Anthropic/claude-code/skills/code-review/*` | Multi-angle bug hunt on diffs | 7 finder angles; recall-biased 1-vote verify (CONFIRMED/PLAUSIBLE/REFUTED with refutation bar); failure_scenario per finding; severity cap 10 | Yes | code-review skill had spec/standards axes but no bug-hunt mode → added as reference | Medium: multi-agent fan-out assumes Agent tool; adapted to "parallel or sequential inline" | HIGH | `code-review/references/multi-angle-diff-review.md`; decide #5 |
| 6 | `Perplexity/deep-research.md` | Deep research loop | Decompose→single-entity parallel keyword search; cross-validate with explicit conflict reporting; claim-level citations; clarifying-question gates; execute-code only for real computational work | Yes | research-orchestrator was a 6-line skeleton → replaced with full procedure | Medium: citation token format is Perplexity-specific — NOT imported; only the discipline | HIGH | `research-orchestrator` rewritten; decide #6 |
| 7 | `Anthropic/claude-code/commands/compact.md` | Session compaction | Structured state summary (intent/decisions/current work/errors/security-constraints-verbatim) | Yes | New — Hermes had no compaction-artifact discipline | Low | MED-HIGH | P8; decide #8 |
| 8 | `Cursor/cursor.md` | Coding-agent system prompt | Sampling only — demonstrates 18KB monolithic always-loaded prompt with tool rules inline | Partially | Duplicates what SOUL+decide do better | High if imported whole (context cost, rigidity) | LOW for import; noted as anti-pattern | agent-patterns anti-patterns #3 |
| 9 | `Misc/devin-cli.md` | Autonomous coding agent | Explicit tool-boundary phrasing ("you do NOT have access to X, attempting will fail"); bounded autonomy language | Yes | Complements delegation prompts | Low | MED | P9 |
| 10 | `Misc/opencode.md` | OpenCode CLI prompt | Terminal-native output conventions; minimal-file-creation rules | Yes | Mostly already in Hermes norms | Low | LOW-MED | P9/P10 |
| 11 | `Misc/hermes.md` | **Captured stock Nous Hermes Agent prompt (Ásgeir's machine)** | Validates that Attila's SOUL.md memory-discipline section is framework-native, not custom. Also shows a stock prompt WITHOUT the decide pipeline → the decide pipeline is Attila's competitive advantage; keep it lean | n/a (reference) | — | None | INFO | Validated Phase-1 map |
| 12 | `Anthropic/claude-code/skills/workflow-authoring/SKILL.md` | Authoring repeatable workflows | Not yet fully processed — candidate for future import into skill-creator | TBD | TBD | — | UNRATED | — |
| 13 | `Anthropic/claude-code/skills/run-skill-generator/SKILL.md` | Skill generation guardrails | Same — candidate | TBD | TBD | — | UNRATED | — |
| 14 | `Perplexity/perplexity-ai.md`, `Google/gemini-*`, `xAI/grok-*`, `OpenAI/*` chatbot prompts | Consumer chatbot behavior | Mostly consumer formatting/personality — not agent-ops | Mostly no | Duplicates SOUL.md | Personality drift risk | LOW | Rejected for import |
| 15 | `Anthropic/anthropic_reminders.md` | Injected reminder texts | Reminder-injection pattern (IP/citation guardrails) | Partial | SOUL.md Step 15 covers citations | Could duplicate/conflict | LOW | Not imported; revisit if citation drift appears |

## Rejected outright

- **ChatGPT/Claude/Gemini consumer personality blocks** — import would fight Hermes' existing identity and user_context coaching contract.
- **Claude Code's 170–330KB full system prompts** — architecture anti-pattern (see above); only their *techniques* were extracted.
- **Codex plan-mode state machine** — Hermes has no plan-mode toggle; only the planning discipline was imported.
- **ChatGPT advanced-memory topic-bucket schema** — Hermes' declarative-facts memory discipline is already cleaner (P7).

## Deferred (unrated, worth a future pass)

- `workflow-authoring` and `run-skill-generator` skills → potentially strengthen `skill-creator`.
- `Claude Cowork` dispatch + setup skills (2026-08 capture) → delegation-topology ideas.
- `Claude Code subagent system prompts` beyond Explore/Plan (statusline-setup, claude-code-guide) for output-contract conventions.

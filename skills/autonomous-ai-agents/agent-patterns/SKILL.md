---
name: agent-patterns
description: Distilled agent-engineering patterns from captured production prompts (Claude Code agents/skills, Codex plan mode, Cursor, Perplexity Deep Research, Devin, OpenCode). Load when designing or improving Hermes skills, subagents, delegation flows, planning workflows, research loops, or context management.
---

# Agent Patterns — generalized from captured production prompts

> **Source corpus:** `~/Documents/SkillReferences/system_prompts_leaks/` (asgeirtj/system_prompts_leaks, cloned 2026-09-11). Techniques generalized — no wording copied. Full source map: `references/agent-techniques-2026-09.md` (this skill) + `skills/decide/SKILL.md` "Imported Techniques" section.
>
> **Use:** when authoring or patching skills (`skill-creator`), designing subagent contracts (`subagent-delegation`), or improving workflows. Each pattern lists WHERE it is already applied in Hermes — check there first before re-implementing.

## P1. Read-only subagent boundary (Anthropic Explore/Plan agents)

Research/planning subagents get an explicit, verbatim read-only contract: no file creation, no edits, no redirects/heredocs, no state-changing commands. The main agent writes; read-only agents only gather and report.

- **Applied in Hermes:** `subagent-delegation` — MiMo visual-QA and exploration delegations must be described as read-only in the delegation prompt.
- **Why it matters:** a planning agent that edits escapes its contract and poisons the working tree before the plan is even agreed.

## P2. Two kinds of unknowns (Codex plan mode)

Before asking the user anything: (a) **discoverable facts** — resolve by exploring the repo/system first; asking without exploring is a failure; (b) **preferences/tradeoffs** — genuinely not derivable, ask early with 2–4 mutually exclusive options + a recommended default. Never ask what the environment can answer; batch questions.

- **Applied in Hermes:** decide "Imported Techniques" #4/#7; `research-orchestrator` pre-flight gate 2.

## P3. Decision-complete plans (Codex plan mode)

A plan is done when the implementer (human or agent) makes no decisions: goal, success criteria, interfaces, data flow, edge cases/failure modes, test criteria, explicit assumptions/defaults. Plan compactly (3–5 sections); mention ≤3 file paths unless specificity prevents mistakes. Non-mutating exploration is allowed and encouraged *before and during* planning; plan-implementation actions are not.

- **Applied in Hermes:** `writing-plans` (compatible — its "zero-context engineer" framing satisfies decision-completeness); decide #4.

## P4. Multi-angle diff review + 1-vote recall-biased verification (Claude Code code-review)

Reviews pin a diff, hunt via independent angles (line-scan / removed-behavior / cross-file / reuse / simplification / efficiency / altitude), pass every candidate with a nameable failure scenario to verification, then keep CONFIRMED + PLAUSIBLE and refute only what is provably impossible from the code. Findings ranked by severity, correctness outranks cleanup.

- **Applied in Hermes:** `code-review/references/multi-angle-diff-review.md`.

## P5. Claim-level citation discipline (Perplexity)

Every sentence with externally-derived fact carries its source inline. Sources that conflict are reported as conflicts with confidence — never averaged. Uncorroborated single sources are marked as such. Missing facts are reported missing, never filled from model memory.

- **Applied in Hermes:** `research-orchestrator` Steps 4–6; SOUL.md Step 15.

## P6. Parallel keyword search fan-out (Perplexity)

Decompose into single-entity sub-questions; issue short keyword queries, batched in ONE turn. Compound queries ("A and B market cap") fail; parallel single-entity queries succeed. Scrape for depth only when snippets don't answer.

- **Applied in Hermes:** `research-orchestrator` Steps 1–3.

## P7. Memory discipline: durable facts vs. session state (Hermes-native, validated against Anthropic memory prompt)

Memory holds durable, user-preference facts written declaratively. Task progress, session outcomes, and logs belong to session_search/transcripts, not memory. Procedures belong in skills. This Hermes rule already matches the best captured practice — do not import heavier memory schemas (ChatGPT-style topic-bucketed memory) without evidence they beat it.

- **Applied in Hermes:** SOUL.md memory section (native).

## P8. Context compaction as a maintained artifact (Anthropic /compact)

For long multi-phase work, keep a running structured state summary: primary request/intent, decisions made, current phase, next step, errors-and-fixes, security constraints verbatim. On any single point of failure (crash, compaction, rate limit) the summary reconstructs the session. Security constraints must survive compaction verbatim.

- **Applied in Hermes:** decide #8. Use the `todo` tool or a session note as the artifact; do not rely on the transcript.

## P9. Explicit non-goals and tool-boundaries in agent contracts (Devin/OpenCode pattern)

Agent role prompts state what the agent does NOT do and which tools it lacks, not only what it does. "Attempting to edit files will fail" beats "please don't edit".

- **Applied in Hermes:** subagent-delegation prompt templates; `agent-patterns` itself is a reference (no execution).

## P10. Skill/agent role separation (Claude Code agents + skills model)

One agent = one narrow contract + explicit `whenToUse` + disallowed tools + output contract. Composition happens at the orchestrator level (the main agent loads/coordinates), never by agents spawning unbounded sub-agents ("do not re-delegate your entire assignment").

- **Applied in Hermes:** decide's domain routing; `subagent-delegation` swarm rules. When creating new skills via `skill-creator`, give every skill: purpose, triggers, inputs/outputs, tools, procedure, verification, failure behavior — the schema this repo's skills follow.

## Anti-patterns observed in the corpus (do not import)

1. **Vibe-based conventions enforcement** — flagging "spirit of the doc" violations without quoting the rule (Claude Code mitigates this; older prompts don't).
2. **Enforcement theater** — claiming rules are "ENFORCED" when the framework cannot enforce them (this repo's own decide skill had this; now documented honestly).
3. **Massive always-loaded prompts** — Cursor/Claude Code carry 170–330KB system prompts with heavy duplication. Hermes' SOUL.md + decide + on-demand skills is the better architecture; keep it.
4. **Duplicated instructions across layers** — the same rule in system prompt, tool description, and skill conflicts over time. One authoritative layer per rule (see decide "placement" principles).

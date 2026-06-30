---
name: session_memory
description: >
  Retrieves missing context from prior session histories and memory when the
  current session lacks confidence. Treats ambiguity as a retrieval trigger,
  not a knowledge gap, and always routes through /decide before acting.
triggers:
  - session lacks context on a prior decision or preference
  - ambiguous references to past work, patterns, or choices
  - conflicting signals in the current conversation
  - user references earlier work that is not in current context
---

# Session Memory

## Purpose
When the current session lacks context — decision, preference, pattern, or prior work — actively look for that context in other session histories or memory before defaulting to assumptions or asking the user.

## When to Activate
Treat any of the following as a retrieval trigger:
- Ambiguity: user references prior work, decisions, or preferences that are not present in current context.
- Missing context: the assistant cannot act confidently because relevant history is absent.
- Conflicting signals: the current prompt suggests multiple incompatible prior paths or decisions.
- Explicit recall: user asks "what did we decide before", "last time we...", or similar.
- Pre-action gap: before acting on a task where prior conventions or choices likely matter.

Do NOT ask the user to repeat context if it is likely recoverable from session history or persistent memory.

## Retrieval Behavior
1. Identify the missing context from the current prompt and gaps in the conversation.
2. Search session history for relevant prior sessions using `session_search` with focused queries.
3. Inspect returned sessions, prioritizing:
   - prior decisions related to the current topic
   - stated preferences or conventions
   - recurring workflows or established patterns
   - prior artifacts (paths, configs, deliverables) that affect current execution
4. If session search is insufficient, review persistent memory for durable facts relevant to the query.
5. Surface retrieved context clearly and concisely before proceeding.

### Context Clues: What to Look For
- Decisions: approvals, rejected options, selected approaches
- Preferences: UI/style choices, model selection rules, tool order
- Patterns: file naming, directory conventions, commit message style
- Prior work: existing project plans, partial implementations, known blockers
- Context clues: usernames, paths, environment facts, API behaviors

### Ambiguous Term Resolution
When the user mentions broad terms like "dashboard" without specifying which one, check BOTH services — this user's setup has two independent dashboards on different ports:

| Term | Port | What it provides |
|------|------|-----------------|
| "Hermes Dashboard", "dashboard" | 9119 | Live chat, skills, config, cron, agent sessions |
| "FreeLLM API", "session-memory", "API dashboard" | 3001 | Session history browser, memory files (MEMORY.md/USER.md), usage stats, model management, API keys |

The `/session-memory` feature lives on port 3001 (FreeLLM API dashboard), NOT on port 9119 (Hermes Dashboard). When the user asks for "session-memory" or "session history," retrieve context from port 3001's API, not 9119.

### surfacing Guidelines
- Summarize retrieved context with source attribution when helpful.
- If multiple relevant sessions exist, merge consensus and flag conflicts.
- Preserve retrieved facts in the current turn so downstream tools benefit.

## /decide Handoff
After retrieval, always route through `/decide` before taking action.
- Pass retrieved context into `/decide` as input.
- Let `/decide` determine the appropriate next path, tool, or response.
- Do not execute domain actions directly after retrieval; treat `/decide` as the mandatory next step.

## Integration Notes
- This skill is passive by design: it does not act as a standalone executor.
- Any skill can trigger this one when encountering missing context.
- `/decide` remains the central reasoning brain; `session_memory` only enriches its input.
- Respect user privacy: only retrieve what is necessary to resolve the current ambiguity.

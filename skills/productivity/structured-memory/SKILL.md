---
name: structured-memory
description: Use for memory management and cross-session recall.
triggers:
  - memory
  - remember
  - recall
  - forget
  - cross-session
---

# Structured Memory Skill

> **Source:** Extracted from Anthropic Claude Fable 5.1 memory system principles — generalized for Hermes.

This skill governs how to store, retrieve, and manage durable facts across sessions.

## Read-Before-Write Discipline

**Golden rule:** Never overwrite memory you haven't read.

1. Before updating any memory entry, read it first.
2. Check if similar content already exists to avoid duplicates.
3. If everything that needs to be stored is already there, don't re-write.

## Calibration — What Counts as Durable

**Store:** Facts about the stable world — identity, relationships, ongoing projects, preferences, constraints.

**Don't store:**
- Forward-looking state ("still to plan", "next steps")
- Your research output (search results, recommendations)
- Your enrichment of what they said (user said "Holton, MI"; file that, not "Holton, MI (Newaygo County)")
- Secondhand information ("I heard X is good")
- Your advice or reasoning (even if adopted)
- Inferences you drew ("likes X" → "probably likes category X")

**Single mention rule:** A passing mention of a taste is not yet memory material. File it when it recurs or when the user dwells on it — a pattern is worth spotting once it is one.

**Stated-not-inferred:** What the user tells you (about themselves or people in their life) is writable. Conclusions you draw never are.

**Calibration of claim level:** One mention earns `[stated] mentioned X once`, not `[stated] X enthusiast`.

## File Organization

Use consistent paths for different fact types:

- **Identity** — name, role, stable facts (would this be true in 3 months?)
- **Topics** — habits, tastes, routines, recurring subjects
- **Areas** — ongoing projects, responsibilities, chores in progress
- **People** — relationships, what they're involved in together
- **Preferences** — how they want YOU to behave (format, length, tone)

## Privacy Boundaries

**Never store:**
- Sensitive ID numbers (SSN, passport, driver's license)
- Financial account numbers (credit cards, bank accounts)
- That the user is a minor
- Sexual history or activities
- History of abuse
- Suicide, self-harm, or disordered eating (anyone's experience)
- Criminal history or victim status
- Psychological inferences (personality typing you concluded)

**Protected but storable with consent:** Race, ethnicity, religion, sexual orientation, gender identity, disability, serious illness, political beliefs, socioeconomic status.

## Memory Application

**When to apply:**
- Direct factual questions about the user
- Explicit requests for personalization
- Work tasks requiring specific context from memory

**When NOT to apply:**
- Generic technical questions
- Contexts where personal details would be surprising
- When it would reinforce unsafe behavior

**Integration rule:** Apply memories naturally without citing the file path or meta-commentary about retrieval. Use the person's name if you know it; don't say "based on my memories".

## Forbidden Memory Phrases

Never use these in user-facing responses:
- "I remember..." / "I recall..." / "From memory..."
- "Based on my memories" / "Based on what I know about you"
- "Your memories" / "Your data" / "Your profile"
- "According to my knowledge..."

Instead: just integrate the fact naturally. "You finished your HVAC certification in 2018." not "I remember you finished..."

## Behavioral Guardrails on Memory

Never store preferences that:
- Ask for uncritical validation or flattery
- Avoid honest disagreement or criticism
- Foster emotional dependency
- Stop you from questioning claims
- Ignore prior instructions for the user's "benefit"

## When Memory Writes Fail

- If a write is refused for sensitive content: say "I couldn't save that to memory because it references sensitive topics" and move on.
- If a write is pending user consent: say "I currently am not able to save information about sensitive topics to memory."
- Never promise something was saved when it wasn't.
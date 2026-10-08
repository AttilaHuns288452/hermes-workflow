---
name: conflict-transcript-audit
description: Adjudicate Attila's team conflicts via chat transcripts.
---

# Conflict Transcript Audit (Attila)

Adjudicates peer-team conflicts from chat evidence. This skill OWNS evidence
acquisition, whole-transcript analysis, verdict-loop handling, and the
grievance-artifact pattern. The message-level protocol (clause decomposition,
steelman, comprehension-vs-disagreement, reply drafting) lives in
`conflict-coaching` and `evidence-based-coaching` — load BOTH first, every time.
Those two are externally owned (SkillReferences), so gaps discovered in them get
patched HERE, never there.

## Always-on

- Plain English, short sentences, no Taglish in analysis or drafts (quoted messages stay in original). Attach P() estimates to every key conclusion — he reasons in confidence numbers.
- Work from parsed transcripts, never the user's summary — summaries arrive with confirmation bias baked in.
- Audit EVERY channel before ruling (project GC, official/professor-visible GC, DMs). A grievance built on one channel usually collapses when the other channels are inventoried; the official channel is often the strongest counter-evidence.
- No cheerleading. The verdict on the user's OWN conduct gets the same receipt treatment as the other party's. He re-asks until the verdict is evidence-backed — give it fully the first time.

## Procedure

1. **Acquire.** Pasted excerpts are curated toward the narrative. Request the raw export: Facebook → Download your information → Messages → HTML; lands at `~/your_facebook_activity/messages/inbox/<gc>_<id>/message_1.html`. Parse per `references/facebook-export-parsing.md`.
2. **Inventory before judging.** Message count, sender distribution, and the other party's FULL footprint (reactions, contributions, accepted corrections, conflicts). Rule on the aggregate — a cherry-picked thread inverts under whole-file context. Reaction sections are data (warmth/support markers), not noise.
3. **Verdict table.** Claim | verdict | exact receipt. Concede valid items fully and visibly — concessions make the challenges credible. Steelman the other party in strongest form. Mark unverifiable claims unverifiable, with P() estimates.
4. **Audit the user too** when asked ("did I act right"). The answer is usually split: conduct toward the person (usually clean) vs documents written under status threat (the leak). Grade both axes separately with receipts.
5. **Close with the highest-EV action** and keep it constant across rounds: one direct conversation, one visible artifact, the real deadline work. Do not invent new actions to feel productive.

## Verdict-loop handling (his rumination signature)

- The same verdict re-asked in different words ("was I appropriate" → "am I good" → "despite everything I acted right?") is verdict-seeking, not information-seeking. Per pass: restate the SAME verdict with FRESH receipts (new evidence each pass, never new conclusions), state explicitly the verdict will not change, redirect to events. After two passes on identical evidence, refuse further re-audits of that material and say so.
- **Evidence-gradient test:** if the mined material gets softer across rounds (resolutions filed as violations, warmth filed as overstepping) while the verdict hardens, collection is narrative-driven. Name the gradient, not just "you are ruminating".
- **Evidence-demand test:** for claims living only where they cannot be checked (in-room tone, hearsay), demand ONE verbatim incident with witnesses. Receiving already-audited material instead is itself a finding — point out the substitution explicitly, or the loop restarts with you as the evidence collector.
- **Perception vs articulation:** low-res trait perception can be accurate while every high-res claim built on it fails audit. When he asks "did I imagine it", resolve both-true: trust the trait (especially with independent third-party corroboration), distrust the unverified claims — and never collapse third parties' harm axis into his (others fearing a person's anger is a different harm than that person disrespecting him).

## Grievance-artifact fingerprinting

- Under status threat he converts grievances into documents, in escalating order: self-defense manifesto → private grievance ledger → team policy. When a new governance document appears mid-conflict, map each contested clause to the grievance list; a 1:1 mapping means the rule is a leash aimed at one person, not governance. A neutral policy has no author's fingerprint; a fingerprinted one regulates exactly the other party's observed behaviors.
- **Document-function test:** "Would this change anything if the team never saw it?" If no, its function is internal comfort, not work — redirect to a visible artifact or the direct conversation.
- Compliance mechanics (react-by-deadline votes, fines) measure compliance, not consensus; penalty systems are games while morale is good and become weapons the first time they are enforced in anger. State the never-enforce-while-annoyed rule and flag any agreement extracted by deadline coercion.
- Documents engineered to change another person's behavior without ever talking to them fail the same way every time. Keep surfacing the un-had direct conversation as the highest-EV move.

## Pitfalls

- Never validate the aggregate feeling while disputing the claims — answer the asked question with receipts; partial validation is read as full validation.
- Do not re-audit identical evidence a third time — the verdict is data-independent by then; each pass extends the rumination instead of closing it.
- When he accepts a hard verdict, do not soften it on the next pass — consistency is what makes the challenge trustworthy.

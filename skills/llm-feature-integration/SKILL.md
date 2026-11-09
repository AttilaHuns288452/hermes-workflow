---
name: llm-feature-integration
description: Use when adding an LLM-powered feature to an app.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [llm, ai-features, api-integration, fallbacks, prompting]
    related_skills: [qa-suite-engineering, patch-hygiene, error-handling]
---

# LLM Feature Integration

Wire an LLM into an app feature (generated answers, artifacts, rewrites,
persona chat) that must stay correct when the LLM is absent, slow, or wrong.
The deterministic path is the product; the LLM enriches it.

## When to Use

- Adding generated explanations, artifacts, quizzes, rewrites, or persona chat
  to an app that must keep working without the LLM.
- Choosing or switching the model behind an existing LLM feature, or extending
  its output contract (new keys, new pickable resources).

Not for agent/tool-use harness construction (`agent-harness-construction`) or
pure cost-routing of model calls (`cost-aware-llm-pipeline`).

## Procedure

1. **Reuse first.** Find the existing registries, spec builders, and renderers
   before building new ones — the LLM's job is to CHOOSE among existing,
   validated building blocks, not to generate presentation code.
2. **Config via env.** `LLM_MODEL` / `LLM_API_KEY` (provider equivalents) in a
   gitignored `.env`, loaded in the server bootstrap; one env var switches
   models. Never hardcode model ids or keys.
3. **Pick the model by probing candidates with the REAL task shape** — the
   actual persona prompt, production-sized payload, and output contract —
   measuring latency and contract compliance. Toy probes misrank (see
   pitfalls). Record the runner-up for a one-line switch.
4. **Strict contract, lenient parse.** Declare the output shape (keys, caps,
   types) in the persona prompt; parse defensively (accept array-or-object
   where both are reasonable, coerce, cap counts). Validate every
   model-supplied IDENTIFIER/selection against a server-side library; drop
   unknown values (log them), never render them.
5. **Deterministic-first gating.** The LLM fills only gaps the deterministic
   composer left empty (picks a diagram only when none exists, generates a
   quiz only when none was computed). An intent-tuned deterministic artifact
   beats a generic model pick; the model never overrides it.
6. **Persona = voice + grounding + contract** in one system message. Repeat
   critical contract requirements in the USER message too (last-position
   attention) and still expect variance. When the user says "train it to act
   accordingly" and the provider exposes no training API, this IS the
   training — say so once in the delivery.
7. **Fallback = the tested path.** No key / timeout / parse failure →
   deterministic output under the same UI contract. The unit suite runs with
   no key so it asserts exactly this path.
8. **Failures visible, backoff gentle.** Log every LLM failure with its reason
   (status, truncation, parse error) — a silent `false` costs an hour of
   guessing. Size the timeout to observed p95 latency; a timeout-triggered
   backoff must not silence the feature for minutes. Also surface the error
   CLASS (no secrets) in a health/debug endpoint (`llmError: null | 'aborted' |
   '403 …'`): on serverless hosts the runtime logs are unreachable from the
   tools you have, and fallback output is visually identical to success. Make
   "enrichment actually fired" a production check (a `polished`-style flag on
   the live API response), not a local-only claim.
9. **Token budget for the contract.** Multi-section JSON output needs
   `max_tokens` sized to the full response — silent truncation masquerades as
   missing trailing keys, which looks exactly like a contract violation.

## Grounding guarantees (source-grounded output)

When the LLM rewrites, summarizes, quizzes, or polishes content that must stay
faithful to a source document (report, notes, spec), the source is the
authority and generated text is a proposal to be proven, not trusted:

1. **Verify support extractively.** Split the source into approved sentences;
   every generated claim must be reconstructable from one or more approved
   sentences. Unsupported spans get dropped and replaced with the approved
   text for that span. Shared numbers or vocabulary are not proof of support:
   a claim can echo the source's words and still assert something the source
   never says.
2. **Scope-check before answering.** Generic aliases and polysemous common
   words ("collapse", "cache", "factoring") match in-scope topics by accident;
   foreign-domain questions must get an honest out-of-scope answer, never a
   fluent in-scope hallucination.
3. **Bounded partial answers.** A question only partially covered gets only
   the supported part plus an explicit statement of what the source does not
   establish — never filled from model knowledge, never silently truncated.
   For compound questions, bound by the weakest conjunct: answer each
   supported segment, name the unsupported segments, cap confidence at
   medium, and never answer the unsupported side.
4. **Citations follow the quote.** Derive the reference from the chunk the
   generated text actually quotes, not from a topic/label match — a
   topically-right citation attached to a different quote is a grounding
   failure.
5. **Validated quiz and document content.** Quiz items draw question, answer, and choices
   from approved sentences; keep a deterministic fallback quiz built from
   approved sentences for when the model's items fail validation. Generated
   documents (guides, notes, reference sheets) obey the answer rules:
   insufficient evidence yields a narrower or clearly marked partial
   document with named gaps — never padded to length with unsupported facts. When
   re-verifying generated quiz items, check the answer against the source entry the
   question asks about (label embedded in the question), not the question's own wording —
   template phrasing swamps the support check and drops real items as unverifiable.
   Validate the requested document topic/type against a server-side enum derived from the
   source and reject unknown values with a clear message before generation begins.
6. **Adversarial regression tests** for exactly these failure modes: an
   unsupported claim is rejected, a generic term does not fake scope, a
   foreign-domain question is flagged, a mismatched citation is repaired,
   and a cached answer is never served across different inputs.
7. **History resolves references, never supplies evidence.** Follow-ups may use
   conversation context to resolve "that", "those two", "explain it again", but every
   substantive follow-up re-retrieves from the source, and prior AI-generated turns are
   excluded from evidence candidates — the model's own earlier claims are not authority.
8. **Source selection is part of the answer contract.** An explicit empty source
   selection is general-knowledge mode: the response carries the mode label, the
   validator FORBIDS source citations (nothing grounds them), and the system is never
   silently widened to "all sources". A question resolving to content outside the
   selected sources gets a re-scope hint naming the missing source — never a quiet
   answer borrowed from a different source.

## Model tools and interactive artifacts

When the model chooses actions or attaches artifacts on top of composed answers:

1. **Tools run real implementations, never model code.** Each tool maps to server-side
   retrieval or a trusted algorithm executor; tool output joins the validation evidence
   so later citations can trace to it. Reject unknown tool names.
2. **Bound the loop** (rounds × calls) and skip the output cache for tool-assisted
   answers — their content varies with tool output, and caching serves one run's
   evidence to the next.
3. **Artifacts are allowlisted data**: type and ids validated against a server-side
   registry, params bounded JSON, unknown entries dropped whole. An artifact the model
   attempted but failed validation is dropped — never replaced with a fabricated
   stand-in.
4. **Deterministic artifact bridges**: when the model composes prose WITHOUT attempting
  an artifact, keep the draft's intent-driven artifact (comparison table, diagram for
  visual asks). Gate the bridge on the same intent the renderer uses — bridging on
  "the draft has one" ships diagrams into short definition answers that never asked.

## Streaming output

- Streaming needs its own output envelope (markdown first for live rendering, then one
  fenced JSON metadata block) feeding the SAME validator and artifact pipeline. Repeat
  the grounding rules in the stream prompt: streamed prose trips fact-pinning far more
  than compact JSON — harden the prompt, never relax the validator.
- Adding streaming breaks every response-capturing harness that calls `res.json()`.
  Update test/QA listeners to branch on content-type and read the SSE envelope's final
  `done` event.
- Render streamed tokens as plain text (textContent — no markdown mid-stream), offer a
  Stop that aborts and keeps the partial answer labeled as partial; the completed
  response replaces the placeholder with the fully rendered answer.

## Pitfalls

- **Small models drop trailing JSON keys on SHORT synthetic payloads while
  complying on full production payloads** (attention drift in a long persona).
  Probe compliance with production-shaped payloads BEFORE building fallbacks
  for the "missing" extras — a toy-input false negative builds dead machinery
  for a path that already works in production. Prompt reminders reduce, not
  eliminate, the variance.
- Compliance proven on the raw API call can still fail through the real
  endpoint (system prompt + history + user message together change behavior).
  Verify compliance through the app's own route, not the direct call.
- LLM prose is untrusted input: render through an escape-first markdown
  pipeline (all input escaped before any tag emission), never raw HTML
  injection — and document that guarantee at the call site.
- Enrichment latency redefines "the response": a placeholder renders first,
  enriched content lands seconds later — or never (fallback). The UI must look
  complete in the deterministic state too, and QA must wait on the
  content-bearing node (see `qa-suite-engineering`).
- **Local green hides serverless egress failures.** Providers can reject
  UA-less or datacenter-origin requests (403 / bot-check) that pass fine from a
  dev machine, and cold egress latency can exceed a locally-tuned timeout —
  the feature then silently degrades to fallback in production only. Send a
  browser User-Agent with server-side LLM calls, size the timeout for egress
  (≈2× local p95, floor 25s), and make a production round-trip part of the
  deliverable.
- If the app has local heuristic generation (intent classifiers, keyword
  composers), the LLM layer sits BEHIND its output, not beside it — two
  sources of truth for one answer diverge the first time they disagree.
- Key any LLM output cache on the COMPLETE input tuple (question, topic,
  level, draft): a partial key silently serves one context's answer to
  another, which reads as model error but is cache contamination.
- A fallback result that contradicts a config change you just made is often
  process-lifetime state: in-memory caches (answers, completions) and require-time env
  reads survive until restart. Restart the process and re-run before debugging
  validation logic or blaming the provider.
- Client code that runs under sandboxed unit tests must guard browser globals
  (`typeof AbortController === 'function'`); a vm test context lacks them while the
  browser has them, and the resulting failure looks like broken feature code.
- **Shared validators rebuild objects from an allowlist** — a new field added at
  the producer (artifact params, provenance metadata) is silently dropped by the
  validator's rebuild case and surfaces downstream as a mysterious missing
  feature. Extend the validator's case in the same change and assert the field
  end-to-end through the rendered output.
- Support checks must search section HEADINGS as well as body text — a
  concept introduced only by its heading gets falsely dropped as
  unverifiable and the answer loses real evidence. The inverse guard stays:
  a matching citation ref alone is not verification; the claim text must
  still occur in the cited passage.
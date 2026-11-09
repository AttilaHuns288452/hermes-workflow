---
name: brief-verification
description: "Verify a pasted brief's claims before executing it."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [brief, prd, audit, verification, claims, delegation]
    related_skills: [product-lens, grilling, quant-trading-research, software-engineering]
---

# Brief Verification

Verify a pasted brief's load-bearing claims against the live system **before** executing it.

A brief written by another model in another context is confident, well-formatted, and built on facts from a machine state that may not exist. It will cite benchmarks that were never computed, versions that belong to a different product, capabilities that are docs-only, and an org chart that does not match the actual profiles. Executing it verbatim builds work on a false baseline — and a false baseline is worse than no baseline, because every later decision calibrates against it.

The user knows this. When they paste a brief they usually pair it with a warning that the author misses context, and they expect you to reason about the brief itself, not just obey it. Treat the brief as **a claim set to audit**, not a specification to implement.

## When to Use

- User pastes a multi-section mission prompt, PRD, audit directive, or "execute this" document authored by another model.
- A brief lists capabilities, versions, benchmarks, team roles, or file locations you are expected to build on.
- Any instruction whose first phase is "discover and verify the existing environment" — that instruction is the author admitting the brief is unverified.

Not for: a live user request (verify scope, don't audit them), or a plan you wrote yourself.

## Procedure

### 1. Extract claims, don't read for intent

Read once for the claim inventory, not the goal. Mark every sentence that asserts a fact about the machine:

- **Benchmark** — "previous results were +X% return, Sharpe Y"
- **Capability** — "we have Monte Carlo / portfolio optimization / an eight-module ecosystem"
- **Identity** — "the integration I previously configured", named repos, named paths
- **Version** — "the update to version N", named CLIs and releases
- **Org** — which profile owns which responsibility
- **Credential** — "the API keys are configured"

A brief with 10+ such claims has 10+ chances to be wrong. That is the whole audit surface.

### 2. Verify each claim with the cheapest decisive probe

| Claim type | Probe | Failure signature |
|---|---|---|
| Benchmark numbers | Grep the repo for the **literal figure**: `grep -rn "38.55" --include=*.md --include=*.csv --include=*.json .` | Zero hits = the number was never computed here. Do not accept the surrounding prose as corroboration. |
| Capability exists | `hermes skills list \| grep <name>`; check the dir has code, not just SKILL.md; check it is in `config skills.external_dirs` if it lives outside the skills root | Listed in a brief but ~8KB SKILL.md with no scripts = documentation, not capability |
| Version / product | `command -v <cli> && <cli> --version` for every candidate | The version often belongs to an unrelated product (a model version, not a CLI) |
| Identity / path | `ls -d <path>`; grep the repo for the claimed module | Brief says "integrated"; it is a standalone script in a project dir with no cron and no profile |
| Org / ownership | Read each `profiles/<name>/SOUL.md` and quote its actual role line | Brief assigns QA to a content-writing profile; the real `qa` profile already exists |
| Credential live | Hit one **signed** endpoint, not just the public one | Public returns `code: 0`, signed returns an auth error → the endpoint works, the key is stale |

Probe the cheapest thing that can falsify the claim. Never probe all of it — one decisive command per claim.

### 3. Build a drift table before touching anything

One row per contradicted claim: **brief says → reality → why it matters**. "Why it matters" is the row's entire value; without it the table is trivia.

A benchmark that does not exist matters because every later strategy gets judged against fiction. A docs-only "ecosystem" matters because the brief's Phase 1 becomes "repair" work on something with nothing to repair. A mis-assigned QA profile matters because the agent that produces work would also be signing it off.

### 4. Decide per claim, and say so

Every claim gets one of:

- **Execute** — verified true, proceed as written.
- **Adapt** — the goal is right, the stated mechanism is wrong. Do the equivalent thing on the real system.
- **Skip, with reason** — and skip the *reason it existed*, not just the line. If a step depends on an unverified capability, skipping it is correct; building it on sand produces working-looking stages that cannot be tested.

Never silently correct the brief. The user needs the drift report **before** the work, because their own mental model came from the same source.

### 5. Then act, and lead with the correction

Deliver the drift findings first, then the work. A session that quietly builds the adaptation and mentions the discrepancy in an appendix has hidden the most important fact.

### 6. Audit proposed NEW components against the incumbent

Briefs love to add an intelligence layer — a decision model, a framework, a service. Before integrating one, answer three questions in order:

1. **What already does this job?** Grep for the existing implementation. It is usually there, under a name the brief did not use (an LLM judge module already wired into the decision path, a rule-based classifier already labelling every row).
2. **Is the incumbent measurable?** Find its outcome record. A judge that logs verdicts but whose `outcome` column is empty has never been scored — it cannot be beaten because it has never been tried.
3. **Can the proposed one be A/B'd on the same data?** If the incumbent has no realized outcomes, the honest answer is "not yet evaluable", not "the new one is better".

When the incumbent is unmeasurable, the finding is that **the measurement is the missing feature**, and fixing that has higher value than adding the proposed layer. Say so, and say what has to accumulate before the comparison is possible (how many realized outcomes, over roughly how long). Then the user can decide to wait rather than pay for a component whose lift is unprovable.

A new component also often solves a problem the brief misidentified: a regime classifier proposed for a system whose regimes are already rule-labelled *and already validated by the data* (one regime's median expected return is materially negative, another positive) cannot improve on a rule that is already correct. Verify the incumbent's accuracy before accepting that the new one is needed.

## Pitfalls

1. **A confident benchmark is not a corroborated benchmark.** Grep for the literal number. If no artifact contains it, the figure is fabricated or misremembered regardless of how many decimal places it has — and it is usually optimistic against every real number in the repo, which is exactly what makes it dangerous as a baseline.
2. **"We already have X" is a claim about a directory, not a capability.** A listed module may be a SKILL.md in a reference tree that is not even on the load path. Check for scripts, tests, or runnable code before treating it as existing.
3. **A version number in a brief may belong to a different product than the one being discussed.** Confirm the product from the installed binary's own `--version`, not from the brief's prose describing what it is.
4. **Two systems with the same name are not the same system.** "Paper trading" can mean "simulates fills locally from OHLCV" and "places orders on an exchange demo account" in the same project tree. Establish which one owns the capability before improving either; reports that mix their figures are wrong at the root.
5. **Verify org claims against SOUL.md, never against the brief's org chart.** Role names in a brief drift toward plausible-sounding assignments; the profile files are ground truth, and the correct owner usually already exists under a name the brief did not use.
6. **A public endpoint returning `code: 0` does not mean the credentials work.** Probe a signed endpoint. This separates "the integration is broken" (it is not) from "this key is stale" (it usually is) — two completely different fixes.
7. **The brief's own caution is evidence.** If it says "verify each starting point", "do not assume", or "treat these as historical reference, not verified current results", the author is telling you it did not check. Believe that line above the others.
8. **Do not deliver the audit as a wall of contradiction.** Group by impact, put the one claim that would have caused real damage first, and keep each row to one line of why-it-matters.
9. **A brief that proposes a new component is making a claim about the incumbent too.** "Add X for capability Y" asserts that Y is currently missing or done badly. Verify Y's current implementation and whether it has outcome data before agreeing — otherwise you are replacing something unmeasured with something also unmeasured, and calling it an improvement.
10. **When the brief's own numbers are optimistic against every artifact in the repo, treat the optimism itself as the finding.** Fabricated benchmarks are usually directionally flattering; the gap between the claim and the worst real number is the risk you are actually reporting.

## Related

- `product-lens` — validate the *why* of a product direction. This skill validates the *facts* behind an already-written brief.
- `grilling` — interview the user to settle decisions. Use when the brief's ambiguity is about intent, not fact.
- `quant-trading-research` — the domain skill when the verified brief turns out to be about trading systems.

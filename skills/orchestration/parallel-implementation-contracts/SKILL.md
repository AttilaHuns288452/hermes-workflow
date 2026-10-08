---
name: parallel-implementation-contracts
description: "Use when splitting coupled multi-file builds across agents."
version: 1.0.0
author: Hermes Agent
triggers:
  - parallel implementation
  - split build across agents
  - multi-file rewrite delegation
  - interface contract
  - disjoint file ownership
---

# Parallel Implementation Contracts

For when the work is NOT yet independent: a tightly-coupled multi-file build that must ship across parallel implementers. (Already-independent investigation/bugfix domains -> `dispatching-parallel-agents`; trustworthy read-only dispatches -> `subagent-playbook`; model roles -> `subagent-delegation`.) The point: write the independence into existence first — the contract manufactures the boundaries that make parallelism safe.

## Procedure

1. **Probe the surface mechanically before drafting the split.** Enumerate the file tree and grep the cross-module call surface (globals, imports, DOM hooks). Never split from a remembered file map — the spec names files your notes missed, and a contract that misses a coupled file sends two implementers into the same code.
2. **Probe live data shapes** (hit the running API/endpoints with real requests) instead of trusting docs or notes; pin exact field names in the contract.
3. **Write ONE contract file** (e.g. `/tmp/<project>_contract.md`) — the only authority on cross-file interfaces. Copy `templates/implementation-contract.md` for the section shape.
4. **Dispatch one entry per owner** in a single `delegate_task` call. Each brief is self-contained (the child knows nothing): goal, owned files (only these), contract path ("read FIRST"), distilled requirements for that area, verification duties. One entry = one agent — splitting one file's work across entries spawns agents fighting over the same file.
5. **Write the QA harness against contract-pinned selectors before dispatching.** Assert on stable `data-*` hooks named in the contract, never on invented class names, so parallel implementers' internal styling choices cannot break the tests. Integration smoke-testing is the orchestrator's job — implementers cannot meaningfully smoke-test an app while siblings are mid-rewrite; each verifies only its own files (syntax checks) plus any untouched test suite.
6. **Read every owned file back from disk before integrating** (exists at the owned path, syntax-clean, plausible size) — a dispatch summary is a self-report, not evidence. Then integrate once, run the full suite together, fix cross-file seams yourself, and commit.

## Rules

- The contract pins INTERFACES only (IDs, signatures, loader order, tokens) — implementations stay free inside their seams. Over-pinning internals wastes the parallelism.
- Briefs state that other modules are being rewritten simultaneously: trust them at their contracted surface, never "fix" a file you do not own.
- New files need loader entries (script tags/imports) — pin loader order in the contract and name who owns the loader file, or scripts load out of order at integration.
- Pin call DIRECTION wherever two owned modules trigger each other ("X owns content and calls `Y.show()`; `Y.show()` is show-only and never calls back into X"). An unpinned A↔B seam where each wires the full flow through the other's entry point produces infinite render recursion that kills the page at first interaction — and the crash surfaces in an innocent consumer.
- Shared canvas/SVG colors read from the token source at draw time (e.g. CSS custom props) so one theme system governs hand-drawn graphics too.
- For big single files, require sectioned writes (skeleton, then append) — children time out writing huge files in one go.

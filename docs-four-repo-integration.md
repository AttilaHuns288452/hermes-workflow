# Hermes Four-Repository Integration

Status: study complete, implementation staged
Date: 2026-10-09

## Scope and evidence

This record covers four upstream repositories requested for integration into the live Hermes profile. Initial reconnaissance was read-only. A recovery manifest was captured before any integration write at:

`/home/attila/.hermes/cache/scratch/hermes-four-repo-baseline-20261009-172219/`

Baseline evidence:

- Hermes: `v0.21.6+131.g38880bd.dirty`, upstream `38880bd2`.
- Local skill files: 407, 41 categories, zero broken frontmatter, zero missing `name` fields.
- Per-turn configured external injection: ECC only.
- Reference retrieval: `reference_index_refresh.py` indexes the `~/Documents/SkillReferences` corpus; `lightrag_build_index.py` indexes local skills plus its configured reference roots.
- LightRAG skill index at study time: 2,025 documents.
- Curator: present but disabled. Existing ecosystem audit, skill provenance, skill-management rollback, and background review machinery remain canonical.
- OpenDesign MCP: disabled in the live registry. It is not treated as an active dependency.

No upstream installer was run. The four repositories were inspected in scratch workspaces and their content was treated as untrusted data.

## Repository studies

### A. UI/UX Pro Max

Source: `https://github.com/nextlevelbuilder/ui-ux-pro-max-skill`

Inspected checkout: `/home/attila/.hermes/cache/scratch/uux-study`

Observed commit: `50d8a7de0900119855614541f15a1a616691eb33`
Tag metadata: `v2.15.0-58-g50d8a7d`; package metadata still says `2.13.0`.
License: MIT, Copyright Next Level Builder.

Inspected the README, CLAUDE.md, package/plugin metadata, all seven skill entrypoints in the checkout, the full UI/UX Pro Max skill package, references, data, scripts, tests, fixtures, catalog/provenance files, and CLI templates. The useful capability is not just prose:

- A deterministic stdlib Python BM25 and regex search engine in `src/ui-ux-pro-max/scripts/core.py` and `search.py`.
- `styles.csv`, `products.csv`, `colors.csv`, `typography.csv`, `ux-guidelines.csv`, `charts.csv`, `motion.csv`, `icons.csv`, `app-interface.csv`, `react-performance.csv`, Google Fonts data, and 22 stack-specific datasets.
- A design-system generator in `scripts/design_system.py` with 192 industry reasoning rules, explicit decision-rule parsing, mode-aware palette handling, design dials, and optional `MASTER.md` plus page overrides.
- Data validation and provenance checks in `scripts/validate_data.py`, plus a substantial test suite.
- Stack guidance is version-aware and labels legacy guidance instead of silently mixing framework generations.

Disposition:

- `ADOPT SEPARATELY`: the data/search package and the main `ui-ux-pro-max` skill. Hermes has `impeccable`, `frontend-design`, `accessibility`, `dataviz`, and an ECC design-system skill, but none provides this structured local design database or deterministic query engine.
- `COMPLEMENT`: compose its product/style/palette/stack lookup with `impeccable` for the design workflow, `design-system` for token auditing, `accessibility` for WCAG implementation, and `dataviz` for chart construction. Do not make it the universal design authority.
- `REFERENCE ONLY`: banner, brand, slide, and UI-styling packages because they overlap existing capabilities or require optional media APIs.
- `REJECT`: the Claude Marketplace/npm installer as a Hermes installation mechanism. Hermes uses `skill_manage` and its own skill roots.
- `BLOCKED`: optional asset-generation scripts that require external image APIs. They are not needed for the accepted search/data integration.

Adaptations required: replace `${CLAUDE_PLUGIN_ROOT}` examples with `${HERMES_SKILL_DIR}`, remove Claude-specific install instructions from the active skill body, preserve the static data/scripts and MIT notice, and keep persistence opt-in with explicit project output paths.

### B. Vibe-Skills

Source: `https://github.com/foryourhealth111-pixel/Vibe-Skills`

Inspected checkout: `/home/attila/.hermes/cache/scratch/Vibe-Skills`

Observed commit: `ddcaa2affca93c1efe026d008b6b93709e5fb7e2`, tag `v4.1.0`.
License: Apache-2.0, with `NOTICE`, `THIRD_PARTY_LICENSES.md`, and `config/upstream-lock.json`.

The repository is a governed Vibe Code Orchestrator, not merely a skill pack. Its runtime includes planner/executor/verifier components, adapters, installers, a CLI, 249 test files, governance configuration, and a historical 254-skill corpus. Its own `docs/governance/bundled-skill-retention-matrix.md` says the live built-in specialist count is zero and that the historical `bundled/skills/` tree is reference or migration residue. Installing the VCO controller would introduce a second orchestration/runtime layer and is therefore not compatible with Hermes.

The complete corpus was enumerated and the candidates that can materially help this user were read in full, including their support files where present:

- `statistical-analysis`: assumption checks, test selection, effect sizes, power analysis, Bayesian and reporting references, plus `scripts/assumption_checks.py`.
- `ml-data-leakage-guard`: prediction-time availability test and leakage patterns for preprocessing, target encoding, temporal data, CV, and post-event features.
- `property-based-testing`: Hypothesis and fast-check properties, generators, shrinking, round-trip/idempotence/invariant patterns.
- `evaluating-code-models`: BigCode/HumanEval/MBPP/MultiPL-E workflow and pass@k cautions.
- `shap`: model explanation, explainer selection, plots, bias/debugging workflows, and production caveats.
- `transformer-lens-interpretability`: activation caching, patching, circuit analysis, and mechanistic-interpretability workflows.
- `deslop`: a narrow AI-generated-code cleanup pass, distinct from broad correctness review.

Disposition:

- `ADOPT SEPARATELY`: the six unique ML/evaluation skills above except `deslop`, with support files preserved. They serve the user's quantitative trading, ML, model evaluation, and agent research workflows and are not currently installed by name.
- `MERGE`: `deslop` guidance into Hermes `simplify`, because both are cleanup workflows and a second cleanup authority would be unnecessary.
- `ALREADY SATISFIED / REJECT`: VCO workflow skills such as brainstorming, planning, TDD, debugging, review, verification, and spec-kit. Hermes already owns these procedures and importing them would create duplicates.
- `REFERENCE ONLY`: the VCO runtime kernel, governance JSONs, protocols, and the remaining specialist corpus. They are useful architecture examples but not a reason to add a second orchestrator.
- `BLOCKED`: skills requiring paid or absent providers, lab/cloud accounts, Sentry/Figma auth, or external media APIs.

The accepted skill files retain Vibe-Skills attribution and source commit. Unsupported Claude/Codex frontmatter fields and host-specific install commands will not be active Hermes instructions.

### C. One Skill to Rule Them All

Source: `https://github.com/rebelytics/one-skill-to-rule-them-all`

Inspected checkout: `/home/attila/.hermes/cache/scratch/osttra`

Observed commit: `da860265ae968bdc6bb13b96c2c75fcb61176b72`, version `3.5.0`.
License: CC-BY-4.0. Attribution required to Eoghan Henn / rebelytics.com.

Inspected `SKILL.md`, all seven references, all three scripts, plugin manifests, release/workflow files, and license/history. The project implements a session-wide task observer with per-observation files, sibling-family checks, staged skill updates, review approval, archival/status conventions, and Claude-specific hooks and paths.

Disposition:

- `REJECT`: installing the Task Observer skill, `new-observation.sh`, its observation directory, Claude hooks, or its staging/install model. Hermes already has the canonical improvement substrate: curator telemetry/backups, ecosystem audits, background review, `skill_manage`, provenance ledgers, LightRAG, session search, and persistent memory. The upstream skill also explicitly conflicts with Hermes by forbidding the harness skill-save control.
- `EXTEND`: Hermes skill-authoring and ecosystem-audit procedures with the portable parts: sibling/family propagation checks, the instrument-guard principle that an empty scan is a claim about the instrument, and the second-violation rule that repeated failure should move to a structural guard instead of another wording change.
- `REFERENCE ONLY`: weekly approval escalation, parked/carrier status semantics, presence checks before applying, and the core-size/delivery gate. These should inform the existing curator if it is re-enabled, not create a second queue or log.
- `BLOCKED`: Claude hook integration. It would need a separate Hermes-native design and explicit approval; it is not required for this integration.

No second observer or hook was installed.

### D. Agent Rules Books

Source: `https://github.com/ciembor/agent-rules-books`

Inspected checkout: `/home/attila/.hermes/cache/scratch/agent-rules-books`

Observed commit: `893a88a6fce3a80c565bf39ac65021b43a8b2990`, `v0.6-3-g893a88a`.
License: MIT, Copyright Maciej Ciemborowicz.

The repository contains 14 book rule sets, each with `SKILL.md`, `mini`, `nano`, and `full` variants, plus usage guidance, a compatibility matrix, workbench traceability, release history, and no executable runtime dependency. The compact files are intended for on-demand skills, while full files are deeper references. The matrix identifies overlaps and two conflict pairs, including DDD versus enterprise application patterns.

Disposition:

- `REFERENCE ONLY`: retain the repository as a searchable external reference corpus. Its compact/full separation is compatible with Hermes progressive disclosure, but importing all 14 as active skills would create competing authorities with `software-engineering`, `domain-modeling`, `red-green-refactor`, `code-review`, and reliability skills.
- `ALREADY SATISFIED`: general clean code, construction, architecture, DDD, refactoring, and release reliability principles are already substantially covered by Hermes canonical skills.
- `COMPLEMENT`: use the book matrix and mini files as point-in-time references when a task needs a specific bias, especially legacy-code characterization, data-intensive systems, release reliability, or behavior-preserving refactoring.
- `REJECT`: bulk active installation and the upstream `npx skills` installer. Hermes should not add a second global skill installer.
- `BLOCKED`: none for local reference use. The repository has no test suite in the checkout; its own release and compatibility artifacts are the validation evidence.

## Cross-repository capability map

| Capability | Upstream evidence | Hermes overlap | Decision |
|---|---|---|---|
| Structured UI design search | UUPM `scripts/core.py`, `data/*.csv` | No equivalent local dataset | Adopt separately |
| Product-level design-system reasoning | UUPM `design_system.py`, `ui-reasoning.csv` | `design-system`, `impeccable` cover adjacent layers | Complement |
| Accessibility/responsive UI rules | UUPM UX/app-interface CSVs | `accessibility`, `impeccable`, `dataviz` | Keep UUPM as searchable reference, not sole authority |
| Governed planner/executor/verifier runtime | Vibe `packages/runtime-core`, `vgo-cli` | Hermes agent loop, decide, delegation, verification | Reject as competing runtime |
| Statistical analysis | Vibe `statistical-analysis` | No focused local equivalent | Adopt separately |
| ML leakage prevention | Vibe `ml-data-leakage-guard` | `quant-trading-research` has backtest discipline but no general leakage gate | Adopt separately |
| Property-based testing | Vibe `property-based-testing` | TDD and testing skills, no property-testing skill | Adopt separately |
| Code-model benchmarks | Vibe `evaluating-code-models` | `agent-eval` compares agents, not benchmark harnesses | Adopt separately |
| Explainability | Vibe `shap` | No local SHAP workflow | Adopt separately |
| Mechanistic interpretability | Vibe `transformer-lens-interpretability` | No local equivalent | Adopt separately |
| AI-slop cleanup | Vibe `deslop` | `simplify` cleanup scope overlaps | Merge into simplify |
| Session observer | Task Observer `SKILL.md`, `new-observation.sh` | Curator, background review, ecosystem audits | Reject runtime, extend methods |
| Family/sibling propagation | Task Observer `observation-log.md` | Not explicit in current authoring/audit | Extend authoring/audit |
| Structural escalation after repeated violation | Task Observer `signals.md` | Not explicit as a named rule | Extend authoring/audit |
| Compact engineering rules | Agent Rules Books `*.mini.md` | Canonical engineering skills already present | Reference-only |
| Full engineering references | Agent Rules Books `*.md` | LightRAG/reference index suitable | Reference-only |

## Target architecture

Keep the existing Hermes flow as the only execution architecture:

`request -> tier/intent -> targeted skill discovery -> canonical procedure -> tools/delegation -> verification -> reusable observation -> controlled improvement`

The integration adds data and references at the edges, not another router:

- UI task -> `ui-ux-pro-max` only when structured style/palette/stack lookup is useful -> `impeccable`/`frontend-design`/`accessibility`/`dataviz` for implementation and review.
- ML/quant task -> focused Vibe-derived skill when its trigger matches -> project-specific skill such as `quant-trading-research` -> measured verification.
- Engineering task -> existing `software-engineering` and project skill; use Agent Rules Books through reference search when a focused book bias is warranted.
- Skill maintenance -> existing `skill_manage`/curator/audit path, strengthened by sibling checks and structural-escalation guidance. No new observer.

Active prompt cost remains bounded: accepted skills expose concise trigger-bearing `SKILL.md` files; large data, references, and full book variants are loaded only through `skill_view(..., file_path=...)` or reference search.

## Recovery and update policy

Before live writes, the affected skill directories and canonical audit files are archived as a timestamped tarball, while the baseline manifest remains available. The integration manifest records source commits, licenses, target paths, and dispositions. Updates are controlled: fetch a source into a scratch clone, compare source commit and local changes, adapt rather than overwrite, run validators, rebuild indexes, and only then replace a staged local copy. No active skill is auto-overwritten by an upstream update.

## Planned implementation

1. Persist the four upstream source checkouts under `~/Documents/SkillReferences/external/` as reference mirrors, without adding them to per-turn injected external skill roots.
2. Add the adapted UUPM search/data skill under `~/.hermes/skills/design/ui-ux-pro-max/`.
3. Add six unique Vibe-derived ML/evaluation skills under `~/.hermes/skills/` and merge the narrow `deslop` boundary into `simplify`.
4. Patch Hermes authoring/audit guidance with the attributed Task Observer methods.
5. Patch ecosystem audit snapshotting to notice the four persistent reference mirrors and local head changes.
6. Rebuild reference and LightRAG indexes, run source validators, discovery checks, and representative integration tests.

## Implementation record

- Recovery archive: `/home/attila/.hermes/backups/four-repo-integration-prewrite-20261009.tar.gz`.
- Persistent source mirrors: `/home/attila/.hermes/upstream-sources/four-repo-integration/{uux-study,Vibe-Skills,agent-rules-books,osttra}`.
- Integration manifest: `/home/attila/.hermes/four-repo-integration-manifest.json`.
- Active staged additions: `skills/design/ui-ux-pro-max`, `skills/data-science/statistical-analysis`, `skills/mlops/data-quality/ml-data-leakage-guard`, `skills/testing/property-based-testing`, `skills/mlops/evaluation/evaluating-code-models`, `skills/mlops/explainability/shap`, and `skills/mlops/interpretability/transformer-lens-interpretability`.
- Existing canonical skills extended: `software-development/simplify`, `software-development/hermes-agent-skill-authoring`, and `workflow/ecosystem-audit`.
- The four mirrors remain outside `skills.external_dirs`, so they are not injected into every session. Their pinned Git heads and manifest hash are now included in the existing ecosystem audit snapshot.

## Verification results

### Passed

- UI/UX Pro Max validator: 12 domain files, 22 stack files, and `ui-reasoning.csv` validated successfully.
- UI/UX Pro Max tests: 164 passed, 8,249 subtests passed in 21.29 seconds.
- Full installed-skill audit: 415 discovered skills, 41 categories, 0 broken frontmatter, 0 missing `name` fields; the seven accepted skill names are enabled in `hermes skills list`.
- LightRAG rebuilt successfully: 2,033 skills indexed at `/home/attila/.hermes/lightrag_index/skill_index.json`.
- Search discovery returns the adapted UI/UX Pro Max and property-based-testing skills.
- Staged-skill provenance and correction markers were checked after adaptation.
- Agent Rules Books study completed: all 14 entrypoints and mini/nano variants read; only the legacy-code workflow met the distinct-workflow threshold.

### Corrections applied before acceptance

- Statistical examples now distinguish mean-difference CIs from Cohen's d CIs, correct Welch/Student terminology, and avoid a broken placeholder Bayes-factor implementation.
- Leakage examples now require train-only mappings, out-of-fold or leave-one-out encodings for cross-validation, and shifted rolling features.
- Property-based testing no longer teaches removed fast-check string arbitraries as current APIs.
- Code-model evaluation now has an explicit no-host-execution gate and a restricted Docker invocation with an image-tag step.
- SHAP guidance now states that baselines can reorder rankings and that explanations do not certify fairness or causality.
- TransformerLens guidance now reflects temporary-hook cleanup behavior and distinguishes persistent hook management.

### Not fully tested

- Optional NumPy/Pandas/Pingouin, SHAP, TransformerLens, and BigCode runtime examples were not executed because their dependencies are absent and no automatic package installation was authorized.
- Docker benchmark execution was not run because it would download images and execute generated code.
- Fresh-process persistence was verified with new CLI subprocesses: `hermes skills list` returned the accepted skills, and LightRAG queries returned `legacy-code-change-safety`, `shap`, and `ml-data-leakage-guard`. A full interactive desktop `/reset` was not required for filesystem/index persistence.

### Remaining risks

- UI/UX Pro Max has a minor provenance gap: six bundled font files lack local OFL text, although upstream metadata identifies their licenses.
- Agent Rules Books remains reference-only because its full content is book-derived and should not become a competing engineering authority.
- The six Vibe-derived skills remain on-demand guidance, not installed runtime packages. Their dependencies are deliberately not added globally.
- `docx-comment-reply` remains blocked because its write-back path depends on a broken sibling path and undisclosed Anthropic-restricted material.
- Existing unrelated skills contain historical dangling-reference strings; the global link scan is not a clean acceptance gate without path-aware parsing.

## Final disposition

Accepted into the live Hermes skill tree with provenance and rollback coverage: the UI/UX Pro Max core search/data skill, six corrected Vibe specialist skills, the narrow `deslop` boundary in `simplify`, Task Observer sibling-review and structural-escalation methods in existing authoring/audit guidance, and ecosystem mirror drift detection.

Reference-only: Agent Rules Books packages and non-runtime UI/UX Pro Max sibling bundles. Rejected or blocked: bulk Vibe import, leaked system-prompt material, OpenDesign activation, and `docx-comment-reply` runtime adoption.

Rollback is available from `/home/attila/.hermes/backups/four-repo-integration-prewrite-20261009.tar.gz`. Future updates must be staged from a scratch checkout, compared against the pinned manifest, adapted without automatic overwrite, validated, and followed by a LightRAG rebuild and ecosystem audit.

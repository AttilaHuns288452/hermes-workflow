# <Project> Implementation Contract

<!-- The ONLY authority on cross-file interfaces. Each owner implements against this file and must not edit files it does not own. Integration and cross-file fixes belong to the orchestrator. -->

## 1. Files & Ownership

<!-- Every file owned by exactly one agent. Name orchestrator-only / shared files nobody else edits. -->

## 2. Loader / Import Order

<!-- Exact script-tag or import order. New files need loader entries — name who owns the loader file. -->

## 3. Module APIs

<!-- Pinned signature per module (window.* or exports). Callers use ONLY these; implementations are free inside them. -->

## 4. Shared IDs / Selectors

<!-- Stable hooks (data-* attributes preferred over class names) that QA asserts on and modules query. -->

## 5. Tokens / Constants

<!-- Shared design tokens, palettes, enums — one source of truth (e.g. CSS custom props read at draw time). -->

## 6. Per-Owner Behavior Requirements

<!-- The distilled spec each owner must satisfy in their area, in its own subsection. -->

## 7. Quality Gates

<!-- What each owner verifies before reporting (syntax checks, untouched test suite), and what the orchestrator runs at integration. -->

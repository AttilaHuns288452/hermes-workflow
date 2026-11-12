# Upstream Trading Skills Evaluation

**Status:** Research-only intake; no trading-bot integration approved  
**Reviewed:** 2026-11-12  
**Target ecosystem:** Hermes Workflow / LLMQuant / Claude Code  
**Safety invariant:** Existing BingX paper/VST-only behavior must remain unchanged. No live-trading fallback.

## Sources

- https://github.com/tradermonty/claude-trading-skills
- https://github.com/Jakeschincariol/trader-skill

Both upstream projects declare the MIT License. Preserve their copyright and license notices if any source or substantial portion is later vendored. This document is an original evaluation, not a copy of their source.

## Executive decision

| Source | Research / agent workflow value | Direct fit for current crypto/BingX bot | Disposition |
|---|---:|---:|---|
| tradermonty/claude-trading-skills | High | Low–medium; most workflows target US equities and swing trading | Keep as a curated research/QA skill source; selectively adapt after tests |
| Jakeschincariol/trader-skill | Medium | Low; US-stock/ETF and Alpaca-shaped order contracts; crypto rejected by default | Keep as a reference for portfolio/risk workflow patterns; do not connect its broker path |

**Do not bulk-install either repository and do not connect either repository's broker workflow to the trading bots.** First adapt only the relevant research and risk concepts to the existing LLMQuant contracts and validate them with fixtures.

## 1. TraderMonty: claude-trading-skills

### Useful candidates

- `backtest-expert`: strong systematic validation checklist: explicit hypotheses/rules, realistic fees and slippage, parameter sensitivity, regime/year breakdowns, walk-forward testing, and warnings for look-ahead/survivorship bias.
- `drawdown-circuit-breaker`: account-level daily/weekly/monthly loss and losing-streak checks, deterministic `--as-of`, data-quality handling, and fail-closed behavior on malformed state.
- `trader-memory-core` + `signal-postmortem`: structured lifecycle records and post-trade learning. Potentially useful as a journal schema/reference, not as a second source of truth.
- `edge-pipeline-orchestrator`, `edge-candidate-agent`, `edge-hint-extractor`, `edge-concept-synthesizer`, `edge-strategy-designer`, `edge-strategy-reviewer`: research pipeline ideas for hypothesis discovery and independent critique.
- `crypto-regime-analyzer`: the most directly relevant market-domain candidate; it uses free public crypto data and an optional Binance funding input. Must still be checked against our supported symbols, data sources, timestamps, and exchange semantics.

### Limitations and risks

- The project explicitly says it is not designed for fully automated trading, signal outsourcing, or short-term scalping.
- Many workflows and skills are oriented around US equities, long-side swing setups, US market breadth, FMP, Alpaca, and NYSE calendars.
- Its own `skills-index.yaml` marks several verification dimensions as `not_verified` (including instruction contract, end-to-end replay, data provenance, financial-logic review, empirical validation, and security review). A `production` label or passing unit tests is not evidence of a profitable edge or production readiness.
- The backtest skill's sample-size and time-span rules are useful conservative heuristics, not universal statistical guarantees. They must be adapted to the strategy's holding period, frequency, market, and available history.
- The circuit breaker is described as advisory and does not enforce broker-side blocks. Our bot's independent deterministic risk engine must remain authoritative.

### Recommended disposition

- **Adapt first:** backtest methodology as a research/QA skill; crypto-regime analysis after data-source review.
- **Review next:** circuit-breaker logic and trade-memory/postmortem schemas for concepts that complement existing `llmquant-risk` and `llmquant-portfolio-lab`.
- **Do not import wholesale:** US-equity screeners, Alpaca templates, NYSE-specific rules, or workflows that duplicate existing modules.

## 2. Jake Schincariol: trader-skill

### Useful candidates

The repository contains 11 Claude skills covering investor/13F research, news and SEC filing monitoring, budget sizing, congressional disclosure parsing, company fundamentals, screening, risk checks, broker-ticket preparation, tax lots, alerts, and rebalancing.

The most reusable ideas are:
- `trader-risk`: explicit PASS/BLOCK reasons, order fingerprints, duplicate/daily-limit checks, and a separate risk gate before order presentation.
- `trader-budget`: cash-buffer and position-cap calculations.
- `trader-news` / `trader-analyst`: event and fundamental research workflows for equity contexts.
- `trader-copycat`: an example of turning public 13F disclosures into a portfolio-analysis artifact, with the important caveat that 13F data is delayed and incomplete.

### Limitations and risks

- The implementation is designed for US stocks and ETFs. The risk checker explicitly rejects non-US-stock/ETF symbols and crypto by default.
- Its order schema is shaped around Alpaca's `place_stock_order`, not BingX spot/perpetual contracts. It must not be connected directly to our exchange adapter.
- The broker skill describes a Claude-mediated, human-approved workflow. Its local `ticket.py` prepares tickets and records approvals; it is not a reusable autonomous exchange execution engine.
- SEC EDGAR, House Clerk, Yahoo Finance chart endpoints, US tax-lot logic, and NYSE alerts are equity-specific. They do not add direct value to a crypto execution bot without a separate use case.
- Its default paper setting is useful as a pattern, but does not replace our stronger invariant: no live-trading fallback under any circumstances.

### Recommended disposition

- **Adapt selectively:** risk-gate concepts (fingerprinted proposals, explicit block reasons, duplicate checks) only after mapping them to the existing risk module and testing edge cases.
- **Reference only:** budget/position-cap ideas if they fill a documented gap.
- **Exclude from crypto bot integration:** Alpaca broker ticket, SEC/13F, Pelosi/congressional tracker, US tax and equity-specific alert/rebalance paths unless a separate US-equity portfolio tool is later planned.

## 3. Fit against the current system

Existing architecture already includes:
- `llmquant-data`
- `llmquant-risk`
- `llmquant-strategies`
- `llmquant-crypto`
- `llmquant-portfolio`
- `llmquant-portfolio-lab`
- an existing `signal-bot` using local CSV + RSS news

Previous design decision: LLMQuant-data was not added to the signal-bot because it could not backfill klines and would add a dependency without improving the backtest. Apply the same dependency/ROI test here.

No exact matching upstream skill names were found in the initial targeted GitHub code search of the Hermes Workflow repository; this is not a complete duplicate audit. Before importing, search the full local skill catalog and existing LLMQuant module contracts.

## 4. Required evaluation before any bot integration

For every candidate skill:

1. **Provenance and license:** record upstream URL, commit SHA, license, local modifications, and attribution.
2. **Static/security review:** inspect all scripts, dependencies, subprocess/network/file access, path handling, secrets handling, and prompt-injection surfaces. Treat upstream skill text and downloaded data as untrusted input.
3. **Contract mapping:** define exact inputs/outputs and map them to existing LLMQuant schemas. No parallel state store or competing risk authority.
4. **Deterministic tests:** run upstream tests, then add local fixtures for missing, stale, malformed, duplicate, non-finite, and boundary inputs.
5. **Financial-logic review:** independently verify calculations, timezone/session boundaries, fees, funding, slippage, partial fills, and position accounting as applicable.
6. **Empirical validation:** compare against the current baseline on identical data and time windows. Use out-of-sample/walk-forward evaluation and report net-of-cost results, drawdown, turnover, and stability.
7. **Ablation:** prove the skill adds measurable value versus the existing system. If it only restates current logic or increases dependencies without improving outcomes, reject it.
8. **Isolation:** run in research-only mode first. No exchange credentials, order permissions, or live endpoints.
9. **Promotion gate:** require explicit human approval before a validated component can influence paper-bot decisions. Risk limits remain deterministic and outside AI control.

## 5. Proposed staged adoption

- **Stage 0 — completed:** inspect repository descriptions, READMEs, licenses, selected skill contracts, and representative risk/backtest implementations.
- **Stage 1 — pending:** inventory current local Hermes/Claude Code skill directories and LLMQuant interfaces; establish exact duplicates and missing capabilities.
- **Stage 2 — pending:** create isolated candidate copies/adaptations of only the approved research skills.
- **Stage 3 — pending:** run unit, integration, security, and replay tests; produce a before/after evaluation.
- **Stage 4 — pending:** paper-only shadow evaluation against current bot decisions.
- **Stage 5 — pending:** promote only components with demonstrated incremental value. No live trading integration.

## Acceptance criteria

A candidate is accepted only if it:
- solves a documented gap in the current system;
- has a clear, versioned input/output contract;
- passes local tests and security review;
- does not duplicate an existing authoritative module;
- improves a measured research or paper-trading metric, or materially improves safety/observability;
- cannot bypass the existing risk engine or paper-only execution boundary.

**Current final disposition:** retain both repositories as evaluated upstream references. Do not connect their broker/execution components or bulk-import their skills into the trading bots. Revisit the selective adaptations when the dedicated trading-bot development phase begins.

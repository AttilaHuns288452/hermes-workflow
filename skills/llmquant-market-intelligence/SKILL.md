---
name: llmquant-market-intelligence
description: Router skill for LLMQuant market-intelligence workflows. Use when the user needs macro context, market sentiment dashboards, institutional flow / 13F sentiment analysis, or event probability signals.
input_data_source: LLMQuant Data
category: market-intelligence
---

# LLMQuant Market Intelligence

This category contains reusable market utility workflows that can support research, trading, and portfolio decisions.

## Routing Rules

1. Identify whether the user needs macro context, sentiment, or event probability evidence.
2. Select one workflow from the index.
3. Open only the selected workflow.
4. Use LLMQuant Data for all market, macro, event, options, and sentiment inputs.
5. Report dates, data windows, stale notices, and missing future data contracts.

## Workflow Index
## Workflow Index
| User intent | Workflow |
|---|---|
| Track cross-asset macro indicators and likely portfolio impact. | [`workflows/macro-view.md`](workflows/macro-view.md) |
| Build a market-wide sentiment dashboard. | [`workflows/market-sentiment.md`](workflows/market-sentiment.md) |
| Compare prediction-market and options-implied event probabilities. | [`workflows/event-probability-signals.md`](workflows/event-probability-signals.md) |
| Compare institutional 13F filings across quarters: entrances, exits, and rank changes among top managers. | [`workflows/13f-smart-money-rollup.md`](workflows/13f-smart-money-rollup.md) |

## LLMQuant Data Contract
## Support Files
- `references/13f-smart-money-rollup.md`

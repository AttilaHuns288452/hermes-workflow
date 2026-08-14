# Fincept Terminal / LLMQuant Data — setup & credit model

Verified 2026-08-09 from this machine + the @llmquant/data-mcp README.

## Local app
- Desktop app installed at `C:\Program Files\FinceptTerminal\FinceptTerminal.exe` (Qt/QML). NOT in AppData — search Program Files.
- The app's data layer is the same API as the MCP server below.

## Hermes wiring
- config.yaml `mcp.servers.llmquant-data`: command `npx`, args `-y @llmquant/data-mcp`, env `LLMQUANT_API_KEY=lqd_data_...`, connect_timeout 60.
- API base https://api.llmquantdata.com (override via `LLMQUANT_BASE_URL`). Docs: docs.llmquantdata.com. Dashboard (API keys, remote MCP URLs): llmquantdata.com/dashboard.
- Beta signup = 150 free credits/mo; this account showed 300 (app bundle may grant more).

## Credit model (beta — amounts may change; per README tool table)
| Cost | Tools |
|---|---|
| 0 | equity_historical_prices (daily OHLCV), crypto_snapshot, wiki_read, paper_read, polymarket event_read/market_read/price_history, macro_indicator_search/snapshot, sec_filing_browse, sec_13f_list_top_managers, etf_lookup, personal_holdings/profile |
| 1 | wiki_search, paper_search, crypto_historical_klines, equity_intraday_prices, macro_indicator_history, sec_filing_read, sec_13f_list_manager_holdings, sec_13f_list_ticker_holders, etf_holdings (unsupported ticker returns 0) |
| 2 | news_browse, polymarket_event_search |

Practical: screening a stock list on daily OHLCV is free; deep research (filing sections, 13F holder lists) is 1 credit each. ~300 credits ≈ 300 heavy research calls.

## Pitfalls
- Large `equity_historical_prices` responses truncate mid-array in chat (>30KB per tool result). For screening windows use `limit=30..90` + `take_from=latest`, not full 200-day pulls.
- 13F `year`+`quarter` must be passed together (or both omitted for latest).
- The 26-tool MCP set has NO valuation/fundamentals tools yet (roadmap: fundamentals, earnings transcripts). For forward P/E / valuation screens, web_search on gurufocus/finbox/stockanalysis/yahoo key-statistics works well (used for a 10-stock screen, 8/8 returned current multiples).
- MCP name in Hermes is `llmquant-data`; tools are prefixed `mcp__llmquant_data__*`.
- The `llmquant-*` router skills are externally owned (skills.external_dirs) — read-only to autonomous curation.

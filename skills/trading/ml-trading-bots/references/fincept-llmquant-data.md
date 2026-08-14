# Fincept Terminal / LLMQuant Data access

## What's wired on this machine
- **MCP server** registered in `C:\Users\YOUR_USERNAME\AppData\Local\hermes\config.yaml` (~line 699): `llmquant-data` → `npx -y @llmquant/data-mcp`, env `LLMQUANT_API_KEY=lqd_data_...`. Calls appear as `mcp__llmquant_data__*` tools.
- **Desktop app**: `C:\Program Files\FinceptTerminal\FinceptTerminal.exe` (Qt/QML). Not required for data access — the MCP is the data layer the app talks to.
- Base URL: `https://api.llmquantdata.com` · remote MCP: `https://mcp.llmquantdata.com/u/lqd_mcp_.../mcp` · repo: github.com/LLMQuant/data-mcp · docs: docs.llmquantdata.com. Beta: 150 free credits/month (this account had 300).

## Credit tiers (beta — amounts may change; 0-cost covers daily screening)
| Cost | Tools |
|---|---|
| 0 | equity_historical_prices (daily OHLCV), crypto_snapshot, macro_indicator_snapshot/search, sec_filing_browse, sec_13f_list_top_managers, etf_lookup, wiki_read, paper_read, polymarket reads/price_history |
| 1 | wiki_search, paper_search, crypto_historical_klines, equity_intraday_prices, macro_indicator_history, sec_filing_read, sec_13f manager/ticker holdings, etf_holdings (charged only when data returned) |
| 2 | news_browse, polymarket_event_search |

## Usage notes
- Equity daily OHLCV + 13F top-managers are free → use them for screening without burning credits.
- No valuation/fundamentals tools in the MCP (roadmap). Get forward P/E from web search instead (gurufocus/finbox/stockanalysis snippets).
- The `llmquant-*` skills (equities/crypto/strategies routers) are the LLMQuant companion package — externally owned, do not edit.
- For backtests, yfinance daily data matched Fincept values — swap the fetch() function if Fincept integration is wanted.

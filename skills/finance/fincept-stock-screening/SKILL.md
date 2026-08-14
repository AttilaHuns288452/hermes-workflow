---
name: fincept-stock-screening
description: Equity screening via the Fincept/LLMQuant data MCP.
---

# Fincept Stock Screening

Screen and analyze US equities using the `llmquant-data` MCP server (Fincept Terminal's data backend) + web valuation sources. Triggers: "best stock to buy", momentum/technical screens, valuation checks, equity comparisons.

## Connection facts
- MCP server: `llmquant-data` (26 tools), registered in `C:\Users\YOUR_USERNAME\AppData\Local\hermes\config.yaml` under `mcp.llmquant-data` — `npx -y @llmquant/data-mcp`, API key in its `env.LLMQUANT_API_KEY`. Enabled, verified working.
- Credit pool: ~300 credits reported in every response meta; data pulls show `creditsUsed: 0` (free within pool).
- Fincept Terminal desktop app (Qt) is installed at `C:\Program Files\FinceptTerminal\FinceptTerminal.exe` — GUI not needed for data; the MCP is the same backend the app uses. To drive the GUI itself, launch it and use computer-use.

## Tool map (all via tool_describe → tool_call)
- Prices: `equity_historical_prices` (daily OHLCV, `^GSPC` works for indices), `equity_intraday_prices` (1h bars)
- Crypto: `crypto_snapshot`, `crypto_historical_klines` (BASE-QUOTE format e.g. BTC-USD)
- ETFs: `etf_lookup`, `etf_holdings` (real SEC N-PORT holdings)
- Macro: `macro_indicator_search/snapshot/history` (US indicators)
- SEC: `sec_filing_browse/read` (10-K/10-Q/8-K sections), `sec_13f_list_*` (top managers, ticker holders)
- Other: `news_browse` (company announcements), `polymarket_*` (prediction markets), `paper_search/read`, `wiki_search/read`, `personal_holdings/profile`

## Screen workflow (verified 2026-08)
1. Pick the candidate basket (e.g. mega-cap tech: AAPL MSFT NVDA GOOGL AMZN META AVGO TSLA PLTR AMD).
2. Batch one `equity_historical_prices` call per ticker in a single turn (parallel). Use `{"limit": 90, "take_from": "latest"}` for the 90-day window.
3. Re-fetch any ticker whose response got truncated with `{"limit": 30, "take_from": "latest"}` — that returns the recent closes in one small response.
4. Compute per ticker: 1M return (close now vs ~21 trading days ago), since-ref return (vs first row of the 90d window), % off 90-day high (max close). Row order is oldest-first; last element = latest close.
5. Valuation: the data MCP has NO multiples endpoints. Get forward P/E per shortlist ticker via parallel web_search — gurufocus.com (fwd PE + GF Value), stockanalysis.com/stocks/<T>/statistics, finbox.com, Yahoo key-statistics pages all answer in snippets.
6. Deliver a ranked table: ticker, last close, 1M %, since-ref %, off-high %, one-line read, verdict. Two-axis call: technicals (momentum/trend) × value (fwd P/E vs growth). Name the best both-axes pick, the best value-with-weak-technicals (buy-the-dip candidate), and the momentum-only trap. Add a not-financial-advice line.

## Pitfalls
- **Response truncation:** 90 rows ≈ 31KB JSON → tool response truncated mid-array, silently losing the newest data. Keep limit ≤ 40 per call unless you accept a follow-up.
- **No valuation in MCP** — never claim P/E from the data server; always web_search.
- **App discovery on Windows:** when checking whether an app is installed, search `C:\Program Files` and `C:\Program Files (x86)` too — AppData/Documents-only searches produce false "not installed" claims (bit me 2026-08 with FinceptTerminal).
- Calls are per-ticker; a 10-name basket is 10 parallel calls — fine within the credit pool.

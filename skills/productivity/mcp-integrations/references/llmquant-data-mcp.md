# LLMQuant Data MCP reference
Official repo: https://github.com/LLMQuant/data-mcp
Package: `@llmquant/data-mcp@0.3.4` (MIT)

## Verified behavior
- Starts via `npx -y @llmquant/data-mcp@0.3.4`
- Requires `LLMQUANT_API_KEY` in env; rejects with `401 Unauthorized` if invalid
- Successfully hands off via stdio after initialization
- Tool inventory: wiki_search/wiki_read, paper_search/paper_read, macro_indicator_search/history/snapshot, crypto_snapshot/historical_klines, equity_historical_prices, sec_13f_list_manager_holdings, sec_13f_list_ticker_holders, sec_13f_list_top_managers, etf_lookup, etf_holdings
- Credits usage per call; free tools in docs marked with 0

## 13F tools
- `sec_13f_list_top_managers`
  - Input schema: `limit` (1-1000), optional `year` + `quarter`
  - Omitting `year`/`quarter` returns the latest covered quarter
  - `available_ranking_periods` are returned in `meta.scope`
- `sec_13f_list_manager_holdings`
- `sec_13f_list_ticker_holders`

## Probe/retest sequence
1. `npx -y @llmquant/data-mcp@0.3.4 --help` -> expects FastMCP warning not fatal
2. `LLMQUANT_API_KEY=*** npx -y @llmquant/data-mcp@0.3.4` -> stays running
3. mcp client handshake + tool call succeeds -> package and key are healthy

## Common mistakes
- `401` without message -> returned by API before MCP handshake
- Wrong env key name -> `LLMQUANT_API_KEY`
- Do not pass API key via headers or args; only env

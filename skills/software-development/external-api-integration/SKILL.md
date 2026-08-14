---
name: external-api-integration
description: Use when wiring live prices or MCP into a Next.js app.
---

# External API Integration (Next.js/Supabase)

Patterns for integrating real external services into cashflow-os-class apps, learned and verified Aug 2026.

## Rule zero: verify from YOUR deployment context

`curl` from a dev machine ≠ serverless/cloud IP. Free finance APIs routinely block datacenter IPs, gate on User-Agent, or serve JS proof-of-work challenges. Test the exact endpoint + headers the app will use BEFORE writing code. See `references/market-data-apis.md` for the verified matrix.

## Market data (live prices)

- Crypto: CoinGecko (keyless, quotes + 24h change + history).
- US stocks/ETFs quotes: Finnhub free key (real-time) → Twelve Data (cloud-friendly) → Yahoo+UA fallback chain.
- Stock history: Yahoo chart API **with browser User-Agent** (Finnhub free has no candles).
- FX: Frankfurter/ECB keyless daily rates (per-date series for history conversion).
- PSE (`.PS`): not available free anywhere (Yahoo feed dead, Twelve Data paid Ultra tier) — manual prices only.
- Full matrix + shapes + wiring rules: `references/market-data-apis.md`.

## Exposing a Next.js app as an MCP server

Real MCP Streamable HTTP at `/api/mcp` so external agents (Claude Desktop, Cursor, OpenCode) can query the user's data: JSON-RPC 2.0 handlers, cookie **or** bearer-token auth (bearer validated then injected as session cookies so existing cookie-based server actions stay RLS-scoped), middleware exemption, CORS, per-user rate limit, E2E verification via playwright JWT extraction. Recipe: `references/mcp-endpoint-pattern.md`.

## Pitfalls (all observed in production)

1. **`AbortSignal.timeout(8000)` on EVERY external fetch.** A hanging upstream freezes the page on its loading state with no error path — the app looked "stuck on Loading forever" until timeouts were added to all 6 fetches.
2. **60s `next.revalidate` cache** = "real-time enough" without rate-limit pain.
3. **Keep data-layer function contracts stable** — consumers (portfolio actions, asset sync, MCP tools) break silently when a provider function changes shape mid-refactor.
4. **After a timed-out coding agent: audit the diff before trusting it.** Observed: agent wrote `dayChangeWeighted / (totalValue - (totalValue - (totalValue - totalValue)))` (denominator = 0 → Infinity) and shipped history fetchers with no timeout. Check math by hand and grep for fetch calls missing signals.
5. **Keyed APIs need env plumbing in THREE places**: `.env.local`, Vercel env (`printf '%s' "$KEY" | npx vercel env add NAME production`), then a redeploy — the key isn't live until all three exist.

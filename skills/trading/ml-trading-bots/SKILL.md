---
name: ml-trading-bots
description: Build ML trading signal bots with honest backtests.
---

# ML Trading Signal Bots

Class: building/validating ML signal bots (daily bars). Governed by the user's quant-grade standard: state edge thesis + failure mode, no lookahead, walk-forward not single split, significance over pretty curves, cost-aware from line one, regime filter mandatory, kill switches before "done", backtest and live share ONE code path. Skeptic first: assume overfitting until cross-validated.

## Protocol (in order)

1. **Intake first** (user's rule — do not silently default): instrument/venue, timeframe & horizon, capital/risk envelope, data access, edge hypothesis in one sentence, regime scope. Propose defaults, get confirmation.
2. **Data**: yfinance daily OHLCV (flatten MultiIndex columns via `get_level_values(0)`). Fincept/LLMQuant MCP available as cross-check — see `references/fincept-llmquant-data.md`.
3. **Features**: momentum (ret_1/5/10, mom20), RSI14 (Wilder), MACD, realized vol, SMA distances 5/20/60/200, vol_z, range%, distance-from-60d-high, dow/month. 17 features, FIXED hyperparams — never tuned per asset (that is overfitting by construction).
4. **Target**: `sign(next_close/close - 1)`. **Must drop y==0 rows** — np.sign's 0 class silently makes the classifier 3-class and `predict_proba[:,1]` becomes P(flat)≈0, so the bot shorts everything. See pitfalls.
5. **Model**: HistGradientBoosting; soft-vote ensemble (HGB+LR+RF50) was better on crypto, worse on equities — make it a flag, default hgb.
6. **Validation**:
   - Walk-forward floor: expanding window, retrain every 21 bars, predict strictly out-of-sample.
   - **Cross-ticker test = the overfitting detector**: train ONLY on 10-12 OTHER tickers' history (strictly before each target date), trade the target. If Sharpe collapses vs own-data, the edge was memorization. Run this before trusting any result.
   - Evidence: general 12-name mixed-sector pool (0.75) ≈ own-ticker (0.82, contains unearned luck) > 3-name peer pool (0.34 — too little data, peer noise). More tickers = better; sector relevance does NOT matter.
7. **Costs from line one**: 10bps/side (BingX taker ~5bps + slippage ~5bps), inside the P&L loop, charged on every position change.
8. **Metrics that matter**: Sharpe, t-stat = Sharpe·√years (significance bar 2.0; label every result), maxDD, trades ≥ 100, profit factor WITH top-5 winning days removed (edge must survive), true directional accuracy = `(pos_prev·rets > 0)` on active days. Never `(strat>0)==(rets>0)` — it credits flat days.
9. **Regime filter**: 200d trend gate on all entries (fixed the short-the-bull disaster: NVDA −75% → +70%). Vol-targeted sizing HURT this edge (cut the good high-vol days) — test every sizing idea, don't assume.
10. **Risk module** (separate file, never hardcoded in signal logic): fixed notional, max concurrent positions, daily-loss breaker, consecutive-loss stop, manual kill flag (file-based). Kill switches are spec, not afterthought.
11. **Paper trade forward before any exchange wiring**: same code path, daily cron, CSV trade log. Only after forward results track the backtest does the exchange executor get built.

## Architecture (user's standard)
`signal_engine.py` (pure logic, no I/O) → `risk_manager.py` (sizing + kill switches) → `backtester.py` (imports signal_engine — never a duplicated backtest-only signal) → `paper_trader.py` / `executor.py` (exchange, gated by key + flag). Pine v5 mirror for TradingView alerts if requested.

## Project state
`C:\Users\YOUR_USERNAME\Documents\Projects\signal-bot\` — all modules built and verified. Paper: BTC/ETH/SOL-USD, 2 USDT/trade, $200 paper. `trading_bot.py` = legacy research script (superseded by the 4-module layout). Next: daily cron for paper trader, then BingX executor. Do NOT re-run the whole config search — see `references/results-log.md`.

## References
- `references/validation-pitfalls.md` — 5 bugs that cost real debugging time + exact symptoms/fixes
- `references/fincept-llmquant-data.md` — Fincept/LLMQuant MCP access + credit tiers
- `references/results-log.md` — backtest matrix by config, cross-tests, significance status

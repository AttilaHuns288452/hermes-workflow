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

## Liveness invariants (a bot that is "running" is not a bot that trades)

Check these before believing any status line. Each one has silently produced a
bot that logged signals for weeks while executing nothing.

1. **Every bot needs an exit path that does not depend on the model.** A
   statistical-only exit (`cal <= 0.45 AND not trend_up`) never fires while a
   position trends — the position pins the symbol forever and every later entry
   is swallowed by "already in position". Add a max-hold backstop (calendar days
   for daily bars, minutes for intraday) checked BEFORE the fresh decision.
   Tune the cap by A/B against hold-until-exit; judge on *positive on every
   asset*, not on the best aggregate (one asset can carry an aggregate that
   loses on another), and check sub-period stability — if every variant loses in
   the last third, the cap is noise and you pick it for operational reasons.
2. **Counters must count realized closes, not rows that look like closes.** A
   SELL row only closes something when it carries `pnl`; no-op "no open position
   to close" rows otherwise inflate `trades` forever. Grep every consumer of a
   trade count — the same bug lives in sibling bots until you sweep them.
3. **Size to the risk envelope the venue client actually enforces.** If sizing
   asks for `equity * pct` while the client caps notional, every order is
   rejected before reaching the exchange and the bot never trades. Clamp sizing
   to the cap so the configured limit IS the size, and read the cap from config
   (never hardcode it). Assert `0 < size <= cap` for every symbol.
4. **One scheduler per job.** Two schedulers on the same task triple-write the
   ledger and corrupt every downstream count. Own each job in exactly one place
   and make writes idempotent (upsert keyed on the natural key, with a lock and
   atomic replace), then prove it by running the job twice and diffing row count.
5. **Prove execution with an artifact, not a log line.** Place a real venue
   order, see the position, close it, confirm flat, reconcile the fee drift.
   "Scheduled and logging" proves a process ran, not that it can trade.

## Optimizing a bot without changing its signals

A performance fix that skips work must reproduce the exact same inputs, or it
silently trades differently. When the caller only reads the final row's
prediction, replicating a single fit is valid — but the fit must use the SAME
training cutoff the original loop used. A retrain-every-N loop predicts the tail
from the LAST retrain index, not from the final row:
`last = min_train + ((n-1-min_train)//RETRAIN_EVERY)*RETRAIN_EVERY`.
Fitting at `n-1` instead moved `expected_return` enough to flip decisions while
`cal_prob_up` matched — always diff EVERY prediction field to ~1e-12, not just
the one you think matters. Measure CPU before and after and report wall clock
too: capping BLAS/OpenMP threads can halve CPU while doubling runtime, which is
the wrong tradeoff for a daily job.

## Project state
`~/Documents/Projects/signal-bot/` — all modules built and verified. Paper:
BTC/ETH/SOL-USD, 2 USDT/trade, $200 paper. `~/Documents/Projects/scalper-bot/`
holds the exchange-bound bot (`production_bot.py` is the only file that calls
`place_order`). Do NOT re-run the whole config search — see
`references/results-log.md`.

## References
- `references/validation-pitfalls.md` — metric/target bugs that cost real debugging time, including the overlapping-window artifact and the overfit measurement battery
- `references/fincept-llmquant-data.md` — Fincept/LLMQuant MCP access + credit tiers
- `references/results-log.md` — backtest matrix by config, cross-tests, significance status

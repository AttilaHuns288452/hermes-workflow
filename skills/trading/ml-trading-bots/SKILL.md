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
6. **A judgment layer must be provably able to REJECT.** A veto / CEO / review
   layer whose provider fails closed-to-approve is worse than no layer: it
   manufactures confidence. Two silent failure modes, both live for a long time
   before anyone noticed: (a) the configured fallback model is not installed, so
   every call 404s; (b) the code then auto-approves by design "because
   commentary cannot veto in degraded mode". Check the provider's actual model
   list against the configured name, then drive the layer with an input that
   SHOULD be refused and assert the verdict flips. A check that only ever
   returns one answer is not a check — report it as broken, not as passing.

   **Prefer a decision model over a chat model for this slot.** A model that
   takes a typed question and returns a probability (Jev: `noul` / `choice` /
   `score`) gives a threshold you can set and a verdict you can later score
   against outcomes; a chat model returns prose you have to parse and cannot
   validate. Measured: the chat path approved 14 of 15 reviews across five
   models, while the decision model returned 0.75 on valid setups and 0.02-0.03
   on invalid ones. Before declaring such a model absent, check its documented
   transport — these often live on a dedicated endpoint and never appear in a
   chat-completions model list, so probing the wrong surface reports a false
   negative. Integrate it only where the input is something the code has not
   already compressed into a number; see `references/adaptive-loop.md` for the
   measured scorecard of which slots it wins and which it loses.

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

## Looking for signal in NEW data (before more model work)

When the existing feature set tests at chance, the next move is different data —
not more tuning. Run these gates in order; each has killed a candidate that
looked promising.

1. **Triage backtestability first.** Probe for a history endpoint and inspect the
   response shape before writing any experiment code. Snapshot-only sources cannot
   be evaluated retrospectively — the only honest experiment is forward collection.
2. **Measure the metric's own noise before scheduling a collector.** Take repeated
   back-to-back snapshots; if the value swings across its range in seconds, widen
   the measurement window (more book levels), not the sampling rate.
3. **Replication gate.** The feature must point the same way on independent
   symbols and time windows. 1 of N above threshold at N tests is the
   false-positive rate, not a discovery.
4. **Lift gate.** Wire it into the real multivariate walk-forward and re-measure.
   A univariate survivor that moves model AUC by ~0 has no lift. Univariate AUC
   and model AUC are different measurements — never quote the first as evidence
   about the second.
5. **Cost gate.** Convert AUC to expected bps and compare against MEASURED
   round-trip cost. AUC 0.55 on a ~3% daily move implies roughly 10-30bps; if
   measured cost is 36-39bps the edge does not pay for itself however real it is.

Prefer **reduction** over addition. A lean subset can beat the full feature set —
a 2-feature calendar model scored 0.539-0.555 across three assets while the
20-feature model scored 0.4901 on the same pipeline. Score feature groups in
isolation first, then combine only groups that cleared chance alone.

A self-improving search needs three parts, and a fixed menu is none of them:
**a ledger** (every hypothesis + result, deduped by hash so nothing is retested),
**a generator** (composes feature groups x horizons, expanding rather than a
fixed list), and **history actually being read** (the generator skips tested
hypotheses). Re-testing the same menu weekly and storing the results is a
selection loop; calling it learning is how "self-improving" gets faked. Verify
the claim by grepping for readers of the results file and for any mutation/
sampling code.

See `references/validation-pitfalls.md` §9-13 for the measured numbers.

## Making it actually learn (evidence → behaviour)

A search that records results is NOT a learning system. The only test that
matters: does the trading path behave differently because of what was learned?
Three ways this silently fails — check all three before claiming a bot learns.

1. **Nothing consumes the output.** Grep the decision path for the learned
   artifact. If `paper_trader`/`executor` never reads the ledger, champions or
   state file, the system is writing a diary. Make the trader load the learned
   parameters before every decision, and make a stale/missing file fall back to
   prior behaviour rather than crash the daily job.
2. **A gate no candidate can pass is a learning rate of zero.** AND-ing several
   promotion gates is statistically defensible and operationally fatal: if the
   best arm sits at 23 trades against a 30-trade floor, no arm is ever eligible
   and the bot can run for years unchanged. Count how many candidates have EVER
   passed; zero means the gate is the bug, not the candidates. Replace the
   binary cliff with continuous allocation (see `references/adaptive-loop.md`).
3. **Zero edge must not mean zero trades.** Size 0 → no fills → no new evidence
   → posterior never moves → permanently size 0. A learning system that can
   switch itself off cannot learn. Keep a small exploration fraction (order 5%
   of normal size) purely to generate evidence; when a real edge appears the
   computed multiplier overtakes the floor automatically.

Blend evidence by **precision, not by sample count**. Two live trades that lost
16% and 8.7% dragged a count-weighted posterior from +19.91 bps to −118 bps and
would have shut the bot off permanently; inverse-variance weighting gave the
same two trades 1.9% weight and a −3.62 bps posterior. Weight follows
`n / variance²`, so thin evidence barely moves a large prior and the estimate
migrates to reality as trades accumulate — that migration IS "gets smarter the
longer it runs", and it must be a property of the math, not a hope.

State costs the way the venue charges them: **fees and slippage per side, the
bid-ask spread crossed ONCE per round trip** (`2*fee + spread + 2*slippage`).
Writing `2*(fee+spread+slippage)` double-counts the spread and reported 76 bps
against a measured 36-39 bps — a bar so high nothing could ever clear it.
Cross-check any cost constant against one real filled round trip before sizing
logic depends on it.

Run `.venv/bin/python tools/selfcheck.py`-style assertions in the daily job: the
learned artifact is fresh, the trader reads it, the exploration floor is active,
cost is inside the measured band, and the judgment layer can still reject. Every
check should map to a defect that once ran silently.

## Project state
`~/Documents/Projects/signal-bot/` — all modules built and verified. Paper:
BTC/ETH/SOL-USD, 2 USDT/trade, $200 paper. `~/Documents/Projects/scalper-bot/`
holds the exchange-bound bot (`production_bot.py` is the only file that calls
`place_order`). Do NOT re-run the whole config search — see
`references/results-log.md`.

## References
- `references/adaptive-loop.md` — continuous allocation vs promotion cliffs, precision-weighted evidence blending, and the measured scorecard for a decision-model (Jev) judgment layer: which slots it wins, which it loses, and how to probe for it
- `references/validation-pitfalls.md` — metric/target bugs that cost real debugging time: the overlapping-window artifact, the overfit measurement battery, and §9-13 on data-source triage, collector-noise measurement, the replication and lift gates, feature dilution, and search-space hygiene
- `references/fincept-llmquant-data.md` — Fincept/LLMQuant MCP access + credit tiers
- `references/results-log.md` — backtest matrix by config, cross-tests, significance status

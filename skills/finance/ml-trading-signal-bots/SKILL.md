---
name: ml-trading-signal-bots
description: Use when building or debugging ML trading signal bots.
---

# ML Trading Signal Bots

Class: building self-learning (walk-forward) ML signal bots and evaluating them honestly.
Reference implementation (working, single file): `C:\Users\YOUR_USERNAME\Documents\Projects\signal-bot\trading_bot.py`
Stack: yfinance + pandas + scikit-learn `HistGradientBoostingClassifier` (HGB). Signals only — no execution.

## Architecture pattern (proven)

- Features: returns (1/5/10d), RSI-14, MACD+signal, realized vol-10, SMA ratios (5/20/60), volume z-score, intraday range %, distance from 60d high. ~13 features.
- Target: `np.sign(close.shift(-1)/close - 1)` — next-day direction, binary.
- Self-learning = walk-forward: train on expanding window, retrain every ~21 bars, predict strictly out-of-sample (never fit the day being predicted).
- Costs: 10 bps per side on position changes; charge drag on the day the position flips.
- Timing: signal at close of day `i` (features of day `i`) → captures `ret[i+1]`; position held during day `j` is `pos[j-1]`.
- Long-only by default. Long/short on an uptrending asset = account death (NVDA: −75% while NVDA rose +437%).
- Live mode: refit on all data, predict next bar, print prob + signal + permutation-importance top features (HGB has NO `feature_importances_`).

## Pitfalls (each one cost real debugging time)

1. **`np.sign(pct_change)` creates a 3rd class (0) on flat days.** If `y` contains any `0.0`, HGB trains 3 classes `[-1, 0, 1]` and `predict_proba[:, 1]` silently becomes P(flat) ≈ 0.000 → the bot shorts everything while showing ~98% training accuracy. Fix: `d = d[d["y"] != 0]` after dropna. ALWAYS check `model.classes_` after fit.
2. **Accuracy metric alignment.** `(strat > 0) == (rets > 0)` counts flat/no-position days as "correct" (strat = −cost, market down → both False → True). Produced fake "80–84% accuracy" while true sign-match was ~54%. Correct metric: `pos_prev[j] * rets[j] > 0` on active days only, where `pos_prev = np.concatenate([[0.0], pos[:-1]])`. Report `coverage` (active days / total) too.
3. **yfinance columns.** On pandas 3.x, single-ticker downloads return MultiIndex columns; flatten with `df.columns.get_level_values(0)` before selecting.
4. **uv venv interpreter mismatch.** `uv venv .venv` picked a different Python than the wheels uv resolved → numpy cp311 files in a cp312 env (import crash: `numpy._core._multiarray_umath` missing). Fix: pin explicitly `uv venv --python 3.11 .venv` (match system python).
5. **HGB probability saturation is normal.** Probs cluster at extremes; don't read them as calibrated odds — the signal is `prob >= thr` vs `<= 1-thr`, thr ≈ 0.55.

## Honest evaluation checklist (the deliverable is truth, not a green Sharpe)

- Run SPY as sanity check: a random edge should read ~50% accuracy. If it reads 60%+ on SPY, suspect a metric bug (pitfall 2) or leakage.
- Always compare vs buy & hold on the same window — a 55–58% daily edge with 50% coverage still loses to buy&hold in a bull market (SPY: 57.7% acc, +0.6% vs +88%).
- Expect the default result to be "no tradeable edge" — that IS a valid deliverable. State it plainly; never dress up backtest luck as a proven signal.
- Big-day miss pattern: model right on small days, flat/wrong on monster days → positive raw accuracy, negative magnitude-weighted edge. Check `corr(pos[t], ret[t+1])` for sign sanity.

## Next iterations (in order of likely impact)

1. Trend/regime filter (only trade with the 200d trend) — kills the short-the-bull failure mode.
2. Better features: overnight gap, cross-asset breadth, sector momentum.
3. Multi-asset ensemble (train on ~20 tickers, signal from the pool).
4. Freqtrade/FreqAI for exchange execution + hyperopt (user explored it 2026-06; native Windows install needs TA-Lib wheel).

Related but different: `tradingagents` (TradingAgents multi-agent framework), `llmquant-*` routers (data access, not model building).

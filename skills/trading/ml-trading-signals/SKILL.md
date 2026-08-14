---
name: ml-trading-signals
description: Build/validate ML trading signal bots, honest backtests.
---

# ML Trading Signal Bots (quant-grade development & validation)

Use when building, extending, backtesting, or validating any ML-driven trading
signal system (equities or crypto), or when asked to "improve the bot / make
signals accurate / beat buy & hold".

## Non-negotiable standards (user's meta-prompt + proven practice)

1. **Edge thesis + failure mode stated up front**, in plain language, before any code.
2. **Walk-forward, not single split**: expanding window, retrain every ~21 bars, predict strictly out-of-sample. Never fit on the row you predict.
3. **Same code path backtest ↔ live**: one shared `decide()`/signal function imported by both. A duplicated backtest-only signal is how silent drift happens.
4. **Costs from line one**: ~10bps/side (exchange taker + slippage). Never bolt on after.
5. **Significance, always reported**: t-stat = Sharpe·√years (|t|>2 = significant), min 100 trades, profit factor WITH and WITHOUT the 5 largest winning days (edge that dies without top-5 wins = variance). Label every result `[SIGNIFICANT]`/`[not significant]` — never claim an edge without it.
6. **Regime filter mandatory**: 200d trend gate on entries. State which regime the strategy assumes.
7. **Risk module separate from signal**: fixed notional or ATR sizing, max concurrent positions, daily-loss breaker, consecutive-loss stop, manual kill file. Never hardcode lot sizes in signal logic.
8. **Benchmark against buy & hold** on BOTH raw return AND risk-adjusted (Sharpe, maxDD). Be honest when the strategy only wins risk-adjusted — and state the leverage math if the Sharpe edge is real (leverage ≈ B&H vol / strat vol to equalize risk).

## Validation methodology (the part that separates quant from curve-fit)

- **Cross-sectional test (user explicitly demands this)**: train on a pool of OTHER tickers (exclude target), test on target. If the edge survives, it generalizes; if it collapses, it was per-ticker memorization. The own-ticker walk-forward Sharpe contains an unquantifiable luck premium (measured: AAPL 1.05 → 0.66 when own data removed).
- **Pool size**: 2–3 tickers is the WORST spot (peer idiosyncrasies, too little data). 7–12 liquid names across sectors is best; sector mix barely matters (12 non-tech names transferred to NVDA ≈ tech pool). More pooled rows = same universal pattern learned more cleanly.
- **Config selection**: choose on group-mean Sharpe across assets, NOT the best single ticker; reject configs that wreck one asset to buy 0.02 mean (that's a lucky-number artifact). Verify threshold robustness (±0.03 on thr).
- **Data history**: 8y hurt equities (COVID/2022 regimes pollute); 4y was better. Crypto tolerated 8y better.
- **Costs of naive variants (tested, with data)**: vol-targeted sizing HURT (cut the good high-vol days); long-bias (always-in during uptrend) FAILED on crypto (held through crashes — the model's exits are the value); shorting strong uptrends = account death; 200d trend filter was the single biggest Sharpe improvement on equities.

## Known pitfalls (each one cost real debugging time)

1. **`np.sign` target creates a 3rd class (0)** on flat days → `predict_proba[:,1]` silently becomes P(flat)≈0 → bot shorts everything. Always check `model.classes_` is binary; drop `y==0` rows.
2. **Accuracy metric bug**: `(strat>0)==(rets>0)` counts flat days (strat=−cost) as "correct" when market falls → fake 80% accuracy. Real accuracy = `pos_prev·rets > 0` on active days only (pos_prev = position decided previous close).
3. **Feature pipeline non-idempotent**: re-running `add_features` on an already-cleaned frame restarts rolling windows → silently drops ~200 warmup rows → probs misaligned with frame. Guard: skip feature computation if a signature column (e.g. `sma200`) already exists.
4. **yfinance columns**: modern yfinance returns MultiIndex — `df.columns.get_level_values(0)`, not string-splitting.
5. **Capture the DatetimeIndex BEFORE `reset_index(drop=True)`** — after reset, `.date()` on ints explodes.
6. **NaN tail in probs**: `0 × NaN = NaN` cascades into the PnL loop — `np.nan_to_num` sizing/prob arrays.
7. **Benchmark leakage in portfolio tests**: exclude the target from its own training pool when building multi-asset portfolios (SOL: 0.22 with leakage vs 0.68 without).

## Reference implementation (working instance)

`~/Documents/Projects/signal-bot/` — full stack: signal_engine.py (pure features/model/decide), risk_manager.py (kill switches), backtester.py, portfolio.py (equal-weight vs B&H, writes quant_report.md), paper_trader.py (forward paper + news overlay), news_watch.py (keyword headline skew + event-risk warnings — an overlay, never a model input). Best config found: HGB (200 iters, lr 0.05, depth 4), 17 features, thr 0.58, flat bias, 10bps. See `references/signal-bot-instance.md` for the full evidence table and commands.

News overlays: yfinance `Ticker.news` → `item["content"]["title"/"summary"]`; keyword word-lists only — label it "not NLP" in the code so nobody over-trusts it.

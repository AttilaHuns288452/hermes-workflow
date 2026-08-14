---
name: ml-trading-signal-bot
description: Use when building ML trading signal bots.
---

# ML Trading Signal Bots

Protocol for building a daily-direction ML signal bot whose results you can trust, plus the subtle bugs that will fake your metrics and the iteration levers that actually moved the needle.

## Core protocol
1. **Data**: yfinance daily OHLCV, 4y window (see "more history" note in evidence). Target: `y = sign(close.shift(-1)/close - 1)` — next-day direction.
2. **Features**: returns (1/5/10d), RSI14 (Wilder), MACD + signal, realized vol 10d, SMA-ratio features (5/20/60/200), 20d momentum, volume z-score (20d), intraday range %, distance from 60d high, day-of-week, month. ~17 features.
3. **Walk-forward — never in-sample**: min_train=252 bars, retrain every 21 bars on an expanding window, predict strictly out-of-sample. This IS the "self-learning": live mode refits on all data at every run.
4. **Costs**: 10 bps per side, charged on position changes (flips through 0 count as 2 units).
5. **Metrics**: strat return vs buy&hold, annualized return, Sharpe (daily mean/std × √252), **t-stat = Sharpe × √years** (label `[SIGNIFICANT]` only when |t| > 2), maxDD, trade count, coverage (% days in market), directional accuracy on active days, win rate.
6. **Robustness gate — mandatory before believing any result**: sweep the signal threshold (e.g. 0.52 / 0.55 / 0.58). Stable Sharpe across thresholds = real edge. Sharpe that collapses = luck/overfit. This is the anti-hype test.
7. **Cross-sectional validation — mandatory**: train on OTHER tickers only (exclude target), backtest on target. If Sharpe survives, the edge is a real market pattern; if it collapses, it was per-ticker memorization. Attila explicitly demands this ("test it against a different data so it actually thinks and not dependent on the data of the ticker because that's biased"). Ship the cross-trained model as the base signal; own-ticker walk-forward only as a secondary overlay.
8. **Honesty rules**: report exactly what the backtest says, including no-edge results. "Accurate signals" claims without the robustness gate are fabrication. Forward paper-trading (log daily signals + track a paper portfolio) is the only real validation — offer it.

## Pitfalls (all hit in real sessions — each silently faked results until caught)
1. **`np.sign` target + flat days = 3rd class.** A day with exactly 0.00 change → y=0 → classifier becomes 3-class → `predict_proba[:, 1]` is now P(flat) ≈ 0, NOT P(up) → bot goes SHORT everything with "99.99% confidence". Symptom: insane train accuracy (98%) + catastrophic losses on an up-trending asset. Fix: drop `y == 0` rows AFTER feature computation.
2. **Accuracy metric bug**: `(strat > 0) == (rets > 0)` counts flat days as "correct" (strat = −cost < 0 and market down → True). Symptom: 80% "accuracy" contradicting the win rate. Real measure: `pos_prev * rets > 0` on days with a position (`pos_prev = shift(pos)` — position held during day j was decided at close j−1).
3. **yfinance MultiIndex columns**: single-ticker download returns MultiIndex ('Price','Ticker'). Flatten with `df.columns.get_level_values(0)` when `isinstance(df.columns, pd.MultiIndex)`, else string cleanup. Naive `str(col).split(',')` on tuples produces garbage keys.
4. **0 × NaN = NaN cascade**: position arrays multiplied by prob/size arrays that are NaN in the pre-training tail. `np.nan_to_num` on any derived sizing/conf array before the PnL loop.
5. **uv venv wheel mismatch**: `uv venv` may pick cp312 while cached wheels are cp311 → `ModuleNotFoundError: numpy._core._multiarray_umath`. Fix: `uv venv --python 3.11` (match interpreter to the wheel set), then `uv pip install --python .venv/Scripts/python.exe ...`.
6. **Sklearn class-order trap**: verify `model.classes_` is [-1, 1] whenever the target can take unexpected values.

## What actually moved the needle (daily bars, 10bps, walk-forward, out-of-sample)
- ✅ **200d SMA trend filter** (only long above / short below): single biggest win. Killed the short-the-bull disaster: NVDA −75% → +70% (Sharpe 0.82). Apply to both backtest positions and live signal gating.
- ✅ **Threshold sweep** as the validation gate (0.52/0.55/0.58): NVDA/AAPL stable at 0.7–1.0 → real edge; GOOGL 0.66→0.15 → fragile, don't trust.
- ❌ **Confidence/vol-target sizing** (scale by (p−0.5) and inverse realized vol): made things WORSE (0.82→0.37) — it cut exactly the high-vol green days the model was right on. Reverted. Sizing ≠ Sharpe when the signal's positive days ARE the volatile days.
- ❌ **8y history on equities**: regime pollution (COVID crash, 2022 bear) → more churn, worse Sharpe. 4y was better. Crypto tolerated 8y better.
- ⚠️ **Ensemble (HGB + scaled logistic + RF soft vote)**: better on crypto (ETH 0.58 vs 0.39), worse on NVDA. Asset-class dependent — expose `--model hgb|ensemble`, don't hard-pick one.
- ⚠️ **Buy&hold beats the bot in bull markets** (bot sits out 40–50% of days): the edge is risk-adjusted (Sharpe), not total return. State this plainly — a good Sharpe ≠ beating buy&hold in a bull window.
- ✅ **Cross-sectional training (pool sizes)**: NVDA Sharpe by training set — own data 0.82, 3 tech peers 0.34 (WORST: too little data + peer noise), 7-name pool 0.71, 12 mixed-sector names 0.75 (BEST; sector mix irrelevant — features are universal microstructure). AAPL own 1.05 → cross 0.66 proves the ~40% "own-data premium" is memorization luck. More tickers = better, up to ~12.
- ✅ **Crypto needs a bigger coin pool**: 10-coin pool (BTC/ETH/SOL/XRP/DOGE/ADA/AVAX/LINK/LTC/DOT) lifted BTC 0.10→0.50, ETH −0.64→+0.09, SOL 0.65 with +40% excess over buy&hold. Tiny 2–3 coin pools were useless. Crypto target → auto-select coin pool.
- ✅ **t-stat reporting ("act like a quant")**: none of the 0.5–0.7 Sharpe results clear t=2 over 2–4y — say "not significant" explicitly and offer forward paper-trading as the only path to significance. Label every backtest output.
- Realistic ceiling observed: Sharpe 0.8–1.0 on names with a genuine edge (NVDA, AAPL); 0–0.4 on most others; crypto unreliable. Anything claiming 2+ from a daily single-asset backtest is fantasy.

## Reusable scaffold
- `templates/trading_bot.py` — final working bot: walk-forward + trend filter + hgb/ensemble flag + backtest/live modes + fixed metrics. Copy into a project (`uv venv --python 3.11`, `uv pip install pandas numpy scikit-learn yfinance`) and iterate.
- Cross mode (`--mode cross`, `--universe`, `--model`, t-stat output, live "why" transparency line, default pools: 12 mixed-sector stocks / 10 coins) was added in the 2026-08 build — the session project copy at `~/Documents/Projects/signal-bot/trading_bot.py` is the current reference; the template predates it.

## Data sources
- `references/fincept-llmquant-data.md` — Fincept Terminal / LLMQuant Data MCP: local app path, Hermes wiring, per-tool credit model (daily OHLCV = 0 credits, deep research = 1–2), and quirks. Premium alternative to yfinance when the bot needs SEC filings / 13F / N-PORT.

# Backtest Results — September 2026

## signal-bot (daily) — 1 Year Walk-Forward

**Date:** 2026-09-05
**Command:** `.venv/bin/python backtester.py --ticker <TICKER> --mode walk --years 1 --scenario all`

| Metric | BTC-USD | ETH-USD | SOL-USD |
|--------|---------|---------|---------|
| Trades | 0 | 0 | 0 |
| Sharpe | 0.00 | 0.00 | 0.00 |
| Return | +0.0% | +0.0% | +0.0% |
| Max DD | 0.0% | 0.0% | 0.0% |

**Root cause:** MIN_EDGE (10bps) too high. expected_return ~1bp never clears 10bps threshold after costs.
**Fix direction:** Lower MIN_EDGE to 5bps or reduce cost assumption.

## scalper-bot (1m) — 1 Year Walk-Forward (BEFORE tuning)

**Date:** 2026-09-05
**Command:** `../signal-bot/.venv/bin/python scalper_backtest.py --ticker <TICKER> --days 365 --scenario all`

| Metric | BTC-USD | ETH-USD | SOL-USD |
|--------|---------|---------|---------|
| Trades | 787 | 897 | 995 |
| Sharpe | -85.6 | -103.4 | -91.4 |
| Return (base) | -52.7% | -60.7% | -64.9% |
| Win rate | 7% | 7% | 12% |
| Profit factor | 0.05 | 0.04 | 0.09 |
| Max DD | -52.7% | -60.7% | -64.9% |

**Root cause:** MIN_EDGE (2.5bps) too low relative to 1m noise.

## scalper-bot (1m) — 1 Year Walk-Forward (AFTER tuning)

**Date:** 2026-09-05
**Changes:** MIN_EDGE 2.5→5bps, MIN_PROB_UP 52→55%, added blocked regimes, shortened horizon 15m→5m

| Metric | BTC-USD | ETH-USD | SOL-USD |
|--------|---------|---------|---------|
| Trades | 23 | 3 | 31 |
| Sharpe | -6.09 | -8.65 | -21.87 |
| Return (base) | -1.8% | -0.3% | -3.6% |
| Win rate | 17% | 0% | 6% |
| Max DD | -2.4% | -0.3% | -3.6% |

**Result:** Dramatically reduced losses (30x improvement on BTC) but still not profitable.

## Realistic Backtest (1h, with proper risk management)

**Date:** 2026-09-05
**Command:** `../signal-bot/.venv/bin/python realistic_backtest.py`
**Settings:** 2 USDT/position, 2% SL, 4% TP, 12h max hold, 7bps costs (5bps fee + 2bps slippage)

| Strategy | Return | Sharpe | Win% | Trades | MaxDD |
|----------|--------|--------|------|--------|-------|
| Multi-Factor (BTC) | +0.1% | 0.94 | 47% | 384 | -0.6% |
| Simple Momentum (BTC) | +0.0% | 0.12 | 48% | 436 | -0.7% |
| Multi-Factor (SOL) | +0.0% | 0.04 | 48% | 396 | -1.6% |
| Hour + Momentum (SOL) | -0.7% | -3.64 | 43% | 427 | -1.5% |
| Simple Momentum (ETH) | -0.9% | -4.71 | 43% | 462 | -1.2% |
| Mean Reversion (BTC) | -1.3% | -9.43 | 46% | 441 | -1.6% |
| Hour + Momentum (ETH) | -1.7% | -9.53 | 40% | 424 | -2.0% |

**Key insight:** With realistic risk management, ALL strategies are flat to slightly negative.
The micro-edges (vol regime, hour-of-day) are too small to overcome transaction costs.

## Conclusion

**There is no exploitable edge in BTC/ETH/SOL at 1h timeframes using price features alone.**
The infrastructure is solid (BingX paper trading connected, realistic backtests, proper risk management)
but the underlying strategy needs a fundamentally different approach to be profitable.

**What would actually work:**
- Daily timeframes (price features have more signal)
- Less efficient coins (more inefficiency to exploit)
- Real-time order book features (only available live, not in backtest)
- Market making / arbitrage (doesn't need directional prediction)

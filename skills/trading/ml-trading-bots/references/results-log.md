# Backtest results log (signal-bot, walk-forward, 10bps/side, out-of-sample)

Config abbreviations: HGB = HistGradientBoosting; ENS = soft-vote HGB+LR+RF50; trend = 200d SMA gate; thr = probability threshold.

## Config search (Sharpe, 4y unless noted — do not re-run this whole search)
| Iteration | Config | NVDA | SPY | BTC | ETH | MSFT | GOOGL | AAPL |
|---|---|---|---|---|---|---|---|---|
| v1 | HGB, 13 feats | −0.95 (3-class bug) | — | — | — | — | — | — |
| v2 | bugs fixed | 0.15 | 0.08 | — | — | — | — | — |
| v3 | + trend filter | **0.82** | 0.06 | 0.10 | −0.37 | −0.37 | 0.38 | 0.11 |
| v4 | + conf/vol sizing | 0.37 | — | — | — | — | — | — (reverted) |
| v5 | ENS @8y | 0.16 | −0.15 | 0.27 | **0.58** | 0.43 | 0.05 | — |
| final | HGB @4y trend (stocks) / ENS @8y (crypto) | 0.82 | 0.06 | 0.10 | 0.58(ENS) | −0.37 | 0.38 | 1.05 |

## Threshold robustness (real edge survives ±0.03; luck doesn't)
- NVDA: thr .52→0.82, .55→0.82, .58→0.73 — stable
- AAPL: .86 / 1.05 / 1.00 — stable
- GOOGL: .66 / .38 / .15 — fragile, don't trust

## Cross-ticker tests (trained ONLY on other tickers — the overfitting detector)
| Target | Pool | Sharpe | vs own-data |
|---|---|---|---|
| NVDA | 7-name tech+SPY | 0.71 | 0.82 |
| NVDA | 12-name mixed sector | 0.75–0.97 (backtester.py) | — |
| AAPL | 6-name | 0.66 | 1.05 (own-data premium = luck) |
| GOOGL | 6-name | 0.31 | 0.38 |
| ETH-USD | BTC,SOL | −0.64 | −0.38 → no edge either way |
| BTC-USD | 9-coin pool | 0.50 | 0.10 |
| SOL-USD | 9-coin pool | **0.65** (+40% excess vs buy&hold) | — |

## Universe size finding (NVDA target)
3 tech peers = 0.34 · 7-name = 0.71 · 12 mixed-sector = 0.75. More tickers = better; sector relevance does not matter. Few-ticker pools are the worst spot (too little data + peer idiosyncrasies).

## Final quant report (backtester.py, cross mode, all `[not significant]` t<2)
BTC-USD Sharpe 0.50 t=1.00 · ETH-USD 0.09 t=0.19 · SOL-USD 0.65 t=1.31 · NVDA 0.97 t=1.43.
Live (2026-08-09): NVDA BUY 61%, BTC/ETH/SOL HOLD. Paper: 2 USDT/trade, $200, 3 concurrent max.

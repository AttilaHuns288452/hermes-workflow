# Backtest results log (signal-bot, walk-forward, 10bps/side, out-of-sample)

**Read the significance caveat at the bottom before trusting any Sharpe here.**
Most of this table was produced before `references/validation-pitfalls.md` §7b
(the overlap artifact) was understood; the per-asset Sharpes are ranking
measurements, not evidence of edge, and none of them cleared t>2.

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

## Status after the full search (search closed, no edge)

Three search spaces have been swept under corrected statistics, and **none
produced an edge**:

| Space | Hypotheses | Survivors after overlap correction |
|---|---|---|
| price-derived feature groups | 123 | 0 |
| funding rate (BTC/ETH/SOL) | 165 | 0 |
| triple-barrier labels | 504 | 0 |

Under the UNCORRECTED statistic the same runs reported 7/45, 24/79, 68/84 and
10/84 survivors, and a funding spec showing +55 to +90 bps/trade net. All of it
dissolved once the effective sample size was divided by the horizon. The lesson
is not "funding/breadth/barrier are bad features" — it is that none of them has
demonstrated tradeable direction at the costs this venue charges (48bps round
trip realistic, measured 36-39).

Do not reopen a search space without first confirming the statistic you will
score it with is overlap-corrected, and do not build a third space to escape a
null result from the first two.

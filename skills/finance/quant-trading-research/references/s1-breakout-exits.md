# S1 Donchian Breakout Exits (2026-09-05 session)

Universe ADA/XRP/DOGE/ETH, Binance 1d 2024-09-05→2026-09-05 (731 bars),
10k USDT, 25% equity/trade, 5bps/side. ATR(14) Wilder; SL checked before TP
intrabar; time exit at close. Replication of user v2 (2x/4x, hold 10, L+S):
+50.6% / Sharpe 1.12 / PF 1.82 / WR 53% / n=59 vs user +38.6%/1.09/1.83/52%/50
— same family, delta = vendor/commissions. All deltas below are relative.

## Full-sample winners (entry/lookbacks/sizing identical)

| variant | ret | Sharpe | WR | PF | DD | n |
|---|---|---|---|---|---|---|
| 2.5/5 hold 10, L+S | +86.5% | 1.59 | 57% | 2.50 | -9.0% | 56 |
| 2.5/5 hold 10, long-only | +71.5% | 1.71 | 65% | 4.93 | -4.8% | 26 |
| 2/5 hold 10, long-only | +57.4% | 1.52 | 62% | 4.03 | -3.9% | 26 |
| 2.5/5 + 1% vol-risk, L+S | +25.3% | 1.83 | 57% | 2.50 | -2.5% | 56 |

Plateau, not spike: 2/5, 2.5/5, 3/6, 2.5/6 all +68–77% long-only.
Hold 15/20: lower Sharpe, DD −12–15%. x1.5 lookbacks: FULL +58%/1.73,
best OOS Sharpe 1.24 — slower-trade alternative.

## Walk-forward (IS 24-25 / OOS 25-26)

| variant | IS | OOS |
|---|---|---|
| 2.5/5 L+S | +61.7% / 2.19 (n=27) | +18.4% / 1.01 (n=27) |
| 2.5/5 long-only | +64.3% / 2.29 (n=18) | +3.9% / 0.83 (n=7, thin) |

Shipped long-only as Sharpe/DD champion with the thin-OOS caveat stated;
`long_only=False` is the max-OOS-return alternative.

## Rejected (measured, not guessed)

SMA200 gate, breakeven-at-5 shift, Chandelier trail (2.5 trail alone: −13.2%),
vol filter (no-op on longs — it only killed shorts). Shorts below SMA200
still hurt: the gate misses early-trend longs starting under a lagging SMA.

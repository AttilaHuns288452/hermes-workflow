---
name: quant-trading-research
description: "Build, test, or finetune quantitative trading strategies."
version: 1.0.0
author: Attila
license: MIT
platforms: [linux]
---

# Quant Trading Research

Build, test, and finetune quantitative trading strategies with realistic backtesting and walk-forward optimization.

## When to Use

- User wants to build or improve a trading bot
- User asks to backtest strategies or find profitable parameters
- User wants to connect to an exchange API for paper trading
- User asks about strategy optimization, grid search, or walk-forward analysis

## Core Workflow

### 1. Data Fetching

Primary: BingX historical klines API (full year of 1h/1d data available).
Fallback: Binance public API for funding rates, OI, long/short ratio.
Keyless OHLC fallback: `bingx_client._request` demands API keys even for
public klines. When keys are missing, fetch daily OHLC from Binance public
`/api/v3/klines?symbol=ADAUSDT&interval=1d&limit=1000` with stdlib urllib —
no key, 1000 bars/call covers 2y daily in one call per symbol.
Env: system python is PEP 668 (no pandas). Run scripts with
`uv run --with pandas --with numpy --with requests python <script>`.

```python
from bingx_client import fetch_historical_klines
from binance_data import fetch_historical_funding

# 1h data for 180 days
df = fetch_historical_klines("BTC-USDT", "1h", days=180)

# Daily data for 2 years
df = fetch_historical_klines("BTC-USDT", "1d", days=730)

# Funding rates (8h periods)
fund = fetch_historical_funding("BTCUSDT", "2025-09-01", "2026-09-05")
```

### 2. Strategy Testing

Test multiple strategies in parallel:
- **Momentum**: buy when N-period return is positive
- **Mean reversion**: buy when price z-score is below threshold
- **Breakout**: buy when price breaks above N-period high
- **Composite**: combine momentum + vol + hour + funding factors

### 3. Realistic Backtest

ALWAYS use realistic constraints:
- Position sizing (20-25% of equity per trade)
- Stop loss (2-3%) and take profit (4-6%)
- Max hold time (10-12 bars)
- Transaction costs (5-7bps per side + slippage)
- Max concurrent positions (3-4)

```python
from realistic_backtest import backtest_realistic

r = backtest_realistic(df, signals,
    position_size_pct=0.25,
    stop_loss_pct=0.03,
    take_profit_pct=0.06,
    max_hold_bars=10,
    cost_bps=5.0,
    slippage_bps=2.0)
```

### 4. Grid Search

Systematically test all combinations:
- Timeframes: 1h, 4h, 1d
- Coins: BTC, ETH, SOL, DOGE, XRP, ADA, LINK, LTC
- Strategies: momentum, mean_reversion, breakout, composite
- Parameters: lookback periods, thresholds, risk settings

Sort results by Sharpe ratio (not return) to find robust strategies.

### 5. Walk-Forward Optimization

Validate on out-of-sample data:
- Train on 252 bars, test on 63 bars
- Roll forward through the dataset
- Prevents overfitting to historical data

Replication-first: before optimizing, replicate the user's baseline on your
own feed and require the same Sharpe/PF/win-rate family (allow a return
delta from vendor/commission differences). Optimize only relative deltas.
Plateau check: a winning SL/TP must have winning neighbors (e.g. 2/5, 2.5/5,
3/6 all green) — a lone spike is a knife-edge, reject it.
Thin-OOS veto: OOS Sharpe on <10 trades validates nothing, however good
full-sample Sharpe looks. Prefer more OOS trades at acceptable Sharpe over
a thin-sample Sharpe champion.

### 6. Portfolio Construction

Combine uncorrelated strategies:
- Max 4 concurrent positions
- 25% equity per position
- Rebalance when signals change

## Key Findings (Crypto, 2025-2026)

| Finding | Detail |
|---|---|
| **Best strategy** | Breakout on 1d timeframe |
| **Best coins** | ADA (LB=96), XRP (LB=96), DOGE (LB=24), ETH (LB=48) |
| **Donchian exits** | SL 2.5x / TP 5x ATR(14), hold 10 bars beats 2x/4x; daily-crypto shorts drag — long-only halves DD, doubles PF (see `references/s1-breakout-exits.md`) |
| **1h strategies** | No exploitable edge — price is random walk |
| **ML on price** | 0% win rate — HGB/ensemble can't predict 1m/1h moves |
| **Funding reversion** | Correlation < 0.05 — no edge |
| **Vol regime** | High vol = +0.013%/hr drift (too small after costs) |
| **Hour-of-day** | Hours 19-21 UTC have +0.03%/hr drift (too small after costs) |

## BingX Paper Trading

Connect to BingX demo environment (VST — virtual settlement token):

```python
from bingx_paper_trader import BingXPaperTrader

trader = BingXPaperTrader()
trader.place_market_order('BTC-USDT', 'BUY', 0.001, 'MARKET', position_side='LONG')
positions = trader.get_positions()
balance = trader.get_account_balance()
```

API keys go in `.env` (gitignored):
```
BINGX_API_KEY=your_key
BINGX_SECRET_KEY=your_secret
```

## Pitfalls

1. **Overfitting**: A strategy that backtests well may fail live. Always use walk-forward validation.
2. **Ignoring costs**: 5bps fees + 2bps slippage eat micro-edges. If edge is < 0.05% per trade, it's noise.
3. **Wrong timeframe**: 1m/1h crypto is too efficient for price-based strategies. Use 1d.
4. **Too many trades**: 400+ trades in 180 days = overtrading. Fewer, higher-quality trades win.
5. **No stop loss**: A single -50% trade wipes out 10 small wins. Always use stops.
6. **Sharpe vs Return**: Sort by Sharpe, not return. High return with -10 Sharpe is a trap.

## Verification

A strategy is "good" when:
- Sharpe > 2.0 on walk-forward test
- Win rate > 45%
- Profit factor > 1.3
- Max drawdown < 15%
- At least 15 trades in test period

Session-specific details in `references/bingx-api.md` and `references/walk-forward-optimization.md`.

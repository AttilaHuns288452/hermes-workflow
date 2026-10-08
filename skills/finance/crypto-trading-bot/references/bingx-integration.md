# BingX Paper Trading Integration

## Overview
Connected scalper-bot to BingX paper trading (VST demo account) for real-time
data, order book features, and realistic execution modeling.

## API Credentials
- **Location:** `~/Documents/Projects/scalper-bot/.env` (gitignored)
- **Base URL:** `https://open-api.bingx.com` (live) / `https://open-api-vst.bingx.com` (paper)
- **Paper Account:** VST (virtual settlement token) demo account
- **Balance:** 0.00 VST initially — needs demo account funding via BingX UI

## Files Created

| File | Purpose |
|------|--------|
| `bingx_client.py` | API client — auth, orders, positions, klines, order book, funding |
| `bingx_features.py` | 20 order book features (imbalance, slope, pressure, funding, OI) |
| `bingx_paper_trader.py` | High-level paper trader class with P&L tracking |
| `binance_klines.py` | Historical kline fetcher (full year of 1m/15m/1h) |
| `binance_data/binance_data.py` | Binance public API for funding rates, long/short ratio |
| `quant_research.py` | Quant strategy testing (momentum, pairs, funding reversion) |
| `realistic_backtest.py` | Realistic backtest with SL/TP, position sizing, costs |
| `simple_strategy.py` | Rules-based strategy (vol regime + hour + momentum) |

## API Endpoints Used

| Endpoint | Use |
|----------|-----|
| `/openApi/swap/v2/quote/contracts` | Available trading pairs |
| `/openApi/swap/v2/quote/depth` | L2 order book (20 levels) |
| `/openApi/swap/v2/quote/premiumIndex` | Funding rate |
| `/openApi/swap/v2/quote/openInterest` | Open interest |
| `/openApi/swap/v2/quote/klines` | OHLCV (1m, 5m, 15m, 1h, 4h, 1d) |
| `/openApi/swap/v2/user/balance` | Account balance (signed) |
| `/openApi/swap/v2/user/positions` | Current positions (signed) |
| `/openApi/swap/v2/trade/order` | Place order (signed) |
| `/openApi/swap/v2/trade/closeAll` | Close positions (signed) |
| `/fapi/v1/fundingRate` | Binance historical funding (8h periods) |
| `/futures/data/topLongShortPositionRatio` | Binance long/short ratio |

## Lessons Learned

### 1. Efficient Market Reality
**Finding:** BTC/ETH/SOL at 1h timeframes have NO exploitable edge from price features alone.

**Evidence:**
- Funding vs 1h return correlation: -0.0085 (essentially zero)
- Vol regime effect: +0.013% per hour (too small to overcome costs)
- Hour-of-day effect: +0.03% per hour (too small to overcome costs)
- Best multi-factor strategy: +0.1% return, 0.94 Sharpe (flat)

**Conclusion:** Price-derived features (SMA, RSI, MACD, momentum) have zero
predictive power for major crypto assets at sub-daily timeframes. This is
expected — these are the most liquid, most efficiently priced markets in the world.

### 2. Data Source Tradeoffs

| Source | 1m Data | 1h Data | Order Book | Funding | Cost |
|--------|---------|---------|------------|---------|------|
| yfinance | 30 days | Years | None | None | Free |
| BingX API | Full year | Full year | 20 levels | Real-time | Free |
| Binance API | Full year | Full year | 20 levels | 8h snapshots | Free |

**Best combo:** BingX for execution + Binance for historical funding data.

### 3. Backtest Realism Matters

**Broken backtest (no risk management):**
- Multi-Factor SOL: +5843% return (nonsense — trades every bar, no constraints)

**Realistic backtest (2 USDT, 2% SL, 4% TP, 7bps costs):**
- Multi-Factor BTC: +0.1% return, 0.94 Sharpe (flat)
- Simple Momentum BTC: +0.0% return, 0.12 Sharpe (flat)
- Hour + Momentum ETH: -1.7% return (small loss)

**Key insight:** Without stop losses, position sizing, and max hold times,
backtests are meaningless. The "great" results were artifacts of unrealistic
assumptions.

### 4. What Would Actually Work

| Path | Why | Feasibility |
|------|-----|------------|
| Daily timeframes | Price features have more signal | Easy — change interval |
| Less efficient coins | More inefficiency to explore | Medium — add altcoins |
| Order book history | L2 data has real predictive power | Hard — needs paid data |
| Funding reversion | Known edge but small | Medium — needs precise timing |
| Market making | Doesn't need directional prediction | Hard — new architecture |

### 5. BingX Paper Trading Setup

1. Create demo account at BingX (VST tokens)
2. Fund the demo account (virtual balance)
3. Store credentials in `.env` (never commit)
4. Test with small orders first
5. Monitor positions via `bingx_paper_trader.py`

**Paper trading base URL:** `https://open-api-vst.bingx.com`
**Live trading base URL:** `https://open-api.bingx.com`

**Switch to live:** Set `BINGX_PAPER_TRADING=false` in `.env`

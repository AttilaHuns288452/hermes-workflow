---
name: crypto-trading-bot
description: Use when working with custom crypto paper-trading bots.
triggers:
  - trading bot
  - signal-bot
  - scalper-bot
  - backtest
  - paper trading
  - trading signal
---

# Crypto Trading Bot

Architecture and operations for the user's two custom crypto paper-trading bots.

## When to Use

- User asks about bot performance, positions, PnL, or "what's it doing"
- Running backtests or interpreting results
- Tuning thresholds (MIN_EDGE, MIN_PROB_UP, UNCERTAINTY_MAX)
- Diagnosing why a bot is flat (0 trades) or losing money
- Checking if live trading is active
- Connecting to exchanges (BingX paper trading)

## Bot Overview

### signal-bot (daily)
- **Location:** `~/Documents/Projects/signal-bot/`
- **Resolution:** Daily bars (252 bars/year)
- **Targets:** BTC-USD, ETH-USD, SOL-USD
- **Model:** HGB (HistGradientBoosting), cross-asset walk-forward
- **Decision:** `decide_statistical` — edge ≥ 10bps, cal_prob ≥ 55%, trend 200d ON
- **Risk:** 2 USDT/trade, 3 max concurrent, 5% daily breaker, 5-consec-loss stop
- **Costs:** 10bps/side (base scenario)
- **Paper envelope:** 200 USDT

### scalper-bot (1m → 1h)
- **Location:** `~/Documents/Projects/scalper-bot/`
- **Resolution:** 1-hour bars (8,760 bars/year) — migrated from 1m
- **Targets:** BTC-USDT, ETH-USDT, SOL-USDT
- **Model:** HGB, cross-asset walk-forward
- **Decision:** `decide_statistical` — edge ≥ 5bps, cal_prob ≥ 55%, 5m horizon
- **Risk:** 2 USDT/trade, 3 max concurrent, 2% SL, 4% TP, 12h max hold
- **Costs:** 7bps/side (5bps fee + 2bps slippage)
- **Paper envelope:** 100 USDT (realistic backtest)
- **Exchange:** BingX paper trading (VST demo account)

## Architecture

Both bots share the same pipeline:

```
research_predictions()  →  decide_statistical()  →  risk gates  →  open/close
     (ML model)            (edge + prob + trend)      (kill switches)
```

### Signal Flow
1. `research_predictions()` — HGB trained on OTHER tickers (cross-asset), walk-forward
2. `decide_statistical()` — expected_edge = expected_return - round-trip cost
3. Risk gates: protection_state → health_state → vol-aware sizing → portfolio_risk
4. Execution: BUY opens ≤2 USDT, SELL closes and logs PnL

### Decision Layer (decision.py)
```
BUY    → edge ≥ MIN_EDGE AND cal_prob ≥ MIN_PROB_UP AND trend_up AND regime ∉ blocked
SELL   → edge ≤ -MIN_EDGE AND cal_prob ≤ 1-MIN_PROB_UP AND trend_down
ABSTAIN→ model leans but edge < MIN_EDGE or uncertainty > UNCERTAINTY_MAX
HOLD   → everything else
```

## Running Backtests

### signal-bot (daily)
```bash
cd ~/Documents/Projects/signal-bot
.venv/bin/python backtester.py --ticker BTC-USD --mode walk --years 1 --scenario all
.venv/bin/python backtester.py --ticker ETH-USD --mode walk --years 1 --scenario all
.venv/bin/python backtester.py --ticker SOL-USD --mode walk --years 1 --scenario all
```

### scalper-bot (1m)
```bash
cd ~/Documents/Projects/scalper-bot
../signal-bot/.venv/bin/python scalper_backtest.py --ticker BTC-USD --days 365 --scenario all
```

**Note:** Scalper backtests are slow (~30 min/ticker) due to 1m data fetching (52 chunked yfinance requests per ticker for 365 days).

## Configuration (config.py)

| Parameter | signal-bot | scalper-bot | Meaning |
|-----------|-----------|-------------|---------|
| PRIMARY_HORIZON | 5 days | 15 min | Forward return target |
| MIN_EDGE | 0.001 (10bps) | 0.00025 (2.5bps) | Min post-cost edge |
| MIN_PROB_UP | 0.55 | 0.52 | Min calibrated P(up) |
| UNCERTAINTY_MAX | 0.12 | 0.12 | Ensemble disagreement cap |
| Cost (base) | 10bps/side | 5bps/side | Round-trip = 2x |

## Known Issues & Tuning Insights

### signal-bot: Too Tight (0 trades in 1y backtest)
- **Symptom:** All signals HOLD/ABSTAIN, 0 trades, 0% return
- **Root cause:** MIN_EDGE (10bps) too high for daily expected returns
- **Evidence:** expected_return ~0.0001 (1bp) vs MIN_EDGE 0.0001 — never clears after costs
- **Fix direction:** Lower MIN_EDGE to 0.0005 (5bps) or reduce cost assumption

### scalper-bot: Too Loose (-52% to -65% in 1y backtest)
- **Symptom:** ~800-1000 trades, 7% win rate, profit factor 0.05
- **Root cause:** MIN_EDGE (2.5bps) too low relative to noise at 1m resolution
- **Evidence:** Trades everything, loses consistently — model has no real edge at 1m
- **Fix direction:** Raise MIN_EDGE to 0.0005+ or add a minimum expected_return filter

### General Pattern
- Both bots use the SAME decision layer (`decide_statistical`)
- The daily bot's thresholds assume day-scale returns (~100x larger than 15m)
- The scalper's thresholds were tightened but TOO much — still trades noise
- **Key insight:** If expected_return is near zero, no threshold will help — the model itself needs work

## Paper Trading Status

- **BingX paper trading connected** (VST demo account)
- **API credentials:** `~/Documents/Projects/scalper-bot/.env` (gitignored)
- **Base URL:** `https://open-api-vst.bingx.com` (paper) / `https://open-api.bingx.com` (live)
- **Balance:** 0.00 VST initially — needs demo account funding via BingX UI
- **No cron jobs active** (checked via `ps aux` and `crontab -l`)
- **Positions rebuild from CSV on each run** (`load_state()`)
- **Kill switch:** `manual_kill.txt` in project dir

## BingX Integration

See `references/bingx-integration.md` for full details on:
- API endpoints used
- Files created (`bingx_client.py`, `bingx_features.py`, etc.)
- Lessons learned (efficient market reality, data source tradeoffs, backtest realism)
- Paper trading setup steps

## Verification

A backtest review is complete when:
- All 3 tickers tested (BTC, ETH, SOL)
- All 3 cost scenarios tested (optimistic, base, adverse)
- Sharpe, return, win rate, max DD, and trade count reported
- Root cause identified for flat or losing results
- Fix direction proposed

Session-specific backtest results in `references/backtest-results-2026-09.md`.

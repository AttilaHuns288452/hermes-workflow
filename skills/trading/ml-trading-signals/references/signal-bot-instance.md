# Signal Bot Instance — evidence & commands (Aug 2026 session)

Project: `C:\Users\YOUR_USERNAME\Documents\Projects\signal-bot\` (venv `.venv`, py 3.11).

## Stack
| File | Role |
|---|---|
| signal_engine.py | pure: add_features (17 feats), clean() (idempotent), make_model (hgb/ensemble), decide(), probs_walk_forward(), probs_cross() |
| risk_manager.py | RiskManager: 2 USDT notional, 3 max concurrent, 5% daily breaker, 5 consec-loss stop, manual_kill.txt override |
| backtester.py | fetch (yfinance), evaluate(), quant report; CLI: --mode walk/cross --thr 0.58 --bias flat/long --model hgb/ensemble |
| portfolio.py | BTC+ETH+SOL equal-weight vs B&H; writes quant_report.md |
| paper_trader.py | daily forward signals + news overlay; logs paper_trades.csv |
| news_watch.py | yfinance news keyword scan (content.title / content.summary); skew + EVENT flags |
| trading_bot.py | legacy research script (superseded) |

## Best config (grid-selected, group-mean criterion)
HGB (max_iter 200, lr 0.05, max_depth 4), 17 features, thr **0.58**, bias **flat**, trend 200d ON, 10bps/side, 4y data, retrain every 21 bars. Grid (mean Sharpe over SOL/ETH/NVDA): thr0.52hgb 0.45 · thr0.52ens 0.37 · thr0.55hgb 0.55 · thr0.55ens 0.54 · **thr0.58hgb 0.58** (all-positive) · thr0.58ens 0.60 (ETH −0.17 → rejected).

## Final cross-validated evidence (thr 0.58, trained on OTHER tickers only)
- SOL-USD: Sharpe 0.68, +121.8% vs B&H +80.5% (beats own B&H outright), t 1.35
- BTC-USD: Sharpe 0.50 (thr 0.55), +10.3%/yr
- ETH-USD: Sharpe 0.18, ~flat
- NVDA: Sharpe 0.87–0.97 (12-name mixed pool), +34%/yr, t ~1.4
- Portfolio (BTC+ETH+SOL, flat bias): +54.0% vs B&H +73.7%; Sharpe 0.55 vs ~0.30; maxDD −47.8% vs −64.4%. Risk-adjusted win only; raw-return gap closable at ~1.6× leverage (unproven).
- ALL t-stats < 2 → every result printed `[not significant]`. Forward paper test is the gate.

## Live commands
```
.venv/Scripts/python.exe backtester.py --ticker SOL-USD          # cross backtest
.venv/Scripts/python.exe backtester.py --ticker NVDA --mode walk # own-history
.venv/Scripts/python.exe portfolio.py                            # vs B&H + report
.venv/Scripts/python.exe paper_trader.py                         # daily paper + news
```
Paper envelope: 2 USDT/trade, 3 concurrent, account 200 USDT, targets BTC/ETH/SOL.
Kill switch: create `manual_kill.txt` in project dir; delete to re-arm.

## Fincept / LLMQuant data notes
- MCP `@llmquant/data-mcp` registered in hermes config.yaml (LLMQUANT_API_KEY `lqd_data_...`).
- Credit table (beta, 150 free/mo; this account 300): 0-credit = daily OHLCV, crypto snapshot, macro snapshot, SEC browse, 13F top managers, ETF lookup; 1-credit = wiki/paper search, klines, intraday, macro history, SEC read, 13F holdings, ETF N-PORT; 2-credit = news browse, polymarket search. All session price calls cost 0.
- Data feed in backtester is yfinance; Fincept REST (https://api.llmquantdata.com) is a drop-in replacement for fetch().

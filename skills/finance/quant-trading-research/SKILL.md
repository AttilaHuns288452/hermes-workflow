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
- Position sizing — **clamp to the venue's limit, don't just multiply**. `equity * pct` on a funded account can ask for orders the client will reject (a 20% slice of a 100k account against a `MAX_POSITION_USDT=10` guard = every order refused, zero trades, no error surfaced in the status line). Prefer a **percentage-of-equity limit enforced inside the order client** (`max_position_usdt` as a high backstop, `max_position_pct` as the working limit) so "1% risk per trade" scales with the account and no caller can bypass it. Two traps: an order sized to *exactly* the cap is refused because sizing uses the close while the gate re-derives the order-book mid — size to **99.5% of the limit** and keep the limit exact; and reading equity once per order bursts the signed rate limit into a `429`, so cache it for ~60s and refuse (never fall back to the larger absolute cap) if the read fails. Full design in `references/bingx-api.md`.
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
| **Funding reversion** | The funding **level** has no edge (corr < 0.05), but its **3-day change** does: `fr_chg3` scored AUC 0.40-0.47 — inverted, i.e. rising funding = crowded longs = reversion down — on BTC, ETH, SOL and DOGE, mean strength 0.553. Weak, but it replicated on all four, which is the reason to keep it. Endpoint returns max 1000 points (~333 days at 8h), thin for training. |
| **Vol regime** | High vol = +0.013%/hr drift (too small after costs) |
| **Hour-of-day** | Hours 19-21 UTC have +0.03%/hr drift (too small after costs) |

## BingX Paper Trading

**Live trading is hard-blocked at the client, not by convention.** Every order path routes through one request helper, so the guard belongs there and nowhere else:

```python
def _request(method, path, params=None, signed=False, paper=True):
    if not paper:                      # not an assertion, not a warning: refuse
        raise RuntimeError("LIVE TRADING BLOCKED: paper-only client")
    base = PAPER_BASE_URL              # never a conditional on `paper`
```

Do not add `paper` as a merely-defaulted parameter that a caller, a config typo, or a refactor can flip — default-plus-no-check means the live endpoint is one wrong keyword away. Verify both directions after the change: `paper=False` must raise, `paper=True` must still return `code: 0`.

Connect to BingX demo environment (VST — virtual settlement token):

```python
from bingx_paper_trader import BingXPaperTrader

trader = BingXPaperTrader()
trader.place_market_order('BTC-USDT', 'BUY', 0.001, 'MARKET', position_side='LONG')
```

API keys go in `.env` (gitignored):
```
BINGX_API_KEY=your_key
BINGX_SECRET_KEY=your_secret
```

**Read the fee schedule from the exchange, don't assume it.** BingX publishes per-contract rates on the contracts endpoint, and they decide whether any strategy can clear costs:

```python
c = [x for x in bingx_client.get_contracts() if x["symbol"] == "BTC-USDT"][0]
print(float(c["makerFeeRate"]) * 1e4, "bps maker",  float(c["takerFeeRate"]) * 1e4, "bps taker")
# observed: 2.00 bps maker / 5.00 bps taker -> 10 bps round trip before slippage
```

A hardcoded "5bps per side" in a cost model can be right or wrong by a factor of two per venue; pull it once, record the source, and recompute the edge-to-cost ratio with the real number.

**The fee is not the cost — read the book.** Fees are tight and uniform; spreads are not. Measured on one venue on the same day: BTC 0.7 bps, but ETH 27.9, SOL 26.1, DOGE 29.0. With 5 bps taker fees that is a ~10 bps round trip on BTC and **36-39 bps on the alts** — a cost model carrying `spread_bps = 0` understates reality by ~2x on most tradable symbols, and a live 1%-sized round trip confirmed it at 36.1 bps against a modelled 20. Pull the top of book per symbol (`/quote/depth`) before quoting any edge-to-cost ratio, and remember a BTC-only result is not evidence for an alt-pair strategy. When you adopt measured costs, add them as a NEW scenario beside the existing baseline — rewriting the baseline silently invalidates every prior experiment and promoted parameter.

**Verify which environment a key belongs to.** A public endpoint returning `code: 0` says nothing about a signed call, and a live-account key will not authenticate against VST (`Incorrect apiKey`) — the demo scope is a separate key. Write one acceptance script that checks credentials, a public endpoint, a signed balance, the live-block guard, and a non-VST-host refusal together, and keep it next to the client so credential state is answerable in one command.

A project that talks to an exchange needs its **own venv**. A bot borrowing another project's interpreter reads as "no dependencies" until the first `ModuleNotFoundError` in an unrelated probe; create it explicitly (`uv venv --python 3.11 .venv` then install), don't discover the borrowing later.

## Two Kinds of "Paper" — Establish Which One You Have

These are different systems and their numbers must never be mixed in a report:

| | Simulated paper | Exchange-demo paper |
|---|---|---|
| Orders reach an exchange? | No | Yes, against VST/demo |
| Fill source | Local model from OHLCV + cost assumption | Real demo-account fills |
| Truth value | Backtest continuation | Execution reality (latency, partial fills, rejects) |
| Fails how | Silently (no counterparty) | Auth, rate limits, rejects |

A project can contain both. Before improving either, answer: does this code path place an order anywhere? Read the module docstring — the honest ones say "no exchange".

### Answering "how is the bot doing?"

The user asks this repeatedly, and the tempting answer is to read the equity number.
Don't. Report, in this order:

1. **Realized PnL with its trade count** — sum `pnl` over actual closes. `−0.14 on 2 trades` and `+0.00 on 0 trades` are different facts; a flat equity curve usually means *nothing happened*, not stability.
2. **Open positions and whether they can close** (see the exit audit below).
3. **Did the scheduled job actually run, and did it place an order?** Tail the cron log for the last cycle and grep the client's error path. A job that logs `Signal: SELL ...` and then `Error processing ... exceeds ...` every day is a bot that has *never traded*, and only the log shows it.
4. **Per-bot verdict from the edge-to-cost ratio** — `CAN trade` / `CANNOT trade`, with the ratio. This is the line that explains a silent bot.
5. **Which numbers are simulated and which are exchange fills.** Never let one PnL statement blend the two.

Keep the raw cost/edge arithmetic and the fill evidence in the same message as the summary. A status answer without the trade count and the executed-order evidence is an opinion.

## Diagnosing "it never trades"

Zero trades in a ledger is a **bug report, not a market verdict**. Walk the gate chain in order — the first gate that fires for ~100% of rows is the answer, and it is almost never the one you assumed:

1. **Is there a real close at all?** Count rows where `pnl` is non-empty. A ledger of 12k `HOLD`/`ABSTAIN` rows with an empty `pnl` column has produced nothing. See "A closed trade is identified by `pnl`, not by the action label" below.
2. **Is the edge bigger than the round-trip cost?** Compute `mean |expected_return|` and compare to `2 x cost_per_side`. This single ratio decides whether the strategy is viable at all — before any gate tuning.
3. **Which gate rejects the survivors?** Bucket the notes: uncertainty, edge-too-small, regime-blocked, already-in-position, portfolio-risk, protection-blocked. The dominant bucket is the diagnosis.
4. **Can an open position ever CLOSE?** Check that an exit path exists that does not depend on a signal condition a persistent regime blocks.

```python
# the viability screen — run this before touching thresholds
edge_bps = mean(abs(x) for x in expected_returns) * 1e4
cost_bps = 2 * cost_per_side_bps          # round trip
print(f"edge {edge_bps:.2f}bps vs cost {cost_bps:.1f}bps -> ratio {edge_bps/cost_bps:.3f}x")
```

**A ratio well under 1.0 means the bot cannot trade by construction.** No threshold change fixes a negative-expectancy signal; the horizon or the instrument is wrong. Report it as `CANNOT trade`, with the ratio, instead of "the market is quiet".

## Exits are a separate system from entries

A strategy with entry logic and no reachable exit is a **one-way ratchet**: the symbol stays pinned, and every later BUY becomes `already in position`. Audit the exit path explicitly:

- Enumerate every call site of `close_position` / the order-close helper. If there is exactly one, and it sits behind a signal condition, there is no backstop.
- Ask what that condition requires in a *persistent* regime. An exit requiring `not trend_up` cannot fire during a months-long uptrend, however confident the model becomes.
- Every position needs at least one exit that is **independent of the model**: max-hold in bars/days, a stop, a take-profit, or a hard time stop. This is a control, not an optimization — add it even before you can prove it improves returns.
- Sibling bots are the reference implementation. When one variant has `_force_close` / `MAX_HOLD_*` and another has none, the difference is an omission, not a design choice.

**A max-hold cap is a parameter, so A/B it — do not ship your first guess.** Port it, then sweep the value and compare per-asset totals:

| cap | asset A | asset B | asset C | verdict |
|---|---|---|---|---|
| none (hold until SELL) | +0.33 | +0.01 | -0.13 | baseline |
| 10 | +0.52 | +1.14 | **-0.05** | wins 2/3 — not good enough |
| 20 | +0.76 | +0.14 | **+0.43** | wins 3/3 — ship this |

Winning on the majority is not winning: a cap that flips one asset negative will do exactly that on live capital. Require positive on **every** asset in the sweep, record the table in the config comment, and pin the chosen value with a test so a later edit has to face the evidence.

## Does it actually learn, or only select?

A weekly champion/challenger job is easy to mistake for a learning system. Three
checks decide it, and all three are greps or one measurement:

1. **Does it generate hypotheses?** Is the challenger grid a fixed literal list?
   A bounded menu re-tested on a schedule is **selection**, not learning — it can
   only find a better configuration of what someone already listed.
2. **Does it consume its own history?** `grep -rn "experiments.csv"` — if every
   hit is an append and none is a read, the accumulated record changes nothing.
3. **Is there anything to learn from?** Measure directional skill before
   answering (see below).

Answering "will it get smart enough to trade on its own" honestly requires
measurement, not architecture. The sharpest single diagnostic is **accuracy where
the model is confident** — a bot with AUC 0.4901 overall whose `cal >= gate`
calls were right only **45.9%** of the time is inverted exactly where it trades,
and that one number explains zero promotions, starved trade counts, and two
round-trips in two months.

When the audit lands on "no skill", the constraint is **data, not code**. OHLCV
derived features carry no 1-5 day directional signal; the reachable improvements
are new information (funding, open interest, order-book imbalance, cross-asset
lead-lag, on-chain), a different objective (volatility/regime are predictable,
direction is not), or a horizon where signal can clear cost. Full procedure,
scoring code, replication rule and the lift test: `references/self-learning-audit.md`.

## Pitfalls

1. **Overfitting**: A strategy that backtests well may fail live. Always use walk-forward validation.
2. **Ignoring costs**: 5bps fees + 2bps slippage eat micro-edges. If edge is < 0.05% per trade, it's noise.
3. **Wrong timeframe — and here is the mechanism**: execution cost is fixed per round trip while the predictable move scales roughly with `sqrt(time)`. A 5-minute horizon predicts sub-basis-point moves against a 16-20bps round trip; a multi-day horizon predicts tens to hundreds of bps against the same cost. That is why 1m/1h starves and 1d works, and it is a property of the cost model, not of the model's skill. Before tuning thresholds, compute the edge-to-cost ratio.
4. **A closed trade is identified by `pnl`, not by the action label.** `len(df[df.action == "SELL"])` counts no-op SELLs ("no open position to close") as completed round-trips and inflates every downstream stat — the status line said `trades 9 (closed)` with zero real closes. Only a successful close writes `pnl`; make that the predicate, tolerate a missing `pnl` column without raising, and grep the pattern across every sibling trader before declaring it fixed.
5. **A reported PnL can be a hardcoded constant.** A status line printing `equity 200.00 | daily PnL +0.00` every run may be reading an `account` field set once in `__init__` and never mutated, plus a `daily_pnl` zeroed each day. Compute equity from ledger realized + live unrealized, label a bare baseline as "fixed baseline, NOT PnL", and never present a constant as a measurement.
6. **Too many trades**: 400+ trades in 180 days = overtrading. Fewer, higher-quality trades win.
7. **No stop loss**: A single -50% trade wipes out 10 small wins. Always use stops.
8. **Sharpe vs Return**: Sort by Sharpe, not return. High return with -10 Sharpe is a trap.
9. **An overlapping target manufactures predictability.** An h-bar return label at bar *t* shares h−1 of h days with the label at *t−1*, so its autocorrelation is `sqrt((h−1)/h)` under a pure random walk — 0.89 for a 5-day target — with zero forward information. Any model that can read recent price action scores brilliantly against it. Never quote persistence or naive autocorrelation on an overlapping label as evidence of edge; judge on non-overlapping samples (every h-th bar) or a purged+embargoed walk-forward.
10. **In-sample fit is not evidence; the CV gap is the measurement.** A return regressor showing in-sample R² 0.65 alongside 5-fold CV corr −0.15 has memorised the window and generalises to nothing — worse than predicting the mean. Run four cheap tests before building anything on a model: in-sample corr/R², K-fold CV corr, a `DummyRegressor` mean baseline, and feature ablation (drop non-stationary price *levels* like raw SMA values, then single-feature). If no subset beats the mean baseline, the signal is absent from that feature set at that horizon and no tuning will find it — change the data (funding rates, order-book imbalance, cross-asset lead-lag), not the hyperparameters.
11. **A faster path must be bit-identical, not close — and one matching field is not proof.** A walk-forward refits every N bars, so the final rows are predicted by a model trained at an *earlier* bar, not at the last one. Short-circuiting to a single fit at `n-1` is 60x faster and quietly changes the output: `cal_prob_up` happened to match to 12 dp while `expected_return` moved −0.018 → −0.030, i.e. the field that decides the trade changed and the field that looked like the answer did not. Replicate the loop's exact refit index (`min_train + ((n-1-min_train)//RETRAIN_EVERY)*RETRAIN_EVERY`), then assert **every field the consumer reads** is equal to full precision, and pin it with a test on a small window so it costs seconds. Never ship a speedup on the argument that trade counts or the headline metric look unchanged.
12. **Before concluding "nothing qualifies", check the binding parameter is IN the grid.** A challenger grid over horizon × feature-set × regime-gate never varied the probability threshold that controls *how often* the model trades, so no arm could reach the minimum-trade floor while the high-sharpe arms stayed under it — the two promotion gates were mutually unsatisfiable and 0 of 152 recorded experiments had ever been eligible. The gates were correct; the search space was incomplete. Enumerate the gates, map each to the parameter that moves it, and confirm that parameter is a grid dimension — otherwise you are searching the wrong space and will read the empty result as "no edge exists". Fix it by adding the dimension as a **pre-registered** arm (the incumbent value as the control), never by hand-lowering the gate.
13. **AUC alone hides the tail — check accuracy where the model is confident.**
    Report `AUC`, the mean baseline, and the hit rate on rows that clear the live
    entry gate. A model can sit at AUC 0.4901 overall and still be *inverted* at
    its own threshold (45.9% correct at `cal >= 0.55`), which is fatal while an
    aggregate number looks merely weak. The confident-call hit rate is the metric
    that explains zero trades; quote it.
14. **A validated weak feature usually does not lift the model — measure the lift,
    and replicate before you trust the validation.** With ~37 candidates tested,
    one or two clearing an AUC bar is what chance produces; replicate across
    independent assets *and* windows (6/6 positive is evidence, 1/1 is not). Then
    measure the model before/after: a univariate AUC of 0.55 typically vanishes as
    one of 21 correlated inputs (observed 0.4901 -> 0.4917). Adding it and calling
    it a win without the after-number is the same error as quoting an in-sample
    Sharpe.
15. **More features can be worse than fewer — run the reduction sweep, not only
    the addition sweep.** A 2-feature calendar model (day-of-week + day-of-month,
    h=1) scored AUC 0.5549 / 0.5392 / 0.5418 on BTC / ETH / SOL while the live
    20-feature model scored 0.4901 — and both of those calendar columns were
    *already in* the 20. Broad feature sets dilute a narrow real signal into noise.
    Before adding candidate #21, score each group alone and in small combinations;
    a lean model that beats the kitchen-sink model is evidence the extra columns
    are costing you, not helping.
16. **A memo you added for speed will break a test that asserts the call happens —
    and a widened signature breaks hand-rolled mock lambdas.** Caching a data
    fetch per `(ticker, window, date)` is a large real win, but a retry test that
    counts downloads then sees a cache hit, and a monkeypatched
    `lambda sym, years, pool: ...` throws `unexpected keyword argument` the moment
    the real function gains a parameter. Two cheap habits: give the cache a clear
    entry point and reset it in the test's `setUp`, and make test doubles accept
    `**kwargs` so a new keyword cannot silently invalidate the suite. Both failures
    present as unrelated tests breaking after an unrelated optimisation.

## Verification

A strategy is "good" when:
- Sharpe > 2.0 on walk-forward test
- Win rate > 45%
- Profit factor > 1.3
- Max drawdown < 15%
- At least 15 trades in test period

### Reading an existing system's claims

Before accepting any performance figure — the user's, a brief's, or a previous report's — regenerate it or state it is unverified. Two traps that produce confident-looking numbers with no evidence behind them:

- **A Sharpe without a t-stat is a rumour.** The repo may already say `|t| < 2 everywhere` next to a Sharpe that gets quoted later without that caveat. Quote the significance, not just the point estimate.
- **A holdout with a handful of trades is not a holdout result.** `n_trades: 4` behind a Sharpe of 1.5 is noise. Check trade count before treating any out-of-sample number as evidence.
- **An empty PnL column means there is no performance history at all.** Scan the ledger for actual fills and closed round-trips; a file full of decisions (`HOLD`/`ABSTAIN`) is a decision log, not a track record. Say "not trading yet" when that is the truth rather than reporting a flat equity curve as stability.
- **A docstring's method claim is not an implementation.** "Walk-forward", "out-of-sample", "purged", "embargoed" are specific mechanisms, not adjectives — open the function and find the index arithmetic before repeating any of them. Full reproduction recipe in `references/walk-forward-optimization.md`.

Session-specific details in `references/bingx-api.md`, `references/walk-forward-optimization.md`, `references/zero-trade-diagnosis.md` (full worked gate-walk with commands), and `references/self-learning-audit.md` (skill measurement, feature discovery, replication rule).

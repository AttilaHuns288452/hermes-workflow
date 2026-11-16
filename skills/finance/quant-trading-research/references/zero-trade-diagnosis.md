# Zero-Trade Diagnosis — worked gate walk

A ledger full of decisions and no fills. Work outside-in; the first gate that rejects ~100% of rows is the cause.

## Step 0 — inventory the ledger

```python
import csv, collections, statistics
rows = list(csv.DictReader(open(LEDGER)))
print(len(rows), collections.Counter(r["action"] for r in rows))
print("real closes:", sum(1 for r in rows if (r.get("pnl") or "").strip()))
```

Empty `pnl` across the whole file = **no round-trip has ever completed**. Everything downstream (Sharpe, win rate, equity) is fabricated by construction. Say "not trading yet", not "flat".

## Step 1 — viability screen (bpp vs cost)

The decisive number is the edge-to-cost ratio, not the win rate:

```python
er = [float(r["expected_return"]) for r in rows if (r.get("expected_return") or "").strip()]
edge_bps = statistics.mean(abs(x) for x in er) * 1e4
cost_bps = 2 * COST_PER_SIDE_BPS        # round trip
ratio = edge_bps / cost_bps
print(f"edge {edge_bps:.2f}bps vs cost {cost_bps:.1f}bps -> {ratio:.3f}x")
```

Observed reference points from one real system (same model and cost model across both):

| Bot | Horizon | mean abs expected return | Round-trip cost | Ratio | Verdict |
|---|---|---|---|---|---|
| scalper | 5 minutes | 0.86 bps | 20 bps | **0.043x** | cannot trade |
| daily | 5 days | 188.7 bps | 20 bps | **9.44x** | viable |

Same code, same model, ~200x difference in viability, entirely from horizon. Cost is fixed per round trip; the predictable move grows with horizon. Below ~1.0x no threshold change helps — change the horizon or stop the bot.

Also worth printing: `sum(1 for x in er if x > cost)` — the count of predictions that *could* ever trigger. Four out of 11,781 is a structural no, not a strict gate.

## Step 2 — which gate eats the survivors

Bucket the `note` column by keyword and count:

```python
reasons = collections.Counter()
for r in rows:
    note = r.get("note") or ""
    for tag in ("no open position", "BLOCKED_REGIMES", "UNCERTAINTY_MAX", "MIN_EDGE",
                "already in position", "portfolio risk", "max concurrent",
                "protection state blocked", "expected edge"):
        if tag in note:
            reasons[tag] += 1
            break
```

The dominant bucket is the diagnosis. `already in position` dominating is not a gate problem — it is an *exit* problem (step 3).

## Step 3 — is there any exit at all

```bash
grep -rn "close_position" *.py | grep -v "def close_position"
```

One call site, sitting behind a signal branch, is a one-way ratchet. Then test the branch's condition against the regime history:

```python
# an exit requiring `not trend_up` cannot fire in a sustained uptrend
buys = {r["symbol"]: r["date"] for r in rows if r["action"] == "BUY"}
blocked = collections.Counter(r["symbol"] for r in rows
                              if "already in position" in (r.get("note") or ""))
print(buys, blocked)
```

Positions opened weeks ago and still open, with a growing `already in position` count, is the signature. The fix is an exit independent of the model (max-hold / stop / time stop), not a looser SELL threshold.

## Step 4 — sizing can hide the signals that did pass

A bot risking ~1% per position produces few trades even with many qualifying signals — 25 signals passing edge+prob, only 2 filled. That is a throttle, not a bug: report it as intentional, and say plainly that raising it raises variance proportionally. Do not silently raise sizing to make the trade count look healthier.

## Reporting

Lead with the gate that fired, the ratio that proves it, and whether the bot is *unable* (structural) or *unwilling* (conservative). "CANNOT trade at this horizon, ratio 0.04x" is the useful sentence; "the market has been quiet" is not.

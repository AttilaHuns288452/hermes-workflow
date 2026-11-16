# Funding rates as a non-price feature space

Funding is the cheapest genuinely new information a crypto perp bot can add: it
encodes how much leverage the market is paying to hold a direction, which no
transformation of the OHLCV series can express. This is the worked recipe,
including the result that looks like a discovery and is not.

---

## Endpoints — the venue that trades is often not the venue that has history

| Source | Status |
|---|---|
| BingX `/openApi/swap/v2/quote/fundingRate` | Current rate only |
| BingX `/openApi/swap/v2/quote/fundingRateHistory` | **Does not exist** — `100404 this api is not exist` |
| Binance `/fapi/v1/fundingRate` | Full history since 2019-09, public and keyless |

So a BingX-traded bot researches funding on Binance. Say that explicitly in the
report: research data source ≠ execution venue. Coverage observed:

| Symbol | Rows | From |
|---|---|---|
| BTCUSDT | 7,867 | 2019-09-10 |
| ETHUSDT | 7,633 | 2019-11-27 |
| SOLUSDT | 6,834 | 2020-09-13 |
| DOGEUSDT | 6,955 | 2020-07-10 |

Paging: `startTime` + `limit=1000`, then advance the cursor to `last.fundingTime
+ 1` and stop when a page comes back short. Page to the present; the loop guard
is for corruption, not for a known endpoint length.

## The lag rule — funding settles at 00/08/16 UTC

A settlement that lands *during* day t is not known at day t's open, so a feature
built from same-day settlements leaks. Aggregate to a daily total and shift by
one day:

```python
f["date"] = f["ts"].dt.tz_convert("UTC").dt.normalize().dt.tz_localize(None)
daily = (f.groupby(["date", "symbol"])["funding"].mean().unstack("symbol")
           .sort_index()) * 3.0          # 3 settlements per day
d["fund_btc_8h"] = daily["BTCUSDT"].shift(1) / 3.0
```

Pin it with three tests, because this is the one bug that silently inflates every
AUC: (1) day t carries day t−1's value, (2) truncating the funding frame at bar
N leaves every earlier feature identical, (3) an empty funding table yields NaN
columns rather than scoring on air.

## Feature groups that stayed small

| Group | Columns |
|---|---|
| level | 8h rate, 30d z-score |
| flow | 7d cumulative, 30d cumulative, 3d change |
| regime | z-score, fraction of last 30d positive, 7d cumulative |
| cross | alt mean minus BTC (leverage premium), its z-score |
| cross dispersion | cross-sectional std of per-symbol funding, its z-score |

Compose 1–3 groups × horizons 1/5/10. Prefix every column (`fund_`) so it cannot
collide with the price groups in the main lab, and keep the ledger hash identical
to the price space for the same (features, horizon) so both spaces share one
record.

## What the numbers actually said

Ranking (held-out tail, purged with embargo covering the horizon):

| | BTC | ETH | SOL |
|---|---|---|---|
| best AUC | 0.6021 | 0.5671 | 0.5774 |
| BH-FDR survivors | 7 / 45 | **0 / 45** | **0 / 45** |

BTC alone produced survivors; ETH and SOL produced none. **That is the expected
shape of a chance result**, and it is the reason the replication rule exists. Do
not report the BTC number as a discovery.

Net-of-cost walk-forward (4 folds, `costs.round_trip_bps("realistic")` = 48 bps):

| Asset | Spec | h | Trades | Gross bps | Gross t | Net bps |
|---|---|---|---|---|---|---|
| ETH | fund_regime | 10 | 500 | 138.0 | 2.78 | +90.0 |
| ETH | fund_level+regime | 10 | 494 | 103.4 | 2.21 | +55.4 |
| BTC | fund_level+regime | 10 | 507 | 57.4 | 2.01 | +9.4 |
| BTC | fund_regime | 10 | 497 | 44.8 | 1.57 | −3.2 |
| SOL | fund_level+regime | 10 | 469 | 32.4 | 0.61 | −15.6 |
| all | fund_level+cross | 1 | ~430 | ~0 | ~0 | −40 to −49 |

## Reading the result

- **h=10 is where funding carries information; h=1 is dead.** That fits the
  economics — funding is a slow positioning signal, not a next-bar predictor — and
  it is a reason to trust the h=10 rows over any h=1 row that happens to look good.
  A single-bar cross-sectional funding spec scored ~0 gross on every asset, so cost
  alone decided it: −40 to −49 bps.
- **One asset is not two.** Net-positive on 3 of 9 asset-spec pairs is not an edge.
  Require the SAME hypothesis to be net-positive with gross t > 2 on at least two
  assets before calling it a lead, and report the negative asset.
- **Verdict when only one spec replicates, with a third asset negative: forward
  paper test, nothing more.** No gate changes, no promotion, do not touch the
  learned state.

## Funding carry is a separate term

A long pays positive funding and a short receives it. Net figures that subtract
only fees/spread/slippage omit that term, so a long-biased implementation can come
out better or worse than the table depending on the sign of the rate while held.
Say so instead of letting the number imply more precision than it has.

## Unresolved attribution

`fund_level+regime` mixes a slow funding trend with a volatility regime, and
`fund_regime` alone is weaker on BTC. Which component carries the signal is not
yet separated — before promoting anything, score the funding columns alone against
a regime-only control, or the win may be a volatility regime wearing a funding
name.

## Wiring it into a scheduled loop

Check the search-space size against the batch size **before** adding the cron
entry: a 45-spec space run at `--n 45` exhausts in one week and the weekly job then
prints "nothing untested left" forever, which teaches nothing while looking
healthy. Widen the space (add 3-group combinations) so the scheduled job keeps
producing evidence, and add a self-check that asserts the weekly script still
invokes the funding runner and that the cached history is fresh.

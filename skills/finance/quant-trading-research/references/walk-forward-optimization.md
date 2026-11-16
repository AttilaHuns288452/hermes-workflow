# Walk-Forward Optimization

## Why Walk-Forward?

Standard backtests overfit. A strategy that looks great on historical data often fails live. Walk-forward analysis prevents this by:
1. Optimizing parameters on a training window
2. Testing on a subsequent out-of-sample window
3. Rolling forward through the dataset

A strategy that passes walk-forward is robust — it works on data it wasn't optimized on.

## Methodology

```
[====TRAIN====][=TEST=]
      [====TRAIN====][=TEST=]
            [====TRAIN====][=TEST=]
                  [====TRAIN====][=TEST=]
```

1. **Train window**: 252 bars (~1 year for daily data)
2. **Test window**: 63 bars (~3 months for daily data)
3. **Step**: Roll forward by test window size
4. **Metric**: Sharpe ratio on test periods

## Implementation

```python
for i in range(train_size, n - test_size, test_size):
    train = df[i-train_size:i]
    test = df[i:i+test_size]
    
    # Find best params on train
    best_params = grid_search(train)
    
    # Test on out-of-sample
    signals = generate_signals(test, best_params)
    metrics = backtest(test, signals)
    
    all_metrics.append(metrics)
```

## Key Findings

- Breakout on a 96-day lookback still shows the most durable behaviour of the
  simple families; momentum and mean reversion decay under out-of-sample testing.
- **Do not trust a "walk-forward Sharpe" until you have confirmed the split
  exists.** A repo once reported `Sharpe 8.25` under a docstring that claimed
  "walk-forward optimization"; the function had no train/test split at all — it
  ran one pass over the whole window, on the same data the lookbacks were grid
  searched on. Reproducing it gave **Sharpe 2.15 and max drawdown −22.2%**, not
  the "Sharpe 5-8 / DD 5-8%" the same file promised. Open the function and find
  the index arithmetic before quoting any out-of-sample number.
- A per-symbol Sharpe in a comment (`ADA 8.25 / XRP 6.27 / DOGE 3.64`) is a
  claim, not evidence. Grep for whether any code path emits it; if nothing does,
  it was transcribed from an ad-hoc run and cannot be reproduced.

## Guard: prove the split is real

Before treating a walk-forward result as evidence, answer three questions in the
source, not the docstring:

1. Is there a train/test boundary at all, or one pass over the full window?
2. Is the parameter being reported the same one that was selected on the training
   slice, or one selected on the whole series?
3. Does a purge/embargo gap of at least the label horizon sit between train and
   test? Overlapping labels leak across a naive boundary.

If any answer is "no", the number is in-sample and must be labelled that way.

## Verification

A strategy passes walk-forward when:
- Average test Sharpe > 2.0, **quoted with its t-stat** (a Sharpe without a t-stat
  is a rumour)
- No test period has Sharpe < -1.0
- Win rate is consistent across periods (> 40%)
- Max drawdown < 20%
- Enough trades per test period to mean anything — a 4-trade holdout behind a
  1.5 Sharpe is noise, not a result

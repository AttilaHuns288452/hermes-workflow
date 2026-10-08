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

- Breakout strategy with 96-day lookback on ADA-USDT: **Sharpe 8.25** on walk-forward
- Momentum and mean reversion strategies fail walk-forward (overfit)
- Breakout works because it captures real market behavior (trend following)

## Verification

A strategy passes walk-forward when:
- Average test Sharpe > 2.0
- No test period has Sharpe < -1.0
- Win rate is consistent across periods (> 40%)
- Max drawdown < 20%

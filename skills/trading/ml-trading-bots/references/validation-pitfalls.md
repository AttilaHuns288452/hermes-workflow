# Validation pitfalls (5 bugs that cost real time — all fixed, all reproducible)

## 1. np.sign target creates a hidden 3rd class
- **Symptom**: `model.classes_` shows `[-1, 0, 1]`; `predict_proba[:,1]` ≈ 0.000 for every row; bot goes SHORT everything (long/short mode) and loses −50% to −90% even on strong uptrends.
- **Cause**: `y = np.sign(close.shift(-1)/close - 1)` returns 0 on days where close-to-close change is exactly 0. With 3 classes sorted `[-1,0,1]`, column 1 of predict_proba = P(flat), not P(up).
- **Fix**: after dropna, filter `d = d[d["y"] != 0]`. Verify binary with `print(model.classes_)`.

## 2. Accuracy metric that credits flat days (fake 80% accuracy)
- **Symptom**: backtest prints 80-84% "accuracy" and positive Sharpe-looking numbers while the account loses money. Win rate (~33%) and accuracy (~80%) can't both be true.
- **Cause**: `hit = (strat > 0) == (rets > 0)` — on days the bot is flat, `strat = -cost < 0`, so any DOWN market day counts as "correct". The metric measures "strategy sign == market sign", not "position direction was right".
- **Fix**: position held during day j was decided at j−1:
  `pos_prev = np.concatenate([[0.0], pos[:-1]])`
  `dir_right = pos_prev[out] * rets[out] > 0` on `active = pos_prev[out] != 0` days.

## 3. Feature pipeline not idempotent → silent 200-row drop, misaligned probs
- **Symptom**: `probs` length ≠ frame length (off by exactly the rolling-window size, e.g. 1061 vs 1261); IndexError at the end of the loop, or live signals computed from a date ~200 bars stale.
- **Cause**: re-running `add_features()` on an already-featured frame restarts `rolling(200)` windows from the frame's first row → first 200 rows become NaN again → dropna removes them. Window history must come from the raw series, not the truncated frame.
- **Fix**: make the cleaner idempotent — `if "sma200" not in df.columns: df = add_features(df)` before dropna. Also: capture `dates = d.index` BEFORE `reset_index(drop=True)` (else `AttributeError: 'int' object has no attribute 'date'`).

## 4. yfinance MultiIndex columns
- `str(col).split(",")[0]` on a single-ticker download mangles names ("('Close', 'NVDA')"). Fix:
  `df.columns = df.columns.get_level_values(0) if isinstance(df.columns, pd.MultiIndex) else [str(c).split(",")[0].strip() for c in df.columns]`

## 5. uv venv: numpy cp311 wheels into a cp312 interpreter
- **Symptom**: `ModuleNotFoundError: No module named 'numpy._core._multiarray_umath'` — numpy compiled for a different Python version sits in site-packages.
- **Fix**: pin the venv python to the system interpreter: `uv venv --python 3.11 .venv` then `uv pip install --python .venv/Scripts/python.exe pandas numpy scikit-learn yfinance`.

## 6. 0 × NaN = NaN cascade
- Sizing arrays derived from `probs` (NaN before min_train) poison the P&L loop. `np.nan_to_num()` on the derived size/conf array before use.

## Debugging pattern that found these
When backtest numbers are mathematically impossible (accuracy 80% + win rate 33%, or "long-only always-in" with 0% accuracy), don't theorize — dump: `classes_`, y-balance, sign-match rate `(np.sign(pos[out]) == np.sign(rets[out])).mean()`, and a few aligned rows of (prob, pos, ret, strat). The sign-match rate vs the printed "accuracy" immediately exposes metric bugs.

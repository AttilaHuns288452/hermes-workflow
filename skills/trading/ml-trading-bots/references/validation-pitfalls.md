# Validation pitfalls (every one cost real debugging time — all reproducible)

**Read §7b first if you are scoring any sweep by AUC or t-stat.** It is the only
bug here that manufactures winners instead of errors, and it silently invalidated
an entire night's "discoveries" once already.

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

## 7. Overlapping target windows manufacture fake predictability
- **Symptom**: an h-bar return target shows autocorrelation ~0.8, and "persistence" (predict today from yesterday's same-horizon return) scores corr ~0.79 — which looks like a huge tradeable signal.
- **Cause**: `logret_h` at bar *t* covers t→t+h; at *t−1* it covers t−1→t+h−1. They share h−1 of h days. Under a pure random walk the correlation is `sqrt((h−1)/h)` by construction — 0.894 for h=5 — with zero forward information. Any model that can read recent price action looks brilliant against an overlapping label.
- **Fix**: judge predictability on NON-overlapping sampling (every h-th bar) and/or per-row purged+embargoed walk-forward. Never quote persistence or naive autocorrelation on an overlapping target as evidence of edge. `EMBARGO_DAYS` exists for this; an evaluation that ignores purging on an overlapping label overstates skill.

### 7b. Overlap also corrupts the SIGNIFICANCE TEST, not just the label (the expensive one)

- **Symptom**: a sweep reports large survivor counts on high AUCs that do not replicate, and the winners look asset-specific (one symbol scores 0.69 with 68 of 84 survivors while a sibling scores 0.59 with zero). Best-of-N p=0.03 in one asset and nothing in another is the tell.
- **Cause**: AUC p-values and t-stats assume independent observations. A horizon-h label spans h bars, so consecutive rows share up to h-1 of their outcome — at h=10 the measured label autocorrelation was 0.645. On ~290 test rows the test behaves as if there were ~290 independent trials when there are nearer 29, understating p by roughly a factor of h.
- **The trap it springs**: the AUC is real (a genuine ranking of the same-period rows); only the confidence is fake. It therefore survives every review that looks at the number and not at the sample, and it produces exactly the result you want to believe.
- **Fix, applied once at the shared layer so every search space inherits it**:
  `def effective_n(n_rows, horizon): return max(10, int(n_rows / max(1, horizon)))`
  and recompute p on the effective split keeping the same class ratio. Also thin the net-of-cost test: take a trade only once the previous one's holding period has finished, or the t-stat inflates by ~sqrt(h).
- **Impact measured when applied retroactively**: DOGE barrier 68/84 survivors → **0**; ETH 24/79 → **0**; BTC funding 7/45 → **0**; a funding spec reading +55 to +90 bps/trade net collapsed to gross t ≤ 1.36 with ~56 independent trades. Every "replicated edge" and every "worth a forward paper test" verdict was an artifact.
- **Cut per-trade counts too**: at h=10 the honest test yields ~5-6% of the row count in independent trades. Expect a few dozen, not hundreds, and size the confidence interval on that. A t-stat computed on 500 overlapping "trades" is not 500 observations.
- **Guard it with a test that MEASURES the autocorrelation** rather than asserting a constant — if the label or horizon changes, the guard should fail loudly instead of silently permitting an inflated p-value.

## 8. Measure overfitting before believing any regressor
- **Symptom**: a return regressor produces plausible-looking predictions, and a model-driven backtest scores deeply negative Sharpe while "improving" trade counts.
- **Cause**: the model memorised the training window. Raw price *levels* (`sma5/20/60/200` as absolute prices, not distances) make this trivially easy and do not generalize across a price regime.
- **Diagnostic battery** (run all four, cheap, decisive):
  1. **In-sample** corr / R² — high is necessary, never sufficient.
  2. **K-fold CV corr** — the real test. If this is ~0 or negative while in-sample R² is high, the model has no edge; stop building on it.
  3. **Mean baseline** (`DummyRegressor`) — the model must beat predicting the mean. If CV corr is below the mean baseline, the model is worse than nothing.
  4. **Feature ablation** — drop levels, keep only stationary features, then single-feature. If no subset beats the mean baseline, the signal is absent from this feature set entirely, and no amount of tuning will help.
- **Response**: ship the model disabled (`USE_RETURN_MODEL = False`) with the measurements in the source comment, and do NOT compensate by loosening promotion or probability gates — that manufactures activity, not edge. Report "no measured edge" and move to different *data* (funding rates, order-book imbalance, cross-asset lead-lag), not to more model tuning.

## 9. Triage a new data source for BACKTESTABILITY before designing any test

- **Symptom**: you build a feature pipeline and a discovery sweep for a source that has no history, then find the only data available is a live snapshot.
- **Rule**: probe for a history endpoint and inspect the response shape BEFORE writing experiment code. A snapshot endpoint (`{"openInterest": "...", "time": <now>}`) and a history endpoint (`[{...}, ...]`) read almost identically in docs and are not the same thing.
- **Triage decides the experiment**: has history → build features and evaluate now. Snapshot-only → the only valid experiment is forward collection; say so and start recording, because any claim about it is otherwise unfalsifiable.
- A plain 404 (`100404 this api is not exist`) IS the answer. Do not route around it into a "maybe" analysis.

## 10. Measure a metric's own noise before committing to a collector

- **Symptom**: a collector runs for weeks and produces a file whose values are sampling noise, so every analysis built on it is worthless.
- **Rule**: take repeated back-to-back snapshots and compute the dispersion of the metric itself before scheduling collection. If it swings across its full range in seconds, the window — not the metric — is the problem.
- **Mechanism**: order-book imbalance over N levels is `(bid_vol-ask_vol)/(bid_vol+ask_vol)`. At 20 levels the window held ~1.7 BTC (a handful of orders) and the ratio swung -0.93 to +0.57 within 12s, std ~0.55. At 1000 levels the same quantity read +0.1298/+0.1289/+0.1295/+0.1327/+0.1318/+0.1278, std 0.0017 — about 300x more stable.
- **Turn the right knob**: widen the measurement window, not the sampling rate. More frequent samples of a noisy window estimate the noise better; they do not reduce it.
- **Corroborate**: the metric should reproduce across independent runs seconds apart, and its spread column should independently reproduce the costs you measured elsewhere. If those two agree, the collector is reading the right thing.

## 11. Replication and lift are two separate gates, both mandatory

A feature that survived one sweep has survived nothing.

1. **Replication** — same direction on independent assets/windows. `1 of 24` pairs above threshold is the false-positive rate of 24 coin flips; treat it as noise. A real one holds: best-of-37 candidate replicated 6/6 across three assets x two windows (0.5427-0.6021), and a 2-feature calendar model held 0.539-0.555 on all three assets. Replication also KILLS: volatility at h=10 scored best on BTC (0.5547) and inverted on SOL (0.4433) — discarded.
2. **Lift** — the univariate survivor must still improve the ACTUAL model. Wired into the real walk-forward, the best-of-37 feature moved AUC 0.4901 → 0.4917, i.e. nothing.

No lift means the feature stays out (or goes in explicitly labelled as no-lift), and the conclusion is "this data carries no tradeable direction" — not "tune harder".

## 12. Adding features can make the model worse — test reduction first

- **Symptom**: a 20-feature model scores AUC 0.4901 while a 2-feature subset (`dow`,`month`) of the same pipeline scores 0.539-0.555 on three assets.
- **Cause**: near-noise columns contribute variance and nothing else; a weak signal gets diluted rather than reinforced.
- **Method**: score single feature groups in isolation (momentum / volatility / regime / trend / calendar / micro) at several horizons, then combine only the groups that individually cleared chance.

## 13. A search-space parameter that changes nothing is not wired in

- **Symptom**: every horizon in a sweep returns the identical AUC (0.5018 for h=1/5/10).
- **Cause**: `horizon` was in the spec and in the dedupe hash but the target was still `sign(close.shift(-1)/close - 1)`. The parameter was recorded and never used, so the ledger filled with duplicates of one test.
- **Rule**: after adding a search dimension, prove it moves the output — two different values must give two different results. Otherwise the loop is testing one hypothesis many times while inflating every "N tested" count.
- **Related**: a threshold on the same probabilities does not change AUC. Enumerate gate/min-probability values as REPORT COLUMNS from one fit, never as separate hypotheses, or the ledger multiplies by the number of thresholds. Also: the embargo must cover the label horizon, or overlapping targets leak across the train/test boundary.

## Debugging pattern that found these
When backtest numbers are mathematically impossible (accuracy 80% + win rate 33%, or "long-only always-in" with 0% accuracy), don't theorize — dump: `classes_`, y-balance, sign-match rate `(np.sign(pos[out]) == np.sign(rets[out])).mean()`, and a few aligned rows of (prob, pos, ret, strat). The sign-match rate vs the printed "accuracy" immediately exposes metric bugs.

"""Self-learning trading signal bot (walk-forward ML). Signals only — no execution.

Usage:
  python trading_bot.py --ticker NVDA --mode backtest
  python trading_bot.py --ticker NVDA --mode live
  python trading_bot.py --ticker ETH-USD --mode backtest --model ensemble
  python trading_bot.py --ticker NVDA --mode backtest --thr 0.58   # robustness sweep

Env: uv venv --python 3.11 .venv && uv pip install --python .venv/Scripts/python.exe pandas numpy scikit-learn yfinance
"""
import argparse
import logging

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

logging.getLogger("yfinance").setLevel(logging.CRITICAL)
import yfinance as yf  # noqa: E402

FEATS = ["ret_1", "ret_5", "ret_10", "rsi", "macd", "macd_sig",
         "vol_10", "sma5", "sma20", "sma60", "sma200", "mom20",
         "vol_z", "range_pct", "hi_dist", "dow", "month"]


def make_hgb():
    return HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05,
                                          max_depth=4, random_state=42)


def make_model(kind: str = "hgb"):
    """'hgb' = single boosting model; 'ensemble' = soft vote HGB+LR+RF.
    Evidence: hgb better on equities, ensemble better on crypto (4y/8y A/B)."""
    if kind == "hgb":
        return make_hgb()
    return VotingClassifier([
        ("hgb", make_hgb()),
        ("lr", Pipeline([("sc", StandardScaler()),
                         ("lr", LogisticRegression(max_iter=1000))])),
        ("rf", RandomForestClassifier(n_estimators=50, max_depth=5,
                                      random_state=42, n_jobs=-1)),
    ], voting="soft")


def fetch(ticker: str, years: int = 4) -> pd.DataFrame:
    df = yf.download(ticker, period=f"{years}y", interval="1d", progress=False, auto_adjust=True)
    if df is None or len(df) < 300:
        raise RuntimeError(f"yfinance returned insufficient data for {ticker}")
    if isinstance(df.columns, pd.MultiIndex):  # single-ticker MultiIndex ('Price','Ticker')
        df.columns = df.columns.get_level_values(0)
    else:
        df.columns = [str(c).split(",")[0].strip() for c in df.columns]
    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    return df


def add_features(d: pd.DataFrame) -> pd.DataFrame:
    c = d["Close"]
    d["ret_1"] = c.pct_change()
    d["ret_5"] = c.pct_change(5)
    d["ret_10"] = c.pct_change(10)
    delta = c.diff()
    ru = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    rd = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    d["rsi"] = 100 - 100 / (1 + ru / rd.replace(0, np.nan))
    e12, e26 = c.ewm(span=12, adjust=False).mean(), c.ewm(span=26, adjust=False).mean()
    d["macd"] = e12 - e26
    d["macd_sig"] = d["macd"].ewm(span=9, adjust=False).mean()
    d["vol_10"] = d["ret_1"].rolling(10).std()
    d["sma5"] = c / c.rolling(5).mean()
    d["sma20"] = c / c.rolling(20).mean()
    d["sma60"] = c / c.rolling(60).mean()
    d["sma200"] = c / c.rolling(200).mean()
    d["mom20"] = c.pct_change(20)
    v = d["Volume"].rolling(20)
    d["vol_z"] = (d["Volume"] - v.mean()) / v.std()
    d["range_pct"] = (d["High"] - d["Low"]) / c
    d["hi_dist"] = c / d["High"].rolling(60).max() - 1
    d["dow"] = d.index.dayofweek
    d["month"] = d.index.month
    d["y"] = np.sign(c.shift(-1) / c - 1)  # 1 if next close is higher
    return d


def walk_forward(d: pd.DataFrame, min_train: int = 252, retrain_every: int = 21,
                 thr: float = 0.55, long_only: bool = True, cost_bps: float = 10.0,
                 trend: bool = True, kind: str = "hgb"):
    """Retrain every `retrain_every` bars on expanding window (the self-learning part),
    predict out-of-sample. Returns (df with probs/pos, metrics dict)."""
    d = d.dropna()
    d = d[d["y"] != 0]  # flat days: np.sign == 0 would create a 3rd class
    dates = d.index
    d = d.reset_index(drop=True)
    X, y = d[FEATS].values, d["y"].values
    n = len(d)
    probs = np.full(n, np.nan)
    model = None
    for i in range(min_train, n):
        if model is None or (i - min_train) % retrain_every == 0:
            model = make_model(kind)
            model.fit(X[:i], y[:i])
        probs[i] = model.predict_proba(X[i:i + 1])[0][1]

    pos = np.zeros(n)
    trend_arr = np.where(d["Close"].values > d["sma200"].values, 1.0, -1.0)
    for i in range(min_train, n):
        p = probs[i]
        t = trend_arr[i] if trend else 1.0
        if long_only:
            pos[i] = 1 if (p >= thr and t == 1) else 0
        else:
            pos[i] = 1 if (p >= thr and t == 1) else (-1 if (p <= 1 - thr and t == -1) else 0)

    rets = d["ret_1"].values
    strat = np.zeros(n)
    cost = cost_bps / 10000
    for i in range(min_train, n - 1):
        strat[i + 1] = pos[i] * rets[i + 1] - cost * abs(pos[i] - pos[i - 1])

    out = np.arange(min_train, n - 1)
    eq = np.cumprod(1 + strat[out])
    bh = np.cumprod(1 + rets[out])
    pos_prev = np.concatenate([[0.0], pos[:-1]])  # position held during day j = decided at j-1
    active = pos_prev[out] != 0
    dir_right = pos_prev[out] * rets[out] > 0  # true directional accuracy
    n_trades = int(np.sum(np.abs(np.diff(pos_prev[out])) > 0))
    metrics = {
        "ticker": d["ticker"][0] if "ticker" in d else "",
        "period": f"{dates[0].date()} -> {dates[-2].date()}",
        "strat_return": eq[-1] - 1, "buy_hold": bh[-1] - 1,
        "sharpe": strat[out].mean() / (strat[out].std() + 1e-12) * np.sqrt(252),
        "max_dd": float((eq / np.maximum.accumulate(eq) - 1).min()),
        "trades": n_trades, "active_days": int(active.sum()),
        "coverage": float(active.mean()),
        "accuracy": float(dir_right[active].mean()) if active.any() else float("nan"),
        "win_rate": float((strat[out][active] > 0).mean()) if active.any() else float("nan"),
        "avg_ret_active": float(strat[out][active].mean()) if active.any() else float("nan"),
    }
    d["prob"] = probs
    d["pos"] = pos
    return d, metrics


def live_signal(d: pd.DataFrame, thr: float = 0.55, kind: str = "hgb"):
    d = add_features(d).dropna()
    d = d[d["y"] != 0]  # keep binary target (flat days -> np.sign 0)
    model = make_model(kind)
    model.fit(d[FEATS], d["y"])
    p = model.predict_proba(d[FEATS].iloc[[-1]])[0][1]
    trend_up = bool(d["Close"].iloc[-1] > d["sma200"].iloc[-1])
    if trend_up:
        sig = "BUY" if p >= thr else "HOLD"
    else:
        sig = "SELL" if p <= 1 - thr else "HOLD"
    from sklearn.inspection import permutation_importance
    imp = permutation_importance(model, d[FEATS].iloc[-252:], d["y"].iloc[-252:],
                                 n_repeats=3, random_state=42, scoring="accuracy")
    top = sorted(zip(FEATS, imp.importances_mean), key=lambda t: -t[1])[:5]
    return {
        "as_of": str(d.index[-1].date()), "close": float(d["Close"].iloc[-1]),
        "prob_up": p, "signal": sig, "retrained_on": len(d),
        "regime": "uptrend" if trend_up else "downtrend",
        "top_features": top,
    }


def main():
    ap = argparse.ArgumentParser(description="Self-learning trading signal bot")
    ap.add_argument("--ticker", default="NVDA")
    ap.add_argument("--mode", choices=["backtest", "live"], default="backtest")
    ap.add_argument("--thr", type=float, default=0.55, help="signal threshold (0.5-0.6)")
    ap.add_argument("--retrain", type=int, default=21, help="retrain every N bars")
    ap.add_argument("--long-only", action="store_true")
    ap.add_argument("--no-trend", action="store_true", help="disable 200d trend filter")
    ap.add_argument("--model", choices=["hgb", "ensemble"], default="hgb")
    ap.add_argument("--years", type=int, default=4)
    a = ap.parse_args()

    d = fetch(a.ticker, a.years)
    d = add_features(d)

    if a.mode == "live":
        s = live_signal(d, a.thr, a.model)
        print(f"{s['signal']} {s['prob_up']:.0%} | {a.ticker} @ {s['close']:.2f} (as of {s['as_of']}) | regime: {s['regime']} | model: {a.model}")
        print(f"model: retrained on {s['retrained_on']} bars | top features: " +
              ", ".join(f"{f} {w:.2f}" for f, w in s["top_features"]))
        return

    _, m = walk_forward(d, retrain_every=a.retrain, thr=a.thr, long_only=a.long_only,
                        trend=not a.no_trend, kind=a.model)
    print(f"{m['ticker'] or a.ticker} | {m['period']} | thr={a.thr} | retrain={a.retrain} bars | trend={'ON' if not a.no_trend else 'OFF'} | model={a.model}")
    print(f"  strat return  {m['strat_return']:+.1%}   buy&hold  {m['buy_hold']:+.1%}   excess {m['strat_return']-m['buy_hold']:+.1%}")
    print(f"  sharpe {m['sharpe']:.2f}   maxDD {m['max_dd']:.1%}   trades {m['trades']}   coverage {m['coverage']:.0%}")
    print(f"  accuracy {m['accuracy']:.1%}   win rate {m['win_rate']:.1%}   avg ret/active day {m['avg_ret_active']:+.3%}")


if __name__ == "__main__":
    main()

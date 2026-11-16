# Does the system actually self-learn?

How to answer "will it become smart enough to make money on its own" with
measurements instead of architecture diagrams. Every number below came from real
runs; reproduce them rather than assuming.

---

## Three requirements for a learning loop

A champion/challenger job is not automatically a learning loop. Check all three.

| requirement | how to check | common reality |
|---|---|---|
| **Generates new hypotheses** | Is the challenger grid a fixed literal list? Grep for `random`, `mutate`, `sample` near it. | Fixed N-combo menu, re-tested weekly. Nothing invents a candidate. |
| **Consumes its own history** | `grep -rn "experiments.csv" --include=*.py`. Does any consumer *read* it, or only append? | Append-only log. Nothing feeds results back into the next run. |
| **Has something to learn from** | Measure the model's out-of-sample skill (below). | AUC at or below 0.5 — there is no signal to learn. |

If (1) and (2) fail you have **selection over a fixed menu**, not learning: it can
only ever find a better configuration of what is already listed. If (3) fails,
nothing built on top can help — every loop, judge, or LLM reasons about noise.

Report it plainly: "it re-tests a fixed menu and reads nothing from its history"
is a complete, correct answer. Do not describe selection as learning.

---

## Measuring directional skill (the sharpest diagnostic)

Take the walk-forward predictions the system already produces and score them
against realised direction. Do not build anything first.

```python
from sklearn.metrics import roc_auc_score, brier_score_loss

d, pred = research_predictions(ticker, years=4, pool=siblings)
df = pred.dropna(subset=["prob_up", "cal_prob_up"])
y = d["y_dir"].reindex(df.index)
m = y.notna() & (y != 0)          # direction only: drop flat bars
df, y = df[m], y[m]

yb = (y.to_numpy() > 0).astype(int)
print("base rate", max(yb.mean(), 1 - yb.mean()))
for col in ("prob_up", "cal_prob_up"):
    p = df[col].to_numpy(float)
    print(col, "AUC", roc_auc_score(yb, p),
          "Brier", brier_score_loss(yb, p.clip(0, 1)))
```

### Read AUC against 0.5, not against 1.0

- **AUC < 0.50 is worse than a coin flip.** Not "weak" — inverted. No sizing,
  stop, or risk rule rescues it.
- **AUC ≈ 0.50 with a high Brier score** means the probabilities are also badly
  calibrated: confident and wrong.

### The confident-call test — the one that actually indicts the model

AUC alone hides tail behaviour. Check accuracy **where the model is confident**,
because that is where trades actually fire:

```python
gate = df["cal_prob_up"].to_numpy() >= config.MIN_PROB_UP
if gate.sum():
    print(f"n={gate.sum()} hit={yb[gate].mean():.4f}")
```

Observed on a live bot: overall AUC 0.4901 (`cal` 0.4761), accuracy at 0.5 ≈
0.497, but at `cal >= 0.55` (n=255) the hit rate was **0.4588** — its
highest-conviction signals were its *worst*. That single line explains every
other symptom: zero promotable experiments, trade counts stuck under the
minimum-trade floor, two round-trips in 69 days. Quote it; it is undeniable in a
way a Sharpe never is.

---

## Feature discovery: the one capability that can move the needle

If the model has no skill, the question becomes "is there signal in this data at
all?" Answer it per-feature, out of sample, before touching the model.

### Scoring rule

- **Chronological split with an embargo of at least the label horizon.** Random
  K-fold leaks on overlapping labels.
- Score **test-window AUC only**.
- Treat an AUC of 0.40 as informative as 0.60 — strength is `abs(auc - 0.5) + 0.5`,
  since a reliable inverted signal is still signal.
- Require `n_test >= ~300` before believing anything.

### The replication rule (this is the part people skip)

With ~37 candidates tested, **one or two clearing your bar is exactly what chance
produces.** A single passing feature is a hypothesis, not a finding. Replicate it
across independent assets AND independent windows before adding it:

| feature | BTC 3y | BTC 4y | ETH 3y | ETH 4y | SOL 3y | SOL 4y |
|---|---|---|---|---|---|---|
| `skew_20` (20d skew of daily returns) | 0.5480 | 0.5547 | 0.5427 | 0.5474 | 0.6021 | 0.5928 |

6/6 positive in the same direction — that is a real (weak) lead. One asset at one
window would not have been.

### The lift test — a weak univariate feature usually does nothing

Adding a validated feature is not the same as improving the model. Measure both
sides:

```
before:  AUC(prob_up) 0.4901   AUC(cal) 0.4761   confident-hit 0.4588
 after:  AUC(prob_up) 0.4917   AUC(cal) 0.4822   confident-hit 0.4652
```

A univariate AUC of 0.55 becomes noise when it is one of 21 correlated features in
a boosted model. **That is the normal outcome, not a bug.** Report the null lift
honestly; keep the feature only if it is causal and cheap, and say it did not
move the model.

---

## What actually creates an edge

When the audit lands on "no signal", the fix is not a better loop:

1. **New information.** Funding rates (crowding), open interest, order-book
   imbalance, liquidation cascades, cross-asset lead-lag (majors → alts),
   stablecoin flows, on-chain. None of these is recoverable from the price series,
   so no amount of feature engineering on OHLCV reaches them.
2. **A different objective.** Volatility and regime are somewhat predictable.
   Predict those and size/trade conditionally instead of predicting direction.
3. **A horizon where signal can clear cost.** See the edge-to-cost rule in the
   main skill — a 5-minute horizon predicting sub-basis-point moves against a
   16-20 bps round trip cannot work regardless of model quality.

## What to say about an LLM/classifier add-on (Jev, or any judge)

A bounded classifier (`choice`/`score`/`noul` + confidence) **cannot add
information that is not in its input.** If the underlying features score AUC
0.49, the classifier scores at chance too. Its genuine value is a better
*contract*: typed output + calibrated confidence replacing free-text
agree/contradict in an existing review slot. Say that precisely — "a code-quality
improvement, not a source of edge" — rather than either dismissing it or selling
it as intelligence.

Before proposing any paid judge: confirm a key exists, and confirm the judge you
already have is measurable. A judge with 14 judgements and 2 recorded outcomes
cannot be evaluated, so replacing it is unfalsifiable either way.

---

## Building the loop (once the audit says "selection only")

Three pieces turn selection into accumulation. Keep them small — one script, one
ledger file, one cron entry. A framework here is a liability, because the whole
value is in the *record*, not the machinery.

### 1. A ledger that makes retesting impossible

Append one JSON line per hypothesis, keyed by a hash of the thing being tested:

```python
def spec_hash(spec):
    blob = json.dumps({"f": sorted(spec["features"]), "h": spec["horizon"]},
                      sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]

seen = {json.loads(l)["hash"] for l in LEDGER.read_text().splitlines()}
untested = [s for s in generate() if spec_hash(s) not in seen]
```

The hash must cover **only what is actually varied in the evaluation**. Get that
wrong and the ledger fills with near-duplicates (see the threshold trap below).
Record failures with a null result — "this region is dead" is the knowledge.

### 2. A generator that composes, rather than a list someone maintains

Group features by family (momentum / volatility / regime / trend / calendar /
micro), then take combinations of 1–3 groups × horizons. That gives a few hundred
hypotheses from a few dozen primitives, and it grows when you add a group instead
of when you add a row. Report the search-space size and how many are untested —
the loop should visibly approach exhaustion.

### 3. Evidence only, never promotion

The loop scores and records. It must not promote, size, or trade. Promotion stays
behind the pre-registered gates, because the loop is exactly the thing that would
otherwise grind out false positives until one passed.

Run it on a schedule with a CPU cap (`systemd-run --user --scope -p
CPUQuota=150%`, see the process-control notes) and let it work through the space
over weeks.

### Two bugs that make the ledger worthless without any error appearing

**The spec field must appear in the TARGET, not just the spec.** A `horizon`
stored in the hypothesis but unused by `evaluate()` produced AUC 0.5018 for h=1,
h=5 and h=10 identically — three ledger rows, one actual test. The tell is
*identical metrics across a dimension you believe you varied*. Whenever two arms
differ only in a parameter, assert the numbers differ; if they don't, the
parameter is decorative.

**A threshold is not a hypothesis.** Enumerating `min_prob ∈ {0.52, 0.55, 0.58}`
tripled the ledger with duplicate rows, because AUC is invariant to a threshold on
the same scores. Fit once per (features, horizon), then report gate statistics
(signal count and hit rate) for every threshold from that single fit. Same for
any other monotone post-processing of predictions.

**Embargo must cover the label horizon**, not just a fixed number of days — a
5- or 10-bar target with a 1-day gap leaks across the split. Use
`max(EMBARGO, horizon)`.


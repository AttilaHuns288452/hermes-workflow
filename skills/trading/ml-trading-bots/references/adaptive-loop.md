# Adaptive loop: turning evidence into behaviour

Depth for the SKILL.md sections "Making it actually learn" and the judgment-layer
rule. Every number here came from a measured run; treat them as calibration
anchors, not constants.

## Continuous allocation instead of a promotion cliff

A binary promotion gate (all-of: margin over champion AND trade floor AND
adverse-sharpe AND t-stat, held for N consecutive weeks) is defensible
statistically and fatal operationally. Count how many candidates have EVER
passed before trusting it. If that count is zero, the gate is the bug.

Replace it with a continuous multiplier computed from the blended estimate:

```
edge_multiplier = 0                                         if posterior <= cost
                = min(1, (posterior - cost) / (2 * cost))   otherwise
```

Zero at cost, full size at 3x cost, linear between. No cohort cliff, no streak
requirement, no cooldown. Every position is scaled by measured edge, so thin
evidence produces small positions rather than all-or-nothing.

**Exploration floor is not optional.** With `edge_multiplier = 0` the bot stops
trading, records no new trades, the posterior never moves, and it is switched off
forever. Keep a small fixed fraction (order 5%) whenever the computed multiplier
is zero, labelled as exploration, purely to keep evidence flowing. When a real
edge appears the computed multiplier overtakes the floor automatically.

## Blending prior and live evidence

Use **inverse-variance (precision) weighting**, not sample-count weighting:

```
var_i     = std_i**2 / n_i
precision = 1 / max(var_i, 1)          # floor so a zero-variance sample
posterior = sum(p_i * mean_i) / sum(p_i)   # cannot claim infinite precision
```

Measured consequence of getting this wrong: a 38-trade backtest prior at
+19.91 bps blended with 2 live trades at -1248.98 bps gave **-118.87 bps** under
count weighting and **-3.62 bps** under precision weighting. The first would have
shut the bot off permanently on two outlier trades (positions held far longer
than intended, -16% and -8.7%). The second gave those trades 1.9% weight.

Report `prior_weight` alongside the posterior so the reader can see how much of
the estimate is live evidence. Two observations should never outrank a large
prior, and a future reader must be able to verify that from the output.

Treat `n < 2` live trades as **no evidence** — sample std is undefined for one
observation.

## Jev: a decision model, not a chat model

Jev (`typesafe/jev`, pinned `typesafe/jev-1.14.0`) answers typed questions with
probabilities and never produces text. Different surface from chat: it is **not**
reachable on a `/chat/completions` style endpoint and does not appear in a normal
model list.

```
POST /provider/v1/systemone
{ "model": "typesafe/jev",
  "state": <text or JSON>,
  "questions": {
    "name": {"type": "noul"|"choice"|"score",
             "instructions": "...",
             "criteria": {...} } } }
-> { "answers": { "name": {"noul": 0.93} |
                  {"choice": "x", "confidence": 0.7, "probabilities": {...}} } }
```

`noul` = probability of yes. `choice` = one of your named options plus the full
distribution. `score` = position on an ordered rubric. Roughly $0.04/M input and
sub-cent per call at ~400 tokens.

### Where it earns its place

| slot | measured | why it works |
|---|---|---|
| **Unstructured text -> signed number** | exploit headline read as bearish at 0.88-0.91, flipping a keyword scorer's +0.05 to -0.91 | keyword matching cannot distinguish "exchange hacked" from "exchange publishes hackathon results"; a decision model can |
| **One binary judgment you can threshold** | 0.75 on a valid setup vs 0.02-0.03 on invalid ones | returns a calibrated probability instead of prose, so a threshold is meaningful and the result is scorable against outcomes later |

### Where it adds nothing (measured failures)

| slot | measured | why |
|---|---|---|
| **Sanity-checking numbers already computed** | normal order rated "broken" at p_wrong 0.71 but **confidence 0.07**; genuinely absurd order only 0.88 | low-confidence verdicts are noise; as a blocker it stops normal trading. Only usable as a high-confidence alarm, never as a gate |
| **Ranking candidate experiments** | **0.20-0.31 confidence** even across a deliberately diverse shortlist | it has seen no outcomes for those candidates, so it has no basis to rank them — and says so. Forcing it produces arbitrary ordering wearing a model's clothing |

General rule: **Jev is a judge, not a source of information.** It cannot improve
direction (a trained model reads the same features), sizing (arithmetic), or cost
(measured from the book). Its accuracy is bounded by the state you hand it, so
integrate it only where the input is something the code does not already compress
into a number.

When a decision point measures poorly, **remove it and pin the limitation in a
test** rather than leaving it wired for appearance. A negative result recorded is
worth more than a feature that looks integrated and does nothing.

## Probing for a model/service before declaring it absent

A model can exist and still be invisible to the obvious probe. Chat-completion
endpoints reject non-chat models (HTTP 400 "model not supported on this
endpoint"), and a local-binary search finds nothing for a hosted service. Before
concluding something does not exist:

1. Check the provider's model/pricing docs for the exact ID and its **transport**.
2. If the ID looks absent from `/models`, try the documented dedicated endpoint
   with its documented request shape — `/models` lists chat models, not every
   callable surface.
3. Only after both, report absence — and say which surfaces you probed.

Declaring "it does not exist" from a single wrong-endpoint 400 is a false
negative that can change the whole architecture of the solution.

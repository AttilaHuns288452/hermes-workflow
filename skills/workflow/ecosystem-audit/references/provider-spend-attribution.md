# Provider spend attribution

For "why is my quota gone" and "why was this model used" when several apps share one API key.

## Read the agent's own ledger first

`state.db` records every call the agent made, tagged with the provider that billed it:

```sql
select billing_provider, model, sum(api_call_count) calls,
       sum(input_tokens) inp, sum(output_tokens) out,
       sum(cache_read_tokens) cache, min(first_seen), max(last_seen)
from session_model_usage
group by billing_provider, model
order by calls desc;
```

`first_seen` / `last_seen` are epoch floats — read them before drawing conclusions, because a model
that looks wrong in the totals is often one old session rather than an ongoing leak.

`estimated_cost_usd` is populated only when Hermes knows the model's price. `cost_status='unknown'`
means the number is not a measurement: report the share and the rate ratio instead of inventing dollars.

## Establish the dashboard's units before comparing anything

Provider dashboards label a column "share of usage" and it is usually **cost** — not tokens, not
requests. Prove the unit before using it:

- token share ≈ request share ⇒ it is not cost;
- a row with a negligible request count **and** a negligible token count but a large share ⇒ it is cost.

Then compare rates, not totals: `share% ÷ millions of tokens`, normalised against the cheapest model in
the table. That ratio is the argument ("this model costs N× the default per token") and it survives the
plan changing.

## Find the other app on the key

A key is shared by everything on the box. When the ledger accounts for the whole bill of one model but
not of another, the difference is a second caller:

- coding-agent CLIs and the local bridge/proxy that fronts them
- local model-bench and eval harnesses
- cron scripts, trading bots, RAG indexes

Enumerate their model configuration instead of guessing — the CLI's settings file, the bridge's route
table, the harness's default. The distinction that matters: a `--model` passed explicitly by a harness
is an intentional act, while a **default** in a settings file bills every casual run at that rate.

## Guard the default, never the option list

Deleting expensive routes kills capability the user installed on purpose. Enforce the default instead:

1. Point every default-model slot at the cheap model — the main slot **and** each alias/slot the CLI
   reads (sonnet/opus/haiku/small-fast equivalents), because each one is a separate path to a bill.
2. Add an allow-list check to a periodic watchdog that already runs; do not create a new daemon. Flag
   any default slot whose value is neither the cheap model nor a free/plan-covered alias, and name the
   variable plus its exact replacement in the alert.
3. Regression-test both directions: set a bad value and confirm the alert fires, restore and confirm it
   is silent.
4. Fix the noise floor first (`SKILL.md` → Pitfalls) or the new alert is buried the same day.

## When the owner escalates from "cheap default" to "remove the provider"

Guarding the default is the right first move, but it is defeatable: an explicit `--model`, a harness that
passes one, or a settings rewrite restores the spend. If the answer to the guard is "no, take the
provider out", the work moves to the route table, and two things decide whether it was done properly:

- the cut belongs in the **generator** behind an opt-in flag, not in the generated table (a hand-deleted
  entry comes back on the next regeneration);
- every **surviving** alias must be probed before declaring success, because removing one provider can
  leave the consumer with no working backend at all (402 empty wallet / 404 model absent are the usual
  answers).

Full steps: `llm-provider-wiring` -> "Removing a provider from a route table". Report the consequence in
the same breath as the fix: the honest end state is a settings file that fails loudly with 402/404 and
spends nothing, never a quiet re-point onto another paid route.

## Report the split, not a scold

State how much of the bill the agent itself caused, how much came from the other app, and which single
default caused it. If a credential was printed while investigating, say so in the same breath and tell
the user to rotate it.

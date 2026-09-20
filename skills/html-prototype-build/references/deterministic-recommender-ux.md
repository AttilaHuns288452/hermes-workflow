# Deterministic recommender UX (NO-AI line)

Scope: prototypes with a ranking/recommendation engine where the user forbids AI/LLM decision-making or generated prose. Everything the user sees about WHY a product ranked must be template-derived from data + their inputs.

## Data-feasibility gate (before coding the engine)

Classify every planned metric by where its number can come from: RAW marketplace/product spec, GW-maintained catalog value (documented, manual), deterministic formula over those, or user input. A metric with no defensible source does not ship — no score invented from unrelated specs (RAM does not imply repairability; price+CPU do not imply lifespan). When the user sends a feasibility-correction brief, remove the unsupported metric from EVERY consumer: scoring, priority lists, comparison rows + verdict logic, catalog filters, use-case criteria keys — grep the field name across js/ and html/, not just the engine.

- Defensible fall-backs that keep the metric class: per-product lifespan invention → a FIXED window applied identically to all products (price ÷ 36-month window); per-category 'durability' score → rename to what the data actually covers ('Build & Protection') or drop; repairability → drop entirely (marketplace specs never support it).
- Provenance header: document the RAW / CATALOG / CALCULATED / USER-GENERATED field classification at the top of the data file, and mirror the formulas in the README.
- Editorial strengths/weaknesses are marketing-copy traps: write spec-based labels (chipset name, capacity, weight, watts), not voice ('rare in this class', 'genuinely a week of classes'). Same for summaries.

## Mental model

Configure criteria → hard-filter → score → rank → explain. NOT a quiz, NOT an AI match.

- **Core step = "what matters most"**: one labeled slider per engine-backed factor, scale `Not important / Nice to have / Important / Very important / Top priority` (internal 0–4), output label live-updates on input.
- Never label the zero point 'Skip it' when the formula keeps a baseline weight for the factor — the scale must not claim a behavior the math doesn't have. State the real behavior on the step: 'Factors you deprioritize still count a little; price and purpose always count.'
- **Category-aware factors only**: render exactly the factors the engine scores for the chosen category; an option the formula ignores is a fake control.
- **Hard requirements filter BEFORE scoring** (keep per-product exclusion reasons for the results page). Budget is typically hard already — never offer a checkbox for a constraint the engine enforces unconditionally.
- Requirements review step before results; transparency note ends with "No AI is used to choose the product."

## Explanation templates (all rule-derived, never free-form)

- Why-ranked-first: budget fit, use-case match, must-haves met, top-priority strength, ownership delta — each a template fired by a component threshold.
- Trade-offs (plural heading over a list): product weaknesses + lowest-scoring component.
- Why A ranked above B: +N component diffs shown both directions.
- What-if chips: bump one weight, rerank, report 'Same winner: X (n/100)' or 'New winner: X'.
- No-result state: relaxation actions (raise budget / relax a must-have / revise) — each action must land on the step where that thing is EDITABLE, not a read-only summary.

## Verification specifics

- **Slider flip test**: dispatch `input` events to set opposite extremes, rerun, assert the ranking or score changes. A robust catalog can keep the same winner — assert score movement, not just winner identity.
- **After renumbering steps**: run the full flow to the final step and assert the review panel is non-empty (catches stale `recStep===N` render gates).
- **Vision-pass the priority step**: unfilled-track contrast and missing thumb ring are the two flags it reliably catches.
- **Greps after copy edits**: removed field names (dead readers), synonym zoo terms, stale step-count literals ('of 7').
- Standardize naming before ship: one figure = one label everywhere ('Est. monthly cost'), one index name ('Ownership Index') including title/aria attributes.
- Cost-model changes ripple wider than the formula file: a lifespan-based monthly cost → fixed-window change touches detail value-tag rows, comparison rows, verdict picks, and reasons — grep the removed term ('lifespan', 'Est. lifespan') across all templates after the engine change.

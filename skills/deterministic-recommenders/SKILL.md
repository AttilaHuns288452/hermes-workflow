---
name: deterministic-recommenders
description: Use when building explainable, non-AI product recommenders.
---

# Deterministic recommender systems (quiz → score → explain)

Class: rule-based ranking engines for product/comparison sites where the brief forbids AI in the decision path (academic projects, auditability requirements). Reference implementation: gadgetwise-prototype (github.com/AttilaHuns288452/gadgetwise-prototype).

## Standing rules
- **NEVER put AI/LLM/embeddings in the ranking path.** Flow: student inputs → validation → hard constraints → weighted scoring → ranking → template-generated explanation. Same inputs must produce the same ranking every time.
- **Infer weights from practical questions; do NOT expose raw weight sliders.** Ask 'how often are you away from a charger?' and scale the battery weight from the answer. Users are students, not ML engineers — manual 0–5 factor sliders get rejected as 'acting like a machine-learning engineer'.
- **Hard constraints ≠ preferences.** Deal breakers (over budget, under X GB, heavier than Y) exclude the product or mark it incompatible; a failed preference only lowers the score. Apply constraints BEFORE scoring.
- **Honesty rule:** a product far over budget cannot win on other merits. Scale the budget weight with how tight the budget is (weight grows with over-budget ratio) AND apply a direct score penalty past ~15% over. Without it, rich components (rating, purpose) mask a 0/100 budget fit and a ₱15k student gets shown a ₱47k laptop.
- **Never score a missing input as zero.** Optional fields (a marketplace listing has price/rating but no curated battery/warranty/sub-scores) must be EXCLUDED from the weighted sum and the weight renormalized over the available inputs — JS arithmetic coerces `null/10 → 0` and `null-min/max-min →` a large negative, so an absent spec silently scores as worst-case and drags real products down. Return `null` from the normalize step for unknown values, skip those factors in the explanation breakdown (do not render a fake 0 bar), and drop nulls out of any pool min/max so they don't corrupt the normalization range. Add a test asserting `factors.sum ≈ total` and that absent factors are absent from the breakdown — the phantom-weight bug is invisible in the UI otherwise.
- **Category-specific everything**: purposes, preferred features, deal-breaker options, and scoring attributes differ per product type. Store a per-item component map (`cx:{perf, battery, portability,...}`) alongside shared fields; fall back to shared fields when cx is absent.
- **Explainable results, built from actual inputs**: per-component score bars with the applied weight (×N, dimmed at zero), 'why this is #1' assembled via conditionals from the user's answers, 'where it falls short' from stored weaknesses, and a 'why A ranked higher than B' component comparison. Never 'AI recommends this'.
- **Alternatives + what-if**: superlatives (best budget/performance/battery/long-term value) computed by the SAME engine and deduped by product; 'what if' chips re-run the identical formula with one input changed and report whether the winner holds.
- Show the monthly-ownership math visibly (price ÷ lifespan-months = ₱/month, labeled 'estimate only') — it is usually a proposal requirement and the core of long-term value.

## Provenance-aware metric derivation (sparse / marketplace data)
When the product source has NO curated specs (a marketplace listing carries price, rating, brand, reviewCount, seller but battery/performance/portability are null), do not fabricate specs and do not leave the metrics card as empty `-` rows. Derive only what the real fields support and label EVERY metric with provenance, rendered next to the value:
- **source**: copied verbatim from the listing (price, originalPrice, rating, reviewCount, seller).
- **calculated**: a deterministic derivation from real fields (price competitiveness vs the product's category peers; listing completeness = % of core fields present; evidence coverage = share of the scoring weight backed by real inputs).
- **estimated**: a reasonable allocation that is NOT a factual claim; it must derive from real inputs and its label must state the assumption (purchase price / 36 = "price/month allocation", explicitly "not a lifespan claim").
- **unavailable**: the field is genuinely unknown; return `null` + a human-readable reason, never a fabricated number and never 0.

Rules:
- Never invent `estimated` from thin air; an estimate derives from real inputs and its rendered label carries the assumption.
- A discount metric renders only when the reference price is genuinely HIGHER than the price; otherwise the "discount" is misleading.
- Missing price -> `unavailable` with a reason, not 0 (a P0 price reads as "free").
- Test: battery/performance stay unavailable (not fabricated), discount hidden when ref <= price, missing price -> unavailable not zero, output is deterministic across runs, and a category with too few peers does not fake a competitiveness score (small-sample honesty).

## Procedure
1. Model data per product: shared fields (price, warranty, lifespan, rating, category) + category component map + strengths/weaknesses/goodFor/notIdeal arrays.
2. Define per-category purpose list, feature list, deal-breaker list; rebuild quiz steps when category changes.
3. Implement `score(product, answers)`: components 0–100 → weights from answers → weighted average; hard constraints filtered out first, with the exclusion reason stored for display.
4. Verify in Node BEFORE the browser: port the formula to a standalone script, score 3 products across 3 personas (tight budget / mid / rich) and assert the winner changes. This catches mask-by-merit flaws the honesty rule exists for.
5. Render results with explanation + alternatives + what-if; every number shown must come from the same scoring function (never hardcode a score in copy).
6. When the user orders explanation-copy changes (e.g. 'Why we recommend it' → 'Why it ranks here', 'BEST MATCH FOR YOU' → 'BEST MATCH'), keep the underlying threshold rules untouched — relabeling must never touch the scoring path, and the results stay verifiable against the score breakdown table.

## Pitfalls
- Lazy-loaded images inserted inside a hidden container never fetch (Chromium does not re-run the intersection check when the container is shown) — quiz-result panels must use eager loading; keep lazy only for initially-visible grids.
- Test clicks on visually-hidden radios inside labels: the label span intercepts the click — dispatch `el.click()` via evaluate instead of pointer clicks, and quote attribute-selector values (`input[name="qBudget"][value="15000"]`; unquoted values throw SyntaxError).
- When restyling an existing prototype, patch the `:root` custom properties instead of rewriting selectors — but dedupe rules the patch sits next to.
- **Reason lines must respect band edges.** Threshold-derived copy like 'Fits your budget at ₱X' is wrong when the price sits below the band floor — branch the wording on the same conditions the score uses (`price < min` → 'Under your budget'). Every displayed sentence is a function of the same numbers; a mismatch reads as a bug even when the math is right.
- **Catalog data drift shows up as UI slop.** A `model` field that repeats the `brand` ('Anker Anker PowerCore') renders duplicated in every template that joins brand+model — fix the data, not the templates. After any catalog edit, re-run the full-catalog image URL check (host included) and the duplicate-image check, not just the changed rows.
---
name: spreadsheet-to-product-research
description: >-
  Convert spreadsheet prototypes into product features.
---

# Spreadsheet → Product Research

The user's spreadsheet is a prototype of how they think, refined over years.
The product brief: convert its LOGIC into features — dashboards, reports,
charts, AI insights, notifications, automations — without recreating any cell.

## Reading the file

- `python -c "import openpyxl"` first — the hermes venv may lack pip; install
  into the system Python with `uv pip install --python "<path>\python.exe" openpyxl pandas`.
- `load_workbook(path, data_only=True)` — list `sheetnames`, then dump each
  sheet `iter_rows(max_row=~18, max_col=~14)`, skipping empty rows. Do NOT
  trust `read_only=True` for dimensions (reports `None` on some files).
- Map every tab: log tabs, dashboards, trackers, reports, charts. READ-ME and
  INPUT tabs reveal the user's categories and currency conventions (e.g. ₱,
  baon, tithing — cultural terms that must survive into the product).

## Analysis pass (the actual skill)

For every metric/calculation found, ask: *why would the user want this?* then
classify each as widget / report / chart / AI insight / notification /
automation / recurring calculation. Deliverables of the analysis:

1. **Metrics they care about** — headline numbers they compute by hand.
2. **Calculations** — formulas they repeat (profit = income − expenses,
   remaining = goal − saved, budget variance, savings rate).
3. **Summaries they check** — weekly grids, monthly overviews, annual reviews,
   health scores.
4. **Hidden insights** — things the spreadsheet implies but doesn't compute:
   liquidity ratio, emergency-fund coverage, passive-income ratio,
   debt-to-asset ratio, payoff dates, seasonality.
5. **Emergent dashboards** — a weekly M→Sun grid becomes a weekly-spending
   widget; a no-spend calendar becomes a gamified month heatmap with a goal
   counter; dividend lines by rate become a passive-income dashboard;
   a debt tracker becomes a payoff simulator with "free by <date>".

## Conversion rules

- **Never recreate the spreadsheet visually.** Excel stores data; the app
  generates insights. Table → dashboard, formula → report, data entry →
  workflow. Ask "how would Apple/Stripe/Notion redesign this?"
- **Map to existing features FIRST** (many spreadsheet metrics may already
  exist in the app — say so, don't rebuild), then propose the gaps as a
  prioritized feature list.
- **Lean into the user's orientation.** If the spreadsheet is net-worth-centric
  (assets, liquidity, investments, debt) rather than budget-centric, the
  product positioning follows: "see your entire financial position" — not
  "track your expenses."
- **Cultural specifics are features.** Tithing lines, baon categories, weekly
  rhythm — preserve the user's vocabulary in the product.
- **Numbers in the spreadsheet are seed data for mocks** (real-looking ₱
  figures), not claims to ship.

## Session pattern

Deliver the analysis table (spreadsheet column → metric → product feature),
then dispatch parallel feature agents with the frozen app design system —
widgets to the dashboard, modules as new features, each brief citing which
spreadsheet tab inspired it. ECC review + build + push as usual (see
`parallel-sprint-shipping`).

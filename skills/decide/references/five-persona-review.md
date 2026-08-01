# Five-Persona Review Protocol

After every milestone (v1, v2, etc.), run this review before marking complete.

## Personas
1. **Everyday user** (no finance background) — understandability, speed, would they return?
2. **Finance power user** — trends, breakdowns, would they trust this over a spreadsheet?
3. **Business owner** — profitability at a glance, decisions they can/can't make
4. **Staff/employee** — simplicity, feedback speed, RBAC visibility
5. **Accountant** — category standards, balance sheet correctness, audit trail, exportability

## Output
1. Five short critiques (specific complaints/praise, not vague sentiment)
2. Prioritized change list: persona, why, effort (small/med/large)
3. Schema-change-if-deferred risks (these get priority — same logic as entity model decision)
4. Explicitly flagged NOT-changing items, with reasoning

## When to use
- After v1 ships, before starting v2
- After major feature set ships
- Any time a UX decision is being reconsidered

Do not let this review turn into scope expansion. The goal is to sharpen what's planned, not add new feature categories. If a critique surfaces something not on the roadmap, flag as "possible future consideration."

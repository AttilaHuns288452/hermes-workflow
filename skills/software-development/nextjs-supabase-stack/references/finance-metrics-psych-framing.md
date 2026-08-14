# Finance-metric psych framing (momentum panels)

Pattern from CashFlow OS sprint 4: porting the user's Excel "VS Past Month Change" panel
(per-metric MoM % + AVG Change composite) into the dashboard briefing strip.

## The pattern

```
VS LAST MONTH │ Income ▲31% · Profit ▲405% · Spending ▼3.8% · Net Worth ▲0.7% │ Momentum ▲88%
```

- All MoM % computed client-side from existing state (`stats`/`lastMonth` for this-vs-last month,
  trend endpoints for net worth) — NO server/migration change needed when the deltas already exist.
- **Gain framing**: income/profit/net-worth rising = green ▲ (what you *kept*), falling = red ▼.
- **Loss-aversion inversion**: spending is the one metric where rising = RED (warning), falling = green
  (a cut is a win) — `good: false` flag flips the color rule.
- **One dominant number** (Miller's law): the AVG composite renders bigger/bolder as "Momentum" —
  five metrics collapse to one glanceable number.
- **Flat = neutral**: `v === 0` renders muted `—`, never a colored arrow (red "▲ 0.0%" is contradictory).
- **Missing baseline = hidden**: `prev <= 0 → null` (see the negative-baseline pitfall in SKILL.md);
  items filter out, the whole block hides when there's no comparison data at all.
- **Placement**: in the briefing strip (first thing after the greeting), separated by `border-l` —
  the only colored elements in an otherwise quiet strip; numbers are the isolation effect.

## Psych principles (validated by the psychology audit)

- Loss aversion (prospect theory): warnings BEFORE overspend change behavior; framing "what you kept"
  rewards logging.
- Doherty threshold: perceived performance = instant paint (see the persistent-cache section in SKILL.md).
- Miller's law: one composite > five metrics; Von Restorff: color reserved for money + direction.

## Spreadsheet porting approach

When the user says "use my Excel file": read the workbook (`read_file` auto-extracts .xlsx to text),
decode the block layout (each month = one block: income/expense lines, savings grid, asset splits,
"VS Past Month Change" % columns + AVG), then map each column to data the app ALREADY computes.
Honest gaps: `Assets %` needs last-month asset snapshots the app doesn't record — skip or proxy via
net-worth trend rather than adding a migration for a dashboard nicety.

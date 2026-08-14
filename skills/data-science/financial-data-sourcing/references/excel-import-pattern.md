# Excel → app-DB import recipe (validated on a real finance tracker, Aug 2026)

## 1. Find the file
`ls -lt ~/Desktop ~/Downloads ~/Documents | grep -i xlsx` — users keep multiple copies (`file (1).xlsx`, `Documents/` copy). Check ALL copies; they're usually identical but verify (row counts + a sample row).

## 2. Inspect safely (openpyxl, not pandas)
```python
import openpyxl
wb = openpyxl.load_workbook(path, read_only=True, data_only=True)  # data_only = cached formula values
for ws in wb.worksheets: print(ws.title, ws.max_row, ws.max_column)
```
read_only sheets report `None` dims — iterate `ws.iter_rows(values_only=True)` instead.

## 3. Find the real table — occupancy probing
Finance-tracker templates pre-fill thousands of formula rows (e.g. 7,997 rows where only 14 have data; sub-category columns filled with `" "` strings). Don't trust `max_row` or filters — count non-empty cells per column:

```python
col_occ = Counter()
for i, r in enumerate(data):
    ne = [j for j, v in enumerate(r) if v not in (None, "")]
    if ne:
        for j in ne[:6]: col_occ[j] += 1
print(col_occ.most_common(12))
```
The columns with ~14 hits are the real ledger; the ~8000-hit columns are formula noise.

## 4. Column-offset trap
Structure was: `row0 = empty`, `row1 = title`, `row2 = header`, `row3+ = data` — and header columns were `(None, 'Month','Date','Detail','Amount','Category','Sub-Category', …)` so data indices were date=2, amount=4, category=5 (NOT 1/3). Always print the first populated rows with indices before writing extraction code. The pretty sheet ("Transaction Log") and the machine sheet ("Data Transaction Log") may differ in offset — use the machine one.

## 5. Account existence probe (no password needed)
`POST {SUPABASE_URL}/auth/v1/token?grant_type=password` with the email + a bogus password:
- `invalid_credentials` → account EXISTS
- `email not registered` → doesn't exist (user must sign up first)
This works with just the anon key.

## 6. Import SQL (user pastes into Supabase SQL Editor — postgres role bypasses RLS)
Generate a single `DO $$ … $$` block that:
1. Resolves `uid` from `auth.users WHERE email = …` (RAISE EXCEPTION if missing)
2. Resolves/creates the personal entity
3. **Idempotency guard**: `SELECT count(*) FROM transactions WHERE entity_id = eid; IF existing > 0 THEN RETURN;` — re-runs can't double-import
4. Creates categories with `WHERE NOT EXISTS (SELECT 1 FROM categories WHERE entity_id=eid AND name=…)` (no unique constraint on name)
5. `INSERT INTO transactions (entity_id, type, amount, category_id, description, date, status)` — check the schema first: `status` was added by a later migration (`ALTER TABLE transactions ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'approved'`), `amount > 0` CHECK, category_id nullable

Present in chat with the explicit instruction: **"copy the code block, not the file name"** (users have pasted the path before).

## 7. Mapping decisions (state them, don't bury them)
- Excel category "Income" → `income`; everything else → `expense`. Savings/transfer rows (Bank, on hand, BingX) stay expenses in the source ledger — say they can become transfers once accounts exist.
- Rows with a category but no amount ("Income | none") are template noise — drop silently, mention it.
- Create the user's taxonomy as real categories rather than forcing into defaults; income rows can map to a default (e.g. "Investments").
- Save the SQL to `supabase/imports/<date>_<name>.sql` for the record; the chat block is the deliverable.

## 8. In-app import feature (server action + dialog) — production gotchas (Aug 2026)

- **Next.js 16 body limit**: server actions default to a **1MB body** — file uploads 413 with "Body exceeded 1 MB limit" BEFORE the action runs. Config key is `experimental.serverActions.bodySizeLimit: "8mb"` — a ROOT-LEVEL `serverActions` key is rejected in Next 16 ("Unrecognized key" warning). next.config changes need a dev-server restart. (The proxy also warns >10MB via `proxyClientMaxBodySize` — irrelevant once the product cap is 5MB.)
- **Parse**: SheetJS (`xlsx` pkg) reads both .xlsx and .csv — `XLSX.read(await file.arrayBuffer(), {type:'array'})` → first sheet → `sheet_to_json(header:1)` → scan first 10 rows for one containing both 'date' and 'amount' (case-insensitive; the user's tracker buries the header at row 2 after a title row). Handle date cells as Date objects AND Excel serials (`XLSX.SSF.parse_date_code`) — build dates from local parts, never `toISOString` (UTC shifts a day in non-UTC TZs). Normalize amounts: abs, 2dp, accept "$1,234.56" strings.
- **Idempotency**: dedupe on `(date, amount, description)` triples — fetch existing rows first (PostgREST default limit is 1000 — raise to ~10k), skip matches. Re-import after a partial batch failure is then safe.
- **Category auto-create**: collect distinct names, insert missing with `NOT EXISTS` guard, then map name→id. Type derived from first row using it ('income' in category name → income).
- **Result summary vs list refresh**: if the post-import list refresh sets a `loading` gate that swaps in skeletons, the dialog unmounts and the just-computed "Imported N · Skipped M" result vanishes before rendering. Fix: `fetchData(silent = true)` param that skips the skeleton gate.
- **E2E the feature with the user's REAL file** (or a faithful CSV of its rows) — header-scan logic only proves itself against the actual file shape. Expect the dedupe to report "skipped N" when the user already ran the SQL import — that's the feature working, not a bug.
- **Deleting test rows can surface unrelated RLS bugs** (see SKILL.md Supabase section): 403 "new row violates row-level security policy" on DELETE with a truncated table name means a trigger-writing-to-RLS-table problem, not your test script.

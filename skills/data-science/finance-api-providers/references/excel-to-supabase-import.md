# Excel ledger → Supabase import (idempotent SQL recipe)

Worked 2026-08 on a personal-finance tracker (15 sheets, 11MB). User pastes generated SQL into the Supabase SQL Editor (postgres role — bypasses RLS/auth for the import; the app has no import feature, so SQL is the established path).

## Reading the workbook (openpyxl)

```python
import openpyxl
wb = openpyxl.load_workbook(path, read_only=True, data_only=True)  # data_only=True = cached formula values
```

- `read_only=True` + `max_row` reports `None` for big files — iterate instead of trusting dims.
- **Header row hunting**: `list(ws.iter_rows(values_only=True))` then find the row whose cells look like column names. Track templates have title rows ABOVE the header ("TRANSACTION LOG", instructions) and sometimes an empty row 0 — the header can sit at index 1 OR 2. Print the first 15 raw rows (indices visible) once before trusting any column mapping.
- **Formula placeholder rows**: trackers pre-fill thousands of rows with `=IF(...)` formulas. `data_only=True` returns the cached value — often `' '` (space) or `None`. Count occupancy per column (`Counter` over non-empty cells); the real ledger has few rows with values in the DATA columns while 7,000+ rows only touch the formula columns. First pass showed "8 of 7,997 rows have data" — that was correct, not an error.
- Dates arrive as `datetime` objects; amounts as `float`/`int`; strip `₱` formatting (it's in the cell format, not the value).

## The idempotent SQL shape

One `DO $$ ... $$` block that self-resolves every FK and refuses to double-import:

```sql
DO $$
DECLARE uid uuid; eid uuid; cat_x uuid; existing int;
BEGIN
  SELECT id INTO uid FROM auth.users WHERE email = 'user@example.com';
  IF uid IS NULL THEN RAISE EXCEPTION 'No account for ... — sign up first'; END IF;

  SELECT id INTO eid FROM entities WHERE user_id = uid AND type = 'personal' ORDER BY created_at LIMIT 1;
  IF eid IS NULL THEN
    INSERT INTO entities (user_id, type, name) VALUES (uid, 'personal', 'Personal') RETURNING id INTO eid;
  END IF;

  SELECT count(*) INTO existing FROM transactions WHERE entity_id = eid;
  IF existing > 0 THEN
    RAISE NOTICE 'Entity already has % transactions — import skipped.', existing;
    RETURN;
  END IF;

  -- categories: create-if-missing by (entity_id, name)
  INSERT INTO categories (entity_id, name, type, is_default)
  SELECT eid, 'Subscriptions', 'expense', false
  WHERE NOT EXISTS (SELECT 1 FROM categories WHERE entity_id = eid AND name = 'Subscriptions');
  SELECT id INTO cat_x FROM categories WHERE entity_id = eid AND name = 'Subscriptions';

  INSERT INTO transactions (entity_id, type, amount, category_id, description, date, status) VALUES
    (eid, 'expense', 500, cat_x, 'Gym', '2025-06-07', 'approved');
  RAISE NOTICE 'Imported N transactions into entity %', eid;
END $$;
```

Key points:
- Check the LIVE schema first (`supabase/migrations/*.sql` may lag; `ALTER TABLE ... ADD COLUMN IF NOT EXISTS status` in later migrations — verify with a PostgREST probe or grep for ALTERs).
- Wrap the whole thing in `DO $$` so a failed mid-import leaves nothing partial (single implicit transaction).
- `RAISE NOTICE` at the end gives the user a visible success line.
- Guard clause on existing-row count = the idempotency (re-paste is a no-op, not a duplicate).

## Handoff rules (user runs it)

- **"Copy the code block, not the file name"** — the user's known failure is pasting the file PATH. Save the SQL to `supabase/imports/<date>_<name>.sql` for the record, but paste the FULL block in chat.
- After "done": verify via PostgREST probe (`/rest/v1/transactions?select=...` with a real user JWT, or as the user through the app UI).

## Excel import side-notes

- Windows Python: the shell `python` may be a venv without pip — use the system interpreter explicitly (`C:\Users\YOUR_USERNAME\AppData\Local\Programs\Python\Python311\python.exe`) and `python -m pip install openpyxl`.
- Write inspection scripts to a project-relative path and `cd` first — absolute `/c/...` args to `python file.py` break (MSYS path mismatch), and `node` from the repo root with a relative filename avoids the `C:\c\Users\...` module-not-found trap.

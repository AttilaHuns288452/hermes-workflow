# Supabase RLS migration security checklist

Verified against two ECC-review BLOCKERs on cashflow-os (approval-workflow RLS,
ERP views). Run every migration through this BEFORE handing it to the user.

## 1. Views bypass RLS by default — HIGH/cross-tenant leak

Plain `CREATE VIEW` in Supabase is security-definer: `authenticated` has SELECT
on it by default and **RLS on base tables never runs** → any logged-in user can
read every entity's rows (customers, invoice numbers, amounts).

Always:
```sql
CREATE OR REPLACE VIEW outstanding_receivables
WITH (security_invoker = true) AS
SELECT ... FROM invoices i LEFT JOIN customers c ...
```
`security_invoker` (PG15+) makes the view run with the querying user's RLS.

## 2. Role-based features are inert without matching RLS policies

App-layer role gates are useless when the DB denies the reads they need.
Symptom pattern (caught twice):
- `getCurrentStaffRole()` queries `entities` then `staff` — both owner-only
  RLS → non-owners resolve to `null` → approve buttons hidden AND every write
  RLS-denied → feature completely dead for everyone except the owner.
- The UI even hides submit-for-approval from the owner → pending unreachable.

Fix in the SAME migration as the feature — one helper + per-table policies:

```sql
CREATE OR REPLACE FUNCTION public.current_staff_role(target_entity UUID)
RETURNS TEXT LANGUAGE sql STABLE SECURITY DEFINER SET search_path = public AS $$
  SELECT CASE
    WHEN e.user_id = auth.uid() THEN 'owner'
    ELSE (SELECT s.role FROM public.staff s
          WHERE s.entity_id = e.id AND s.user_id = auth.uid() LIMIT 1)
  END
  FROM public.entities e
  WHERE e.id = target_entity
$$;

DO $$ BEGIN
  CREATE POLICY "staff view transactions" ON transactions FOR SELECT
    USING (public.current_staff_role(transactions.entity_id) IS NOT NULL);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
```

Owner policies stay `EXISTS (SELECT 1 FROM entities e WHERE e.id = <t>.entity_id AND e.user_id = auth.uid())`.

## 3. Child/line tables need their own staff-read policies

`invoice_lines` / `po_lines` / `payroll_lines` reference parents via FK but
have NO entity_id column — a parent policy does not cover them. Staff see
headers with no lines (line fetches 404). Join through the parent:

```sql
CREATE POLICY "staff view invoice_lines" ON invoice_lines FOR SELECT
  USING (EXISTS (SELECT 1 FROM invoices i WHERE i.id = invoice_lines.invoice_id
    AND public.current_staff_role(i.entity_id) IS NOT NULL));
```

Also gate INSERTs through the parent-entity join so cross-entity line inserts
are blocked even though FKs bypass RLS.

## 4. Money columns: CHECK constraints + server-side validation

- `CHECK (subtotal >= 0 AND discount >= 0 AND tax >= 0 AND total >= 0)` on
  invoice-like tables; `CHECK (amount > 0)` on payments/claims.
- Server actions must validate and REJECT (never silently filter) invalid
  lines: `Line N: description required / quantity must be > 0 / unit price
  cannot be negative` — silent filtering corrupts money math with no error.
- Round to 2dp in the SAME place (line totals AND header total) or a two-line
  invoice can drift by a cent (`Math.round(x*100)/100`).
- `paid` transitions only from `sent` (explicit transition map); never set
  `paid_amount = total` on a draft.

## 5. Idempotency pattern (user re-runs migrations by hand)

No CLI/PAT → the user pastes into Supabase SQL Editor. Re-run safety is
mandatory:
- `CREATE TABLE IF NOT EXISTS`, `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`,
  `CREATE INDEX IF NOT EXISTS`
- Policies inside `DO $$ BEGIN ... EXCEPTION WHEN duplicate_object THEN NULL; END $$`
- `CREATE OR REPLACE VIEW` + `WITH (security_invoker = true)` (re-runnable)
- Prereq comments (`-- Prereq: 001-011 applied`), helper function is
  `CREATE OR REPLACE FUNCTION` (idempotent).

## 6. Post-apply verification

After the user reports success, probe from the API with the anon key:

```bash
for t in customers suppliers invoices invoice_lines; do
  curl -s -o /dev/null -w "$t:%{http_code}\n" \
    "$URL/rest/v1/$t?select=id&limit=1" -H "apikey: $KEY" -H "Authorization: Bearer $KEY"
done
```
200 = table + RLS live (anon with no session gets RLS-enforced empty results,
not 401/404). A 404/PGRST205 means the migration didn't land.

## 7. App-layer rules that pair with RLS

- Server actions: derive status/submitted_by server-side; never trust client
  `status` (approvers → approved, staff → pending, non-member → error).
- Conditional writes for concurrent review: `UPDATE ... .eq('id', id)
  .eq('status','pending')` + check returned rows → "Already reviewed".
- No self-approval: reject when `submitted_by === caller's staff id`.
- Entity-scope EVERY write with `.eq('entity_id', entityId)` — RLS-filtered
  updates otherwise silently no-op (success, 0 rows).
- Pre-check FK parents belong to the entity before insert (FK checks bypass
  RLS): `SELECT id FROM customers WHERE id = $1 AND entity_id = $2`.
- Retry once on unique-violation code `23505` when generating sequential
  invoice/PO numbers (count+1 races).

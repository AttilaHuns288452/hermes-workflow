# Playwright + Supabase verification snippets

All proven in session (cashflow-os, Next.js 16 + @supabase/ssr, Supabase hosted).

## 1. Extract user JWT from the auth cookie (supabase-ssr)

Session is in a cookie, NOT localStorage (localStorage keys are often empty).

```js
const token = await page.evaluate(() => {
  const m = document.cookie.match(/sb-[a-z0-9-]+-auth-token=([^;]+)/);
  const v = m[1].replace(/^base64-/, "").replace(/-/g, "+").replace(/_/g, "/");
  return JSON.parse(atob(v)).access_token;
});
```

## 2. Verify DB rows directly via PostgREST (from inside the page)

```js
const res = await page.evaluate(async ([url, key, token]) => {
  const H = { apikey: key, Authorization: "Bearer " + token };
  const r = await fetch(url + "/rest/v1/transactions?select=status,description&status=eq.pending", { headers: H });
  return r.json();
}, [ENV_URL, ENV_KEY, token]);
```

Read URL + anon key in Node from `.env.local` (values are quoted — strip quotes), pass into `page.evaluate`. UI "PASS" ≠ row exists — always cross-check.

## 3. Live-schema guard (graceful skip when migrations missing)

```js
const schema = await page.evaluate(async ([url, key]) => {
  const token = /* §1 */;
  const H = { apikey: key, Authorization: "Bearer " + token };
  const r = await fetch(url + "/rest/v1/information_schema.columns?table_name=eq.loans&select=column_name", { headers: H });
  return r.json(); // [{column_name:...}] or null on 404
}, [ENV_URL, ENV_KEY]);
```

PostgREST exposes `information_schema` — use it to detect whether new tables/columns are live before running feature E2E.

## 4. Migration application paths (no DDL via code)

Tried and failed: pooler with service-role key as password (`FATAL: password authentication failed`), `https://<ref>.supabase.co/pg/query` (removed: `{"error":"requested path is invalid"}`). Working paths:
- Supabase Dashboard → SQL Editor (paste migration SQL)
- DB password (Settings → Database → reset) + psycopg2/psql via pooler: `aws-0-<region>.pooler.supabase.com:6543`, user `postgres.<ref>`, `sslmode=require`
- Management API with PAT: `POST https://api.supabase.com/v1/projects/<ref>/database/query`

Keep migrations in `supabase/migrations/NNN_*.sql` as source of truth regardless (repo ≠ live; live can drift ahead).

## 5. Radix Select (shadcn) safe automation sequence

```js
// WRONG: page.locator('[name="category_id"]').click()  — hidden native select, does nothing
// WRONG: page.keyboard.press("Escape") after opening — closes the whole Dialog
const trigger = page.getByRole("combobox").nth(1); // nth carefully; count comboboxes first
await trigger.click();
await page.waitForTimeout(600); // let the listbox animation settle
await page.locator('[role="option"]').first().click();
await page.waitForTimeout(600);
// verify: hidden select now has a value — inputValue() on [name="..."]
```

Radix closes the listbox on option select; if it stays open, the next click lands on the portal overlay (force-click does NOT help — it clicks the topmost element at those coordinates).

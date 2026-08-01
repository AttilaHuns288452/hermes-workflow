# Supabase CRUD Anti-Patterns to Avoid in Delegated Code

When delegating Supabase frontend code to DeepSeek V4 Flash, include these anti-patterns in the briefing to prevent slow apps.

## Anti-Pattern 1: Sequential Inserts for Seed/Batch Data

**Bad (17 round trips):**
```js
for (const name of names) {
  await supabase.from('roles').insert({ name });
}
```

**Good (1 round trip):**
```js
const rows = names.map((name, i) => ({ name, position: i }));
await supabase.from('roles').insert(rows);
```

Supabase JS client accepts arrays for batch insert. Always batch.

## Anti-Pattern 2: Full Refetch After Every CRUD Operation

**Bad (2 network calls per click):**
```js
async function moveItem(id, roleId) {
  await supabase.from('members').update({ role_id: roleId }).eq('id', id);
  await fetchAll();  // ← re-fetches EVERYTHING
  render();          // ← rebuilds entire DOM
}
```

**Good (optimistic local update, 0 extra fetches):**
```js
async function moveItem(id, roleId) {
  await supabase.from('members').update({ role_id: roleId }).eq('id', id);
  const item = members.find(m => m.id === id);
  if (item) item.role_id = roleId;
  render();
}
```

Only call `fetchAll()` on initial page load. All subsequent operations update local state arrays and re-render.

## Anti-Pattern 3: No Loading State

Always show a loading spinner while the initial fetch is in flight:
```html
<div id="loading"><div class="spinner"></div>Loading from Supabase…</div>
```
Hide it in the first `render()` call after `fetchAll()` completes.

## Supabase Management API (for automated setup)

When the user wants you to set up Supabase programmatically:

```bash
# List projects
curl -sH "Authorization: Bearer $SUPABASE_MCP_TOKEN" https://api.supabase.com/v1/projects

# Get API keys (anon + service_role)
curl -sH "Authorization: Bearer $SUPABASE_MCP_TOKEN" "https://api.supabase.com/v1/projects/[id]/api-keys"

# Run SQL via Management API
curl -sX POST "https://api.supabase.com/v1/projects/[id]/database/query" \
  -H "Authorization: Bearer $SUPABASE_MCP_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "CREATE TABLE..."}'
```

### CRITICAL: The `/database/query` endpoint only runs ONE SQL statement
Multi-statement SQL files (migrations) must be split and run sequentially. The endpoint returns 201 for DDL, but only the first statement executes. Split with Python:

```python
import re, requests

sql = open("migration.sql").read()
# Split on semicolons (not inside $$...$$ blocks)
stmts = [s.strip() for s in re.split(r';(?=\s*(?:--.*)?$)', sql, re.MULTILINE) if s.strip()]

for stmt in stmts:
    resp = requests.post(
        f"https://api.supabase.com/v1/projects/{ref}/database/query",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"query": stmt},
    )
    # 200/201 = OK, 400 = "already exists" (idempotent, safe to ignore for CREATE OR REPLACE)
```

**Pitfall:** `$$` blocks (PL/pgSQL function bodies) can contain internal semicolons that the split regex breaks. Write function bodies as a single `CREATE OR REPLACE FUNCTION ... $$ ... $$ LANGUAGE plpgsql` statement — don't split them.

Env vars: `SUPABASE_MCP_TOKEN` (personal access token), `LMS_SUPABASE_DB_PASSWORD` (DB password).

## Anti-Pattern 4: Multiple Server Actions from One Page (N+1 Auth Lookups)

**Bad (8 parallel actions, each does auth.getUser() + entity lookup):**
```tsx
// DashboardPage calls 8 server actions — each one independently:
// 1. createClient() → 2. auth.getUser() → 3. entities.select() → 4. actual query
const [s, nw, t, li, sp, lm, cur, nwt] = await Promise.all([
  getMonthlyStats(entityId),    // auth lookup 1
  getNetWorth(entityId),        // auth lookup 2
  getMonthlyTrend(entityId),    // auth lookup 3
  // ... 5 more
]);
// 8 auth calls + 8 entity lookups = 16 Supabase round trips
```

**Good (1 merged action, 1 round trip):**
```ts
// One server action that computes everything in a single request
export async function getDashboardData() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser(); // once
  
  // Fetch all tables in one Promise.all
  const [{ data: txns }, { data: assets }, { data: debts }] = await Promise.all([
    supabase.from("transactions").select("*").eq(/*...*/),
    supabase.from("assets").select("*").eq(/*...*/),
    supabase.from("debts").select("*").eq(/*...*/),
  ]);
  
  // Compute everything server-side, return single object
  return { stats, netWorth, trend, spending, /*...*/ };
}
```

Then dashboard calls one action: `const data = await getDashboardData();`

**Intermediate fix (if merging is too heavy):** Wrap `getEntity()` in `React.cache()`:
```ts
import { cache } from "react";
export const getEntity = cache(async () => { /*...*/ });
```
This memoizes the auth+entity lookup per request. 8 parallel calls share 1 result.
Still 8 DB queries though — merging is the full fix.

## Anti-Pattern 5: Recharts Type Errors from `PieLabel` / `Tooltip formatter`

Recharts types are strict in TS strict mode. Two recurring fixes:

```tsx
// Pie label: percent is optional in PieLabelRenderProps
<Pie label={(p: any) => `${p.name} ${((p.percent ?? 0) * 100).toFixed(0)}%`}

// Tooltip formatter: value is ValueType | undefined
<Tooltip formatter={(v: any) => `$${Number(v).toLocaleString()}`} />
```

Use `any` casts on the callback params — Recharts types don't narrow properly.

When a subagent times out on a large scaffold/build task (40+ files), the SHORTEST path to done is:

1. **Check what was written:** `find src -type f | sort` — see which files exist
2. **Do NOT re-dispatch.** A second subagent will repeat the same work and time out again.
3. **Orchestrator fills remaining gaps directly** — write the missing feature components, route pages, and middleware. The subagent handled the complex UI primitives (shadcn components); the orchestrator handles the thin wiring (route pages, layout wrappers).
4. **Fix type errors from partial build** — the subagent's code may have minor TS issues. Fix inline (recharts types, null coalescing).
5. **Build + deploy** — once the build passes, push and deploy immediately.

This pattern saved ~10 minutes vs re-dispatching and produced a complete build in 2 extra orchestrator turns.

**Key insight:** Subagents are best for complex, self-contained units (UI primitives, auth flows, chart components). For wiring/glue code (route pages, middleware, layout shells), the orchestrator is faster.

When delegating tasks that involve Supabase credentials:
- NEVER print keys to stdout — pipe directly via sed or env vars
- Use `sed -i "s|PLACEHOLDER|$VALUE|g" file.html` to inject keys
- The final summary must NOT contain actual key values
- Temp files with keys should be cleaned up after use

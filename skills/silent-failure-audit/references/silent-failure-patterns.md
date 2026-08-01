# Silent Failure Pattern Catalog

Concrete patterns found in a Next.js + Supabase codebase audit. Grep queries and code examples for each.

---

## Pattern 1: Unchecked DB Mutations

### Detection

```bash
# Find mutations where no error destructuring happens
grep -rn "await supabase" src/ --include="*.ts" --include="*.tsx" | grep -v "const.*error" | grep -v "// ponytail"
```

### Example (bad)

```typescript
await supabase.from("accounts").delete().eq("id", id);
return { success: true };  // ← success even if delete failed
```

### Example (good)

```typescript
const { error } = await supabase.from("accounts").delete().eq("id", id);
if (error) return { error: error.message };
return { success: true };
```

### Impact
🔴 HIGH — Data silently lost. User sees "saved" when it wasn't.

---

## Pattern 2: `.single()` Without Error Check

### Detection

```bash
grep -rn "\.single()" src/ --include="*.ts" --include="*.tsx"
```

### Example (bad)

```typescript
const { data } = await supabase.from("entities").select("currency").eq("id", entityId).single();
return data?.currency || "USD";
// On error (no rows, multiple rows, DB failure) → `data` is null → silently returns "USD"
```

### Example (good)

```typescript
const { data, error } = await supabase.from("entities").select("currency").eq("id", entityId).single();
if (error || !data) return { error: error?.message || "Entity not found" };
return data.currency;
```

### Impact
🔴 HIGH if downstream logic depends on the result. 🟡 MEDIUM if a safe fallback exists (but still hides the underlying error).

---

## Pattern 3: `.then()` Without `.catch()`

### Detection

```bash
# Find promise chains in React components
grep -rn "\.then(" src/ --include="*.tsx"
```

### Example (bad)

```typescript
useEffect(() => {
  Promise.all([getAssets(), getDebts()]).then(([a, d]) => {
    setAssets(a);
    setDebts(d);
    setLoading(false);  // ← never fires if either promise rejects
  });
}, []);
// Component shows infinite loading spinner
```

### Example (good)

```typescript
useEffect(() => {
  Promise.all([getAssets(), getDebts()])
    .then(([a, d]) => { setAssets(a); setDebts(d); })
    .catch((e) => { console.error("Failed to load balance sheet", e); setError("Failed to load"); })
    .finally(() => setLoading(false));
}, []);
```

### Impact
🔴 HIGH — Component never finishes loading. Infinite spinner with no error message.

---

## Pattern 4: Client Handlers Ignoring Server Action Errors

### Detection

```bash
# Find client handlers that call server actions
grep -rn "await.*Action\|await create\|await delete\|await update" src/features/*/components/ --include="*.tsx"
```

### Example (bad)

```typescript
const handleAdd = async (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault();
  await createAsset({ name, type, value });  // return value ignored
  onOpenChange(false);  // dialog closes even if createAsset failed
};
```

### Example (good)

```typescript
const handleAdd = async (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault();
  const result = await createAsset({ name, type, value });
  if ("error" in result) {
    setSubmitError(result.error);
    return;
  }
  onOpenChange(false);
};
```

### Impact
🟡 MEDIUM — Dialog/form closes, user sees no feedback that the operation failed.

---

## Pattern 5: Missing `error` State in Async Components

### Detection

```bash
# Find components with loading state but no error state
grep -rn "loading\|Loading" src/features/*/components/ --include="*.tsx" | grep -v "error\|Error"
```

### Example (bad)

```typescript
function BalanceSheet() {
  const [loading, setLoading] = useState(true);
  // No error state!
  
  useEffect(() => {
    fetchData().then(() => setLoading(false));  // No .catch()
  }, []);
  
  if (loading) return <div>Loading...</div>;  // ← hangs forever on reject
  return <div>...</div>;
}
```

### Example (good)

```typescript
function BalanceSheet() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    fetchData()
      .catch((e) => setError("Failed to load data"))
      .finally(() => setLoading(false));
  }, []);
  
  if (loading) return <div>Loading...</div>;
  if (error) return <div className="text-red-500">{error}</div>;
  return <div>...</div>;
}
```

### Impact
🔴 HIGH if no `.catch()`/`.finally()` — infinite loading. 🟡 MEDIUM if error is logged but not displayed.

---

## Pattern 6: Empty `catch` Blocks

### Detection

```bash
# Find catch blocks that do nothing
grep -rn "catch\s*(" src/ --include="*.ts" --include="*.tsx" -A1 | grep -E "^\s*catch.*\{\s*\}\s*$"
```

These are rare in well-maintained codebases but catastrophic when present — they make debugging impossible.

### Impact
🔴 HIGH — All errors disappear without a trace.

---

## Pattern 7: State Update in Unmounted Component

### Detection

```bash
# Look for async operations in useEffect without cleanup
grep -rn "useEffect" src/features/*/components/ --include="*.tsx" -A20 | grep -E "\.then\(|await"
```

### Problem
If a component unmounts before the async operation completes, calling `setState` or `setLoading(false)` on the unmounted component is a no-op in React 18+ (warning in dev) but still silently breaks the expected flow.

### Mitigation
Use an `aborted` / `mounted` ref, or prefer async/await with try/finally inside the effect.

---

## Severity Summary

| Pattern | Severity | What's at stake |
|---------|----------|----------------|
| Unchecked mutation | 🔴 HIGH | Silent data loss |
| `.single()` error ignored | 🔴 HIGH | Wrong fallback data, bad UX |
| `.then()` no `.catch()` | 🔴 HIGH | Infinite loading, broken page |
| Empty catch block | 🔴 HIGH | All errors invisible |
| Handler ignores error | 🟡 MEDIUM | Operation "succeeds" on screen, fails in DB |
| Missing error state | 🟡 MEDIUM | User stuck on loading spinner |
| Unmounted setState | 🟢 LOW | Dev warnings, stale updates |

## Tooling

For grepping across large codebases:

```bash
# Ripgrep is faster for large projects
rg "await supabase" src/ --include="*.ts" --include="*.tsx" | rg -v "const.*error"

# Search files tool (if ripgrep not available)
search_files(target='content', pattern='await supabase', file_glob='*.ts')
```

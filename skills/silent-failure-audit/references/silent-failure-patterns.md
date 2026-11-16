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

## Pattern 8: Load Error Rendered as Empty State

### Detection
Find loaders where the error path clears/ignores the data and the empty branch renders unconditionally:

```bash
rg "setItems\(\[\]\)|setMessages\(\[\]\)" src/ -A3 -B3
```

### Example (bad)

```typescript
load().then(({ data, error }) => {
  if (error) { setItems([]); return; }  // ← failure becomes "No messages yet"
  setItems(data);
});
```

### Example (good)

```typescript
load().then(({ data, error }) => {
  if (error) { setLoadError(error.message); return; }  // distinct error state + retry
  setItems(data ?? []);
});
// render: error ? <InlineError onRetry={load}/> : items.length ? <List/> : <EmptyState/>
```

### Impact
🔴 HIGH — User cannot tell "nothing here" from "load failed"; acts on false emptiness.

---

## Pattern 9: Input Cleared Before Mutation Resolves

### Detection
Compare the draft-clearing call site against the await of the send/create mutation:

```bash
rg "setBody\(''\)|setDraft\(''\)|reset\(\)" src/ -B5
```

### Example (bad)

```typescript
setBody('');          // cleared first
await sendChat(body); // if this fails the typed text is gone
```

### Example (good)

```typescript
const ok = await sendChat(body);
if (ok?.error) { setSendError(ok.error); return; }  // body preserved for retry
setBody('');
```

### Impact
🟡 MEDIUM — Failed send/submit silently destroys the user's typed input.

---

## Pattern 10: Revalidation Clobbers User Selection

### Detection
Effects whose dependency array includes a visibility/refresh trigger AND re-initialize selection state:

```bash
rg "useEffect" src/ -A6 | rg "setVisible|visible|refresh"
```

### Example (bad)

```typescript
useEffect(() => { setDay(firstAvailableDay); }, [visible]);  // tab-return resets the user's chosen day
```

### Example (good)

```typescript
useEffect(() => {
  if (!day) setDay(firstAvailableDay);  // initialize once, never overwrite user choice
  refetch();                            // revalidation refreshes DATA, not selection
}, [visible]);
```

Same rule for cached navigation state vs the URL: on money/stateful deep links the URL id is
authoritative — a stale React Router `location.state` must never select which record is fetched or
charged; fall back to it only when the URL carries no id.

### Impact
🔴 HIGH on money/stateful routes (wrong record acted on). 🟡 MEDIUM otherwise (selection jumps).

---

## Pattern 11: Unguarded Background Loop Dies Permanently

### Detection
Find every fire-and-forget periodic worker and check whether the loop body is inside a try/catch:

```bash
rg "setInterval\(|while \(true\)|while true do|schedule\.repeat|@Scheduled" src/ -A2
```

### Example (bad)

```typescript
setInterval(() => {
  for (const job of dueJobs) process(job); // one throw and the interval is dead forever
}, 60_000);
```

### Example (good)

```typescript
const tick = () => {
  try { for (const job of dueJobs) process(job); }
  catch (e) { log.error("worker tick failed", e); }   // keep the loop alive
};
setInterval(tick, 60_000);
tick();
```

### Impact
🔴 HIGH — No crash, no error surfaced. That subsystem silently stops for the process's lifetime: no notifications, no payouts, no cleanup. The classic tell is "it worked for an hour and then never again".

---

## Pattern 12: Counter That Nobody Reads

### Detection
For each persisted/accumulated stat, grep for a READER (not just the writer):

```bash
rg "friendship|streak|mastery|reputation" src/ --stats | head
# then, per key, count sites that COMPARE or BRANCH on it
rg "(friendship|streak|mastery) *(>=|>|<|\? |&&)" src/
```

### Example (bad)

```typescript
user.pet.friendship += 2;   // written every feed
// no threshold check, no reward, no display gate anywhere
```

### Example (good)

```typescript
const reached = Math.floor(f.points / THRESHOLD);
if (reached > f.claimed) { grant(reached - f.claimed); f.claimed = reached; }
```

### Impact
🟡 MEDIUM — An unimplemented feature disguised as a mechanic: the UI shows a bar that fills and means nothing. Same for a step the loop never reaches. Grep the reader, every time.

---

## Pattern 13: Cross-Cutting Init Trapped in a Lazy Path

### Detection
List modules that create process-wide singletons (audio, telemetry, socket, error reporter) and check who imports them — if the only importer is a lazily-mounted route/menu, the layer does not exist until a user visits it:

```bash
rg "^import .*(audio|telemetry|socket|init)" src/ -l
rg "lazy\(|dynamic\(|import\(" src/ -A1 | rg -B1 "audio|telemetry|socket"
```

### Example (bad)

```typescript
// settings-panel.tsx  ← only importer
import { audio } from "@/lib/audio";
audio.start();   // nobody hears anything until Settings is opened
```

### Example (good)

```typescript
// app-shell.tsx / root layout — the always-loaded entry
import { audio } from "@/lib/audio";
audio.start();   // idempotent start; panels only read state
```

### Impact
🟡 MEDIUM — Feature works perfectly in the one path you tested and is absent everywhere else. Same shape as a load-time `FindFirstChild` scan that races the data it is looking for: wait for the resource, then also hook its subsequent additions.

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
| Load error → empty state | 🔴 HIGH | Failure indistinguishable from "nothing here" |
| Input cleared pre-mutation | 🟡 MEDIUM | Typed input silently destroyed on failure |
| Revalidation resets selection | 🔴 HIGH on money/stateful routes | Wrong record acted on |
| Unguarded loop death | 🔴 HIGH | Whole subsystem stops forever, no error |
| Counter with no reader | 🟡 MEDIUM | UI mechanic that means nothing |
| Init in a lazy path | 🟡 MEDIUM | Feature absent outside the one path tested |

## Tooling

For grepping across large codebases:

```bash
# Ripgrep is faster for large projects
rg "await supabase" src/ --include="*.ts" --include="*.tsx" | rg -v "const.*error"

# Search files tool (if ripgrep not available)
search_files(target='content', pattern='await supabase', file_glob='*.ts')
```

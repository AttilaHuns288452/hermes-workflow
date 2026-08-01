# Code Quality Audit — Real-World Example

Quality-focused audit of a Next.js 16 / Supabase / Tailwind v4 / shadcn finance app (cashflow-os). This is the "micro-level code quality" dimension — after the cross-layer drift checks pass.

## Finding Inventory

| Category | Count | Key Signal |
|----------|-------|------------|
| `as any` casts | 12 | 10 of 12 from untyped `.select("..., categories(name)")` joins |
| Empty catch blocks | 1 | `} catch {` in date formatter — harmless but uncatchable |
| `.then()` without `.catch()` in effects | 10+ | Every component that fetches currency setting |
| `catch (e: any)` | 1 | API route — unnecessary annotation |
| Unused imports | 1 | `CardHeader, CardTitle` from shadcn card |
| One-letter state vars | 1 component | `[n, setN]`, `[t, setT]`, `[b, setB]` in `AddAccountForm` |
| Auth route flash | 1 | Root page redirects to `/dashboard` without auth check |

## Notable Examples

### as any — The Joined-Data Epidemic

```ts
// actions.ts — 10 files do this:
const cat = (t as any).categories?.name || "Other";
```

Root cause: `.select("type, amount, categories(name)")` in Supabase returns `{type, amount, categories: {name: string} | null}`, but components destructure it as the base type plus a manual `(t as any)` access. Fix in one place: a `WithCategory<T>` helper type.

### useEffect .then() Without .catch()

```tsx
// Every component that reads a setting:
useEffect(() => { getCurrencySetting().then(setCurrency); }, []);
// If getCurrencySetting() rejects — silent failure, state stays "USD"
```

Low-risk because `getCurrencySetting()` has internal try/catch, but the pattern propagates. Future refactors that remove the internal try/catch create invisible bugs.

### Unused Import Artifact

```tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
// CardHeader and CardTitle never appear in the JSX — copy-paste residue
```

### Auth Root Path

```tsx
// page.tsx — always redirects, no auth guard:
export default function Home() {
  redirect("/dashboard");
}
```

Result: unauthenticated users see a loading spinner → dashboard tries to fetch → `getEntity()` returns `{ error: "Not authenticated" }` → component shows error. Works, but flashes the loading state first. A `middleware.ts` redirect at the framework level would skip the flash.

## What the Example Teaches

1. **`as any` counts are a health metric** — >5 in a single-feature app means the type system isn't being trusted.
2. **Chained `.then()` without `.catch()` is the most common cheap fix** — 10+ files can be hardened in one pass with a regex replace.
3. **One-letter state names in form components** are grep-hostile. Code search for "search for the setter of `setN`" returns noise from all files.
4. **Auth flash** reveals when middleware is missing — not a bug, but a UX roughness that compounds with slow connections.

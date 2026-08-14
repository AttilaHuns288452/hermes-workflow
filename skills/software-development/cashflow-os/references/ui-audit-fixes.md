# UI/UX audit fix rounds (MiMo-style vision audit) — 2026-08-05

How the round runs: an audit list arrives as numbered one-line fixes; the one-line fix IS the spec.
Apply surgically, per-file ownership, no commits. Quality bar: `npx tsc --noEmit` && `npm run build` green, no unused imports.

## Grep-first N/A discipline

Items can reference UI that doesn't exist in the current tree (stale build, already-fixed, or never-shipped).
This round: AppShell "Rendering..." label and a login `<hr>` divider were both ABSENT (`grep -rni "endering" src/` → 0 hits; LoginForm footer already used `border-t`).
Mark N/A with evidence instead of inventing a fix. Parent orchestrators expect per-fix accounting (12 fixed / 2 N/A).

## Skeleton loading recipe (replaced bare `Loading...` divs on 4 pages)

Primitive: `src/components/ui/skeleton.tsx` — `<Skeleton className>` = `animate-pulse rounded-md bg-fg-soft` (already animate-pulse; pass `rounded-xl` for card blocks).

Layout mirrors the final page, all pages share the shape:

```tsx
if (loading)
  return (
    <div className="space-y-6 p-4 md:p-6" aria-busy="true">
      <span className="sr-only">Loading</span>
      <div className="space-y-2">
        <Skeleton className="h-3 w-24" />
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-4 w-64" />
      </div>
      <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4"> {/* final cols; h-28 rounded-xl per card */}
        {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-28 rounded-xl" />)}
      </div>
      <div className="rounded-xl border border-border bg-card p-5 shadow-card">
        <Skeleton className="h-4 w-32" />
        <Skeleton className="mt-2 h-6 w-48" />
        <div className="mt-5 space-y-3">
          {Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-9 w-full" />)}
        </div>
      </div>
    </div>
  );
```

- Grid skeletons reuse the FINAL grid classes (sm:grid-cols-2 lg:grid-cols-4 / md:grid-cols-3 / md:grid-cols-2) so layout doesn't jump.
- `aria-busy="true"` + sr-only, standardized copy: plain "Loading" (was "Loading portfolio..." etc.).
- Table-card skeleton = real card chrome (`rounded-xl border border-border bg-card p-5 shadow-card`) + header bars + `h-9 w-full` row bars.

## Per-fix classes (this round)

- **Stat-card icon chips**: `chipClasses` maps (`bg-green-soft text-green` etc.) render icons in colored filled circles = pill pattern → plain `<span className="inline-flex h-8 w-8 items-center justify-center text-muted-foreground">` (add `text-accent` for the primary card). Delete the chipClasses map; keep green/red ONLY on the value text. `colorClasses` (text-*) stays.
- **Muted-tint strips** (`bg-muted/30 border border-border/60` briefing strips, net-worth mini-panels): restyle as standard card surface — `border bg-card shadow-card rounded-xl px-5 py-3.5`.
- **Chart empty states**: all-zero weekly grid rendered seven '—' dashes → muted copy ("No spending recorded this week") + `Link href="/transactions"` ("Add a transaction") inside the card, header kept. Keep the sr-only EEEE full-day names.
- **Ambiguous day labels**: `cell.day[0]` single letters → date-fns `format(new Date(date + 'T00:00:00'), 'EEE')` (Mon..Sun); date-fns v4, parse with T00:00:00 (see SKILL.md date-fns notes).
- **Uneven footers**: flex justify-between stat lines → `grid grid-cols-3` + `text-center` per item.
- **Below-the-fold primary actions**: QuickAdd form sat after the widget rows → move directly after the stat-card row, before the chart grids.
- **BYOK key input** (AiSettingsCard): real `Input` (border/bg come from ui/input — don't restyle the component), placeholder "Enter your API key…" (hasKey → "•••••••• (leave blank to keep)"), `autoComplete="off"`, Save button already wired to `saveAiSettings` — verify the action name in `@/features/settings/actions`, never change server-action contracts. Key input gated by `provider !== "builtin"`.

## Settings page anatomy (src/app/settings/page.tsx — client component)

- **Profile card**: email via client `createBrowserClient(NEXT_PUBLIC_SUPABASE_URL!, NEXT_PUBLIC_SUPABASE_ANON_KEY!).auth.getUser()` (exact AppShell pattern — no new server action needed); active entity via existing `getUserEntities()` from `@/features/business/actions` (returns `id, name, type`) matched against localStorage `selectedEntity`. Rows: `flex items-center justify-between border-b border-border pb-3` label/value.
- **Appearance card**: Light/Dark segmented buttons (mirror AppShell's Personal|Business switch classes: active `bg-accent-soft text-accent`, else `text-muted-foreground hover:bg-fg-soft`, `aria-pressed`). Toggle = `document.documentElement.classList.toggle('dark', next)` + localStorage `theme`; init state from classList in useEffect (hydration-safe).
- **Data & Privacy card**: Sign out → existing `signOut()` from `@/features/auth/actions` + `router.push('/login')` (guard with try/catch — failed signOut shouldn't trap the user). CSV: there is NO dedicated CSV route — exports are client buttons / a server action on `/reports`; link to `/reports` ("Statements & CSV exports").
- safeGet/safeSet localStorage try/catch helpers: copy from AppShell (`src/components/layout/AppShell.tsx`), don't redefine.
- Section-card chrome: mono eyebrow + `font-display text-lg font-semibold` h2 + `text-sm text-muted-foreground` blurb + `pt-6` CardContent.

## Process pitfalls

- **git diff noise**: `git diff --stat` vs HEAD includes the pre-existing UNCOMMITTED sprint changes — a huge stat (600+ lines on a file you touched 3 lines of) does NOT mean you corrupted line endings. Confirm with `git log -1` + `git status --short`; `git diff --ignore-cr-at-eol` separates CRLF churn from real edits. Never `git add -A` in a shared sprint.
- Large `npm run build` route table at the end = success; check exit code, not just output tail.

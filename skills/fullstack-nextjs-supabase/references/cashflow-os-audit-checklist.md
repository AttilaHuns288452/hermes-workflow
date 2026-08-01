# CashFlow OS Audit Checklist

Reusable audit for any Next.js + Supabase finance app. Run these greps
after a batch of agent changes to catch the most common regression classes.

## 1. Hardcoded currency symbols

```bash
grep -rn '\$[0-9]' src/features/ src/app/ src/components/ \
  --include="*.tsx" --include="*.ts" \
  | grep -v node_modules | grep -v '.next' \
  | grep -v formatCurrency | grep -v 'minimumFractionDigits'
```

Every hit is a line that should use `formatCurrency(amount, currency)`.
Also check server actions that build text strings:

```bash
grep -rn '`\${.*\$\$' src/features/ --include="*.ts"
```

## 2. Dynamic Tailwind class names (JIT-purged)

```bash
grep -rn 'text-\${' src/ --include="*.tsx"
grep -rn 'bg-\${'  src/ --include="*.tsx"
grep -rn 'border-\${' src/ --include="*.tsx"
```

Every hit is a template-literal class name that Tailwind's JIT scanner
cannot see. Replace with a static mapping object:

```tsx
const colorClasses = {
  emerald: "text-emerald-600 dark:text-emerald-400",
  red: "text-red-600 dark:text-red-400",
  blue: "text-blue-600 dark:text-blue-400",
  purple: "text-purple-600 dark:text-purple-400",
};
// Use: colorClasses[card.color] instead of `text-${card.color}-600`
```

## 3. Entity bypass (getEntity not used)

```bash
grep -rn 'entities.*select.*user_id.*personal' src/features/ \
  --include="*.ts" | grep -v entity.ts | grep -v auth
```

Every hit is a server action that bypasses the shared `getEntity()` and
hardcodes the personal entity. Fix: replace with `const entity = await
getEntity(); if ("error" in entity) return ...; const { supabase,
entityId } = entity;`.

## 4. Duplicate functions across files

```bash
# Find function names defined in more than one file
grep -rn 'export async function' src/features/ --include="*.ts" \
  | sed 's/.*export async function \([a-zA-Z]*\).*/\1/' \
  | sort | uniq -c | sort -rn | head -10
```

Any function with count > 1 is a duplicate. Keep the canonical version
and delete the rest. CashFlow OS had `createBusinessEntity` and
`getEntities` duplicated across `accounts/actions.ts` and
`business/actions.ts`.

## 5. localStorage access in client components (hydration risk)

```bash
grep -rn 'localStorage' src/ --include="*.tsx" \
  | grep -v useEffect | grep -v 'typeof window'
```

Any hit outside a `useEffect` or without a `typeof window !==
"undefined"` guard risks a hydration mismatch. Fix: move the read into
`useEffect` or wrap with a `typeof window` guard.

## 6. Dark mode not activated

```bash
grep -rn 'className=.*dark' src/app/layout.tsx
```

If `.dark` CSS variant is defined in `globals.css` but no `dark` class
is on `<html>`, the app is permanently in light mode. Fix: add `dark`
to the `<html>` className.

## 7. Missing form fields

Check transaction/entry forms for minimum required fields:
- description (text input)
- date (date picker, default to today)
- tags (optional, comma-separated)
- recurring (checkbox)

If the form only sends `type`, `amount`, `category_id`, and hardcodes
`date: format(new Date(), "yyyy-MM-dd")`, it is incomplete.
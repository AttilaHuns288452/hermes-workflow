# shadcn/ui Theming

## CSS Variables

shadcn/ui uses CSS variables for dynamic theming. Default variables:

```css
:root {
  --background: hsl(0 0% 100%);
  --foreground: hsl(240 10% 3.9%);
  --card: hsl(0 0% 100%);
  --card-foreground: hsl(240 10% 3.9%);
  --popover: hsl(0 0% 100%);
  --popover-foreground: hsl(240 10% 3.9%);
  --primary: hsl(240 5.9% 10%);
  --primary-foreground: hsl(0 0% 98%);
  --secondary: hsl(240 4.8% 95.9%);
  --secondary-foreground: hsl(240 5.9% 10%);
  --muted: hsl(240 4.8% 95.9%);
  --muted-foreground: hsl(240 3.8% 46.1%);
  --accent: hsl(240 4.8% 95.9%);
  --accent-foreground: hsl(240 5.9% 10%);
  --destructive: hsl(0 84.2% 60.2%);
  --destructive-foreground: hsl(0 0% 98%);
  --border: hsl(240 5.9% 90%);
  --input: hsl(240 5.9% 90%);
  --ring: hsl(240 5.9% 10%);
  --radius: 0.5rem;
}

.dark {
  --background: hsl(240 10% 3.9%);
  --foreground: hsl(0 0% 98%);
  --card: hsl(240 10% 3.9%);
  --card-foreground: hsl(0 0% 98%);
  --popover: hsl(240 10% 3.9%);
  --popover-foreground: hsl(0 0% 98%);
  --primary: hsl(0 0% 98%);
  --primary-foreground: hsl(240 5.9% 10%);
  --secondary: hsl(240 3.7% 15.9%);
  --secondary-foreground: hsl(0 0% 98%);
  --muted: hsl(240 3.7% 15.9%);
  --muted-foreground: hsl(240 5% 64.9%);
  --accent: hsl(240 3.7% 15.9%);
  --accent-foreground: hsl(0 0% 98%);
  --destructive: hsl(0 62.8% 30.6%);
  --destructive-foreground: hsl(0 0% 98%);
  --border: hsl(240 3.7% 15.9%);
  --input: hsl(240 3.7% 15.9%);
  --ring: hsl(240 4.9% 83.9%);
}
```

## Semantic Token Usage

Always use semantic tokens in components:
- `bg-background` / `text-foreground` — page-level
- `bg-card` / `text-card-foreground` — card surfaces
- `bg-primary` / `text-primary-foreground` — primary actions
- `bg-muted` / `text-muted-foreground` — subdued content
- `border-border` / `ring-ring` — borders and focus rings
- Never use raw values like `bg-blue-500` in components

## Dark Mode

- Toggled by adding `.dark` class to `<html>` 
- Tailwind v3: `darkMode: 'class'` in config
- Tailwind v4: `@custom-variant dark (&:where(.dark, .dark *))`

## Custom Colors

In Tailwind v3 — extend in `tailwind.config.ts`:
```ts
theme: {
  extend: {
    colors: {
      primary: { ... }
    }
  }
}
```

In Tailwind v4 — use CSS variables:
```css
@theme {
  --color-primary: var(--primary);
}
```

## Border Radius

- `--radius: 0.5rem` (default) — consistent rounded corners
- Override per variant if needed
- `rounded-[var(--radius)]` in component classes

## Component Variants

Components use the `cva` (class-variance-authority) pattern:
```tsx
const buttonVariants = cva(
  "inline-flex items-center justify-center ...",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground ...",
        destructive: "...",
        outline: "...",
        secondary: "...",
        ghost: "...",
        link: "...",
      },
      size: {
        default: "h-9 px-4 py-2",
        sm: "h-8 ...",
        lg: "h-10 ...",
        icon: "h-9 w-9",
      },
    },
  }
)
```

## Tailwind v3 vs v4

| Feature | v3 | v4 |
|---------|----|----|
| Theme config | `tailwind.config.ts` | `@theme` directive in CSS |
| Dark mode | `darkMode: 'class'` config | `@custom-variant dark` in CSS |
| Custom colors | `extend.colors` in config | `--color-*` CSS variables |
| Plugins | `plugins: [require(...)]` | `@import` or `@plugin` in CSS |
| Prefix | `prefix: 'tw-'` in config | `@import "tailwindcss" prefix(tw)` in CSS |

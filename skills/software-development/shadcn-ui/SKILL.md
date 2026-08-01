---
name: shadcn-ui
description: shadcn/ui component framework — install, configure, compose, and customize components with the shadcn CLI and AI skill system.
tags: [shadcn, ui, components, react, tailwind, radix, registry]
user-invocable: true
---

# shadcn/ui — Hermes Integration

This skill integrates [shadcn/ui](https://ui.shadcn.com) into Hermes. It covers CLI usage, component composition, theming, registry authoring, and the AI skill ecosystem.

## Quick Install (per project)

The shadcn AI skill auto-activates when a `components.json` is detected. Install it:

```bash
npx skills add shadcn/ui
```

This clones the [shadcn/ui skill repo](https://github.com/shadcn/ui.git) into `.agents/skills/shadcn/` and configures it for Hermes, Claude Code, Cursor, and other AI tools.

## CLI Commands

All commands use the project's package runner (`npx shadcn@latest`, `pnpm dlx shadcn@latest`, or `bunx --bun shadcn@latest`):

| Command | Description |
|---------|-----------|
| `npx shadcn@latest init` | Initialize shadcn in a project |
| `npx shadcn@latest add <component>` | Install a component |
| `npx shadcn@latest search <query>` | Search registries for components |
| `npx shadcn@latest docs <component>` | Get component documentation |
| `npx shadcn@latest diff <component>` | Show local vs upstream diff |
| `npx shadcn@latest info --json` | Project config + installed components |
| `npx shadcn@latest build` | Build local registry |
| `npx shadcn@latest view <component>` | View component source |

## Project Context

```bash
npx shadcn@latest info --json
```

Returns: framework, aliases, Tailwind version, base library (`base` or `radix`), icon library, installed components, and resolved file paths.

Use `npx shadcn@latest docs <component>` before writing custom code.

## Composition Rules

### Styling & Tailwind
- Use **`className` for layout only** — never override component colors/typography
- **No `space-x-*` / `space-y-*`** — use `flex` + `gap-*` instead
- **`size-*`** when width == height (not `w-10 h-10`)
- **`truncate`** shorthand (not `overflow-hidden text-ellipsis whitespace-nowrap`)
- **No manual `dark:` overrides** — use semantic tokens (`bg-background`, `text-muted-foreground`)
- **`cn()`** for conditional classes (not template literal ternaries)
- **No manual `z-index`** on overlay components (Dialog, Sheet, Popover handle their own)

### Forms
- **`FieldGroup` + `Field`** for form layout (never raw `div` with spacing)
- **`InputGroup` + `InputGroupInput`/`InputGroupTextarea`** (never raw `Input` inside `InputGroup`)
- **`ToggleGroup`** for option sets (2-7 choices)
- **`FieldSet` + `FieldLegend`** for grouped checkboxes/radios
- **Field validation**: `data-invalid` + `aria-invalid` on control, `data-invalid` on `Field`
- **Buttons inside inputs**: use `InputGroup` + `InputGroupAddon`

### Composition
- **Compose, don't reinvent**: Settings = Tabs + Card + form controls. Dashboard = Sidebar + Card + Chart + Table.
- **Built-in variants**: `variant="outline"`, `size="sm"`, etc.
- **Semantic colors**: `bg-primary`, `text-muted-foreground` — never raw `bg-blue-500`

## Theming

- CSS variables for colors, border-radius, spacing
- OKLCH color space for consistent luminance
- Dark mode via `.dark` class
- Custom colors via `--color-*` variables
- Tailwind v3 and v4 both supported

## MCP Server

The [shadcn MCP server](https://ui.shadcn.com/docs/mcp) lets AI assistants search, browse, and install components from registries directly:

```json
{
  "mcpServers": {
    "shadcn": {
      "command": "npx",
      "args": ["-y", "@shadcn/mcp"]
    }
  }
}
```

## Registry Authoring

Build custom component registries via `registry.json`. Schema:
- **Item types**: `registry:lib`, `registry:component`, `registry:ui`, `registry:hook`, `registry:page`, `registry:block`, `registry:file`
- **File objects**: path, content (inline or `file:` prefix), type
- **Dependencies**: npm packages, registry items
- **CSS variables**: `--primary`, `--radius`, etc.

See [Registry docs](https://ui.shadcn.com/docs/registry) for the full schema.

## How the AI Skill Works

1. **Project detection** — activates when `components.json` is found
2. **Context injection** — runs `shadcn info --json` on each interaction
3. **Pattern enforcement** — follows composition rules (FieldGroup, ToggleGroup, etc.)
4. **Component discovery** — uses `shadcn docs`, `shadcn search`, or MCP tools

## Pitfalls

### Windows npm cache: ENOTEMPTY on `shadcn add`
`npx shadcn@latest add` often fails on Windows with `npm error ENOTEMPTY: directory not empty, rmdir ...` from a stale `_npx` cache. Delete it:
```bash
rm -rf ~/AppData/Local/npm-cache/_npx
```
If that doesn't fix it, **skip the CLI entirely.** Write `components.json` by hand and write shadcn components manually using the `forwardRef` + `cn()` pattern. Each component is ~30 lines — faster than fighting npm.

### CLI timeout on `shadcn init`
`npx shadcn@latest init -d` can hang indefinitely. Workaround: write `components.json` manually:
```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default", "rsc": true, "tsx": true,
  "tailwind": { "config": "tailwind.config.ts", "css": "src/app/globals.css", "baseColor": "neutral", "cssVariables": true, "prefix": "" },
  "aliases": { "components": "@/components", "utils": "@/lib/utils", "ui": "@/components/ui", "lib": "@/lib", "hooks": "@/hooks" }
}
```
Install Radix primitives directly (`npm install @radix-ui/react-slot @radix-ui/react-dialog @radix-ui/react-select @radix-ui/react-tabs @radix-ui/react-label @radix-ui/react-separator @radix-ui/react-avatar clsx tailwind-merge class-variance-authority`), then write components by hand.

### Manual component template
When writing shadcn components without the CLI, use this pattern:
```tsx
import * as React from "react"
import { cn } from "@/lib/utils"

const Card = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("rounded-lg border bg-card text-card-foreground shadow-sm", className)} {...props} />
  )
)
Card.displayName = "Card"
```

## References

- [Installation](https://ui.shadcn.com/docs/installation)
- [Components](https://ui.shadcn.com/docs/components)
- [CLI Reference](https://ui.shadcn.com/docs/cli)
- [Theming](https://ui.shadcn.com/docs/theming)
- [Registry](https://ui.shadcn.com/docs/registry)
- [MCP Server](https://ui.shadcn.com/docs/mcp)
- [Skills System](https://skills.sh)

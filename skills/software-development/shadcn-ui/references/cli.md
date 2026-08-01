# shadcn CLI Reference

Full reference for all CLI commands: `init`, `add`, `search`, `view`, `docs`, `diff`, `info`, and `build`.

## init

```bash
npx shadcn@latest init [options]
```

Initialize shadcn/ui in a project.

**Flags:**
- `--base-color <color>` — Base color (zinc, slate, gray, neutral, stone, or CSS hex)
- `--css-variables` — Use CSS variables for theming
- `--force`, `-f` — Overwrite existing configuration
- `--defaults`, `-d` — Use default configuration
- `--yes`, `-y` — Skip confirmation prompts
- `--path <path>` — Target directory
- `--preset <preset>` — Use a preset

## add

```bash
npx shadcn@latest add [component] [options]
```

Add components to your project.

**Flags:**
- `--all` — Add all components
- `--overlay` — Add overlay components (dialog, sheet, etc.)
- `--path <path>` — Target directory
- `--yes`, `-y` — Skip confirmation
- `--dry-run` — Show what would be installed
- `--registry <name>` — Registry name for custom registries

## search

```bash
npx shadcn@latest search [query]
```

Search registries for components.

**Flags:**
- `--registry <name>` — Search a specific registry

## view

```bash
npx shadcn@latest view <component> [options]
```

View component source code.

**Flags:**
- `--registry <name>` — Registry name
- `--json` — Output as JSON

## docs

```bash
npx shadcn@latest docs <component> [options]
```

Get documentation and example URLs for a component.

**Flags:**
- `--registry <name>` — Registry name
- `--json` — Output as JSON

## diff

```bash
npx shadcn@latest diff <component> [options]
```

Show diff between local and upstream component.

**Flags:**
- `--registry <name>` — Registry name

## info

```bash
npx shadcn@latest info --json
```

Show project configuration and installed components.

**Output includes:** framework, aliases, Tailwind version, base library, icon library, installed components, resolved file paths.

## build

```bash
npx shadcn@latest build [options]
```

Build a local registry.

**Flags:**
- `--cwd <path>` — Working directory

## Presets

A preset is a string like `shadcn/ui:button` or a full registry URL. Use with `init --preset` or `add`:

```bash
npx shadcn@latest init --preset app
npx shadcn@latest add --preset shadcn/ui:sidebar
```

## Templates

Templates allow scaffolding projects from a template registry:

```bash
npx shadcn@latest init --preset <template-url>
```

## Smart Merge

When adding components to an existing project, the CLI uses a smart merge strategy:
- Detects changes made to previously installed components
- Shows a unified diff
- Options: skip, overwrite, or merge

## Dry Run

```bash
npx shadcn@latest add button --dry-run
```

Show what would be added without writing files.

---
name: obsidian-codebase-graph
description: Map a codebase into an interconnected Obsidian vault as folder, file, and symbol notes linked by code relationships. Use when the user asks to note a project to Obsidian, create a codebase graph, visualize architecture in Obsidian, sync code structure to notes, import a repo into Obsidian, map dependencies, or generate project notes from code.
platforms: [windows, macos, linux]
---

# Obsidian Codebase Graph

Create an Obsidian knowledge graph from an existing codebase by emitting markdown notes with frontmatter and `[[wikilinks]]`. The output mirrors the filesystem hierarchy and surfaces real code relationships: imports, exports, calls, inheritance, implements, shared types, and aliases.

Automation entry point: `scripts/generate_codebase_graph.py`

## Vault path

Resolve the vault path before creating notes. Use `OBSIDIAN_VAULT_PATH` if set; otherwise use `~/Documents/Obsidian Vault`. Do not pass shell variables to file tools. On Windows, use `C:\Users\<user>\Documents\Obsidian Vault` semantics.

## Scope

Use this for codebases, especially:
- Next.js / TypeScript projects
- React component trees
- Node.js / Express services
- Full-stack apps with a clear folder hierarchy

Trigger phrases include:
- "note to Obsidian"
- "map this project to Obsidian"
- "create an Obsidian graph from this codebase"
- "sync the codebase into notes"
- "visualize architecture in Obsidian"

## Note schema

Use this schema for every generated note.

### Root / project index note
- Filename: `<ProjectRoot>.md`
- Frontmatter:
  - `type: project`
  - `path: <relative project root>`
  - `framework: <optional>`
  - `language: <optional>`
- Body:
  - heading `# <Project Name>`
  - short description paragraph
  - `## Folders` list of `[[<Folder>]]` links
  - `## Entry Points` list of linked entry files when detectable
  - `## Quick Links` for README, docs, config files when present

### Folder note
- Filename: `<Folder>.md` under the vault project notes folder, using a path derived from the actual folder name; use spaces and title casing for readability
- Frontmatter:
  - `type: folder`
  - `path: <relative folder path>`
  - `children: <array of child note names>`
- Body:
  - `# <Folder>`
  - `## Files` list of `[[<FileName>]]` links
  - optional `## Notes` section for architecture comments

### File note
- Filename derived from the source file name
- Frontmatter:
  - `type: file`
  - `path: <relative source path>`
  - `extension: <ts|tsx|js|jsx|json|md|...>`
  - `imports: [<array of imported symbol or module links>]`
  - `exports: [<array of exported symbol or module links>]`
  - `dependencies: [<array of file links imported>]`
- Body:
  - `# <File Name>`
  - `\`\`\`ts` summary block showing imports/exports when helpful
  - `## Symbols` list of `[[<SymbolName>]]` links
  - `## Relationships` section with `[[<Target>]]` links grouped by relationship type

### Symbol note
Use one note per meaningful symbol: classes, interfaces, types, functions, components, hooks, constants, enums, callbacks, and named exports larger than trivial.

- Filename: `<SymbolName>.md`
- Frontmatter:
  - `type: <class|interface|type|function|component|hook|constant|enum|callback>`
  - `file: <relative source file path>`
  - `definedIn: [[<FileNoteName>]]`
  - `imports: [<symbols referenced>]`
  - `exports: [<symbols it exposes>]`
  - `implements: [<interface links>]`
  - `extends: [<class links>]`
  - `calls: [<function or component links>]`
  - `referencedBy: [<reverse callers or importers>]`
  - `sharedTypes: [<shared type or interface links>]`
  - `tags: [<optional descriptive tags>]`
- Body:
  - `# <Symbol Name>`
  - `## Summary` 1-3 sentences describing role
  - `## Location` `[[<FileNoteName>]]`
  - `## Relationships` bullet list of `[[<related symbol>]]` links with short context
  - `## Source` literal code block or snippet when it aids navigation

### Relationship edge types
Use consistent edge labels in notes and metadata:
- `imports` / `importedBy`
- `exports`
- `calls` / `calledBy`
- `extends`
- `implements`
- `usesType` / `typeUsedBy`
- `aliases`
- `references`

## Folder naming and vault layout

Create the vault notes under a dedicated project notes folder:
- Use `<ProjectRoot> Project` as the root notes folder name unless the user specifies otherwise.
- Mirror the source folder hierarchy inside that notes folder.
- Keep paths readable and OS-safe.
- Each folder note links to its child file notes.
- Each file note links to its child symbol notes.
- Parent folder notes aggregate their children in frontmatter for graph navigation.

## Linking conventions

- Use `[[Note Name]]` for local links.
- When multiple symbols have similar names, disambiguate with `[[Note Name|alias]]`.
- Prefer human-readable note names over raw filenames when it helps graph clarity.
- Keep symbol note names stable; if a file changes, preserve existing symbol note names when possible.

## Generation workflow

1. Confirm source directory and output vault folder.
2. Scan the filesystem tree and build a folder, file, and candidate symbol inventory.
3. Parse source files for import/export/declaration relationships where practical. If full parsing is too heavy, use lightweight heuristics and clearly mark relationships as `estimated`.
4. Create folder notes and file notes first.
5. Create symbol notes.
6. Backfill reverse relationship metadata: `referencedBy`, `importedBy`, `calledBy`.
7. Write a project index note at the root linking to all top-level folders.
8. Update folder and file notes to include their newly created symbol links.

## Automation — TypeScript/Next.js (primary)

Use `scripts/generate_codebase_graph.py` with the upgraded regex-based parser:

```bash
# Generate codebase graph for any TS/TSX/JS/JSX project
python scripts/generate_codebase_graph.py '<source_root>' '<vault_root>'

# Clean regenerate (removes existing project notes folder first)
python scripts/generate_codebase_graph.py '<source_root>' --clean

# Dry-run (show summary without writing files)
python scripts/generate_codebase_graph.py '<source_root>' --skip-vault
```

## Update-after-changes workflow (Rule 5 enforcement)

After any structural code change to a project, the Obsidian code graph MUST be regenerated. This is enforced by **Rule 5** in `/decide`:

```bash
# Regenerate existing graph (safe — uses --clean to wipe stale notes)
python $HERMES_HOME/skills/note-taking/obsidian-codebase-graph/scripts/generate_codebase_graph.py \
  "$HOME/Documents/Projects/$PROJECT" --clean
```

Detection logic:
- Run `test -d "$OBSIDIAN_VAULT/<Project Name> Project/"` to check if notes exist
- If yes → `--clean` regenerate
- If no + structural change → create without `--clean`
- Skip only for cosmetic changes (typos, comments, config values) — Rule 5 allows judgment here

The script uses **regex-based TypeScript/JSX parsing** — not Python's `ast.parse()` — so it correctly handles:
- TypeScript syntax (generics, type annotations, `interface`, `type`)
- JSX/TSX (React components, JSX return values)
- Named/default/namespace imports and exports
- `export type`, `export interface`, `export enum`
- React hooks (`use*` patterns) auto-detection
- Component detection (functions returning JSX)

Result: `<Project Name> Project/` folder in the vault with linked markdown notes.

## Usage patterns

| Scenario | Command |
|----------|---------|
| First-time graph | `python generate_codebase_graph.py .` |
| Regenerate clean | `python generate_codebase_graph.py . --clean` |
| Different vault | `python generate_codebase_graph.py . 'D:\Obsidian\Vault'` |
| Quick stats only | `python generate_codebase_graph.py . --skip-vault` |

## Validation and repair

After generation:
- Verify that every linked note exists.
- Ensure no empty or placeholder files remain unless intended.
- Repair broken links by regenerating the affected note instead of creating duplicates.
- Verify the graph is readable by checking folder note `children` lists and file note `dependencies` lists.
- Open Obsidian graph view (Ctrl+O → `Cmd+G` on Mac) on the project notes folder.

## Execution guidance

- The script auto-ignores: `node_modules`, `.next`, `dist`, `build`, `.git`, `out`, `graphify-out`, `coverage`, `.turbo`, `.cache`, and more.
- Prefer non-destructive generation: create new notes under the target project notes folder rather than editing unrelated notes.
- Use `--clean` to wipe and regenerate if the project structure changed significantly.
- If parsing is incomplete due to language or tooling limits (e.g. dynamically computed exports), the script notes it in the index page.
- When the vault argument is omitted, defaults to `~/Documents/Obsidian Vault`.

## Pitfalls

### Regex parser is heuristic, not a full TypeScript AST

The script uses regex patterns to extract symbols. This handles **~90% of real-world Next.js/TS patterns** but may miss:
- Re-export chains (`export { X } from './foo'`)
- Destructured imports used as call expressions
- Dynamic imports (`const X = await import('...')`)
- Symbols created via `Object.assign` or factory functions
- Computed property names or complex generics

**If a symbol is missing**: the file note and folder note are still created with correct wikilinks. You can manually add a `[[SymbolName]]` note with frontmatter.

### Script ignores non-TS/JS source extensions

Files with `.css`, `.scss`, `.less`, `.json`, `.md`, `.yaml`, `.toml` are listed as file notes but NOT parsed for symbols. They appear in the graph as file nodes but have no symbol children.

### Single-file projects produce little value from auto-generation

If the entire project is 1–3 files, skip the auto-generator. Create a manual `File Structure.md` note that:
- Lists every file with its type and purpose (table)
- Documents the DOM or section hierarchy as a tree
- Lists all symbols with descriptions
- Links back to the main project note

## Example outcome

Project root: `apps/web`
Index note: `apps web Project.md`
Folder note: `components.md`
File note: `Header.tsx`
Symbol note: `Header.tsx.md` may instead be `Header.md` with frontmatter `file: apps/web/components/Header.tsx`.

Actual filesystem layout:
```
apps/web/
  app/
    layout.tsx
    page.tsx
  components/
    Header.tsx
```

Generated vault notes:
- `apps web Project.md`
- `app.md`
- `layout.tsx.md`
- `page.tsx.md`
- `components.md`
- `Header.tsx.md`
- `Header.md`

Links:
- `apps web Project.md` -> `[[app]]`, `[[components]]`
- `app.md` -> `[[layout.tsx]]`, `[[page.tsx]]`
- `Header.tsx.md` -> `[[Header]]`

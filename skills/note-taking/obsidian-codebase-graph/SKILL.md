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

## Automation

Use `scripts/generate_codebase_graph.py` for generation:

```bash
python scripts/generate_codebase_graph.py '<source_root>' '<vault_root>'
```

Result: a project notes folder under the vault with linked markdown notes ready for Obsidian graph view.

## Validation and repair

After generation:
- Verify that every linked note exists.
- Ensure no empty or placeholder files remain unless intended.
- Repair broken links by regenerating the affected note instead of creating duplicates.
- Verify the graph is readable by checking folder note `children` lists and file note `dependencies` lists.

## Execution guidance

- Prefer non-destructive generation: create new notes under the target project notes folder rather than editing unrelated notes.
- If a project note already exists for the requested root, merge the new graph into it by appending missing sections rather than overwriting.
- If the user asks for `note to Obsidian`, treat it as a request to execute this workflow for the current or specified project.
- If parsing is incomplete due to language or tooling limits, emit a `## Parsing Notes` section in the project index stating what was heuristically inferred versus statically verified.

## Pitfalls

### `generate_codebase_graph.py` uses `ast.parse()` — does NOT handle HTML, CSS, or plain JS files

The script relies on Python's built-in `ast` module for symbol extraction. This means it **only** works for files with extensions `.py`, `.js`, `.ts`, `.tsx`, `.jsx` that contain valid Python-parsable AST. It cannot parse:

- **HTML files** (`.html`, `.htm`) — embedded `<script>` blocks and CSS inside `<style>` are invisible to `ast.parse()`
- **CSS-only files** (`.css`, `.scss`, `.less`)
- **JSON config files** beyond simple flat detection
- **Markdown files** (`.md`) with code blocks

**When the project is a single-file or non-TS/JS app** (e.g. a single `index.html` with embedded CSS/JS):
- The auto-generator will produce a note with no symbols, no imports/exports, and no useful relationships
- **Instead**: create a manual `File Structure.md` note that:
  - Lists every file in the project with its type and purpose (table)
  - Documents the DOM or section hierarchy as a tree
  - Lists all JavaScript symbols (functions, variables, event handlers) as a symbol table
  - Links back to the main project note and any design/architecture notes
  - Use this as the "file note" replacement; it's more useful than an empty auto-generated note

### Single-file projects produce little value from auto-generation

If the entire project is 1–3 files (especially HTML or mixed-content files), skip the auto-generator entirely. The manual `File Structure.md` approach above produces richer, more accurate output. Reserve the auto-generator for multi-file TypeScript/JS/Python projects with meaningful import/export graphs.

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

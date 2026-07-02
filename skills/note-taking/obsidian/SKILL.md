---
name: obsidian
description: Read, search, create, and edit notes in the Obsidian vault. Also covers Obsidian Flavored Markdown (wikilinks, callouts, embeds, properties), Bases (.base), JSON Canvas (.canvas), and Obsidian CLI. Upstream: kepano/obsidian-skills.
platforms: [linux, macos, windows]
tags: [obsidian, notes, knowledge-management, vault, wikilinks, callouts, canvas, bases]
related_skills:
  - obsidian-codebase-graph
  - obsidian-knowledge-graph
  - graphify-integrate
  - obsidian-markdown
  - obsidian-bases
  - json-canvas
  - obsidian-cli
---

# Obsidian Vault

Use this skill for filesystem-first Obsidian vault work: reading notes, listing notes, searching note files, creating notes, appending content, and adding wikilinks.

## Vault path

Use a known or resolved vault path before calling file tools.

The documented vault-path convention is the `OBSIDIAN_VAULT_PATH` environment variable, for example from `~/.hermes/.env`. If it is unset, use `~/Documents/Obsidian Vault`.

File tools do not expand shell variables. Do not pass paths containing `$OBSIDIAN_VAULT_PATH` to `read_file`, `write_file`, `patch`, or `search_files`; resolve the vault path first and pass a concrete absolute path. Vault paths may contain spaces, which is another reason to prefer file tools over shell commands.

If the vault path is unknown, `terminal` is acceptable for resolving `OBSIDIAN_VAULT_PATH` or checking whether the fallback path exists. Once the path is known, switch back to file tools.

## Read a note

Use `read_file` with the resolved absolute path to the note. Prefer this over `cat` because it provides line numbers and pagination.

## List notes

Use `search_files` with `target: "files"` and the resolved vault path. Prefer this over `find` or `ls`.

- To list all markdown notes, use `pattern: "*.md"` under the vault path.
- To list a subfolder, search under that subfolder's absolute path.

## Search

Use `search_files` for both filename and content searches. Prefer this over `grep`, `find`, or `ls`.

- For filenames, use `search_files` with `target: "files"` and a filename `pattern`.
- For note contents, use `search_files` with `target: "content"`, the content regex as `pattern`, and `file_glob: "*.md"` when you want to restrict matches to markdown notes.

## Create a note

Use `write_file` with the resolved absolute path and the full markdown content. Prefer this over shell heredocs or `echo` because it avoids shell quoting issues and returns structured results.

## Note Quality Standards (ATM Machine Grade)

Every project note in the vault MUST follow these quality standards. This is NOT optional — Obsidian is a mandatory phase of every project workflow.

### Main Project Note Template (`Projects/<name>/<Name>.md`)

```
# <Project Name>

<One-paragraph summary>

## Overview
<Broader description: what it does, why, who it's for>

## Key Features
- <Feature> — <explanation>
- <Feature> — <explanation>

## Project Structure
```text
project/
├── src/
│   └── <file>      # Purpose
```

## Architecture
<For each major class/module: purpose, key methods, edge cases>

## Code Patterns
```<language>
<concrete usage example>
```

## Related Files
- [[Note]] — description

## Knowledge Graph Map
```mermaid
graph TD
    N["Note"] --> S["SubNote"]
```

## Tags
#project #language #category
```

### Supporting Note Template (per module/file)
```
# <Module Name>

<One-paragraph purpose>

## Class Definition
class <Name>: <key fields>

## Methods
| Method | Description |

## Key Implementation Details
<Edge cases, design decisions, important algorithms>

## Knowledge Graph Position
```mermaid
graph TD
    <module> --> <related>
```

## Related Files
- [[Parent Note]]

## Tags
#project #<module-tag>
```

### Mandatory Rules
1. **Always include wikilinks** (`[[Note Name]]`) — every note must link to at least its parent project note
2. **Always include a Mermaid knowledge graph map** on the main project note
3. **Always include tags** at the bottom (project tag + language tag + category tag)
4. **Use `write_file`** for new notes — never shell heredocs or `echo`
5. **Use `patch`** for targeted edits to existing notes
6. **Update notes continuously** as the project evolves, not just at the end
7. **Graphify is mandatory partner** — the Obsidian bundle now includes `graphify-integrate` as a required layer. Graphify exports code-symbol notes with wikilinks directly into the vault, creating a complementary code-level knowledge graph. After every Graphify export, refresh the vault knowledge graph via `obsidian-knowledge-graph`.

### Reference Files
- `references/atm-machine-note-example.md` — concrete example of ATM Machine project note quality (the reference standard)
- `references/graphify-obsidian-integration.md` — using Graphify (code-level knowledge graph) to generate [[wikilinked]] code-symbol notes in the vault
- `templates/atm-machine-main-note.md` — ready-to-copy main note skeleton

### See Also
- `free-ai-model-router` skill's "Obsidian: Always Part of the Workflow" section for the full note quality specification
- `decide` skill's "Mandatory Include Rule" — ensures Obsidian is always selected for project tasks

## Knowledge-Graph MCP Server
Hermes includes a file-tool MCP server that scans any Obsidian vault and produces a structured node/edge knowledge graph. Usages: "generate my knowledge graph" → `obsidian_knowledge_graph`, "how is my vault connected?" → `obsidian_graph_summary`.

Schema:
- Vault root → folder nodes → note nodes → code_block / section nodes
- tag nodes (global) and concept nodes (cross-note terms ≥ 2 occurrences)
- Edge types: `contains`, `links_to`, `tagged`, `references`, `depends_on`, `alias_of`, `shared_concept`

### Writing a similar stdio MCP scanner (template)
The pattern in `obsidian_kg_mcp.py` is a minimal, reusable stdio MCP server:
1. Define `Node`/`Edge` dataclasses + `scan_vault()` that walks a directory and emits `{nodes, edges}`.
2. Wrap in an `mcp.server.Server`, register tools with `@app.list_tools()` / `@app.call_tool()`.
3. `main()` runs the server via `mcp.server.stdio.stdio_server`.
4. Register under `mcp_servers.<name>` in `~/.hermes/config.yaml` with `command: python`, `args: ["-m", "module_name"]`, and the correct `cwd`.

### Knowledge-Graph Rendering Script
`scripts/render_kg.py` converts the JSON output of `obsidian_knowledge_graph` into an interactive standalone HTML graph (vis-network CDN, Catppuccin dark theme). Run it after generating the graph to get an browser-viewable map with search, filter, and node details.

### Pitfalls
- **`execute_code` approval blocks**: Subprocess pty requests ("User has NOT consented") can block `execute_code` or `terminal`. Use direct shell for quick probes and don't let it silently time out.
- **`vscode-mcp-server` deprecation status**: The npm package shows `vscode-mcp-server@0.2.0` deprecated on npm, but it still starts and responds to MCP handshakes correctly on Windows via `npx -y`. It works for connectivity tests today; do not hardcode a `.cmd` global path — use `npx -y` so npm resolves it whether or not it's globally installed. Long-term reliability depends on whether the package is maintained beyond deprecation.
- **Type mixing in scanners**: Use `Node` dataclass instances throughout the scan and only call `.to_dict()` at flatten time. Don't mix typed and dict objects into the same typed collection before calling typed methods — it causes `'dict' object has no attribute 'to_dict'` errors.

## Append to a note

Prefer a native file-tool workflow when it is not awkward:

- Read the target note with `read_file`.
- Use `patch` for an anchored append when there is stable context, such as adding a section after an existing heading or appending before a known trailing block.
- Use `write_file` when rewriting the whole note is clearer than constructing a fragile patch.

For an anchored append with `patch`, replace the anchor with the anchor plus the new content.

For a simple append with no stable context, `terminal` is acceptable if it is the clearest safe option.

## Targeted edits

Use `patch` for focused note changes when the current content gives you stable context. Prefer this over shell text rewriting.

## Obsidian-Flavored Markdown

Obsidian extends CommonMark and GFM. This section covers Obsidian-specific syntax.

> **External skill (via `kepano/obsidian-skills`):** `obsidian-markdown` with references `CALLOUTS.md`, `EMBEDS.md`, `PROPERTIES.md`.

### Wikilinks (Internal Links)

```markdown
[[Note Name]]                          Link to note
[[Note Name|Display Text]]             Custom display text
[[Note Name#Heading]]                  Link to heading
[[Note Name#^block-id]]                Link to block
[[#Heading in same note]]              Same-note heading link
```

Define a block ID by appending `^block-id` to any paragraph:
```markdown
This paragraph can be linked to. ^my-block-id
```
For lists and quotes, place the block ID on a separate line after the block.

> Use `[[wikilinks]]` for notes within the vault (Obsidian tracks renames automatically) and `[text](url)` for external URLs only.

### Embedded Content

Use `![[embed]]` syntax to embed content from other notes, images, PDFs, audio, video, and canvases:

```markdown
![[Note Name]]                          Embed entire note
![[Note Name#Heading]]                  Embed specific heading
![[Note Name#^block-id]]                Embed specific block
![[image.png]]                          Embed image (with optional |widthxheight)
![[document.pdf]]                       Embed PDF
![[audio.mp3]]                          Embed audio file
![[video.mp4]]                          Embed video file
![[canvas.canvas]]                      Embed canvas view
```

Image sizing: `![[image.png|100]]` (100px wide), `![[image.png|100x200]]` (100w x 200h).

### Callouts

Callouts highlight information with an optional expandable block:

```markdown
> [!type] Title
> Content line 1
> Content line 2
```

Supported types: `note`, `abstract`/`summary`/`tldr`, `info`, `todo`, `tip`/`hint`/`important`, `success`/`check`/`done`, `question`/`help`/`faq`, `warning`/`caution`/`attention`, `failure`/`fail`/`missing`, `danger`/`error`, `bug`, `example`, `quote`/`cite`.

Collapsible callouts — add `+` (default open) or `-` (default collapsed):
```markdown
> [!faq]+ Are callouts foldable?
> Yes, they are.
```

### Properties (Frontmatter)

Obsidian uses YAML frontmatter with typed properties:

```yaml
---
title: My Note
tags:
  - tag1
  - tag2
aliases:
  - Alternative Name
date: 2024-01-01
status: draft
cssclass: my-custom-style
---
```

Property types: `text` (default), `number`, `date`, `datetime`, `checkbox` (boolean). Define in Obsidian's Properties view or inline in frontmatter.

### Comments

Hidden comments that only show in Editing view:

```markdown
%% This is a comment and won't appear in Reading or Live Preview %%
```

### Aliases

Multiple names for the same note — added in frontmatter:

```yaml
---
aliases:
  - Alternative Title
  - Another Name
---
```

Wikilinks with pipe: `[[Alternative Title|]]` resolves to the current note.

### Tags

Two forms:
- **Inline tags**: `#tag` anywhere in content
- **Property tags**: `tags: [tag1, tag2]` in frontmatter. Tag hierarchy: `#project/active/coding`

## Obsidian Bases (.base files)

> **External skill (via `kepano/obsidian-skills`):** `obsidian-bases`

Bases provide database-like views of notes. `.base` files use YAML:

```yaml
filters:
  and:
    - 'status == "active"'
    - not:
        - 'file.hasTag("archived")'

formulas:
  days_since_creation: '(date(today) - date(file.ctime)) / (1000 * 60 * 60 * 24)'

views:
  - type: table
    name: Active Items
    columns:
      - property: title
      - property: formula.days_since_creation
        displayName: "Age (days)"
```

**View types:** `table`, `cards`, `list`, `map`. Each view has `name`, `type`, optional `filter` override, and `columns`/`order`.

**Gotchas:** Unquoted strings with special YAML chars break parsing. Mismatched quotes in formula expressions fail silently. Reference `formula.X` only after defining `X` in `formulas`.

## JSON Canvas (.canvas files)

> **External skill (via `kepano/obsidian-skills`):** `json-canvas`

Visual canvases follow the [JSON Canvas Spec 1.0](https://jsoncanvas.org/spec/1.0/):

```json
{
  "nodes": [
    {
      "id": "a1b2c3d4e5f6a7b8",
      "type": "text",
      "text": "Main Idea",
      "x": 100, "y": 100,
      "width": 300, "height": 200
    }
  ],
  "edges": [
    {
      "id": "e1f2a3b4c5d6e7f8",
      "fromNode": "a1b2c3d4e5f6a7b8",
      "toNode": "b2c3d4e5f6a7b8a1",
      "fromSide": "bottom",
      "toSide": "top",
      "label": "leads to"
    }
  ]
}
```

**Node types:** `text`, `file` (link to note), `group` (container, has `children` array).

**IDs:** 16-character hex strings. Must be unique across all nodes and edges.

**Edge sides:** `top`, `right`, `bottom`, `left`. Endpoints (`fromEnd`, `toEnd`): `none`, `arrow`, `dot`.

## Obsidian CLI

> **External skill (via `kepano/obsidian-skills`):** `obsidian-cli`

For plugin/theme development and vault automation. Requires Obsidian to be open.

```bash
obsidian help                           # All commands
obsidian create name="My Note" content="Hello"
obsidian search query="keyword"
obsidian open path="folder/note.md"
obsidian properties set key=status value=draft
obsidian plugin reload                  # Reload plugins during dev
obsidian js 'console.log("hello")'      # Run arbitrary JS
obsidian screenshot path="output.png"   # Capture screenshot
obsidian dom inspect path=".markdown-reading-view"
```

Parameters use `key=value`, flags are bare (e.g., `silent`, `overwrite`, `new`). Use `file=<name>` for wikilink-style resolution or `path=<path>` for exact vault path. Use `vault=<name>` as the first param to target a specific vault.

## Upstream Resources

- **kepano/obsidian-skills** — https://github.com/kepano/obsidian-skills — full skill set with detailed references (CALLOUTS.md, EMBEDS.md, PROPERTIES.md) loaded via external_dirs
- **Obsidian Flavored Markdown:** https://help.obsidian.md/obsidian-flavored-markdown
- **Obsidian CLI:** https://help.obsidian.md/cli
- **JSON Canvas Spec:** https://jsoncanvas.org/spec/1.0/

---
name: project-documentation
description: Generate structured documentation folder for a codebase — overview, architecture, modules, data flow, dependencies, gaps. Creates 6 subfolders with README.md files inside the Obsidian vault.
platforms: [linux, macos, windows]
on_demand: true
related_skills:
  - note-taking/obsidian-codebase-graph
  - note-taking/obsidian
  - note-taking/obsidian-knowledge-graph
---

# Project Documentation Generator

> **ON-DEMAND ONLY** — Never auto-generate documentation without explicit user request. Trigger phrases: "create documentation for", "document [project]", "generate project docs", or "organize and recreate my whole obsidian notes" which triggers for ALL active projects.

Generates a 6-folder documentation tree for a given project inside the Obsidian vault under `Documentation/<Project Name>/`.

## Folder Structure

```
Documentation/<Project Name>/
├── 01_overview/
│   └── README.md          — One-paragraph purpose, tech stack, entry point(s)
├── 02_architecture/
│   └── README.md          — ASCII/Mermaid system diagram, major component roles
├── 03_modules/
│   └── *.md               — One file per major module/directory in the actual codebase
├── 04_data_flow/
│   └── README.md          — 2-3 real execution paths end-to-end with file/function names
├── 05_dependencies/
│   └── README.md          — Internal module deps + external libs/services + why
└── 06_gaps_and_todos/
    └── README.md          — Undocumented/fragile/uncertain parts flagged honestly
```

## Reference Templates

- `references/01-master-template.md` — Exact file outline to copy for each of the 6 sections
- `references/deep-code-annotation-template.md` — Required inline-commenting style for code blocks (deep C#-bridging annotations, formatted separator headers, concept-to-C# mapping table)

**IMPORTANT:** Every code block in documentation MUST use the deep annotation style from `references/deep-code-annotation-template.md`. The user explicitly corrected "brief annotation" to require line-by-line C#-bridging comments. Read this reference file before writing any code block in modules or data-flow docs.

## Workflow

### Step 0 — Directory Prep
Create the folder structure first, then fill files. Path: `~/Documents/Obsidian Vault/Documentation/<Project Name>/<section>/README.md`

```bash
mkdir -p "Documentation/<Project Name>/{01_overview,02_architecture,03_modules,04_data_flow,05_dependencies,06_gaps_and_todos}"
```

### Step 1 — Explore the Codebase (Batch Parallel for Multi-Project)

For a single project, use these tools in order:

1. **CodeGraph MCP** (primary): `codegraph_files()` for tree + symbol counts, `codegraph_explore()` for symbols, `codegraph_search()` for specific functions
2. **Read key configs**: `package.json`, `README.md`, `DESIGN.md`, `tsconfig.json`, `next.config.ts` — these tell you deps, scripts, and project intent in < 1000 tokens
3. **Terminal `ls -R`**: Full directory listing to see every file at once. Pipe to `grep` to filter by type.
4. **search_files**: find by content pattern if you need specific references
5. **read_file**: read specific entry points and key modules

For **multiple projects** (e.g., "document all my projects"), use `delegate_task` to explore each codebase in parallel via subagents. Each subagent gets the project path and returns a structured summary. Then compose all 6 files per project from the summaries.

### Step 2 — Read These Files Always
- `package.json` / `pyproject.toml` / `Cargo.toml` — dependencies, scripts, name
- `README.md` — stated purpose
- Config files (next.config, tsconfig, tailwind)
- Entry point files (main.py, app/page.tsx, atm.html)
- Key module files in src/ or app/ or lib/
- DESIGN.md if it exists (architecture decisions)

### Step 3 — Base on Actual Code, Not Assumptions
- Use real file names and function names from the codebase
- If unsure how something connects, say so in `06_gaps_and_todos/README.md`
- NEVER invent explanations or make up data flow paths
- For gaps: check if a contact form actually submits, if persistence exists, if tests exist
- The 06_gaps_and_todos file is your honesty mechanism — use it liberally

### Step 4 — Writing Rules (Style & Format)

**Critical style rule: Docs MUST contain literal code blocks, file tree graphs with emoji, wikilinks, and relationship diagrams** — modeled on auto-generated CodeGraph notes. This is a user preference enforced across all project docs.

#### 4a — YAML Frontmatter
Every file starts with:
```
---
type: project-doc
section: overview       # or architecture, modules, data-flow, dependencies, gaps
project: <Project Name>
tags: [project-name, section-tag, ...]
---
```

#### 4b — File Tree Diagram (01_overview)
Include a full project file tree with emoji annotations:
```
## 📁 File Tree

project-root/
├── src/
│   ├── core/
│   │   ├── account.py              # [[Account]] model class
│   │   └── bank.py                 # [[Bank]] registry
│   └── ui/
│       └── atm_ui.py               # [[ATMUI]] console interface
├── main.py                         # 🟢 Entry point
└── package.json                    # 📦 Config
```
Use emoji prefixes: 🟢 entry, 🌐 web, 🎨 style, ⚙️ core, 📦 config, 🖥️ UI, 🐍 Python, 📝 blog, 🗺️ sitemap, 🧪 test, 🔧 script.

#### 4c — Literal Code Blocks with Deep Explanatory Comments

Pull actual source code from the filesystem using `read_file`. Include the real function signatures, not paraphrases.

**CRITICAL: Deep inline comments required.** Each code block must be annotated with line-by-line or block-by-block explanations. Do NOT settle for "brief annotation" — the user explicitly corrected this style. The required depth is:

1. **Section separators** — Use `═══` headers to group related code into clear sections:
   ```python
   # ═══════════════════════════════════════════════════════════════════
   # 📦 SECTION HEADER — explains the purpose of the block below
   # ═══════════════════════════════════════════════════════════════════
   ```

2. **Inline demarkation** — Use `# ──` or `// ──` to mark sub-sections within a function:
   ```python
   # ── CONSTRUCTOR (like C# constructor) ──
   ```

3. **Every unfamiliar syntax gets a C# equivalent** — When the code uses something outside basic Java/C# CRUD experience, annotate with a direct comparison:
   ```python
   # `amount: float` — TYPE HINT (like C# `float amount` but optional)
   # `-> Transaction` — return type hint (like C# `Transaction` return type)
   # `raise ValueError(...)` — like `throw new ArgumentException(...)` in C#
   # `try:` — like C# `try { }`
   # `except ValueError as e:` — like C# `catch (ArgumentException e)`
   ```

4. **💡 or ℹ️ callout comments** for concepts that need extra context:
   ```python
   # 💡 WHY THIS MATTERS: The underscore `_` prefix is a CONVENTION meaning
   # "private" — Python doesn't enforce it like C# does, but it signals intent.
   ```

5. **Code flow walkthrough** — Before a complex block, add a plain-language summary:
   ```python
   # ── What this does, step by step ──
   # 1. Takes user input from Scanner
   # 2. Validates the PIN is exactly 4 digits (same regex pattern as C#)
   # 3. Creates a hashmap entry with account number as key
   # 4. Returns success message
   ```

6. **Target audience rule:** Write each comment as if explaining to a developer whose experience is **only basic C# CRUD** (forms, validation, database connections, if/else, loops, and switch). They know Java/C# class basics but have NOT seen: Python decorators, dataclasses, JavaScript closures/async, TypeScript generics, React hooks, or functional patterns like map/filter/reduce.

Example of correct depth:
```python
# ═══════════════════════════════════════════════════════════════════════
# 📦 @dataclass DECORATOR — what is this?
#
# A DECORATOR (the `@` thing) is like a stamp you put on a class to give
# it superpowers. `@dataclass` auto-writes the constructor, ToString,
# and equality checks for you.
#
# `@dataclass(frozen=True)` — like C#'s `record` with `init`-only props.
#   `frozen=True` = IMMUTABLE — once created, fields cannot change.
#   Like a read-only struct in C#. Critical for audit trail integrity.
# ═══════════════════════════════════════════════════════════════════════
@dataclass(frozen=True)
class Transaction:
    id: str                    # Unique ID (like Guid in C#)
    type: str                  # "deposit" or "withdrawal"
    amount: float
    timestamp: str             # Formatted like "2026-07-02 14:30:00"
    balance_after: float       # Balance AFTER this transaction ran
    description: str = ""
```

Incorrect (what NOT to do — too shallow, user will correct):
```python
@dataclass(frozen=True)
class Transaction:
    """Immutable transaction record."""
    id: str
    type: str
    amount: float
```

#### 4d — Relationship / Graph Diagrams (02_architecture, 05_dependencies)
Use ASCII boxes + arrows for class hierarchies and import graphs:
```
Transaction  ←── Account  ←── Bank
   (dataclass)     (entity)     (registry)
```
For data flows use step-by-step numbered traces with actual code paths:
```
## Flow: Deposit
User enters $200
    │
    ▼
Account.deposit(200.0)
    │  balance = 500 → 700
    └── Transaction.create("deposit", 200.0, 700.0)
```

#### 4e — Wikilinks at Bottom of Every File
```
**→ [[01_overview]]** · **→ [[02_architecture]]** · **→ [[03_modules]]** · **→ [[05_dependencies]]**
```
This connects the doc set in Obsidian's graph view.

#### 4f — Section-Specific Formatting
- **01_overview**: File tree + purpose + tech stack table + quick start
- **02_architecture**: ASCII class hierarchy + component tree + architecture decision table
- **03_modules**: One `###` heading per module with real code blocks from that file. Show key functions/classes with their actual signatures.
- **04_data_flow**: 3-5 numbered flows. Each flow: user action → function calls → data mutation → output. Include actual code paths as annotations.
- **05_dependencies**: Import graph (ASCII) + npm/PyPI table + external services + cross-implementation API map (if dual codebases exist)
- **06_gaps_and_todos**: Each gap has a code snippet showing the problematic code + inline `// ←` or `# ←` annotation + suggested fix code block. End with priority todo list.

#### 4g — General Writing Rules
- Keep each file scannable: short sections, no filler prose
- Use actual file/function names, not generic placeholders
- Each README stands alone (don't assume reader has read the others)
- Write ALL 6 files for a project in parallel batches (max 5 writes per batch) for speed

### Step 5 — Batch Write All Files
Use `write_file` with all 6 files per project. `write_file` auto-creates parent directories. Batch them:
- First batch: 01_overview + 02_architecture + 03_modules
- Second batch: 04_data_flow + 05_dependencies + 06_gaps_and_todos
- Or all 6 at once if tool permits parallel writes

## Pitfalls

- **CodeGraph MCP may be rate-limited** — if it fails, fall back to terminal `find` + `grep` + `read_file`
- **Project may not have CodeGraph index** — run `codegraph init` first in that project, or use terminal-only exploration
- **Some projects are Next.js** — the automated `generate_codebase_graph.py` script only handles TS/JSX; Python/C# projects need manual exploration
- **Don't auto-run this** — wait for explicit user trigger ("create documentation for X" or "organize and recreate my whole obsidian notes")
- **Subagent exploration** is useful for deep dives — delegate codebase exploration to subagents for large projects, then compose the docs from their summaries

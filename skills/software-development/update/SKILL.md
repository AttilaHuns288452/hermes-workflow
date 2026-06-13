---
name: update
description: "General-purpose ecosystem update workflow: take a new repo/tool URL, clone it, set it up, run Graphify on it, export to Obsidian vault, check for complementary integrations, create cross-linked Obsidian docs, and refresh the knowledge graph. One command to wire any new thing into the full Hermes+Obsidian ecosystem."
triggers:
  - "/update <repo-url>"
  - "add <tool/repo> to the ecosystem"
  - "integrate <repo> into my workflow"
  - "make <repo> work with everything else"
  - "onboard <tool>"
  - "setup and document <repo>"
---

# /update

## Role
Single-command ecosystem onboarding. Takes a new repo URL or tool name, and wires it into the full environment:
1. Clone + set up the project (`software-development/setup`)
2. Build a code-level knowledge graph and export to Obsidian (`graphify-integrate`)
3. Check for complementary integrations (ECC, free-ai-tools, Graphify, etc.)
4. Create Obsidian documentation with cross-linking wikilinks
5. Refresh the Obsidian knowledge graph
6. Update `/decide` if the new repo introduces novel routing patterns

## Trigger Detection (for /decide)
The decide skill routes to `/update` when the user says:
- `/update <url>` — full ecosystem integration
- `/update <project-path>` — integrate an existing local project
- `integrate <repo> into the ecosystem`
- `add <tool> to my stack`
- `onboard <repo>`
- `make <repo> work with everything`

## Workflow

### Step 0 — Parse Input
The input can be:
1. **GitHub URL** — `https://github.com/<owner>/<repo>`
   - Extract `owner`, `repo`, `repo_path = ~/Documents/Projects/<repo>`
2. **Local path** — `~/Documents/Projects/<name>` or absolute path
   - Verify it exists, use as-is
3. **Tool name only** — search for it first:
   - Search web for the official GitHub repo
   - Ask the user which one if multiple matches

Set `PROJECT_NAME` and `PROJECT_PATH`.

### Step 1 — Clone if Not Already Present
```bash
if [ ! -d "$PROJECT_PATH" ]; then
  git clone "$URL" "$PROJECT_PATH"
fi
cd "$PROJECT_PATH"
```

### Step 2 — Read Project Identity
Identify what kind of project this is:
- **Agent framework**? (check for AGENTS.md, CLAUDE.md, skills/, agents/ directories)
- **Model/resource catalog**? (check for model lists, provider configs, API references)
- **Data catalog / directory / reference repo**? (check for a flat structure of data-files/ or category-dirs with README-based listings; the project IS a directory of things, not a tool to run; no package.json, no build scripts, nothing to install)
- **Tool/library**? (check for CLI entry point, library code)
- **Graph/visualization**? (check for graph, viz, or diagram keywords)
- **Other**?

This determines which complementary integration checks to run in Step 4 and which workflow branch to follow — data-catalog repos skip Graphify and follow a **skill-creation + website-update** path instead (see Step 4 variant below).

### Step 3 — Data-Catalog Branch (Skip Install + Graphify)

If the project was classified as **Data catalog / directory / reference repo** in Step 2, skip Steps 3–4 and follow this branch instead:

**3a. Analyze the data structure** — determine what data the catalog provides:
```bash
# Count items per category
for dir in */; do
  catname=$(echo "$dir" | sed 's/\/$//')
  readme="${dir}README.md"
  if [ -f "$readme" ]; then
    count=$(grep -c "^| \[" "$readme" 2>/dev/null)
    echo "  $catname: $count items"
  fi
done
```

**3b. Create a Hermes skill** (`skill_manage action='create'`) that makes the catalog searchable:
- **Triggers** — "find an API for", "API to", "scraper for X", "search for X in catalog"
- **Body** — document the catalog structure, include grep commands per category, show common search patterns
- **Cross-references** — route to complementary skills (e.g. mcp-integrations for MCP entries, ecc-bridge for scrapers)
- **Pitfalls** — note affiliate links, pricing, stale entries, large file sizes

See `references/data-catalog-integration.md` for a worked example (API-mega-list).

**3c. Create Obsidian documentation** — `<vault>/Projects/<PROJECT_NAME>.md` with:
- Overview, features, project structure
- Architecture Mermaid graph showing integration with Hermes ecosystem
- Search patterns and examples
- Wikilinks to related projects and skills
- Tags

**3d. Update `/decide` routing** — add the new skill to:
- Domain Skills routing section
- Complementary Setup Routing section
- Known Integration Patterns table (especially cross-refs to mcp-integrations, ecc-bridge, etc.)

**3e. Update the GH Pages website** — if the repo tracks a hermes-workflow site:
- **index.html** — add skill card to the appropriate category's skill data array
- **SKILLS_CATALOG.md** — add full entry with triggers, pipeline, integration
- **INTEGRATION.md** — add to Domain Skill Execution, Cross-Skill Integration Points, Quick Reference table, File Layout section
- **README.md** — add to Ecosystem list

**3f. Commit and push** — then verify the website is deployed:
```bash
cd ~/Documents/Projects/hw-new
git add -A
git commit -m "Integrate <name>: new skill + docs + website updates"
git push
curl -s -o /dev/null -w "%{http_code}" "https://attilahuns288452.github.io/hermes-workflow/"
```

**3g. Verify the new skill card renders** — navigate to the GH Pages site, click the relevant category tab, and confirm the card appears with the correct description.

**3g-ii. (Optional) Build/update ecosystem dashboard** — If the data catalog significantly expands the ecosystem or the user asked for a dashboard, create or update the ecosystem dashboard:
- See `references/dashboard-integration.md` for the full workflow (data gathering, HTML building, deployment, verification)
- Steps: gather stats → build/update dashboard.html → copy to hw-new/dashboard.html → add nav link + tab + skill card → update /decide routing → create/update Obsidian note → commit/push → verify

**3h. Jump to Step 9** (skip Steps 3–8 which are for code repos).

### Step 4 — Install Dependencies (code repos only)
Delegate to `software-development/setup` for project-specific setup:
- Check `package.json` → `npm install`
- Check `requirements.txt` / `pyproject.toml` → `pip install` / `uv sync`
- Check for build steps → `npm run build` / `make`
- Verify basic health (--version, --help, or import check)

### Step 4 — Build Code Knowledge Graph + Export to Obsidian
Run `graphify-integrate` workflow (call the skill or run steps directly):

```bash
cd "$PROJECT_PATH"
graphify . --no-viz 2>&1
graphify export obsidian --dir "$VAULT/Projects/$PROJECT_NAME/graphify"
```

If graphify is not installed, the integration continues without it — just skip this step.

### Step 5 — Complementary Integration Check
Check what existing repos/tools this new one complements:

| Identity | Check Against | Action |
|---|---|---|
| Agent framework | `ECC/`, external-agent-ecosystem-adapter | Route to adapter skill for Phase 2 conflict resolution |
| Coding agent CLI | `freebuff`, `opencode`, `codebuff` | Cross-reference with `free-ai-model-router` for combined model selection; create wikilink between coding agent notes |
| Model/resource | `free-ai-tools/`, `free-ai-model-router` | Cross-reference model lists; run model-recommender-workflow |
| Graph/viz tool | `obsidian-codebase-graph`, `Graphify` | Cross-link graph-related notes |
| Hermes MCP tool | `~/.hermes/config.yaml` | Check port overlaps, register MCP server |
| Standalone tool | `setup` → Phase 2.5 checklist | Run through complementary check, add note "no known complements" |

For each complement found:
1. Add `[[wikilink]]` from the existing project note → new project
2. Add `[[wikilink]]` from the new project note → existing project
3. Update the existing project note's "Related Files" or Mermaid dependency graph

### Step 6 — Create Obsidian Project Note
Create `<vault>/Projects/<PROJECT_NAME>.md` with:
- **Overview** — what the tool/repo does
- **Architecture** — how it fits in the ecosystem (Mermaid graph)
- **Related Files** section with [[wikilinks]] to complementary notes
- **Tags** — `#project <domain>`

### Step 7 — Add Cross-Linking Wikilinks
For each complement identified in Step 5:
```patch
# In complementary note's "Related Files" section:
- [[Projects/ExistingNote|ExistingNote]]
+ [[Projects/ExistingNote|ExistingNote]]
+ [[Projects/<NEW_PROJECT>|<NEW_PROJECT>]] — <relationship description>
```

### Step 8 — Update /decide If New Pattern Discovered
Check if this integration reveals a new routing pattern:

| Discovery | Action |
|---|---|
| New repo type not covered by /decide rules | Add to Complementary Setup Routing |
| New complement relationship discovered | Add to Known Integration Patterns table |
| New conflict type identified | Add to Conflict Resolution section |

See `/decide` → Session Evolution & Self-Update for the exact patch format.

### Step 9 — Refresh Knowledge Graph
```bash
python ~/AppData/Local/hermes/skills/note-taking/obsidian-knowledge-graph/scripts/scan_vault.py \
  "~/Documents/Obsidian Vault" "~/Documents/Obsidian Vault/kg_output.json"

python ~/AppData/Local/hermes/skills/note-taking/obsidian/scripts/render_kg.py \
  "~/Documents/Obsidian Vault/kg_output.json" "~/Documents/Obsidian Vault/knowledge_graph.html"
```

### Step 10 — Report
Produce a summary:
- **Project**: name, path, GitHub URL (if applicable)
- **Setup**: installed, verified
- **Graphify**: nodes/edges/exports
- **Complementary integrations found**: list
- **Cross-links added**: list (both directions)
- **Obsidian note**: path
- **Knowledge graph**: N nodes, M edges after refresh
- **/decide updated**: yes/no + what was added

## Automation Script
Where possible, call these scripts instead of manual steps:

| Step | Script |
|---|---|
| Graphify + Obsidian export | `python ~/.hermes/scripts/graphify-obsidian-integration.py <path>` |
| Vault scan | `scan_vault.py` (obsidian-knowledge-graph skill) |
| Knowledge graph render | `render_kg.py` (obsidian skill) |

## Examples

### Full ecosystem onboarding for a new GitHub repo (code project)
```bash
# What the /update skill does:
/update https://github.com/owner/repo
# 1. git clone to ~/Documents/Projects/repo
# 2. npm install / pip install
# 3. graphify . --no-viz + export obsidian
# 4. Check: complements ECC? free-ai-tools? Graphify?
# 5. Create ~/Documents/Obsidian Vault/Projects/repo.md
# 6. Add wikilinks to existing complementary notes
# 7. Refresh Obisidian knowledge graph
# 8. Patch /decide if needed
```

### Data-catalog integration (API-mega-list example)
```bash
# What the /update skill does for a data catalog:
/update https://github.com/cporter202/API-mega-list
# 1. git clone to ~/Documents/Projects/API-mega-list
# 2. Analyze: 18 categories, 10,498 Apify actors, no code to run
# 3. Skip deps, skip Graphify (no code to graph)
# 4. Create productivity/api-mega-list skill with grep-based search
# 5. Create ~/Documents/Obsidian Vault/Projects/API-mega-list.md
# 6. Update /decide: Domain Skills routing + Known Integration Patterns
# 7. Update GH Pages: index.html (skill card), SKILLS_CATALOG.md,
#    INTEGRATION.md, README.md
# 8. git commit + push + verify deployment
```

### Integrating from a local path
```bash
/update ~/Documents/Projects/my-tool
# Skips clone, starts from Step 2
```

## Pitfalls
- **Graphify requires GEMINI_API_KEY** for docs — code-only repos work without it
- **Conflict resolution happens here** — if the new repo has AGENTS.md that claims orchestrator role, flag it and add role boundary
- **Large repos** — graphify can be slow on >2000 files; use `--no-viz` and `--no-cluster`
- **MCP port overlaps** — if the new repo starts MCP servers, check Hermes config for port conflicts
- **No graphify** — if graphify is not installed, the knowledge graph step is skipped. Install with `uv tool install graphifyy` and `uv tool install "graphifyy[mcp]"`
- **Data-catalog — verify it's not a live service** — Before treating a repo as a data catalog, confirm by running Phase 0.5 checks (see `setup` skill): no API routes, no database, no server-side code. A repo that LOOKS like a directory but is actually an API server needs the code-project path, not the data-catalog path.
- **GH Pages skill data array format** — When updating index.html's skill data, entries follow `{n:'Skill Name',c:'category',d:'One-line description.'}` with COMMA after each entry. No trailing comma on the last entry. JS engines parse this strictly — a missing comma breaks the entire skills grid.
- **SKILLS_CATALOG.md table format** — The file uses `||` (double pipes) as leading table delimiters (empty first column in markdown). When patching this file, match the exact table format: `|| "Query" | Execution Path |\n||---------|---------------|\n|| "...`  Using a single `|` instead of `||` will misalign the table.
- **Website skill count accuracy** — After adding a new skill card to index.html, verify the "117" hero stat is still accurate. If the actual count changes (e.g. 117 → 120), update index.html, README.md, SKILLS_CATALOG.md, and the decide skill's references to match the real count.

## Ecosystem Documentation Export (NEW)

When the user asks to **document their Hermes setup** — make a GitHub repo resourceful, show their full skill ecosystem, create a reference — apply this workflow:

### Trigger Detection
- "make my repo resourceful"
- "document my Hermes setup"
- "show how everything integrates"
- "put my skills in the repo and how they connect"
- "create a meta-prompt for my setup"
- "make the repo representative of my full agent config"

### Phase 0 — Mirror the Actual Skills Tree (CRITICAL)

**⚠️ Do NOT create reference/stub .md files.** The user wants their actual
installed Hermes Agent skills in the repo, not summarized references.

Copy the entire Hermes Agent skills tree into the repo's `skills/` directory,
preserving the `category/skill-name/SKILL.md` directory structure:

```python
import shutil, os
from pathlib import Path

hermes_skills = Path.home() / "AppData/Local/hermes/skills"
repo_skills = Path("skills")  # relative to repo root

# Remove any old flat .md stubs
if repo_skills.exists():
    for item in repo_skills.iterdir():
        if item.is_file() and item.suffix == ".md":
            item.unlink()
        elif item.is_dir() and item.name != ".git":
            shutil.rmtree(item)

# Walk and copy every SKILL.md preserving structure
for root, dirs, files in os.walk(hermes_skills):
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    if "SKILL.md" not in files:
        continue
    src = Path(root) / "SKILL.md"
    rel = src.relative_to(hermes_skills)
    dst = repo_skills / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

# Also copy .bundled_manifest (lists shipped skills)
manifest = hermes_skills / ".bundled_manifest"
if manifest.exists():
    shutil.copy2(manifest, repo_skills / ".bundled_manifest")

# Copy supporting files from custom/authored skills
support_dirs = ("references", "scripts", "templates")
for skill_rel in ["decide", "core-identity-guard", "ecc-bridge",
                  "workflow/token-saver", "workflow/session_memory",
                  "note-taking/obsidian"]:
    src_dir = hermes_skills / skill_rel
    dst_dir = repo_skills / skill_rel
    if src_dir.exists():
        for item in src_dir.iterdir():
            if item.is_dir() and item.name in support_dirs:
                dst_sub = dst_dir / item.name
                if dst_sub.exists():
                    shutil.rmtree(dst_sub)
                if item.exists():
                    shutil.copytree(item, dst_sub)
```

**Verify** the copy produced the right structure:
```bash
# Count SKILL.md files
find skills/ -name "SKILL.md" | wc -l

# Show category listing
find skills/ -maxdepth 2 -name "SKILL.md" \
  | sed 's|skills/||;s|/.*||' \
  | sort | uniq -c | sort -rn

# Check no old flat .md remain
ls skills/*.md 2>/dev/null && echo "WARNING: flat .md files remain!" || echo "OK: no flat .md files"
```

**After copying, remove old files from git tracking:**
```bash
cd <repo-directory>
git rm -r --cached skills/ 2>/dev/null   # remove old stub entries
git add skills/                           # add new properly-structured skills
```

### Phase 1 — Audit the Current Ecosystem
Before generating reference documentation, scan the actual environment to
get accurate counts for web site and meta-prompt:

```bash
# Scan Hermes skills
find ~/AppData/Local/hermes/skills/ -maxdepth 2 -name "SKILL.md" | sort

# Count categories and skills per category
find ~/AppData/Local/hermes/skills/ -maxdepth 2 -name "SKILL.md" | sed 's|.*/skills/||;s|/.*||' | sort | uniq -c | sort -rn

# Check Hermes config for MCP servers, custom providers, model settings
grep -A3 "mcp_servers" ~/.hermes/config.yaml 2>/dev/null
grep -A5 "model" ~/.hermes/config.yaml 2>/dev/null

# Check Obsidian vault
ls ~/Documents/Obsidian\ Vault/ 2>/dev/null
```

### Phase 2 — Generate the Deliverables

#### 2a — META_PROMPT.md (Copy-Paste Prompt)
Create a self-contained markdown file the user can paste into a fresh Hermes Agent session to reproduce their full setup. Structure:

```markdown
# Meta Prompt — [User]'s Hermes Agent Setup

Copy and paste this entire block into a new Hermes Agent session to
see my complete skill ecosystem, model chain, guardrail, and workflow pipeline.

---

\`\`\`
=== HERMES AGENT SYSTEM CONFIGURATION ===
...
\`\`\`

---

## Custom Skills (Loaded via \`skill_view\`)

### 1. decide — Routing Brain
**Path:** \`~/.hermes/skills/decide/SKILL.md\`
**Description:** [one-liner]
**Key behaviors:** [how it affects the session]

[... repeat for each custom skill ...]

---

## Pipeline (Execution Order)
Every request runs through this sequence:
1. **session_memory** — [what it does]
2. **🛡️ Core Identity Guardrail** — [what it does]
3. **/decide** — [what it does]
4. **⚡ Token Saver** — [what it does]
5. **🧬 Graphify + CodeGraph** — [what it does]
6. **🎯 Domain Skills** — [what they do]
7. **🤖 Model Routing** — [what it does]
8. **📝 Obsidian Docs** — [what it does]
9. **🕸️ KG Refresh** — [what it does]

---

## Model Chain
| Layer | Provider | Models | When Used |
|-------|----------|--------|-----------|
| 1 | OpenCode | 5 free models | Primary/default |
| 2 | Freebuff | 6 cloud models | Fallback |
| 3 | FreeLLMAPI | 110+ models | Wide selection |
| 4 | OpenRouter | 29+ free models | Research |
| 5 | Paid BYOK | - | Last resort |

---

## Key Config
- **Obsidian vault:** [path]
- **CodeGraph MCP:** [status]
- **Graphify:** [version, nodes]
- **Custom providers:** [list]
```

**Key design principles:**
- Self-contained — a fresh session should understand the full setup from this one file.
- List all custom skills with their actual trigger conditions and behavior implications.
- Include the pipeline execution order so the reader knows what runs first.
- Include the model chain with fallback layers.
- Keep under 450 lines — dense reference, not prose.

#### 2b — SKILLS_CATALOG.md (Full Skill Registry)
Compile all skills across all categories with:
- **Category header** with count of skills
- **Per-category summary**: skill names, triggers, use cases, integration notes
- **Custom/author-authored skills** prominently flagged (⭐)
- **Bundle rules** called out (e.g. Obsidian 3-skill bundle)
- **Pipeline integration** — where each category plugs in
- **Use cases** — common request types each skill handles

Structure template:
```markdown
# Skill Catalog — [User]'s Hermes Agent Ecosystem
**[N] skills · [M] categories**

---

## ⭐ Custom Skills (Author-Authored)
| Skill | Trigger | Use Case | Pipeline Stage |
|-------|---------|----------|----------------|
| decide | always | Routing brain | Step 3 |
| ... | ... | ... | ... |

---

## [Category Name] — [N] skills
[Description and integration]
| Skill | Trigger | Description |
|-------|---------|-------------|
| ... | ... | ... |
```

**Key design principles:**
- Group by category, not alphabetically.
- For large categories (16+ skills), use a combined entry with sub-list.
- Include total count at top.
- Use emoji labels for quick scanning.
- Include bundle rules in a callout section.

#### 2c — INTEGRATION.md (Architecture + Data Flow)
Three complementary views:

**View 1 — ASCII Architecture Diagram**
Show the full pipeline as a box-and-arrow diagram: session_memory → guardrail → /decide → token-saver → Graphify/CodeGraph → domain skills → model routing → Obsidian docs → KG refresh.

**View 2 — 8-Step Data Flow**
For each pipeline step, document:
- What tool(s) it calls
- What data it reads/writes
- Which skills are responsible
- What output it passes to the next step

**View 3 — Cross-Skill Integration Matrix**
Show which skills depend on which and how data flows between them:
- decide → reads triggers from all skills → orders invocation
- token-saver → probes Graphify MCP + CodeGraph MCP → decides if read_file is needed
- obsidian-docs → writes to vault → triggers KG refresh
- Model chain → each layer checked before next with fallback rules

#### 2d — Website Update
Update the repo's index.html to reflect the full ecosystem:
1. **Hero stats** — update skill count, add category count
2. **Nav links** — add links to SETUP.md, META_PROMPT.md, SKILLS_CATALOG.md, INTEGRATION.md
3. **Skills section** — browsable skill catalog with:
   - Category filter tabs (click to filter: Custom, Creative, Dev, etc.)
   - Cards with skill names, categories, and one-line descriptions
   - Visual distinction for custom/authored skills
   - Links to the full markdown docs
4. **Footer** — link to all major docs files, updated stats
5. **Category filter JS** — filter cards by data-cat attribute when tab is clicked
   ```javascript
   document.querySelectorAll('.cat-tab').forEach(btn => {
     btn.addEventListener('click', () => {
       document.querySelectorAll('.cat-tab').forEach(b => b.classList.remove('active'));
       btn.classList.add('active');
       const cat = btn.dataset.cat;
       document.querySelectorAll('#skillsGrid .card').forEach(card => {
         card.style.display = (cat === 'all' || card.dataset.cat === cat) ? '' : 'none';
       });
     });
   });
   ```

### Phase 3 — Commit and Verify
```bash
cd <repo-directory>
git add -A
git status
git commit -m "Add full ecosystem documentation: META_PROMPT.md, SKILLS_CATALOG.md (N skills, M categories), INTEGRATION.md pipeline flow, website updated with interactive catalog"
git push origin <branch>
```

After push, verify:
- Website loads at GitHub Pages URL
- Nav links navigate to correct anchors
- Category filter tabs work (click each category, verify filtering)
- Meta prompt file opens and renders correctly
- Skill catalog numbers match actual skill count

### Pitfalls
- **Stats drift**: Skill count, KG nodes, and model count in meta-prompt/website are snapshots. Add "Last updated: [date]".
- **Website file size**: index.html can grow large (100KB+) with inline CSS+JS. Keep the skills catalog section concise — one card per category group, not per individual skill.
- **Custom skills in the repo**: The actual SKILL.md files belong in `skills/` subdirectory of the repo, referenced but not duplicated by the catalog.
- **Skill count accuracy**: Use `find ~/AppData/Local/hermes/skills/ -maxdepth 2 -name "SKILL.md" | wc -l` for an accurate count. Never guess.
- **Meta-prompt paths**: Contains system paths that only make sense on the author's machine. Frame as "this user's setup" rather than a universal template.
- **Graphify CLI limitations**: On Windows, `graphify export obsidian` doesn't exist (v0.8.37). Don't claim it in documentation — stick to commands that actually work (`query`, `explain`, `path`, `benchmark`, etc.).
- **Stub .md files trap**: When documenting a Hermes setup, it's tempting to create clean reference stubs (e.g., `decide.md`, `token-saver.md`). **Don't.** The user wants their actual installed skills mirrored verbatim. Copy `~/.hermes/skills/` preserving `dir/SKILL.md` structure — never summarize or flatten into single `.md` files. See Phase 0 above.
- **Windows path mismatch between tools**: On Windows, `execute_code` (Python) and `terminal` (git-bash) resolve `/tmp` differently.
  - `execute_code` runs as a native Windows process: `Path("/tmp")` → `C:\tmp\`
  - `terminal` runs via git-bash: `/tmp` → `C:\Users\<user>\AppData\Local\Temp\`
  - **Fix**: Always use `os.environ["TEMP"]` or the full native Windows path (`C:\Users\<user>\AppData\Local\Temp\...`) in Python scripts that work with files created/modified by `terminal`. Or do all work in a single tool (e.g., do everything from Python via `from hermes_tools import terminal` instead of mixing `execute_code` and `terminal`).

## Related Skills
- `software-development/setup` — performs Phase 1-3 (clone, install, verify)
- `software-development/graphify-integrate` — runs Graphify + Obsidian export
- `decide` — routing brain; gets patched with new patterns
- `workflow/session_memory` — retrieves context from prior sessions
- `note-taking/obsidian` — creates/manages Obsidian notes (loaded via bundle rule)
- `software-development/hermes-agent-skill-authoring` — authoring SKILL.md files with proper frontmatter (referenced when adding actual skill files to the repo)
- `workflow/free-ai-model-router` — model chain documentation (referenced in model routing section of the catalog)

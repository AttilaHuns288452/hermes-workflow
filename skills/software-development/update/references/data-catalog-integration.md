# Data-Catalog Integration — Worked Example

**Based on:** API-mega-list (cporter202/API-mega-list) — June 2026 session  
**Pattern:** Clone a data-catalog repo → create Hermes skill → Obsidian doc → /decide routing → GH Pages website update → commit/verify

---

## When to Use This Pattern

This pattern applies when the target repo **IS the data** — a directory of APIs, tools, models, links, or other resources — NOT a tool to install and run. Key indicators:
- No `package.json`, `requirements.txt`, `Cargo.toml`, or `Makefile`
- No server-side code, no API routes, no database schemas
- Structure: one directory per category, each with a `README.md` containing listings
- The purpose is to **find things**, not to **run things**

## Step-by-Step Process

### 1. Clone and Analyze

```bash
cd ~/Documents/Projects
git clone --depth 1 <repo-url> <repo-name>

# List categories
for dir in <repo-name>/*/; do
  catname=$(echo "$dir" | sed 's/\/$//')
  readme="${dir}README.md"
  if [ -f "$readme" ]; then
    count=$(grep -c "^| \[" "$readme" 2>/dev/null)
    echo "  $catname: $count items"
  fi
done
```

### 2. Create the Hermes Skill

Use `skill_manage(action='create', category='<category>')`. The SKILL.md should include:

```yaml
triggers:
  - "find an API for"
  - "search APIs for"
  - "API that can"
  - "browse APIs"
  - "available APIs"
  - "<repo-keyword>"
```

Body sections:
- **Overview** — link to repo, local path, total item count
- **Repository Structure** — tabular listing of each category with item counts
- **How to Search** — grep commands: by keyword across all categories, by category, with context, random pick
- **Category Inventory** — table: #, Category, Dir, Items, Typical Use Cases
- **Common Search Patterns** — concrete grep commands for common use cases
- **Integration with Existing Skills** — which complementary skills to route to
- **Pitfalls** — affiliate links, stale data, large file sizes, pricing notes
- **Related**

### 3. Create Obsidian Documentation

Write `<vault>/Projects/<PROJECT_NAME>.md` with:
- **Overview** — source repo, local path, type, scale
- **Features** — bullet list of key capabilities
- **Project Structure** — code-block tree
- **Architecture** — Mermaid graph showing integration into the Hermes pipeline
- **Code Patterns** — shell one-liners for common operations
- **Related Files** — wikilinks to related project notes and Hermes skills
- **Tags** — `#project <domain>`

### 4. Update /decide Routing

Three places to update in `~/.hermes/skills/decide/SKILL.md`:

**A. Domain Skills section** — add routing entry:
```
- **API search / find an API / need an API that can X** → `<category>/<skill-name>`
  - Routes to grep-based search across N categories of M items
  - MCP server queries → also route to `mcp-integrations` for wiring
  - Scraper queries → also route to `ecc-bridge` for alternatives
```

**B. Complementary Setup Routing section** — describe how the skill wires into the broader ecosystem:
```
- **<Skill-name> (<one-line>)** → route to BOTH `setup` AND
  `<category>/<skill-name>`. After cloning the repo (path),
  the skill provides grep-based search across N categories.
  For MCP Servers found in the list, route to `mcp-integrations`.
  For scraping APIs, cross-reference with `ecc-bridge`.
  Has M items across N categories.
```

**C. Known Integration Patterns table** — add rows:
```
| Skill + Complementary Skill | Trigger | Action |
|---|---|---|
| <skill-name> + MCP Servers | User finds an MCP Server in the list | Route to `mcp-integrations` for Hermes config wiring |
| <skill-name> + ECC Scrapers | User finds a web scraper in the list | Cross-reference with ECC agents via `ecc-bridge` |
```

### 5. Update GH Pages Website

For projects with a hermes-workflow GH Pages site at `~/Documents/Projects/hw-new/`:

**A. index.html** — Add a skill card to the skills data array:
```javascript
// Find the right category section, add after alphabetically-adjacent entry
{n:'<Display Name>',c:'<category>',d:'<one-line description>.'},
```

The object format: `{n:'Name',c:'category',d:'Description.'}` — comma after each entry.

**B. SKILLS_CATALOG.md** — Add a full entry following the existing format:
```
### <skill-name>
- **What:** <bold description> — <details>
- **Trigger:** <trigger phrases>
- **Pipeline:** Step 5 — <routing details>
- **Integration:** <cross-refs>
```

Also increment the count in the header: `**N skills**`.

**C. INTEGRATION.md** — Four places:
1. **Domain Skill Execution** (Step 5) — add `├─ <Category>: <skill-path> (<one-line>)`
2. **Cross-Skill Integration Points** — add a new subsection showing the pipeline: data source → skill → MCP wiring
3. **Quick Reference table** — add a row: `|| "<Query pattern>" | session_memory → guardrail → /decide → <skill-path> → <follow-up actions> → result |`
4. **File Layout section** — update the category count: `├── <category>/ → N skills (<skill-name>, ...)`

**D. README.md** — Add to Ecosystem list:
```markdown
- **<Display Name>** — <one-line with count> (searchable via `<skill-path>` skill)
```

### 6. Commit, Push, Verify

```bash
cd ~/Documents/Projects/hw-new
git add -A
git status
git commit -m "Integrate <name>: new skill + docs + website updates

- Created <category>/<skill-name> Hermes skill (<count> items / <N> categories)
- Created Obsidian project note (Projects/<name>.md) with Mermaid graph
- Updated /decide skill with API-search routing + Known Integration Patterns
- Updated SKILLS_CATALOG.md (N skills), INTEGRATION.md, README.md
- Added <name> card to index.html (<category> tab)
- Website shows N skills (+1) across all categories"
git push
```

Then verify:
```bash
# Check HTTP status
curl -s -o /dev/null -w "%{http_code}" "https://attilahuns288452.github.io/hermes-workflow/"

# Verify text renders in browser
# Navigate to the site, click the category tab, confirm the new card appears
```

## Concrete Example: API-mega-list

| Step | What Was Done | Files Changed |
|------|---------------|---------------|
| Clone | `git clone --depth 1 https://github.com/cporter202/API-mega-list.git` | — |
| Analyze | 18 categories, 10,498 APIs counted | — |
| Create Skill | `productivity/api-mega-list` — grep-based search, category table, cross-refs | `~/.hermes/skills/productivity/api-mega-list/SKILL.md` |
| Obsidian Note | ATM-Machine quality with Mermaid architecture graph | `~/Documents/Obsidian Vault/Projects/API-mega-list.md` |
| Update /decide | Domain Skills + Complementary Setup + Known Integration Patterns | `~/.hermes/skills/decide/SKILL.md` (3 patches) |
| Update index.html | Added `{n:'API Mega List',c:'productivity',...}` | `hw-new/index.html` (+1 line) |
| Update SKILLS_CATALOG.md | Full entry + count 135→136 | `hw-new/SKILLS_CATALOG.md` (+30 lines) |
| Update INTEGRATION.md | Domain skills + Cross-Skill + Quick Reference + File Layout | `hw-new/INTEGRATION.md` (4 patches) |
| Update README.md | Added to Ecosystem list | `hw-new/README.md` (+1 line) |
| Commit & Push | `b78ae90` → master | 4 files, 40 insertions, 8 deletions |
| Verify | HTTP 200, "API Mega List" text present on page | — |

## Related Hermes Skills

- `productivity/api-mega-list` — the skill created by this exact integration
- `software-development/setup` — Phase 2.5 delegates data-catalog repos to /update
- `software-development/hermes-agent-skill-authoring` — for skill authoring conventions

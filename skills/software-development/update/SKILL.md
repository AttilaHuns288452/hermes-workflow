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
graphify update . 2>&1

# Then create the Obsidian note manually from graph stats
# (There is NO graphify export command — create notes with the obsidian skill)
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
# 3. graphify update . + create Obsidian note manually from graph stats
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
- **SKILLS_CATALOG.md table format** — The file uses `||` (double pipes) as leading table delimiters (empty first column in markdown). When patching this file, match the exact table format: `|| "Query" | Execution Path |\\n||---------|---------------|\\n|| "..."`  Using a single `|` instead of `||` will misalign the table.
- **Website skill count accuracy** — After adding a new skill card to index.html, verify the hero stat is still accurate. Compare: `find ~/AppData/Local/hermes/skills/ -name 'SKILL.md' | wc -l` (local) vs `find skills/ -name 'SKILL.md' | wc -l` (repo). The local and repo counts can differ when the repo has bundled/reference-only skills. Update index.html, README.md, SKILLS_CATALOG.md, and the decide skill's references with the repo's count — not the local install's count.
- **Misleading template placeholders** — `api_key: none` in a config template passes every secret scan (it's not a real key) but silently breaks all API calls. Apply the template placeholder verification (Phase 2d) before every commit. Other common offenders: `password: password`, `secret: ""`, `key: ""`, `token: none`.
- **README install command drift** — After mirroring a tool's install instructions into README.md or SETUP.md, the command can go stale when the upstream project changes build systems (pip→npm, npm→pnpm, setup.py→pyproject.toml). Cross-reference install commands against the actual project's package manifests before each ecosystem doc export.

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

# Copy supporting files from ALL skills that have them (generic walk)
support_dirs = {"references", "scripts", "templates", "assets"}
for root, dirs, files in os.walk(hermes_skills):
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    if "SKILL.md" not in files:
        continue
    skill_rel = Path(root).relative_to(hermes_skills)
    for sd in support_dirs:
        src_dir = hermes_skills / skill_rel / sd
        dst_dir = repo_skills / skill_rel / sd
        if src_dir.exists():
            if dst_dir.exists():
                shutil.rmtree(dst_dir)
            shutil.copytree(src_dir, dst_dir)
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

### Phase 0a — 📋 Content Accuracy Audit (Local vs Repo)
**⚠️ Symlinks**: On MSYS/Windows, `find` does NOT follow symlinks by default. LLMQuant skills at `~/.hermes/skills/llmquant-*` are symlinks to `~/.agents/skills/`. Always use `find -L` when counting local skills: `find -L ~/AppData/Local/hermes/skills/ -name 'SKILL.md' | wc -l`. The non-L value will be lower (misses symlinked skills).

**Why:** After mirroring, the repo may be stale or missing skills relative to the local install. Reference files may have diverged (local added warnings, repo fixed secrets). Run this check before the security audit to find and fix silent drift.

**Step 1 — Compare total counts:**
```bash
echo "Local: $(find ~/AppData/Local/hermes/skills/ -name 'SKILL.md' | wc -l)"
echo "Repo:  $(find skills/ -name 'SKILL.md' | wc -l)"
```

**Step 2 — List skills missing from repo (local-only):**
```bash
comm -13 <(cd skills && find . -name 'SKILL.md' | sed 's|./||;s|/SKILL\.md||' | sort) \
         <(find ~/AppData/Local/hermes/skills/ -name 'SKILL.md' | sed 's|.*/skills/||;s|/SKILL\.md||' | sort)
```
Any results = skills that need to be copied to the repo. Copy them with their full directory tree.

**Step 3 — List skills missing from local install (repo-only):**
```bash
comm -23 <(cd skills && find . -name 'SKILL.md' | sed 's|./||;s|/SKILL\.md||' | sort) \
         <(find ~/AppData/Local/hermes/skills/ -name 'SKILL.md' | sed 's|.*/skills/||;s|/SKILL\.md||' | sort)
```
Any results = skills the repo has but local doesn't — expected if the repo includes bundled/reference-only skills. Document the delta.

For each repo-only domain skill, check if the local Hermes setup already supports the domain through other means (MCP server, config keys, API tokens). Example: the 18 `llmquant-*` skills exist in the repo but aren't installed locally — yet the `llmquant-data` MCP server is wired in `~/.hermes/config.yaml` with an active API key. The user can query data via MCP but the local decide skill won't route to llmquant guidance skills.

**When repo-only skills have local config support:** Consider installing the missing skills from the repo → local `~/.hermes/skills/` to enable full routing + domain guidance, not just raw MCP data access. After installing, update the decide skill with routing entries for the new domain.

**Step 4 — Content-compare every common skill:**
```bash
comm -12 <(cd skills && find . -name 'SKILL.md' | sed 's|./||;s|/SKILL\.md||' | sort) \
         <(find ~/AppData/Local/hermes/skills/ -name 'SKILL.md' | sed 's|.*/skills/||;s|/SKILL\.md||' | sort) \
  | while read skill; do
      repo_f="skills/$skill/SKILL.md"
      local_f="$HOME/AppData/Local/hermes/skills/$skill/SKILL.md"
      if [ -f "$repo_f" ] && [ -f "$local_f" ]; then
        diff -w "$local_f" "$repo_f" > /dev/null 2>&1 || echo "  MISMATCH: $skill"
      fi
    done
```
Any result = SKILL.md content has drifted. Investigate which direction has newer content (check timestamps: `ls -la "$local_f" "$repo_f"`). Copy the newer version.

**Step 5 — Check reference files for merge-necessary divergence:**
```bash
for skill in $(comm -12 <(cd skills && find . -name 'SKILL.md' | sed 's|./||;s|/SKILL\.md||' | sort) \
                      <(find ~/AppData/Local/hermes/skills/ -name 'SKILL.md' | sed 's|.*/skills/||;s|/SKILL\.md||' | sort)); do
  for ref_dir in references scripts templates assets; do
    if [ -d "$HOME/AppData/Local/hermes/skills/$skill/$ref_dir" ] || [ -d "skills/$skill/$ref_dir" ]; then
      diff -rqw "$HOME/AppData/Local/hermes/skills/$skill/$ref_dir" "skills/$skill/$ref_dir" 2>/dev/null \
        | grep -v 'Only in' || true
    fi
  done
done
```
Lines starting with `Content` indicate a file exists in both but differs — these need manual merge attention (e.g., repo has a security fix, local has new warnings).

**Step 6 — Resolve content differences:**
- **SKILL.md mismatches**: Check timestamps. If local is newer, `cp local_f repo_f`. If repo is newer, investigate why remote was directly edited.
- **Reference file merges**: When both sides have unique content (local has warnings, repo has redacted secrets), copy the local version to the repo first, then apply the repo's security redactions on top.
- **Missing skills**: `cp -r` the full skill directory including support files.
- **After all merges**: Re-run `diff -w` to confirm zero content differences across the common set.

**Step 7 — Check for flat `.SKILL.md` files and non-SKILL.md support files:**
The content audit above only covers `SKILL.md`. But Hermes creates additional support files that should also be mirrored:

```bash
# Find flat .SKILL.md files (single-file skills) local-only
echo "=== Flat .SKILL.md files ==="
comm -13 <(cd skills && find . -name '*.SKILL.md' | sed 's|./||' | sort) \
         <(find ~/AppData/Local/hermes/skills/ -name '*.SKILL.md' | sed 's|.*/skills/||' | sort)

# Check for missing non-SKILL.md support files (workflows, scripts, references, assets)
echo "=== Missing support directories ==="
for dir in workflows scripts references assets templates; do
  for skill_dir in ~/AppData/Local/hermes/skills/*/ ~/AppData/Local/hermes/skills/*/*/; do
    local_sub="$skill_dir$dir"
    rel_name=$(echo "$skill_dir" | sed 's|.*/skills/||')
    repo_sub="skills/$rel_name$dir"
    if [ -d "$local_sub" ] && [ ! -d "$repo_sub" ]; then
      echo "  MISSING: $rel_name$dir"
    fi
  done
done

# Check for missing standalone files (LICENSE, README.md, *.md at flat level)
echo "=== Missing standalone files ==="
find ~/AppData/Local/hermes/skills/ -maxdepth 2 -name 'LICENSE*' -o -name 'README.md' -o -name 'CHANGELOG*' 2>/dev/null | \
while read f; do
  rel=$(echo "$f" | sed 's|.*/skills/||')
  [ ! -f "skills/$rel" ] && echo "  MISSING: $rel"
done
```

For each missing file:
- **Flat `.SKILL.md` files**: Copy to repo preserving path
- **Support directories**: `cp -r` the entire directory
- **Standalone files**: Copy to repo

**Step 8 — Update decide routing for newly installed skills:**
After adding repo-only domain skills to the local install (e.g., bulk-installing 18 `llmquant-*` skills), update the decide skill to route to them:
1. Count the new skills: `find ~/AppData/Local/hermes/skills/ -name 'SKILL.md' | wc -l`
2. Update decide's local skill count reference in both places (e.g., "117 skills" → new count)
3. Add a domain routing entry in decide's Domain Skills section for the new category
4. Sync the updated decide SKILL.md to the repo's copy as well

**Design principle:** The user expects content fidelity between local install and repo mirror. Structural mirroring (file exists) is insufficient — actual content must match too.

### Phase 0.5 — 🔒 Security Audit (Pre-Commit Secret Scan)

**⚠️ Critical**: Mirrored skills can contain real API keys, credentials, and tokens in `references/` files, code examples, and setup transcripts. Before proceeding to documentation generation, run a thorough secret scan.

**Step 1 — Scan all mirrored files for API key patterns**:
```bash
cd <repo-root>
for pattern in \
  'sk-[A-Za-z0-9]\{20,\}' \
  'freellmapi-[a-f0-9]\{32,\}' \
  'ghp_[A-Za-z0-9]\{36,\}' \
  'gho_[A-Za-z0-9]\{36,\}' \
  'ghu_[A-Za-z0-9]\{36,\}' \
  'ghb_[A-Za-z0-9]\{36,\}' \
  'xox[bpras]-[A-Za-z0-9-]\{10,\}' \
  'AIza[0-9A-Za-z_-]\{35\}' \
  'AKIA[0-9A-Z]\{16\}' \
; do
  matches=$(grep -rn "$pattern" --include='*.md' --include='*.yaml' --include='*.yml' \
    --include='*.json' --include='*.py' --include='*.sh' --include='*.example' \
    --include='*.template' skills/ 2>/dev/null | grep -v '\[REDACTED\]' | head -5)
  if [ -n "$matches" ]; then
    echo "🔴 LEAKED: $pattern"
    echo "$matches"
  fi
done
```

**Step 2 — Check `.env.example` and `config.yaml.template`** for real keys:
```bash
grep -v '^#\|^$' .env.example | grep -v 'YOUR_\|CHANGE_ME\|PLACEHOLDER' && echo "⚠️ Real values in .env.example"
grep -n 'api.key\|api_key\|password\|token\|secret' config.yaml.template 2>/dev/null | grep -v 'CHANGE_ME\|<.*>\|your-' && echo "⚠️ Suspicious values in config.yaml.template"
```

**Step 3 — Check git history for previously committed secrets**:
```bash
for pattern in 'freellmapi-[a-f0-9]\{32,\}' 'sk-[A-Za-z0-9]\{20,\}'; do
  for commit in $(git log --all --format="%H"); do
    git show "$commit" --textconv 2>/dev/null | grep -q "$pattern" && \
      echo "🔴 CRITICAL: '$pattern' found in commit $commit"
  done
done
```

**Remediation workflow** (when secrets are found):
1. 🔑 **Rotate** the exposed key on the service immediately
2. 🧹 **Scrub** the key from all local files → replace with `[REDACTED]`
3. 📝 **Update** `.env` + Hermes auth with the new rotated key
4. 🗑️ **Amend** git history: `git commit --amend --no-edit` (HEAD) or filter-branch (older)
5. 📤 **Force push**: `git push --force-with-lease origin <branch>`
6. ✅ **Verify** the remote shows a clean commit history
7. 🔄 **Notify** anyone who may have cloned the repo since the leak

**Step 4 — Only proceed** if all scans pass (no real secrets found).

See `references/secret-scan-patterns.md` for additional provider-specific patterns and the full key-rotation workflow script.

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
#### 2d — Website Update + Config Templates

Update the repo's index.html to reflect the full ecosystem,
and generate plug-and-play config templates from the live setup:

**Website update:**
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

**Config templates** (for plug-and-play reproduction):
- Create **`config.yaml.template`** — copy the real `~/.hermes/config.yaml`, replacing user-specific values (API keys, paths) with placeholders marked `# ← CHANGE ME`. Include: MCP server definitions, model provider settings, provider sections, any custom config. If the real config has no model section but `hermes status` shows model settings, document the expected config format.
- Create **`.env.example`** — document every env var the setup needs: API key names (without values), path overrides, port preferences, model routing options. Use descriptive variable names. Group by category (required auth, optional auth, path overrides, behavior flags).
- Both files belong at the repo root. Reference them from README.md in the quick-start section.

**Template placeholder verification (critical):** After creating or updating config templates, check for misleading default values that pass security scans but silently break at runtime:
```bash
cd <repo-directory>
# Check for values that look valid but aren't
grep -n 'api_key: none\|password: password\|secret: ""\|key: ""' config.yaml.template .env.example 2>/dev/null
# Check for bare 'none' or empty-string placeholders in config values
grep -nE ':\s+none\s*$|:\s+""\s*$' config.yaml.template 2>/dev/null
```
Any match = replace with a proper `YOUR_*_HERE` placeholder marked `# ← CHANGE ME`. Never leave `none` or empty strings as defaults — a new user will try the template verbatim, get silent failures, and not know why.

**Install command verification:** After generating any install/setup instructions for a tool in README.md or SETUP.md, verify the command actually matches the tool's real install method:
```bash
# If README says "pip install" but the project uses npm → fix it
# Check: does the project have package.json? requirements.txt? pyproject.toml?
ls <project-dir>/package.json 2>/dev/null && echo "npm/yarn project"
ls <project-dir>/requirements.txt 2>/dev/null && echo "pip project"
ls <project-dir>/pyproject.toml 2>/dev/null && echo "pip/uv project"
```
Cross-reference the README's install instructions against these files. A mismatch (e.g. `pip install` on an npm project) will immediately confuse new users.

#### 2e — Create SETUP.md (Step-by-Step Setup Guide)

Create a step-by-step setup guide at the repo root that walks a first-time user
through all steps to get the full ecosystem running.

**When to create/update:** This is needed whenever the ecosystem has a complex
self-hosted component (FreeLLMAPI, Graphify, CodeGraph) that requires manual
dashboard setup, API key generation, or multi-step wiring. A README with `cp templates`
is not enough — new users need a numbered walkthrough.

**Structure template:**
```markdown
# Hermes Workflow — Full Setup Guide

> **N steps** to get the complete pipeline running.

## Step 1: Install Hermes Agent
[One-line install command. No prose.]

## Step 2: Clone This Repo
`git clone https://github.com/USER/REPO.git`

## Step N: Install & Configure [Complex Tool]
[Detailed sub-steps with copy-paste commands:
  a. Clone & install
  b. Start the services
  c. Open admin dashboard (URL)
  d. Create admin account (default credentials)
  e. Get unified API key
  f. Wire into Hermes (three options: auth CLI, config file, .env)
  g. Verify with curl]
...
```

**Key design principles:**
- Every step has a concrete, copy-pasteable command
- The most complex tool gets sub-steps (6a–6g) with dashboard URL, admin account creation, key retrieval
- Troubleshooting table at the end covers the 3–5 most common failure modes
- Link back to detailed docs at the bottom
- Keep each step 2–5 lines — scannable

**After creating:**
1. Update README.md to add a nav link: `> **Detailed instructions:** See [SETUP.md](SETUP.md)`
2. Update META_PROMPT.md model routing section to reference SETUP.md for first-time tool setup
3. Verify with `curl -s -o /dev/null -w "%{http_code}" "$GITHUB_PAGES_URL/SETUP.md"` returns 200 after push

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
- **Security scan: 90+ languages etc.** — The OCR skill's language coverage is a different domain; use `(skills|SKILL).*[0-9]{2,}` to disambiguate.
- **Skill count accuracy**: Use `find ~/AppData/Local/hermes/skills/ -maxdepth 2 -name "SKILL.md" | wc -l` for an accurate count. Never guess.
- **Repo count ≠ local count**: The repo's skill count (`find skills/ -name "SKILL.md" | wc -l` inside the repo) may differ from the local install. When updating ecosystem docs (index.html, dashboard.html, decide SKILL.md, SKILLS_CATALOG.md), verify counts against the **repo's own filesystem** — not the local install. The repo can have more skills (e.g., bundled/reference skills) than the active local set.
- **Meta-prompt paths**: Contains system paths that only make sense on the author's machine. Frame as "this user's setup" rather than a universal template.
- **Graphify CLI limitations**: On Windows, `graphify export obsidian` doesn't exist (v0.8.37). Don't claim it in documentation — stick to commands that actually work (`query`, `explain`, `path`, `benchmark`, etc.).
- **Stub .md files trap**: When documenting a Hermes setup, it's tempting to create clean reference stubs (e.g., `decide.md`, `token-saver.md`). **Don't.** The user wants their actual installed skills mirrored verbatim. Copy `~/.hermes/skills/` preserving `dir/SKILL.md` structure — never summarize or flatten into single `.md` files. See Phase 0 above.
- **Windows path mismatch between tools**: On Windows, `execute_code` (Python) and `terminal` (git-bash) resolve `/tmp` differently.
  - `execute_code` runs as a native Windows process: `Path("/tmp")` → `C:\tmp\`
  - `terminal` runs via git-bash: `/tmp` → `C:\Users\<user>\AppData\Local\Temp\`
  - **Fix**: Always use `os.environ["TEMP"]` or the full native Windows path (`C:\Users\<user>\AppData\Local\Temp\...`) in Python scripts that work with files created/modified by `terminal`. Or do all work in a single tool (e.g., do everything from Python via `from hermes_tools import terminal` instead of mixing `execute_code` and `terminal`).
- **`find` misses symlinked skill directories on MSYS/Windows**: MSYS git-bash `find` does NOT follow symlinks by default. If any skills are symlinks (e.g., LLMQuant skills at `~/.hermes/skills/llmquant-*` → `~/.agents/skills/llmquant-*`), `find ~/.hermes/skills/ -name "SKILL.md"` silently omits them — giving a misleadingly low count.
  - **Always use `find -L`** when counting installed skills: `find -L ~/.hermes/skills/ -name "SKILL.md" | wc -l`
  - For the repo mirror (no symlinks), plain `find` is fine: `find skills/ -name "SKILL.md" | wc -l`
  - To disambiguate, compare `find` vs `find -L`: any difference reveals symlinked skills that should be verified as intact before treating the count as authoritative.
  - When a skill category shows 0 matches in a `find` scan but `ls -d` shows the files exist, 90% of the time the directories are symlinks — rerun with `find -L`.

## Related Skills
- `software-development/setup` — performs Phase 1-3 (clone, install, verify)
- `software-development/graphify-integrate` — runs Graphify + Obsidian export
- `decide` — routing brain; gets patched with new patterns
- `workflow/session_memory` — retrieves context from prior sessions
- `note-taking/obsidian` — creates/manages Obsidian notes (loaded via bundle rule)
- `software-development/hermes-agent-skill-authoring` — authoring SKILL.md files with proper frontmatter (referenced when adding actual skill files to the repo)
- `workflow/free-ai-model-router` — model chain documentation (referenced in model routing section of the catalog)

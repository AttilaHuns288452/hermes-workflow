# Dashboard Integration (Ecosystem Visualization)

## Overview

When a new data-catalog or ecosystem component is added, you may also build
or update a **live ecosystem dashboard** — a single-file HTML page that
aggregates stats from across the Hermes Agent setup (projects, skills,
graphify/codegraph nodes, model counts, API catalogs, MCP servers, ECC agents)
and deploys alongside the main GH Pages site.

## When to Build a Dashboard

Build (or update) a dashboard when:

- The user asks for "a dashboard", "show me everything", "ecosystem view",
  "visual summary of the setup"
- A new data catalog is added that substantially expands the ecosystem scale
  (e.g. 10K+ new entries that shift the overall API/agent/project count)
- The ecosystem crosses a meaningful threshold (100 skills, 1K graph nodes, etc.)
- The user says "set this up" and the integration scope is broad enough to
  merit a central reference page

## Workflow

### Step 1 — Gather Data Sources

Collect all stats from the live environment:

```bash
# Projects
ls ~/Documents/Projects/ | grep -vE 'hw-new|^hermes-|^\.'

# Skill count
find ~/AppData/Local/hermes/skills/ -maxdepth 2 -name "SKILL.md" | wc -l

# Skill categories
find ~/AppData/Local/hermes/skills/ -maxdepth 2 -name "SKILL.md" \
  | sed 's|.*/skills/||;s|/.*||' | sort | uniq -c | sort -rn

# Graphify stats (parse graph.json in each project)
for f in ~/Documents/Projects/*/graphify-out/graph.json; do
  [ -f "$f" ] && python -c "import json; d=json.load(open('$f')); print(f'$(basename $(dirname $(dirname $f))): {len(d[\"nodes\"])} nodes, {len(d[\"edges\"])} edges')"
done

# CodeGraph stats
codegraph stats 2>/dev/null || echo "CodeGraph stats unavailable"

# Free model ecosystem
ls ~/Documents/Projects/free-llm-api/ 2>/dev/null
ls ~/Documents/Projects/CodeBuff/open-chat-api/ 2>/dev/null

# API Mega List
for d in ~/Documents/Projects/API-mega-list/*/; do
  catname=$(basename "$d")
  count=$(grep -c "^| \[" "${d}README.md" 2>/dev/null)
  [ -n "$count" ] && echo "  $catname: $count"
done

# MCP servers (from Hermes config)
grep -A2 "mcp_servers:" ~/.hermes/config.yaml 2>/dev/null | grep "name:" | sed 's/.*name: //'

# ECC agents
find ~/Documents/Projects/ECC -maxdepth 2 -name "*.md" -exec grep -l "^model:" {} \; 2>/dev/null | wc -l

# Session count & memory stats (if available)
ls ~/AppData/Local/hermes/sessions/*.db 2>/dev/null
wc -l ~/AppData/Local/hermes/MEMORY.md ~/AppData/Local/hermes/USER.md 2>/dev/null
```

### Step 2 — Build the Dashboard HTML

Create a single-file HTML (`dashboard.html`) with:

- **Header section**: `🌙 Hermes Agent Dashboard` title, last-updated timestamp
- **Stat cards row**: projects, skills, Graphify nodes, CodeGraph nodes, total APIs,
  free models, MCP servers, ECC agents — each in a glassmorphism card
- **Vis-network force-directed graph**: rendering project nodes connected by
  Graphify/CodeGraph edge counts. `vis-network` loaded from CDN. Graph is
  populated from gathered data — not a live backend.
- **Project grid**: each project as a card with name, description, graph stats
- **Free AI Model Ecosystem panel**: 5-layer routing chain (OpenCode → Freebuff →
  FreeLLMAPI → OpenRouter:free → Paid) with model counts per layer
- **API Mega List Explorer**: searchable category cards — each shows category name,
  API count, primary use — with a search input that filters cards by keyword
- **MCP Servers panel**: lists each wired server with its endpoint/description
- **ECC Agents panel**: agent count, free-compatibility ratio
- **Skill breakdown**: per-category skill counts as a visual chart

Key JS libraries (load from CDN):
- Chart.js 4.x (`https://cdn.jsdelivr.net/npm/chart.js`)
- vis-network 9.x (`https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.6/...`)
- Bootstrap 5.x CSS + JS (for responsive layout)
- Google Fonts (Inter + JetBrains Mono for code stats)

### Step 3 — Deploy to GH Pages

Copy the dashboard into the hermes-workflow repo:

```bash
cp ~/Documents/Projects/hermes-dashboard/index.html \
   ~/Documents/Projects/hw-new/dashboard.html
```

### Step 4 — Integrate with Main Site

Update `hw-new/index.html` with these changes:

**a) Nav link** — add a `📊 Dashboard` link in the navigation bar:
```html
<a href="dashboard.html">📊 Dashboard</a>
```

**b) Skill tab** — add a `dashboard` category button in the filter tabs:
```html
<button class="cat-tab" data-cat="dashboard">📊 Dashboard</button>
```

**c) Category mapping** — add dashboard to the emoji/label map:
```javascript
'dashboard':'📊 Dashboard'
```

**d) Skill card** — add the dashboard as a skill entry in the SKILLS array:
```javascript
{n:'Hermes Dashboard',c:'dashboard',d:'Local live stats — projects, graph maps, APIs, models, skills, MCP, ECC. One-pane ecosystem view.'}
```

### Step 5 — Update Ecosystem Docs

- **SKILLS_CATALOG.md** — add a `hermes-dashboard` entry with triggers,
  pipeline stage, and integration notes. Update the total skill count
  (137 for this ecosystem).
- **INTEGRATION.md** — add dashboard to the Quick Reference Table pipeline
  traces. Update the overview count if needed.
- **README.md** — add "Live Dashboard" to the features list. Update the
  Key Stats table with new rows if the dashboard uncovered new metrics.

### Step 6 — Update /decide Routing

In `decide/SKILL.md`:

**a) Domain Skills** — add dashboard routing:
```
- **Dashboard / ecosystem overview / show stats / project graph / model ecosystem / how many APIs / Graphify + CodeGraph node map** → `productivity/hermes-dashboard`
  - Routes to local dashboard HTML at ~/Documents/Projects/hermes-dashboard/index.html
  - Also available via GH Pages: attilahuns288452.github.io/hermes-workflow/dashboard.html
  - Direct HTML render — no further pipeline steps needed
```

**b) Complementary Setup Routing** — mention dashboard as a post-setup
deliverable for data-catalog integrations.

**c) Known Integration Patterns** — add:
```
| Dashboard ecosystem overview | User asks "show me everything", "dashboard", "ecosystem stats", "what projects exist", "graph stats" | Route to `productivity/hermes-dashboard`. Single HTML page at ~/Documents/Projects/hermes-dashboard/index.html. All stats are static — no live backend needed. |
```

### Step 7 — Create Obsidian Project Note

Create `Projects/Hermes Dashboard.md` in the vault with:
- Overview of the dashboard purpose and contents
- What data sources it aggregates
- How to open it (local file://, GH Pages, http.server)
- Current stat snapshot
- Mermaid graph showing data flows from source → dashboard → consumer
- Wikilinks to all referenced project notes

### Step 8 — Commit and Push

```bash
cd ~/Documents/Projects/hw-new
git add -A
git commit -m "Add Hermes Dashboard: live ecosystem stats, vis-network node map, 26K APIs, 8K+16K graph nodes, 5-layer model chain, 6 MCP servers"
git push
```

### Step 9 — Verify Deployment

1. Check HTTP status: `curl -s -o /dev/null -w "%{http_code}" "https://USER.github.io/hermes-workflow/dashboard.html"` → must return `200`
2. Navigate to the main site in a browser and confirm:
   - The `📊 Dashboard` nav link appears
   - Clicking it opens `dashboard.html` with correct content
   - The `📊 Dashboard` tab works in the skill grid
   - The Hermes Dashboard skill card appears with correct description
3. Navigate to dashboard.html directly and confirm:
   - Stat cards render with correct numbers
   - vis-network graph canvas appears (check for `canvas` element in DOM)
   - API Mega List Explorer cards are clickable
   - Search input filters categories by keyword

## Pitfalls

- **vis-network canvas invisible on initial load**: If the vis-network graph
  renders off-screen or with zero dimensions, call `network.fit()` **after**
  the container is visible and has non-zero dimensions. Wrap in
  `requestAnimationFrame` or a short `setTimeout(..., 100)`.
- **Chart.js + vis-network CDN loading order**: Chart.js must be loaded
  before Chart.register() calls. vis-network must be loaded before `new vis.Network()`.
  Load in order: Chart.js → vis-network → your scripts.
- **file:// CORS restrictions**: If the dashboard fetches external data files
  at runtime (not baked in), it must be served via HTTP. Use
  `python -m http.server 8765` from the dashboard directory.
- **Bootstrap modal conflicts**: If using Bootstrap 5 modals alongside
  vis-network, the network graph container inside a modal may render at
  zero dimensions until the modal's `shown.bs.modal` event fires — re-fit
  the network on that event.
- **Stale stats trap**: Dashboard stats are static snapshots. Include a
  "Last updated: [datetime]" header so users know the data age. Add a
  refresh button that reloads the page (no-op for static HTML, but signals
  intent).
- **Large API card lists**: Don't render all 18 API categories as cards if
  content is minimal — group by domain (e.g. "Data Extraction", "Social",
  "AI") and show counts. The search input should filter by card title + tags.
- **Bootstrap column overflow**: With 7-8 stat cards in a row on small
  screens, use responsive columns: `col-lg col-md-4 col-sm-6 col-12` so
  they stack gracefully.
- **GH Pages path resolution**: dashboard.html sits at the root of the GH
  Pages site, same as index.html. Nav links use `href="dashboard.html"`
  (same-directory relative). Assets (CSS, JS) loaded from CDN — no relative
  paths needed.

## Example Output

See the live dashboard at `https://attilahuns288452.github.io/hermes-workflow/dashboard.html`
and the source at `~/Documents/Projects/hermes-dashboard/index.html`.

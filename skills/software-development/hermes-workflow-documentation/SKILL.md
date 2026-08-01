---
name: hermes-workflow-documentation
description: Build and maintain a GitHub Pages documentation website for a Hermes Agent workflow skills repo. Covers scanning all skills, building a categorized catalog, adding install/getting-started instructions, model recommendations, pipeline/architecture docs, and deploying via git push.
version: 1.1.0
author: Hermes Agent
triggers:
  - workflow docs
  - hermes website
  - skills catalog
  - hermes workflow site
---

# Hermes Workflow Documentation

## When to Use

The user asks to improve, revamp, build, or update the documentation website for their Hermes Agent workflow skills repo (typically hosted on GitHub Pages). Common trigger phrases:
- "improve the html of my hermes workflow system"
- "revamp the website using our ui skills"
- "update the skills to be accurate to our skills repo"
- "update the README and github repo"

## User Preferences (style/quality)

- **Premium aesthetic required** — "make it look like a $10,000 website". Deliver glass-morphism surfaces, ambient animated backgrounds (floating orbs + noise texture), staggered scroll reveals, gradient accents. Basic dark theme with cards does not satisfy.
- **Animated diagrams over static text** — the pipeline and /decide flow MUST be rendered as animated SVG diagrams, not static card lists. Use `@keyframes fadeNode` CSS animations with staggered delays per node, gradient-filled boxes, dashed connector paths, and arrowhead polygons.
- **Accurate skill counts** — distinguish between "repo skills" (SKILL.md files in the repo) and "total ecosystem skills" (output of `hermes skills list | wc -l`). The user corrected 163 → 641. Show both numbers on the site.

## Workflow

### 1. Audit the Repo

```bash
# Count repo-skills (SKILL.md files in this repo)
find ./skills -name SKILL.md | wc -l
find ./skills -name SKILL.md | sort | sed 's|./skills/||;s|/SKILL.md||'

# Count total ecosystem skills (includes external repos)
hermes skills list | wc -l
```

The repo count goes in the hero as "Repo Skills". The total from `hermes skills list` goes in the hero as "Total Skills". Add a tooltip/box explaining how to get the full count via `external_dirs`.

Also check:
- `README.md` — existing stats and claims (verify every number against reality)
- `SETUP.md` — install instructions for freshness
- `index.html` — current website design and skill data
- `SKILLS_CATALOG.md` — if present, cross-reference skills

### 2. Design the Site

The site is a Vite React app (not a single static HTML file anymore):
- `src/App.jsx` — the entire site, one function component per section (Hero, InstallSection, PipelineSection, FeaturesSection, SkillsSection, ModelsSection, GuardrailSection, AgentsSection, IntegrationsSection, KGSection, FooterCTA). Sections render in `<main>` in App's return.
- `src/data-skills.json` — skills data by category (category → [{n, d}]). The Skills section and hero counts derive from it.
- `src/data-agents.json`, `src/data-integrations.json` — agents and integrations data.
- `docs/` — Vite build output (deploy artifact, committed per repo convention). Root `index.html` stays the Vite source entry.
- New feature sections follow the existing pattern: a section function using `Reveal` + `SpotlightGrid` + `spotlight-card` cards, registered in `<main>` and added to the Nav `links` array.

Section inventory (contents are still as below, but rendered as React components):

| Section | Content |
|---------|---------|
| **Hero** | Key stats (skill count, agent count, node counts, token savings) |
| **Get Started** | 2×2 grid: Install Hermes, Clone repo + install skills, Install tools, Run pipeline |
| **Recommended Model** | DeepSeek V4 Flash via OpenCode Zen — featured box with copy-button code snippet |
| **Pipeline** | Animated 9-step flow: session_memory → guardrail → /decide → token saver → Graphify+CodeGraph → domain skills → model routing → Obsidian docs → KG refresh |
| **/decide** | Visual flow diagram of the routing brain's steps |
| **Skills** | Tabbed grid organized by category — ALL skills from the repo, data-driven |
| **Guardrail** | 6 immutable safety rules |
| **Token Saver** | 56× verified reduction with benchmark stats |
| **Knowledge Graph** | 276 nodes / 1,091 edges stats |
| **ECC Agents** | Searchable/filterable agent library (64 agents, bridge badges for free compat) |
| **Ecosystem** | Integration cards for each ecosystem component |
| **Footer** | Links + model attribution |

### 3. Key UI Patterns

- **Copy buttons** on every install command — placed inside `<pre>` blocks with `position:absolute;top:.5rem;right:.5rem;opacity:0` shown on hover (`pre:hover .copy-btn{opacity:1}`). On click: `navigator.clipboard.writeText(...)` with green 'Copied!' feedback, reset after 1.5s.
- **Category tabs** for skills — generated dynamically from JS data. Include count per tab: `All (N)`, `Category (N)`. Click switches active class and re-renders grid.
- **Fade-in scroll reveals** — IntersectionObserver watching `.reveal` class, toggles `.visible` at `threshold:.08`, `rootMargin:0 0 -40px 0`. Each section gets `transform:translateY(30px);opacity:0` transitioning to `opacity:1;transform:translateY(0)` at 0.7s cubic-bezier.
- **Dark glass theme** with CSS custom properties:
  - Ambient background: 3 fixed `filter:blur(80px)` orbs animating with 20s `@keyframes orbFloat` + noisetexture overlay (SVG filter at 2.5%)
  - Glass surfaces: `background:rgba(12,20,40,.55);border:1px solid rgba(255,255,255,.04);backdrop-filter:blur(12px)`
  - Hero dot-grid: `background-image:linear-gradient(rgba(accent,.06) 1px,transparent 1px)` with `mask-image:radial-gradient(...)`
  - Pulsing green dot: `@keyframes pulse` + `box-shadow:0 0 12px rgba(61,220,132,.4)`
  - Hover lift: all cards get `transform:translateY(-2px)` + `border-color` shift on hover
- **Responsive** — hamburger nav, stacked grids at 768px, single-column at 480px.

### 4. Animated SVG Diagrams

Replace static card lists for pipeline and /decide sections with inline SVG flowcharts. Zero JS libraries — pure SVG + CSS `@keyframes`.

**Pattern (for a node group):**
```html
<g class="node" style="opacity:0;animation:fadeNode .5s .2s forwards">
  <rect x="10" y="55" width="120" height="70" rx="10" fill="url(#g1)" fill-opacity=".12" stroke="var(--accent)" stroke-opacity=".3"/>
  <text class="label" x="70" y="82" text-anchor="middle">LABEL</text>
  <text class="sublabel" x="70" y="102" text-anchor="middle">Subtitle</text>
  <rect x="10" y="55" width="20" height="20" rx="5" fill="url(#g1)"/>
  <text x="20" y="69" text-anchor="middle" fill="white" font-size="9" font-weight="700">1</text>
</g>
```

**CSS for diagrams:**
```css
.svg-diagram{width:100%;max-width:860px;margin:1.5rem auto;display:block;overflow:visible}
.svg-diagram .node:hover rect{filter:brightness(1.3)}
.svg-diagram .node .label{font-family:Inter;font-size:11px;font-weight:600;fill:var(--text);pointer-events:none}
.svg-diagram .node .sublabel{font-family:Inter;font-size:8px;fill:var(--text3);pointer-events:none}
.svg-diagram .conn{fill:none;stroke-width:1.5;stroke-linecap:round}
.svg-arrow{fill:var(--border-light);opacity:.5}
@keyframes fadeNode{to{opacity:1}}
```

Color key: blue (`g1`)=standard steps, red (`g2`)=guardrail, green (`g3`)=optimization/completion, gold=model routing.

Connector pattern: `<path class="conn" stroke="#2a4070" stroke-dasharray="4 4" d="M... L..." opacity=".5"/>`

Arrow polygons between connected nodes: `<polygon class="svg-arrow" points="x,y x2,y2 x3,y3"/>`

### 5. Update Supporting Docs

- `README.md` — update stats (skill count, node counts), website features list, model recommendation
- `SETUP.md` — add DeepSeek V4 Flash banner at top, update Layer 1 in model table, fix skill counts
- Verify ALL numbers match reality before publishing

### 6. Add New Skills / Features (proven recipe)

When new skills or features land, update BOTH the catalog and the site:

1. **`src/data-skills.json`** — add `{n, d}` entries to the right category array. This alone makes them appear in the Skills browser and hero counts.
2. **`SKILLS_CATALOG.md`** — add an entry under the matching `## Category:` section (real descriptions come from `head -8 <skill>/SKILL.md`). Bump the header `N skills` count AND the note's `total_skills` / listed-entries math in lockstep, or the catalog is internally inconsistent.
3. **`src/App.jsx`** — for headline features: hero badge string, a `FeaturesSection` card, a pipeline node (`PipelineSection` nodes array), and a live-pipeline ticker message (`AIPipelineVisual` messages array). Nav `links` array if a new section is added.
4. **Rebuild + commit** — `npm run build`, then commit the changed `docs/` assets (repo convention: rebuilt assets get committed, e.g. "rebuild assets after readme update"). Source + catalog + docs can go in separate commits.
5. Keep numbers consistent across site, catalog, and README — "665 skills", "141 skills", profile counts etc. must agree everywhere.

## Premium Overhaul Workflow (vision-audit → delegate → verify)

When the user asks to make the site "premium" or "like a $100k website", use the vision-audit loop:

### Step 1 — Screenshot the live site
```bash
# Use Firecrawl to get a full-page screenshot
# Pass the screenshot to MiMo (vision_analyze) for a brutal UX audit
```

### Step 2 — Delegate the coding to DeepSeek V4 Flash
Write a detailed briefing with specific, numbered fixes based on the vision audit. Example audit findings that improved the site from 5/10 to 8.5/10:
1. Information overload → progressive disclosure (8 items + "Show more")
2. No whitespace → increase section padding (py-32 md:py-40)
3. Weak hierarchy → bigger headings (clamp up to 3.5rem), bolder card titles
4. Cramped diagrams → increase SVG viewBox, rect sizes, font sizes
5. Color inconsistency → keep CTA in blue/cyan family, no purple in interactive elements
6. Low contrast text → brighter secondary color (#a0aec8 over #8895b8)
7. Missing closing CTA → add "Ready to build?" section before footer
8. Nav covering sections → scroll-mt-24 on all section ids

### Step 3 — Post-improvement vision check
Screenshot the updated site and pass to MiMo again for before/after scoring. This closes the loop and gives the user a quantified improvement report.

### Step 4 — Handle subagent timeout
If the delegated coding subagent times out at 600s, check `git diff --stat` — it likely saved changes but didn't finish build/deploy. Build and deploy yourself.

## Deploy

**Step A — Pre-build guard (mandatory).** Root `index.html` must be the Vite source entry, not a built file with hashed asset paths. Run the guard first:

```bash
node scripts/verify-vite-entry.js
```

Expected output:
- `✓ index.html points to /src/main.jsx` → safe to build
- `✗ index.html contains stale hashed asset path: ...` → recover before building (see below)

Also run the inline check if the script is unavailable:
```bash
# Must show /src/main.jsx, not /repo-name/assets/index-*.js
grep -E 'src=\"/src/main\.jsx\"|src=\"/src/main\.tsx\"' index.html || echo "⚠️ Root index.html is NOT the Vite entry — build will fail"
```

**⚠️ CRITICAL: After `git merge` or `git pull --rebase`, root `index.html` may get overwritten with the built version from the remote (which references hashed assets). ALWAYS re-run the pre-build guard after any merge/rebase, even if you ran it before. The merge conflict resolution for `index.html` must ALWAYS take the Vite source entry version (with `/src/main.jsx`), never the built version.**

**Step B — Build**
```bash
npm run build
```

**Step C — Verify build output**
```bash
test -f docs/index.html && echo "✓ Build OK" || echo "✗ Build failed"
```

**Step D — Copy built assets to root (for GitHub Pages fallback)**
```bash
cp docs/index.html index.html
cp -r docs/assets/* assets/
```
Note: The root `index.html` copy will reference hashed assets — this is fine for GitHub Pages serving. The Vite source entry is only needed for `npm run build`. After build, the root copy should match `docs/index.html`.

**Step E — Preview before pushing (optional but recommended)**
```bash
npx vite preview --port 4173 &
curl -s -o /dev/null -w '%{http_code}' http://localhost:4173/hermes-workflow/  # expect 200
kill %1
```

**Step F — Push**
```bash
git add -A
git commit -m "Revamp website: [summary of changes]"
git push origin master
```

Verify HTTP 200 on GitHub Pages URL. If the site shows a blank white page after deploy, see `references/vite-github-pages-deploy.md` for the fix (Vite dev-path issue).

**If build fails with `Failed to resolve /repo-name/assets/index-XXX.js from index.html`:**
1. Root `index.html` has been overwritten with stale built output. Restore it:
   ```bash
   cp templates/index.html index.html
   # or manually: <script type="module" src="/src/main.jsx"></script>
   ```
2. Re-run `npm run build` — it should now pass.
3. Re-run the guard to confirm the root stays clean.

**Never commit the built `index.html` to root.** GitHub Pages should be configured to serve from `/docs`; the root stays as the Vite source entry.

## Data Sources

Populate the website's skill data from the actual repo:

```bash
find ./skills -name SKILL.md | sort | sed 's|./skills/||;s|/SKILL.md||'
```

Group into categories matching the repo's directory structure. Each category gets its own tab in the skill grid.

## Pitfalls

- **⚠️ Empty `git diff` on files you JUST edited = a parallel process committed identical work** — in agent workflows (parallel subagents, parent re-running a task), another process may commit your exact changes mid-session. Symptoms: `git status` clean for files you patched, `git diff <file>` empty, `git check-ignore` confirms nothing is ignored, `git ls-files -v` shows normal tracked flags. Don't assume your edits were lost or your patch tool failed. Diagnose: `git log --oneline -3` (HEAD moved?), `git log --oneline -1 -- <file>` (a commit touching it appeared), `git diff HEAD --stat`, `git show <new-commit> --stat` to compare content. If content matches, skip re-editing and just rebuild/recommit the deploy artifacts that the parallel commit missed.
- **⚠️ INVERSE: Root `index.html` overwritten with built output breaks `vite build`** — this is the most common failure mode. If someone copies `docs/index.html` (containing hardcoded hashed assets like `index-Co6ofMD_.js`) to the repo root, the next `vite build` fails with "Failed to resolve ... from index.html". Root `index.html` must ALWAYS reference `/src/main.jsx`. Use the pre-build guard in Step A every time. If it fails, restore from `templates/index.html`. See `references/vite-github-pages-deploy.md` § "CRITICAL WARNING" for the full recovery recipe.
- **Vite app deployed as source shows white screen** — if `index.html` references `/src/main.jsx` instead of built assets, the page won't render. See `references/vite-github-pages-deploy.md` for diagnosis and fix
- **Don't hardcode skill counts** — scan the repo for the actual count
- **Don't copy stale data from the old site** — the old README/website may claim different numbers than the repo actually has. Always verify against `find ./skills -name SKILL.md | wc -l`
- **Model routing tables** — OpenRouter :free models change frequently. Mark known-deprecated models with `text-decoration:line-through;opacity:.5`
- **ECC agents list** — comes from the ECC repo, not from your local skills. Keep the 64-agent list updated
- **DeepSeek V4 Flash** is the recommended free model — feature it prominently with a gold-bordered recommendation box
- **The skills-install command** that newcomers need:
  ```bash
  find ./skills -name SKILL.md -exec dirname {} \; | while read dir; do
    hermes skills install "$dir"
  done
  ```
  Include this with a copy button in the "Get Started" section

## Support Files

- `scripts/verify-vite-entry.js` — run before every build to ensure root `index.html` is the Vite source entry, not stale built output
- `templates/index.html` — known-good Vite entry template; restore root `index.html` from this when it has been corrupted by built output
- `references/vite-github-pages-deploy.md` — full white-screen and inverse (stale-hash build failure) recovery guide
- `references/animated-svg-flowchart-patterns.md` — SVG/CSS patterns for the animated pipeline diagrams
- `references/vision-audit-checklist.md` — MiMo vision audit questions, fixes that worked, and before/after scores for premium website overhauls

## References

- `creative/premium` — Apple-inspired premium aesthetic for design guidance
- `creative/popular-web-designs` — 54 real design systems as reference
- `software-development/setup` — for the broader project setup workflow
- `note-taking/project-documentation` — for generating Obsidian-side documentation

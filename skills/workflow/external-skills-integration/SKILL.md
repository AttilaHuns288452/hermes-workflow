---
name: external-skills-integration
description: "Four major skill repos integrated into Hermes via external_dirs: Superpowers (obra, 14 dev-methodology skills), Agent Skills (addyosmani, 24 production engineering skills), Garden Skills (ConardLi, 5 design/creative skills), Claude SEO (AgricIDaniel, 25 SEO skills). Use when asked about external skills, skill setup, or any of these repos."
version: 1.0.0
metadata:
  hermes:
    tags: [external, integration, setup, skills]
    category: workflow
    related_skills: [hermes-agent, setup, skill-creator]
---

# External Skills Integration

Four major agent-skill repositories are integrated into Hermes via the `skills.external_dirs` config option.

## Location

All repos cloned (shallow) under:
```
~/Documents/Repos/external-skills/
├── superpowers/        # obra/superpowers — 234k ⭐
├── agent-skills/       # addyosmani/agent-skills — 64k ⭐
├── garden-skills/      # ConardLi/garden-skills — 8.4k ⭐
└── claude-seo/         # AgricIDaniel/claude-seo — 9.3k ⭐
```

## How Integration Works

Hermes' `skills.external_dirs` config points at each repo's `skills/` directory. Hermes scans those directories for `SKILL.md` files at startup and lists them alongside local skills. They're loaded on-demand via `skill_view()` just like any Hermes skill.

**IMPORTANT — Windows config path:** Hermes has two config files on Windows. The **active** one (used at runtime) lives at:
```
C:\Users\<username>\AppData\Local\hermes\config.yaml
```
There is also `~/.hermes/config.yaml` (1.4 KB), which is a **profile override** — editing it does NOT add external_dirs to the running Hermes instance. Always edit the active config at the `AppData\Local` path.

**Config YAML (in the active config):**
```yaml
skills:
  external_dirs:
    - C:/Path/To/Repos/external-skills/superpowers/skills
    - C:/Path/To/Repos/external-skills/agent-skills/skills
    - C:/Path/To/Repos/external-skills/garden-skills/skills
    - C:/Path/To/Repos/external-skills/claude-seo/skills
```

**Precedence:** Local `~/.hermes/skills/` wins over external on exact name collision.

---

## 1. obra/superpowers (v6.0.3)

**Stars:** 234k | **URL:** https://github.com/obra/superpowers

A complete agentic software development methodology. 14 skills covering the full dev lifecycle.

### Skills (14)
| Skill | What It Does |
|-------|-------------|
| `brainstorming` | Socratic design refinement before writing code |
| `writing-plans` | Break work into bite-sized tasks with exact specs |
| `executing-plans` | Follow structured plans to implement code |
| `subagent-driven-development` | Multi-agent orchestration (controller + implementers + reviewer) |
| `test-driven-development` | RED-GREEN-REFACTOR cycle with anti-pattern refs ⚠️ Collision |
| `systematic-debugging` | 4-phase root cause debugging ⚠️ Collision |
| `requesting-code-review` | Structured pre-review checklist ⚠️ Collision |
| `receiving-code-review` | How to process and act on review feedback |
| `verification-before-completion` | Self-check before declaring done |
| `using-git-worktrees` | Parallel dev branches via git worktrees |
| `dispatching-parallel-agents` | Orchestrate multiple concurrent agents |
| `finishing-a-development-branch` | Merge/PR decision workflow |
| `writing-skills` | Meta-skill for creating/maintaining skills |
| `using-superpowers` | Onboarding/reference for the system |

### How to Update
```bash
cd ~/Documents/Repos/external-skills/superpowers && git pull
# Then reload skills in Hermes: /reload-skills
```

---

## 2. addyosmani/agent-skills (64k ⭐)

**URL:** https://github.com/addyosmani/agent-skills

24 production-grade engineering skills by Google Chrome Engineer Addy Osmani. Covers the full def→plan→build→verify→review→ship lifecycle.

### Skills (24)
| Skill | What It Does |
|-------|-------------|
| `using-agent-skills` | Meta-skill: discovers and invokes the right skill |
| `spec-driven-development` | Write full PRD before any code |
| `planning-and-task-breakdown` | Decompose specs into verifiable tasks |
| `incremental-implementation` | Thin vertical slices, feature flags |
| `test-driven-development` | Red-Green-Refactor ⚠️ Collision |
| `interview-me` | Extracts requirements via one-question-at-a-time interview |
| `idea-refine` | Divergent/convergent thinking for vague ideas |
| `code-review-and-quality` | Five-axis review with severity labels |
| `code-simplification` | Chesterton's Fence, Rule of 500 |
| `debugging-and-error-recovery` | Five-step triage: reproduce→localize→reduce→fix→guard |
| `security-and-hardening` | OWASP Top 10, three-tier boundary system |
| `performance-optimization` | Measure-first, Core Web Vitals |
| `browser-testing-with-devtools` | Chrome DevTools MCP for DOM/console/network |
| `frontend-ui-engineering` | Component architecture, design systems, WCAG |
| `api-and-interface-design` | Contract-first design, Hyrum's Law |
| `context-engineering` | Rules files, context packing, MCP integrations |
| `source-driven-development` | Ground decisions in official docs |
| `doubt-driven-development` | Adversarial review: CLAIM→EXTRACT→DOUBT→RECONCILE |
| `git-workflow-and-versioning` | Trunk-based, atomic commits |
| `ci-cd-and-automation` | Shift Left, Faster is Safer |
| `observability-and-instrumentation` | RED metrics, OpenTelemetry |
| `deprecation-and-migration` | Code-as-liability mindset |
| `documentation-and-adrs` | Document the *why* |
| `shipping-and-launch` | Pre-launch checklists, deploy with confidence |

### How to Update
```bash
cd ~/Documents/Repos/external-skills/agent-skills && git pull
# Then: /reload-skills
```

---

## 3. ConardLi/garden-skills (8.4k ⭐)

**URL:** https://github.com/ConardLi/garden-skills

5 production-ready design/creative skills for web design, video presentations, image generation, knowledge retrieval, and beautiful articles.

### Skills (5)
| Skill | What It Does |
|-------|-------------|
| `web-design-engineer` (v1.2.2) | 6-step design workflow + 25 anchored style recipes |
| `web-video-presentation` (v1.2.2) | Click-driven 16:9 presentations with 23 themes |
| `gpt-image-2` (v1.0.4) | 18 visual categories, 79 structured prompt templates |
| `kb-retriever` (v1.0.1) | Local knowledge base retrieval (bounded 5 rounds) |
| `beautiful-article` (v0.1.0) | Turn any source into polished self-contained HTML articles |

### How to Update
```bash
cd ~/Documents/Repos/external-skills/garden-skills && git pull
# Then: /reload-skills
```

---

## 4. AgricIDaniel/claude-seo (v2.2.0, 9.3k ⭐)

**URL:** https://github.com/AgricIDaniel/claude-seo

Comprehensive SEO analysis plugin. 25 sub-skills covering technical SEO, E-E-A-T, schema, GEO/AEO, backlinks, local SEO, Google APIs, and more.

### Skills (25)
All prefixed with `seo-` — no collisions with local skills.

**→ Hermes tool mapping:** Reference `seo-audit-with-hermes-tools.md` under `references/` for a complete mapping of claude-seo audit steps to Hermes browser/web tools.
**→ SEO fix patterns:** Reference `seo-nextjs-fix-patterns.md` under `references/` for Next.js-specific fix patterns discovered during hands-on remediation (client-component H1 trap, OG per-page, sitemap gen, stale content counts).

| Skill | Command |
|-------|---------|
| `seo` | Orchestrator: routes to all sub-commands |
| `seo-audit` | Full site audit with parallel sub-agents |
| `seo-page` | Deep single-page analysis |
| `seo-technical` | 9-category technical SEO audit |
| `seo-content` | E-E-A-T and content quality analysis |
| `seo-content-brief` | Keyword + outline briefs |
| `seo-schema` | Schema.org detection, validation, generation |
| `seo-geo` | AI Overviews / Generative Engine Optimization |
| `seo-sitemap` | XML sitemap analysis or generation |
| `seo-images` | Image optimization analysis |
| `seo-plan` | Strategic SEO planning |
| `seo-local` | Local SEO (GBP, citations, reviews) |
| `seo-maps` | Maps intelligence (geo-grid, GBP audit) |
| `seo-hreflang` | International / i18n SEO audit |
| `seo-google` | GSC, PageSpeed, CrUX, Indexing, GA4 |
| `seo-backlinks` | Backlink profile analysis |
| `seo-cluster` | SERP-based semantic clustering |
| `seo-sxo` | Search Experience Optimization |
| `seo-drift` | SEO drift monitoring (SQLite snapshots) |
| `seo-ecommerce` | E-commerce SEO and marketplace intelligence |
| `seo-programmatic` | Programmatic SEO at scale |
| `seo-competitor-pages` | Competitor comparison pages |
| `seo-dataforseo` | DataForSEO extension |
| `seo-image-gen` | AI image generation for SEO assets |
| `seo-flow` | FLOW framework prompts |

**Note:** Claude SEO was designed for Claude Code's plugin system. Its SKILL.md files are Hermes-compatible via `external_dirs`, but the sub-agent delegation patterns and Python scripts (in `scripts/`) assume Claude Code tooling. Some workflows may reference Claude Code-specific tools (`Read`, `Write`, `Edit`, `Bash`). Adapt as needed.

### Automatic Update
```bash
cd ~/Documents/Repos/external-skills/claude-seo && git pull
# Then: /reload-skills
```

---

## Name Collisions (Handled by Hermes Precedence)

| Colliding Name | Local Skill Source | External Versions | Resolution |
|---------------|-------------------|-------------------|------------|
| `test-driven-development` | opencode-power-pack | superpowers, agent-skills | **Local wins** — our version takes precedence |
| `requesting-code-review` | opencode-power-pack | superpowers | **Local wins** |
| `systematic-debugging` | opencode-power-pack | superpowers | **Local wins** |

Hermes automatically prioritizes local `~/.hermes/skills/` over external dirs on exact name match. The external versions remain accessible for reference comparison.

---

## Updating All Repos at Once

```bash
cd ~/Documents/Repos/external-skills
for repo in superpowers agent-skills garden-skills claude-seo; do
  echo "=== Updating $repo ==="
  cd "$repo" && git pull && cd ..
done
echo "Done. Run /reload-skills in Hermes."
```

## Configuration Workflow (Windows)

Editing Hermes config to add `external_dirs` or manage MCP servers on Windows has several pitfalls. Follow this recipe.

### 1. Find the Right Config

Hermes has two config files on Windows. The one you need is:

```
C:\Users\<username>\AppData\Local\hermes\config.yaml
```

The `~/.hermes/config.yaml` file is only a profile override (~1.4 KB) — it does NOT control external_dirs or MCP servers.

### 2. Adding MCP Servers (Recommended: `hermes mcp add`)

Use the Hermes CLI to add MCP servers instead of editing the config file directly:

```bash
echo y | hermes mcp add <name> --command <cmd> --args '<arg1> <arg2>'
```

**Example — adding an MCP server with args:**
```bash
echo y | hermes mcp add graphify --command python --args '-m graphify.serve'
```

**Note:** The `--args` flag is positional. Keep them inside quotes. The `echo y |` answers the "Save config anyway?" prompt.

### 3. Setting Config Values: `hermes config set`

For **scalar values**, use `hermes config set` directly:

```bash
hermes config set mcp_servers.graphify.cwd "C:\\path\\to\\project"
```

For **list values** (like `args`), use JSON array syntax:

```bash
hermes config set mcp_servers.vscode.args '["-y", "vscode-mcp-server"]'
```

For **env dict** values, set key by key:

```bash
hermes config set mcp_servers.llmquant-data.env.LLMQUANT_API_KEY "your-key"
```

### 4. Editing `external_dirs` (Python text manipulation only)

`hermes config set skills.external_dirs [...]` **does not work for list values**. It stores the value as a YAML string, not a YAML list. To set external_dirs, use Python text manipulation:

```python
import re
with open('$HERMES_HOME/config.yaml', 'r') as f:
    text = f.read()
old = r'(external_dirs:).*'
new = r'\1\n    - C:/path/to/first/skills\n    - C:/path/to/second/skills'
text = re.sub(old, new, text)
with open('$HERMES_HOME/config.yaml', 'w') as f:
    f.write(text)
```

### 5. ⚠️ NEVER Use yaml.dump() on the Full Config

Do NOT do this:
```python
# DESTRUCTIVE — loses anchors, flow styles, MCP servers, and more
cfg = yaml.safe_load(open('config.yaml'))
cfg['skills']['external_dirs'] = [...]
yaml.dump(cfg, open('config.yaml', 'w'))
```

The Hermes config is complex (18+ KB, 676+ lines). `yaml.safe_load()` + `yaml.dump()` drops flow-style sequences, anchors, and nested structures — this **will lose MCP server configurations** (vscode, llmquant-data, graphify, obsidian-kg, agentmemory, etc.).

If the config was corrupted by a yaml.dump round-trip, re-add missing MCP servers via `hermes mcp add` (see step 2).

### 6. External Skills Require a New Session

Unlike local skills (`/reload-skills`), `external_dirs` is read **only at Hermes startup**. After editing the config, you must start a new session for external skills to appear.

---

## Troubleshooting

- **Skills not showing:** External_dirs are read at startup only. Start a **new session** (`/reset` or relaunch Hermes). `/reload-skills` only refreshes local `~/.hermes/skills/`, not external dirs.
- **Config not applied:** Verify you edited the **active** config (`C:\Users\<user>\AppData\Local\hermes\config.yaml`), not the profile stub at `~/.hermes/config.yaml`.
- **Name collision confusion:** Local skills always win — `skill_view("test-driven-development")` loads the local one
- **Claude Code-specific tool refs:** claude-seo skills mention `Read`/`Write`/`Edit`/`Bash` which are Claude Code tool names. Hermes uses equivalent tools (`read_file`/`write_file`/`patch`/`terminal`)
- **Config got corrupted (yaml.dump round-trip):** Restore missing MCP servers by re-adding their entries. Each MCP block looks like:
  ```yaml
  mcp_servers:
    <name>:
      command: <exec>
      args: [<arg1>, <arg2>]
      env: { ... }
      connect_timeout: 30
  ```
  Insert them back into the config file under `mcp_servers:`.

---
name: external-skills-integration
description: "Six major skill repos integrated into Hermes via external_dirs: Superpowers (obra, 14 dev-methodology skills), Agent Skills (addyosmani, 24 production engineering skills), Garden Skills (ConardLi, 5 design/creative skills), Claude SEO (AgricIDaniel, 25 SEO skills), Obsidian Skills (kepano, 5 Obsidian syntax skills), and Karpathy Skills (multica-ai, behavioral coding guidelines). Use when asked about external skills, skill setup, or any of these repos."
version: 1.0.0
metadata:
  hermes:
    tags: [external, integration, setup, skills]
    category: workflow
    related_skills: [hermes-agent, setup, skill-creator]
---

# External Skills Integration

Six major agent-skill repositories are integrated into Hermes via the `skills.external_dirs` config option.

## Location

All repos cloned (shallow) under:
```
~/Documents/Repos/external-skills/
├── superpowers/        # obra/superpowers — 234k ⭐
├── agent-skills/       # addyosmani/agent-skills — 64k ⭐
├── garden-skills/      # ConardLi/garden-skills — 8.4k ⭐
├── claude-seo/         # AgricIDaniel/claude-seo — 9.3k ⭐
├── obsidian-skills/    # kepano/obsidian-skills — Obsidian OFM, Bases, Canvas, CLI
└── karpathy-skills/    # multica-ai/andrej-karpathy-skills — behavioral coding guidelines (Hermes-native at software-development/karpathy-guidelines)
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
    - C:/Users/YOUR_USERNAME/Documents/Repos/external-skills/superpowers/skills
    - C:/Users/YOUR_USERNAME/Documents/Repos/external-skills/agent-skills/skills
    - C:/Users/YOUR_USERNAME/Documents/Repos/external-skills/garden-skills/skills
    - C:/Users/YOUR_USERNAME/Documents/Repos/external-skills/claude-seo/skills
    - C:/Users/YOUR_USERNAME/Documents/Repos/external-skills/obsidian-skills/skills
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

**Companion Hermes skill:** `software-development/superpowers-methodology` — a meta-skill that describes the full Superpowers pipeline (brainstorm→design→plan→TDD→review→finish) and maps each phase to the corresponding skill. Load this alongside the external_dir when the user wants the structured Superpowers workflow. Created in the same session that installed the external_dir.

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

### How to Update
```bash
cd ~/Documents/Repos/external-skills/claude-seo && git pull
# Then: /reload-skills
```

---

## 5. kepano/obsidian-skills

**URL:** https://github.com/kepano/obsidian-skills

Obsidian plugin-style skills covering Obsidian Flavored Markdown (OFM), Bases, JSON Canvas, and CLI interaction. Designed for Claude Code, Codex, and OpenCode, but fully Hermes-compatible via external_dirs.

### Skills (5)
| Skill | What It Does |
|-------|-------------|
| `obsidian-markdown` | Obsidian-flavored markdown: wikilinks, embeds, callouts, properties, comments, aliases, tags |
| `obsidian-bases` | `.base` files: filters, formulas, views (table/cards/list/map), summaries |
| `json-canvas` | `.canvas` files: nodes (text/file/group), edges with sides & endpoints |
| `obsidian-cli` | CLI interaction with running Obsidian: create, search, open, plugin reload, JS |
| `defuddle` | Extract clean markdown from web pages via Defuddle CLI (redundant with Hermes `web_extract`) |

**Companion Hermes skill:** `note-taking/obsidian` — updated to include full OFM syntax coverage (callouts, embeds, properties, aliases, comments, tags), Bases (.base) with YAML schema, JSON Canvas spec, and Obsidian CLI commands. Routes to `note-taking` bundle in `/decide`.

### Repository Layout
```
obsidian-skills/
├── .claude-plugin/
├── LICENSE
├── README.md
└── skills/
    ├── obsidian-markdown/
    │   ├── SKILL.md
    │   └── references/
    │       ├── CALLOUTS.md
    │       ├── EMBEDS.md
    │       └── PROPERTIES.md
    ├── obsidian-bases/
    │   └── SKILL.md
    ├── json-canvas/
    │   └── SKILL.md
    ├── obsidian-cli/
    │   └── SKILL.md
    └── defuddle/
        └── SKILL.md
```

### How to Update
```bash
cd ~/Documents/Repos/external-skills/obsidian-skills && git pull
# Then: /reload-skills
```

---

## 6. multica-ai/andrej-karpathy-skills

**URL:** https://github.com/multica-ai/andrej-karpathy-skills

Behavioral coding guidelines from Andrej Karpathy — 4 principles that reduce common LLM coding mistakes.

### Skills (1)
| Skill | What It Does |
|-------|-------------|
| `karpathy-guidelines` | Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution — loaded as cross-cutting guardrails on any code task via `/decide` routing |

**Hermes skill:** `software-development/karpathy-guidelines` — already shipped with Hermes, more comprehensive than the upstream CLIFF.md. Includes Framework-Specific Pitfalls (Next.js loading states, Python numpy typing, CSS gap, React hooks deps). Loaded automatically via `/decide` alongside any coding task.

**Upstream CLIFF.md reference:** The repo contains `CLIFF.md` which defines the 4 principles. The Hermes skill expands on each with concrete code examples and framework-specific patterns.

### How to Update
```bash
cd ~/Documents/Repos/external-skills/karpathy-skills && git pull
# Then: /reload-skills
```

---

## Name Collisions

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
for repo in superpowers agent-skills garden-skills claude-seo obsidian-skills karpathy-skills; do
  echo "=== Updating $repo ==="
  (cd "$repo" && git pull)
done
echo "Done. Run /reload-skills in Hermes."
```

## 7. npx skills CLI Ecosystem

**URL:** Installable via `npx skills add <repo>` | **Home:** https://github.com/nicepkg/skills-cli

The `npx skills` CLI installs skills to `~/.agents/skills/`. These are NOT in the git-cloned external repos — they come from the npm skills ecosystem (MengTo/Skills, anthropics/skills, mattpocock/skills, vercel-labs/agent-skills, etc.).

### Installation Pattern

```bash
# Install all skills from a repo (interactive selection without --yes)
npx skills add https://github.com/MengTo/Skills.git --yes

# Install individual skills
npx skills add https://github.com/anthropics/skills --skill frontend-design --yes
npx skills add https://github.com/mattpocock/skills --skill improve-codebase-architecture --yes
npx skills add https://github.com/mattpocock/skills --skill grill-me --yes
npx skills add https://github.com/vercel-labs/skills --skill find-skills --yes
npx skills add https://github.com/vercel-labs/agent-browser --skill agent-browser --yes
npx skills add https://github.com/vercel-labs/agent-skills --skill web-design-guidelines --yes
```

The `--yes` flag skips the project-vs-global scope prompt. Without `--skill`, all skills in the repo are installed. Use `--global` only if a skill explicitly supports it (PromptScript skills reject `--global`).

### Wiring into Hermes

After installing via npx skills, add the path to Hermes config:

```bash
hermes config set skills.external_dirs '["C:/Users/YOUR_USERNAME/.agents/skills"]'
```

**Important:** `hermes config set` with a JSON array string DOES work for list values now — it stores the value as a JSON-encoded string that Hermes parses correctly. If merging with existing dirs, read the current config first and include the full list.

The CLI reports "symlinked: Hermes Agent" on install, but Hermes won't see the skills until `external_dirs` is set. External_dirs are read at startup only — start a new session after adding.

### After Install: Update /decide Routing

When new skills add unique capabilities not covered by existing routing (like `find-skills` for skill discovery), add entries to the decide skill's Selection Rules table using `skill_manage(action='patch', name='decide')`.

### Verifying the ZCode/Hermes Shared-Skill Sync (`.agents/skills`)

`~/.agents/skills/` is the **shared one-directory bridge**: ZCode reads it as its flat skill dir, Hermes mounts it via external_dirs. When asked "are the skills configured correctly for ZCode", verify in one pass:

```bash
ls "C:/Users/YOUR_USERNAME/.agents/skills/" | wc -l                 # total entries
ls "C:/Users/YOUR_USERNAME/.agents/skills/" | grep -c "\-\-"        # flattened category--subskill entries
ls "C:/Users/YOUR_USERNAME/.agents/skills/" | grep -v "\-\-" | wc -l # standalone entries
# Core pipeline must be present (ZCode reads FLAT only — sub-skills flattened as category--name):
for s in decide core-identity-guard subagent-delegation workflow--task_tier workflow--token-saver; do
  ls -d "C:/Users/YOUR_USERNAME/.agents/skills/$s" >/dev/null 2>&1 && echo "OK  $s" || echo "MISS $s"
done
grep -A 15 "^skills:" "C:/Users/YOUR_USERNAME/AppData/Local/hermes/config.yaml" | grep agents  # bidirectional wiring
```

**What correct looks like:**
- `workflow/task_tier` + `workflow/token-saver` in Hermes appear as `workflow--task_tier` / `workflow--token-saver` in `.agents` — the `--` flattening is the expected convention, NOT a typo.
- ZCode provider check: `~/.zcode/v2/config.json` → the enabled `builtin:*` provider must match what AGENTS.md claims (e.g. `builtin:zai-start-plan` enabled = GLM-5.2 lane).
- Count drift is normal (AGENTS.md snapshots go stale); presence of core pipeline + flattening convention is the real signal.
- **Known cosmetic collision:** `decide` exists in BOTH `AppData/Local/hermes/skills/` and `.agents/skills/` (same shared content) → `skill_view(name='decide')` errors "Ambiguous skill name". Harmless; load by category path when it bites. Dedupe one side if it ever matters.

### Common Issues

- **PromptScript skills fail with `--global`:** PromptScript (anthropics/skills format) requires project-scope installation. Omit `--global` for these.
- **95 MengTo skills:** `MengTo/Skills` has 95 design/creative skills. Installing all with `--yes` works, but some PromptScript ones may fail — these are the WebGL/three.js ones that need project scope.
- **Duplicates:** If a skill name collides with a local or external-dir skill, the local `~/.hermes/skills/` wins.

---

## Configuration Workflow (Windows)

Editing Hermes config to add `external_dirs` or manage MCP servers on Windows has several pitfalls. Follow this recipe.

> **Reference file:** `references/external-dirs-setup-windows.md` — step-by-step guide for adding external_dirs with sed, Python, or manual editing.

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

### 4. Editing `external_dirs`

`hermes config set skills.external_dirs [...]` stores the value as a JSON-encoded YAML string, which Hermes parses correctly. Pass the full list as a JSON array:

```bash
hermes config set skills.external_dirs '["C:/Users/YOUR_USERNAME/path1","C:/Users/YOUR_USERNAME/path2"]'
```

To merge with existing dirs, read the current config first with `grep` or `yq`, then include the full list. For complex config edits, use the approaches in `references/external-dirs-setup-windows.md` instead (sed or manual edit).

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

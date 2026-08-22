---
name: decide
description: Master orchestrator that runs on every prompt, selects and sequences
  the appropriate skills, injects context, and enforces execution order. Always
  runs first. Never skipped.
triggers:
  - always
---

# /decide Skill

> **⚠️ HONESTY NOTE:** Previous versions documented "ACTIVE enforcement" that was never actually followed. This version is restructured so the critical rules are literally the first thing you read. If you find yourself skipping a rule below, stop and check why.

---

## ⚡ Enforcement Mechanism — How /decide Actually Gets Loaded

**Critical fact:** The `triggers: [always]` frontmatter field is aspirational metadata. Hermes does NOT auto-load skills based on triggers. The only file guaranteed to enter every session's system prompt is **SOUL.md** at `$HERMES_HOME/SOUL.md` (per Hermes docs: "always loaded when present — it sets the agent's identity").

**The enforcement chain:**
1. Hermes loads SOUL.md into the system prompt at session start (framework-level, not skill-level)
2. SOUL.md contains the mandatory pipeline: "Step 0: Load `skill_view(name='decide')`"
3. The agent reads that instruction and loads /decide
4. /decide then governs the rest of the session

**If SOUL.md doesn't mention /decide, /decide doesn't run.** The skill's own `triggers: [always]` cannot self-invoke. This is why previous versions documented "ACTIVE enforcement" that was "never actually followed" — there was no enforcement mechanism.

**To update the pipeline enforcement:** edit `$HERMES_HOME/SOUL.md` (on Windows: `C:\Users\YOUR_USERNAME\AppData\Local\hermes\SOUL.md`). The 8-step pipeline lives there: /decide load → session_search → guardrail → task_tier → enforced rules → skill selection → execute → self-audit.

See `references/soul-md-enforcement.md` for the full SOUL.md pipeline template.

---

## 🤖 Model Roles & Delegation

> Full details in `subagent-delegation` skill. Quick reference:

| Role | Model | Use for |
|------|-------|---------|
| Orchestrator / Planning | **Hermes chat model** (currently `opencode-go/meta/muse-spark-1.2-contributor`) | **ROUTING + REASONING ONLY.** Never writes code, runs git, patches files, does build/deploy. |
| **Main coding agent — implementation, editing, coding, execution** | `opencode-go/meta/muse-spark-1.2-contributor` | **ALL coding, git, deploy, build, patches, merge conflicts, terminal commands** — delegate via `delegate_task`, `opencode run`, or oh-my-opencode-slim Pantheon swarm |
| **Multimodal** | `opencode/mimo-v2.5-free` | **ALL image/video/visual tasks** — screenshots, UI audits, design review |
| **Difficult multimodal** | `opencode-go/mimo-v2.5-pro` | Complex, long-running multimodal reasoning tasks |

**Delegation rule:** 1-2 patches → `delegate_task` to Muse Spark 1.2 Contributor @ opencode-go. 3+ independent tasks → `delegate_task(tasks=...)` or Pantheon swarm. Bounded coding → `opencode run --model opencode-go/meta/muse-spark-1.2-contributor`. **Check ECC/Agency agent roster first** — if task matches a specialty agent (reviewer, resolver, architect, security, ML, DevOps), route there before generic delegation. The orchestrator NEVER writes code, runs git, or does build/deploy.

**⚠️ NEVER use bare model IDs through the opencode CLI** (`deepseek-v4-flash`, `mimo-v2.5`, `glm-5.2`) — they resolve to the opencode-zen route (pay-as-you-go, historically 429-exhausted). Always qualify: `opencode-go/deepseek-v4-flash`, `opencode-go/muse-spark-1.2-contributor`, `opencode-go/mimo-v2.5`. Hermes config already pins everything to opencode-go; the trap is only in ad-hoc `opencode run` calls and OpenDesign generation.

**Rate-limit fallback (auto, don't ask):** free → paid equivalent. Never use paid for mundane delegation unless rate-limited. **600s timeout** — break large batches into 4-6 items.

## 🟢 Active Session Rules (always loaded via skills)

| Rule | Source skill | What |
|------|-------------|------|
| Vision → MiMo subagent | `subagent-delegation` | Never call `vision_analyze` from orchestrator. Delegate to MiMo, feed results to Muse Spark (@ opencode-go). |
| QA depth: test everything | `subagent-delegation` | Click every button, test every state, every edge case. |
| Cache-busting: no stale pages | `subagent-delegation` | Add `<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">` to all static sites. |
|| Skill lookup: TF-IDF | `lightrag-skill-finder` | Sub-second, 0 API. Query: `python C:/Users/YOUR_USERNAME/AppData/Local/hermes/lightrag_index/find.py "<query>"`. Build: same dir, read all SKILL.md files → build_index.py. |
| Design: 21st.dev first | `21st.dev` MCP | Before building UI, run `get_inspiration` for design tokens. Before coding components, `get_component` for shadcn code. |
| Code quality: ECC agents | `ecc-bridge` | Route to ECC code-reviewer for architecture/code reviews. Check agent roster before generic delegation. |
| SOUL.md trimmed | — | 13.5KB → 9.6KB. Skills carry details, SOUL.md only pipeline + delegation pointer. |

## ⚡ Session Startup Protocol (Execute Immediately on Load)

Do these steps in order, right now, before any other action:

```
Step 1 — session_search(): Check for relevant context from past sessions
Step 2 — Determine task_tier: Is this Tier 1, 2, or 3?
Step 3 — Announce compliance: State which rules apply in your first response
Step 4 — Proceed to domain routing below
```

**Mandatory compliance announcement format** in your first response to the user:

```
📋 **Startup Compliance:**
- Tier: [1/2/3]
- Rule 1 (Token Saver): [ACTIVE / SKIP — reason]
- Rule 2 (OpenMontage): [ACTIVE / SKIP — reason]
- Rule 3 (CodeGraph/Graphify): [ACTIVE / SKIP — reason]
```

This serves two purposes:
1. **Forces conscious acknowledgment** — you can't skip what you've just stated
2. **Gives the user a way to verify** — if you claim "Rule 1: ACTIVE" and then call read_file without probing, that's an observable violation

---

## 🔴 ENFORCED RULES — Must Follow, in Order, Every Session

These rules apply to EVERY session. They are not suggestions. If you catch yourself calling `read_file` on a code project without probing CodeGraph first, or writing ad-hoc FFmpeg scripts instead of using OpenMontage, you are violating them.

### Rule 1: Token Saver Probe Chain (Before ANY read_file)

**BEFORE** calling `read_file()` on any file under `~/Documents/Projects/`, you MUST run these probes:

1. **Step A** — Identify `$PROJECT` from the file path. All projects live at `~/Documents/Projects/$PROJECT/`.
2. **Step B** — Probe CodeGraph MCP (always available, ~300 tokens). Use the MCP tools in this order:
   - **Step B1** — `mcp_codegraph_codegraph_explore(query="<symbol_or_term>")` — primary probe. Single call returns definitions, structure, and source of relevant symbols across files. Usually enough on its own.
   - **Step B2** (if B1 insufficient) — `mcp_codegraph_codegraph_search(query="<term>")` for broader name search, or `mcp_codegraph_codegraph_callers/callees/impact` for relation analysis.
   
   Covers ALL projects under `~/Documents/Projects/` (8,421 files, 144,827 nodes, 326,322 edges indexed globally). Returns source code + locations. **⚠️ CWD dependency:** if the session working directory is NOT inside a project (e.g. `C:\Users\YOUR_USERNAME`), you MUST pass `projectPath` to every CodeGraph MCP call or you get "No CodeGraph project is loaded for this session." Example: `mcp_codegraph_codegraph_explore(query="symbol", projectPath="C:\\Users\\Attila\\Documents\\Projects\\$PROJECT")`. MCP tools are still preferred over terminal CLI.

   **Terminal fallback** (use only if MCP tools are unavailable or you need a full list):
   ```bash
   cd ~/Documents/Projects && codegraph query "<symbol_or_term>"
   ```
3. **Step C** — Probe Graphify if index exists (~300 tokens):
   ```bash
   test -f ~/Documents/Projects/$PROJECT/graphify-out/graph.json && \
     cd ~/Documents/Projects/$PROJECT && \
     ~/.local/bin/graphify.exe query "<question>" --budget 2000 --graph graphify-out/graph.json
   ```
   21/24 projects have indices (all except Hermes Skills, hermes-dashboard, unit-converter).
4. **Step D** — Targeted read_file ONLY if A-C were insufficient:
   ```python
   read_file(path, offset=N, limit=50)  # Never full-project reads
   ```

**Consequence:** A full probe chain costs ~1,500 tokens. A raw full-project read can cost 15K–370K tokens. Skipping the probe wastes 50× to 1,233× tokens per query.

**Exception:** System files, temp files, config files under `~/AppData/` or `~/.hermes/` — these are not code projects, skip the probe.

### Rule 2: OpenMontage First for Video

**ANY** video production request (TikTok, Shorts, explainer, cinematic, documentary, talking head, product demo) → route to `media/openmontage-production` FIRST.

- Read `~/OpenMontage/AGENT_GUIDE.md` at session start
- Run preflight (`python -c "from tools.tool_registry import registry; ..."`)
- Follow the pipeline stages via director skills
- Use `video_compose(operation='remotion_render')` for composition — NOT ad-hoc FFmpeg scripts

**Fallback to `media/short-video-production` ONLY if** OpenMontage preflight shows blockers (e.g., Chrome unavailable, pipeline def missing, tool registry empty).

**Why this matters:** OpenMontage has 13 production pipelines, 12 verified API keys, 182/184 passing tests, and proper Remotion-based composition. Last session proved that bypassing it produces a 2.8MB slideshow that looks terrible. This rule exists because the assistant kept writing ad-hoc scripts instead of using the pipeline.

### Rule 3: CodeGraph + Graphify Are Active Tools

- **CodeGraph MCP (preferred):** `mcp_codegraph_codegraph_explore/search/callers/callees/impact` — use MCP tools for any codebase question. Returns source code inline. **⚠️ Pass `projectPath` when CWD is not inside a project.**
- **CodeGraph CLI (fallback):** `codegraph query/callers/callees/impact` — use if MCP tools are unavailable.
- **Graphify (v0.8.37):** `~/.local/bin/graphify.exe query` — use for structural BFS traversal
- `read_file` is **LAST RESORT** for code files under `~/Documents/Projects/`

### Rule 4: task_tier Gate

Run `task_tier` immediately after session_memory + core-identity-guard. The structured output governs:

| TIER | Token Saver | Obsidian Bundle | KG Refresh |
|------|------------|-----------------|------------|
| 1 (atomic) | SKIP | SKIP | SKIP |
| 2 (task) | **RUN** | SKIP | SKIP (unless structural change) |
| 3 (project) | **RUN** | **RUN** (all 3 Obsidian skills) | **RUN** |

> **Obsidian Bundle** = create/update note + codebase graph + KG viz
> **KG Refresh** = regenerate `obsidian-knowledge-graph`

---

## 🟡 Aspirational Guidelines (Use Judgment)

### G1: Obsidian Bundle for Tier 3 (trigger-based)

After completing a Tier 3 task — or any time the user says "update the obsidian notes" or "create the obsidian notes after creating a project" — run the full Obsidian bundle:
1. `obsidian-codebase-graph --clean` on the affected project
2. Create/update the project's main Obsidian note (ATM-Machine template: Overview, Features, Structure, Architecture, Code Patterns, Mermaid graph, wikilinks, tags)
3. Run `obsidian-knowledge-graph` to refresh vault-wide interconnectivity viz
4. Refresh the KG render in any dashboard

> **Note:** This is **on-demand only** — don't run automatically after every code change. The triggers are: user asks for note update, user creates a new project, or Tier 3 task completion.
### G2: Self-Audit (Run Before Finishing Each Session)

Before delivering your final response, verify your startup compliance matches reality:

```diff
📋 Startup Compliance (what I announced):
- Rule 1 (Token Saver): [ACTIVE / SKIP]
- Rule 2 (OpenMontage): [ACTIVE / SKIP]

[X] Did I actually probe CodeGraph before every read_file?
    → If I said ACTIVE but didn't probe, this is a violation. Fix it.
[X] Did I route video to OpenMontage (not ad-hoc scripts)?
    → If I said ACTIVE but wrote FFmpeg, this is a violation. Fix it.
[X] Did I DELEGATE coding to a subagent, or did the orchestrator write product code itself?
    → Any write_file/patch/terminal on ~/Documents/Projects/ code by the orchestrator = violation. Fix it.
[X] Is the task_tier classification still accurate?
[X] Did I use the right tool for the task?
[X] If code-related: did I use CodeGraph + Graphify before read_file?
```

**Consequence of violation:** If any box is unchecked, the startup compliance announcement was misleading. Do NOT deliver results until all boxes are checked. If you cannot fix the violation (e.g., you already read files without probing), disclose it to the user and correct in the next action.

### G3: session_memory Always First
Every session: call session_search() to check for relevant context before routing anything. Never skip.

### G4: On-Demand Over Automatic for Token-Heavy Operations

Any automated post-task workflow that consumes significant tokens should default to **on-demand** (triggered by explicit user request) rather than automatic enforcement after every change. This includes:

- Obsidian code graph regeneration
- Full project analysis passes
- Bulk format exports (e.g., markdown-exporter batch runs)
- Cross-referencing / graph rebuilds
- Dashboard or knowledge graph refreshes

The user explicitly prioritizes **token efficiency** over having everything auto-synced. Only run these automatically if:
- The user explicitly opted in (said "keep doing this automatically")
- OR the task is Tier 3 and the user confirmed they want the full bundle during this session
- OR you asked and they said yes

**Rationale from the user:** "so you know i would not waste tokens when i dont need it"

---

## Execution Order (Summary)

```
1. session_search()              → context retrieval
2. core-identity-guard            → safety
3. task_tier                      → classification gate
4. ENFORCED RULES check           → which rules apply?
   - Rule 1 (Token Saver) if Tier 2/3 and code reading
   - Rule 2 (OpenMontage) if video
   - Rule 3 (CodeGraph/Graphify) if code query
5. Domain skill selection         → routing (see below)
6. **Execute** — with tooling from chosen skill. If task has 3+ independent subtasks or is Tier 3 → delegate subtasks to parallel subagents via `delegate_task(tasks=...)` (see `subagent-delegation`).
7. Post-execution                 → Obsidian Bundle if Tier 3 OR user requested note update
8. Self-audit (G2)                → verify rules were followed
```

---

## Selection Rules

### Soul Files (Personality + Constraints)
- Coding / implementation / Next.js / Supabase / TypeScript → `soul`
- Finance / investing / portfolio / cash flow / macro / CFA → `soul_finance`
- Fintech tasks (code + finance) → activate **both** soul and soul_finance

### Domain Skills
| Trigger | Route To |
|---------|----------|
| Video production / TikTok / Shorts / animated explainer | `media/openmontage-production` **first** |
| Writing finance scripts / "What's the Difference" / Mr. Finance Guy / TikTok finance / reel / short / compare X and Y for video | `mr-finance-guy` |
| Setup / install / configure / bootstrap | `software-development/setup` |
| Setup + skill audit / repo reconciliation | `software-development/repo-integration-reconciliation` |
| API search / data source / scraper / MCP server | `productivity/api-mega-list` |
| Internet research / read any URL / social platforms (Twitter/X, Reddit, YouTube, GitHub, Bilibili, XiaoHongShu, Facebook, Instagram, LinkedIn, V2EX, Xueqiu, RSS) / "research this topic" / "look this up" / web search beyond firecrawl | `agent-reach` (CLI capability layer — run `agent-reach doctor --json` first for multi-backend platforms; probe `active_backend`; use upstream tools directly: `yt-dlp`, `gh`, `curl r.jina.ai`, `mcporter call exa...`) |
| Ecosystem dashboard / stats / project graph | `productivity/hermes-dashboard` |
| Update / ecosystem integrate / onboard | `software-development/update` |
| Graphify / Obsidian code-graph export | `software-development/graphify-integrate` |
|| Update / create Obsidian notes / sync code to vault / "update the obsidian notes" / "create the obsidian notes after creating a project" / codebase-to-Obsidian mapping / project initialization graph / generate codebase notes / visualize architecture in Obsidian | `note-taking/obsidian-codebase-graph` (use `--clean` flag for regenerating) |
|| Document project codebase / generate project documentation / "create a documentation folder structure" / "generate docs for [project]" / document system architecture in Obsidian / create organized project documentation / codebase documentation structure / recreate my whole obsidian notes into organized structure | `note-taking/project-documentation` (on-demand — 6-subfolder structure: 01_overview, 02_architecture, 03_modules, 04_data_flow, 05_dependencies, 06_gaps_and_todos) |
|| Coding / implementation | `software-development` or domain-specific |
|| "as a student" / "student mode" / "code this like a student" / "for a student" / "student-level" / "at my level" (combined with code/create/write/build/implement) | `student` |
|| The trigger phrase that fired is logged in the reasoning output for debugging.
| Design / UI / visual (generic fallback ONLY) | `creative` |
| Tailwind UI components / Flowbite / generate theme from brand color / Flowbite MCP / Figma-to-code via Flowbite | `flowbite` MCP → `mcp_flowbite_generate_theme` (brandColor + instructions), `mcp_flowbite_convert_figma_to_code` (needs FIGMA_ACCESS_TOKEN) + `tailwindcss` skill |
| Specific brand/company UI kit — "make it look like Stripe / Linear / Airbnb / Vercel / Figma / Notion…" | ihlamury `design-skills` → `<brand>-ui-skills` (87 kits: `airbnb-ui-skills`, `stripe-ui-skills`, `linear-ui-skills`, `vercel-ui-skills`, `figma-ui-skills`, `framer-ui-skills`, `notion-ui-skills`, `github-ui-skills`, `slack-ui-skills`, `supabase-ui-skills`, `openai-ui-skills`, `anthropic-ui-skills`, `apple-ui-skills`, `shopify-ui-skills`, …). Match the brand name to its bare skill name; if exact kit unknown, fall back to `creative`. |
| UI "slop" cleanup / deslop / fix spacing·hierarchy·typography·small layout | `baseline-ui` + `improve-ui` (from ibelick `ui-skills`) |
| Name a motion/animation effect ("what's it called when a popover opens / iOS rubber-band scroll") | `animation-vocabulary` (from emilkowalski `skills`) |
| Add / improve / review web animations & motion | `improve-animations` + `review-animations` + `find-animation-opportunities` (emilkowalski) |
| Design critique / structured feedback on a design | `design-critique` (from `designer-skills`) |
| Visual style / aesthetic / theme — glassmorphism·brutalism·bento·editorial·gradient·claymorphism·cosmic·dramatic·geometric·minimal·retro | use the **bare style name** from `awesome-design-skills` (67 styles: `glassmorphism`, `brutalism`, `bento`, `editorial`, `gradient`, `claymorphism`, `clean`, `bold`, `flat`, `corporate`, `futuristic`, `doodle`, `dithered`, …). Match the requested vibe to its bare name (e.g. load `glassmorphism`). |
| Design system / component library / design tokens / theming | `designer-skills`: pick the leaf skill by need — `component-spec`, `design-token`, `pattern-library`, `theming-system`, `motion-system`, `icon-system` (under `design-systems/skills/`). No exact leaf match → `find-skills` with "design system component spec token". |
| UX strategy / user research / personas / journey maps | `designer-skills`: `user-persona`, `journey-map`, `empathy-map`, `jobs-to-be-done`, `interview-script`, `research-repository` (under `design-research/skills/` & `ux-strategy/skills/`). Fallback `find-skills` "UX research persona". |
| Interaction design / UX laws / forms / error handling | `designer-skills`: `animation-principles`, `fitts-law`, `doherty-threshold`, `form-design`, `error-handling-ux`, `feedback-patterns` (under `interaction-design/skills/`). |
| Prototyping / usability testing / heuristic eval | `designer-skills`: `prototype-strategy`, `heuristic-evaluation`, `a-b-test-design`, `accessibility-test-plan`, `click-test-plan` (under `prototyping-testing/skills/`). |
| UI design craft — color/visual/aesthetic/dark mode | `designer-skills`: `color-system`, `aesthetic-usability`, `dark-mode-design`, `data-visualization`, `law-of-common-region` (under `ui-design/skills/`). |
| Design critique / visual review | `designer-skills`: `design-critique` (under `design-ops/skills/`) + `visual-critique/skills/` leaves: `critique-color`, `critique-typography`, `critique-composition`, `critique-affordance`. |
| Designer toolkit — design rationale / system adoption / ux-writing | `designer-skills`: `design-rationale`, `design-system-adoption`, `ux-writing`, `presentation-deck` (under `designer-toolkit/skills/`). |
| **Design director / full design workflow — design, redesign, shape, critique, audit, polish, distill, harden, layout, typeset, clarify, adapt, optimize, animate any frontend** (landing, dashboard, app UI, component, form, onboarding) | **`impeccable`** (local pbakaus v4.0.4, design-director skill + 59-rule detector). Setup: run `node <skill-base-dir>/scripts/context.mjs` once per session (loads PRODUCT.md, DESIGN.md, surface brief); load the owning playbook from `reference/` (e.g. `new-work.md`, `critique.md`, `audit.md`); load `reference/craft-floor.md` immediately before editing UI. Seed project context when missing: `init` → PRODUCT.md, `document` → DESIGN.md. Detector: `npx impeccable detect` on UI files (59 deterministic rules incl. AI-slop patterns); `impeccable ignores` for per-project waivers. ⚠️ Name collides with the typeui style skill in `awesome-design-skills` — always load the local one: `C:\Users\YOUR_USERNAME\AppData\Local\hermes\skills\impeccable`. |
| Brand/aesthetic from Open Design's imported systems — "make it look like BMW / Binance / Bugatti / Lamborghini / Nike / Tesla / Mission Control…" (66 kits) | `opendesign/od-<brand>` — bare name `od-bmw`, `od-binance`, `od-bugatti`, `od-lamborghini`, `od-nike`, `od-tesla`, `od-mission-control`, etc. (list via `skills_list` under category `opendesign`). Each is a full DESIGN.md spec (palette, typography, spacing, components, do/don't). |
| AI slop in prose / writing / copy / scripts — remove AI-isms, filler phrases, formulaic structures, adverbs | `writing/stop-slop` (banned phrases + before/after references + 1–10 scoring) |
> **Design routing note:** 262 design skills are registered locally via `skills.external_dirs` (ihlamury `design-skills`, `awesome-design-skills`, `designer-skills`, ibelick `ui-skills`, emilkowalski `skills`) plus 66 imported Open Design systems under category `opendesign/` (`od-*`) and the local `impeccable` design director. Routing order for ANY design/UI/visual request: ① `impeccable` for full design workflows (design/redesign/critique/audit/polish) — it generates/consumes PRODUCT.md + DESIGN.md per project; ② a SPECIFIC bare-named style/brand skill (`glassmorphism`, `stripe-ui-skills`, `od-bmw`) when the user names a brand/vibe; ③ `creative` generic fallback only. Hermes resolves skills by **bare name** (e.g. `glassmorphism`, `od-bmw`); use `find-skills` or `skills_list` if unsure which design skill fits.
| ECC agent invocation | `ecc-bridge` |
| Delegate coding / which model for what / subagent setup / "use deepseek for this" / "delegate to coding agent" | `subagent-delegation` |
| Complex / multi-step task with 3+ independent subtasks | `subagent-delegation` — delegate independent subtasks to parallel subagents via `delegate_task(tasks=...)` |
| OpenCode coding agent delegation (code write/modify) | `autonomous-ai-agents/opencode` — use `opencode run --model opencode-go/meta/muse-spark-1.2-contributor` |
| oh-my-opencode-slim / Pantheon agent swarm / multi-agent coding / agent orchestration / agent council / multi-model consensus | `autonomous-ai-agents/oh-my-opencode-slim` — uses Pantheon agents (Orchestrator=chat model, Oracle/Explorer/Librarian/Designer/Fixer=muse-spark-1.2-contributor, Observer=mimo-v2.5) |
| SkillClaw / skill evolution / auto-evolve / self-evolving skills / background skill improvement / cross-session skill refinement | `skillclaw` — runs `skillclaw start --daemon` on port 30000, auto-evolves Hermes skills from session data |
| Research / papers / monitoring | `research--arxiv`, `research--blogwatcher`, `research--grounded-citations` |
| Email | `email--himalaya` (`himalaya`), `gmail` |
| GitHub / PR / repo | `github` |
| Find / discover a skill that matches a task | `find-skills` (from vercel-labs/skills) |
| Skill lookup — which skill for X (sub-second TF-IDF, no API) | `lightrag-skill-finder` (local TF-IDF over 295 skills) |
| Browse, search, or explore skills by category / browse skill catalog / find skill for X | `find-skills` |
| Productivity / docs / PDFs | `productivity` |
| Any Supabase task (schema, auth, RLS, migrations, edge functions, realtime) | `supabase` (always) + `software-development/fullstack-nextjs-supabase` for Next.js apps |
| Deploy to Vercel / fix production deploy | `vercel-deployment`; Netlify → `netlify-deploy`; static site → `devops/static-site-github-pages-deploy` |
| Browser automation / e2e / scrape via browser / screenshots of web pages | `agent-browser` (CLI) or `playwright` (script) or `browser-testing-with-devtools` (CDP) |
| Take a desktop/system screenshot | `screenshot` |
| Text-to-speech / voiceover audio (ElevenLabs mandatory for voiceovers) | `elevenlabs-tts` (Rachel voice; key in MoneyPrinterTurbo/.elevenlabs_key) |
| YouTube video → transcript / summary / thread / blog | `media--youtube-content` (`youtube-content`) |
| Extract text from PDFs/scans/images (OCR) | `productivity--ocr-and-documents` (`ocr-and-documents`) |
| Image generation / editing (ComfyUI local, GPT-Image-2, assets) | `creative--comfyui`, `gpt-image-2`, `unsplash-asset-images`, `aura-asset-images` |
| ML models / HF hub / llama.cpp local inference / W&B | `mlops--huggingface-hub`, `mlops/inference/llama-cpp`, `mlops/evaluation/weights-and-biases` |
| Philips Hue / smart home | `smart-home--openhue` (`openhue`) |
| Wix app extensions | `wix-app` |
| Music/audio generation (Suno-style, spectrograms) | `media--heartmula`, `media--songsee`, `songwriting-and-ai-music` |
| Export markdown to DOCX/PPTX/XLSX/PDF/HTML/CSV/JSON/XML/LaTeX/IPYNB / convert table to spreadsheet / extract code blocks from markdown / generate formatted report / markdown exporter | `productivity/markdown-exporter` |
| Data / notebooks / analytics | `data-science` |
| Media / audio / video | `media` |
| Smart home | `smart-home--openhue` (`openhue`) |
| MLOps / models | `mlops` |
| Notes / Obsidian / wikilinks / callouts / embeds / properties / vault operations / .base files / Bases / JSON Canvas / .canvas files / Obsidian CLI / plugin dev / theme dev / knowledge graph / KG viz | `note-taking` (bundle all three: `obsidian` for core syntax + operations, `obsidian-codebase-graph` for code graph mapping, `obsidian-knowledge-graph` for vault graph viz) |
| Backup / restore / credential sync / Google Drive backup / rclone / migrate Hermes | `workflow/hermes-backup-workflow` |
| Workflow / model selection | `workflow` |
| Local AI mode / use local model / local only / offline mode / run locally / no cloud (opt-in only — only when user explicitly says "local mode" or similar) | `workflow/local-ai-routing` (load on demand only) |
| SEO / site audit / schema / rankings | `seo` |
| Marketing / sales / content / growth | `productivity/ai-marketing-skills` |
| App building / prototype | `software-development/buildable-plugin` |
| Start new feature / implement spec / design-first workflow / structured dev pipeline / Superpowers methodology / obra superpowers | `software-development/superpowers-methodology` |
| Web data / search / scrape / interact / parse / crawl / monitor / Firecrawl | `firecrawl` umbrella; route to leaf: `firecrawl-search`, `firecrawl-scrape`, `firecrawl-interact`, `firecrawl-parse`, `firecrawl-crawl`, `firecrawl-map`, `firecrawl-monitor`, `firecrawl-deep-research`, `firecrawl-workflows` |
|| Computer use / GUI agent / GUI automation / Simular Agent / Agent S / Agent S2 / Agent S3 / desktop automation | `autonomous-ai-agents/agent-s-gui` — runs `gui_agents` package or `agent_s` CLI |
||| Kanban / multi-agent coordination / task board / decompose work / agent pipeline / parallel workers / orchestrator routing / triage tasks / swarm | `hermes-kanban-setup` — Hermes built-in kanban (`hermes kanban`, SQLite dispatcher). Orchestrator profile has `kanban_*` tools. Create triage tasks → dispatcher auto-decomposes → workers execute. `hermes kanban list` to view. |
||| **No trigger match** → fallback: run `python C:/Users/YOUR_USERNAME/AppData/Local/hermes/lightrag_index/find.py "<user prompt>"` to surface top-5 relevant skills from 665 indexed. Load the top match, execute. |

### Cross-Cutting Behavioral Guidelines (Load alongside any code task)
| Trigger | Load With |
|---------|-----------|
| Writing / reviewing / refactoring code — remind me to think before coding, keep it simple, make surgical changes, define success criteria / behavioral guardrails / Karpathy principles / avoid overcomplication | `software-development/karpathy-guidelines` |

### Quant & Finance Skills (LLMQuant Domain)
| Trigger | Route To |
|---------|----------|
| Commodities | `llmquant-commodities` |
| Credit | `llmquant-credit` |
| Crypto | `llmquant-crypto` |
| Data query (fetch financial data) | `llmquant-data` (gateway router) |
| Equities | `llmquant-equities` |
| Equity Derivatives | `llmquant-equity-derivatives` |
| ETFs | `llmquant-etfs` |
| Events | `llmquant-events` |
| Investor Lenses | `llmquant-investor-lenses` |
| Macro | `llmquant-macro` |
| Market Intelligence | `llmquant-market-intelligence` |
| Options | `llmquant-options` |
| TradingAgents multi-agent trading framework / stock analysis agents / multi-agent stock research / automated trading analysis | `software-development/tradingagents` — configured for OpenRouter + DeepSeek V4 Flash |
| Portfolio | `llmquant-portfolio` |
| Portfolio Lab | `llmquant-portfolio-lab` |
| Prediction Markets | `llmquant-prediction-markets` |
| Rates & FX | `llmquant-rates-fx` |
| Risk | `llmquant-risk` |
| Strategies | `llmquant-strategies` |

For general finance/investing → activate `soul_finance` + relevant LLMQuant skill.
For fintech-code → `soul` + `soul_finance` + relevant LLMQuant skill.

---

## MCP & Tool Routing (12 servers enabled — pick the server, then its tool)

MCP tools are deferred: `tool_search` → `tool_describe` → `tool_call`. Never claim a tool is unavailable without searching first. The skill index below is the route table; the tool name IS the tool.

| Need | MCP Server → Tools | Notes |
|------|-------------------|-------|
| **UI components / design inspiration / shadcn code** | `21st` → `search`, `get_inspiration`, `get_component`, `get_take`, `generate` | Design-first: use BEFORE building UI (decide rule). 35 tools |
| **Tailwind components / Flowbite theme generation / Figma→code** | `flowbite` → `generate_theme` (brandColor + instructions), `convert_figma_to_code` (figmaNodeUrl) | `npx -y flowbite-mcp`; verified live 2026-08-09. Tools: `mcp_flowbite_generate_theme`, `mcp_flowbite_convert_figma_to_code`. Figma tool needs `FIGMA_ACCESS_TOKEN` env (not set) |
| **Codebase symbol lookup (any `~/Documents/Projects/` code)** | `codegraph` → `codegraph_explore` (primary), `codegraph_search`, `codegraph_callers/callees/impact`, `codegraph_files`, `codegraph_status` | **Pass `projectPath`** when CWD is outside the project. 144,827 nodes / 326,322 edges / 8,421 files indexed |
| **Codebase structure / graph queries** | `graphify` → `query_graph`, `get_node`, `get_neighbors`, `god_nodes`, `shortest_path` | Index per-project (21/24 projects); `graph_stats` to check |
| **Web search / scrape / crawl / extract / monitor / deep research** | `firecrawl` → `firecrawl_search`, `firecrawl_scrape`, `firecrawl_extract`, `firecrawl_crawl`, `firecrawl_map`, `firecrawl_monitor_*`, `firecrawl_deep_research`, `firecrawl_agent`, `firecrawl_interact` | 27 tools; umbrella skill `firecrawl` routes to leaves |
| **Financial / market data (crypto, equities, ETFs, macro, SEC filings, 13F, prediction markets, LLMQuant wiki/papers)** | `llmquant-data` → `equity_*`, `crypto_*`, `etf_*`, `macro_*`, `sec_filing_*`, `sec_13f_*`, `polymarket_*`, `wiki_*`, `paper_*`, `news_browse` | 26 tools; router skills `llmquant-*` per asset class |
| **Obsidian vault graph / KG queries** | `obsidian-kg` → `obsidian_knowledge_graph` (+ list/read resources) | On-demand only (token-heavy) |
| **Session memory recall / insight search** | `agentmemory` → `memory_recall`, `memory_smart_search`, `memory_sessions`, `memory_save` | Cross-session insights; use before re-asking user |
| **VS Code integration** | `vscode` → `open_project`, `open_file`, `create_diff`, `execute_shell_command`, `check_extension_status` | Use when user is working in VS Code |
| **Figma** | `figma` (Composio) → design file tools | Auth via Composio; 401 → re-auth |
| **Figma dev-mode export (SVG/PNG assets, layout data)** | `figma-dev` → `download_figma_images`, `get_figma_data` | `npx -y figma-developer-mcp`; 2 tools |
| **Open Design app (design generation, plugins)** | `opendesign` MCP | Daemon-gated: app must be running; else use `od-*` skills directly |

**Core Hermes tool reflexes (no MCP needed):**
- `skill_view`/`skills_list` — load skill BEFORE acting; `skills_list(category=...)` to browse (e.g. `opendesign`, `media`)
- `tool_search`/`tool_describe`/`tool_call` — any deferred capability (21st, codegraph, firecrawl, graphify, llmquant-data, obsidian-kg, vscode, agentmemory, flowbite, video, project). Search catalog before declaring unavailable.
- `vision_analyze` — images; user rule: hard vision via MiMo subagent (delegate), simple inline ok
- `open_preview`/`focus_pane` — show the user HTML/localhost/files in the desktop app
- `MEDIA:/path` in replies — deliver files natively (images inline, audio/video playable)
- `delegate_task` — 1-2 patches → Muse Spark child; 3+ independent → parallel batch; children can't call clarify/memory/cron
- `cronjob`, `todo`, `memory`, `session_search` — schedule, track, persist, recall
- `process`/`close_terminal` — manage background runs; `terminal(background=true, notify_on_complete=true)` for long builds

---

## Reasoning Protocol (Background — Use When Routing Confidence Is Low)

### Step 1 — Decompose the prompt
Break the request into actual components. Name them explicitly before routing.

### Step 2 — Challenge the obvious interpretation
Ask: is the surface reading what's actually being asked? Check for implicit context, user shorthand, prior patterns.

### Step 3 — Score routing confidence
- **High** — intent is unambiguous, skill maps cleanly
- **Medium** — plausible match but alternatives exist
- **Low** — best guess; flag assumption in output. If entire routing is Low, ask clarifying question.

### Step 4 — Second-order thinking
Pre-load skills that step 2 of the workflow will need. Example: new feature → pre-load code review + Obsidian update.

### Step 5 — Self-challenge
Could one skill handle this instead of three? Minimum viable skill set.

---

## Complementary Setup Routing

When the user asks for setup/install/configure of a new repo or tool, proactively check for complementary integrations:

| New Repo | Also Route To |
|----------|---------------|
| Any new project | `graphify-integrate` + Obsidian bundle (build graph via `obsidian-codebase-graph --clean`, create note, cross-link) — only when user requests it |
| Agent framework (ECC, devfleet, etc.) | `external-agent-ecosystem-adapter` |
| Model/provider resource | `free-ai-tools` (model catalog) + `model-recommender-workflow` |
| Freebuff / Codebuff | `free-ai-model-router` (combined model selection) |
| FreeLLMAPI | `free-ai-model-router` (alternative model source) |
| API-mega-list | `productivity/api-mega-list` + check MCP Server candidates |
| Agent Reach / agent-reach | `agent-reach` skill + `mcporter` Exa config + verify with `agent-reach doctor` |
| Buildable Plugin | `software-development/buildable-plugin` + design/plan/review skills |
| AI Marketing Skills | `productivity/ai-marketing-skills` |
| Firecrawl / web search / scrape / interact / parse / web data extraction | `firecrawl` umbrella + leaf skills (`firecrawl-search`, `firecrawl-scrape`, `firecrawl-interact`, `firecrawl-parse`, `firecrawl-crawl`, `firecrawl-map`, `firecrawl-monitor`, `firecrawl-research-index`, `firecrawl-deep-research`, `firecrawl-workflows`) |
| Simular Agent SDK / Agent S / Agent S2 / Agent S3 / gui-agents / computer use agent / GUI automation | `autonomous-ai-agents/agent-s-gui` — `gui_agents` package at `/c/Users/YOUR_USERNAME/Documents/Projects/agent-s`, `agent_s` CLI available in Hermes venv |

---

## Conflict Resolution

- Two domain skills overlap → activate both; primary soul governs
- No skill matches → fall back to closest soul file, flag the gap in output
- Ambiguous intent → assume, state in one line, proceed (unless entire routing is Low confidence)

## Output Format

State once at the start of each session, then execute immediately:

```
**Intent:** [what was detected]
**Skills activated:** [list in execution order]
**MCP/tools:** [which MCP servers + core tools the task needs]
**Tier:** [from task_tier]
```

Then proceed. No lengthy reasoning blocks printed — output is the work.

## Self-Correction

If routing produces a wrong result:
1. Record what went wrong
2. Record what should have been selected
3. Patch /decide with the correction
4. Notify the user

Update /decide when: new repo integrated, new routing pattern discovered, complementary relationship found, conflict resolved.

---

## Quick Reference: Token Saver Commands

Use MCP tools FIRST (**pass `projectPath` when CWD is not inside a project**):
```
mcp_codegraph_codegraph_explore(query="<term>", projectPath="C:\\Users\\Attila\\Documents\\Projects\\$PROJ")  # Primary — one call, returns source + locations
mcp_codegraph_codegraph_search(query="<term>")      # Broader name search
mcp_codegraph_codegraph_callers(symbol="<fn>")      # Who calls this function
mcp_codegraph_codegraph_callees(symbol="<fn>")      # What this function calls
mcp_codegraph_codegraph_impact(symbol="<fn>")       # Refactoring impact analysis
mcp_codegraph_codegraph_files(pattern="*.tsx")      # File tree with metadata
mcp_codegraph_codegraph_status()                    # Index health check
```

Terminal fallback (if MCP tools are unavailable):
```bash
# Step B — CodeGraph (always works)
cd ~/Documents/Projects && codegraph query "<term>"
cd ~/Documents/Projects && codegraph callers "<function>"
cd ~/Documents/Projects && codegraph callees "<function>"
cd ~/Documents/Projects && codegraph impact "<function>"

# Step C — Graphify (if index exists)
test -f ~/Documents/Projects/$PROJECT/graphify-out/graph.json && \
  cd ~/Documents/Projects/$PROJECT && \
  ~/.local/bin/graphify.exe query "<question>" --budget 2000 --graph graphify-out/graph.json
```

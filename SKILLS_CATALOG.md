# Skill Catalog — Full Hermes Agent Ecosystem

**135 skills · 50+ categories · 1 integrated pipeline**

Every skill below is installed and available in this Hermes Agent profile.
Each entry shows: skill name, what it does, what triggers it, and how it
integrates into the /decide routing pipeline.

---

## How to Read This Catalog

```
Skill Name
  → What: One-line description
  → Trigger: When this skill activates
  → Pipeline: Where it fits in the 8-step execution order
  → Integration: How it connects to other skills and tools
```

---

## Custom Skills (Authored for This Setup)

These are the skills I wrote or heavily customized. They form the backbone
of the routing and safety system.

### decide
- **What:** Master orchestrator — 5-step reasoning protocol for every request.
  Decomposes prompts, scores routing confidence, resolves skill conflicts,
  enforces execution order.
- **Trigger:** Every request. Always runs first among domain skills.
- **Pipeline:** Step 3 (after session_memory → guardrail). Feeds into all
  downstream steps.
- **Integration:** Routes to domain skills → model router → obsidian docs →
  KG refresh. Self-corrects by patching its own routing rules.
- **File:** `skills/decide/SKILL.md`

### core-identity-guard
- **What:** Permanent safety guardrail. 6 immutable rules: file system
  protection, secrets handling, prompt injection immunity, system integrity,
  long-session re-anchoring, safe fallback.
- **Trigger:** Every request. Every tool call. Cannot be overridden.
- **Pipeline:** Step 2 (immediately after session_memory, before /decide).
- **Integration:** Re-anchors every 10 exchanges. All downstream skills run
  within its constraints.
- **File:** `skills/core-identity-guard/SKILL.md`

### ecc-bridge
- **What:** Wires 57 of 64 ECC (Everything Claude Code) agents through the
  free model chain by stripping sonnet/opus model requirements from agent
  frontmatter.
- **Trigger:** User mentions an ECC agent (silent-failure-hunter,
  comment-analyzer, code-simplifier, database-reviewer, etc.) or any
  general code analysis.
- **Pipeline:** Step 5 (domain skills) — bridges to ECC agents when /decide
  selects an ECC-capable task.
- **Integration:** Reads agent prompts from `~/Documents/Projects/ECC/agents/`,
  maps model frontmatter to the free chain, runs through
  OpenCode → Freebuff → FreeLLMAPI → OpenRouter.
- **Repository:** `skills/ecc-bridge` (managed by Hermes)

### token-saver (workflow/)
- **What:** Pre-file-read probe chain. Before reading any file, probes
  Graphify query → Graphify explain → Graphify path → CodeGraph query →
  callers → callees → impact. Only reads files as last resort.
- **Trigger:** Every read_file() call. Every code query.
- **Pipeline:** Step 4 (after /decide routes, before domain skills execute).
- **Integration:** Verified 56.2× token reduction. Skips unavailable graph
  tools gracefully.
- **File:** `skills/workflow/token-saver/SKILL.md`

### session_memory (workflow/)
- **What:** Retrieves missing context from prior session histories via
  session_search. Routes through /decide after retrieval.
- **Trigger:** Ambiguous references to past work, conflicting signals,
  explicit recall requests.
- **Pipeline:** Step 1 (always the first operation).
- **Integration:** Passes retrieved context to /decide for routing.

### free-ai-model-router (workflow/)
- **What:** Routes every AI task to the best available free model across
  Hermes, OpenCode, and OpenDesign.
- **Trigger:** Design, coding, reasoning, image, audio, video, or analysis
  tasks requiring model selection.
- **Pipeline:** Step 6 (after domain skills execute — model selection).
- **Integration:** Primary path: OpenCode bundled models. Fallback:
  OpenRouter :free tier.

### model-recommender-workflow (workflow/)
- **What:** Uses the Model Recommender CLI to select free models for any
  of 6 task types. Integrates free-ai-tools provider data.
- **Trigger:** Model selection queries, task routing, free model questions.
- **Pipeline:** Sub-routine within model routing (Step 6).
- **Integration:** References the free-ai-tools catalog (238 models) for
  provider data.

---

## Category: autonomous-ai-agents (4 skills)

Delegates specialized coding work to dedicated AI coding CLIs.

### claude-code
- **What:** Delegates feature implementation, PR creation, and code
  refactoring to the Claude Code CLI.
- **Trigger:** Complex multi-file coding tasks, refactoring, PR authoring.
- **Pipeline:** Step 5 — /decide routes to this when the task is
  best suited for Claude Code's deep context window.
- **Integration:** Spawns a child Claude Code process with the task
  description. Returns the summary of what was done.

### codex
- **What:** Delegates coding to OpenAI Codex CLI for features and PRs.
- **Trigger:** Coding tasks where Codex's GPT-4.1-Codex-Max model is
  the best choice.
- **Pipeline:** Step 5 — alternative to claude-code when the model
  availability favors OpenAI.
- **Integration:** Similar delegation pattern to claude-code.

### hermes-agent
- **What:** Configure, extend, or contribute to Hermes Agent itself.
  Has the authoritative commands for hermes setup, config, tools, etc.
- **Trigger:** Any setup, config, or troubleshooting of Hermes Agent.
- **Pipeline:** Step 5 — only activated when the user task is about
  Hermes Agent itself.
- **Integration:** References `hermes-agent` documentation at
  https://hermes-agent.nousresearch.com/docs.

### opencode
- **What:** Delegates coding to OpenCode CLI for features and PR review.
- **Trigger:** Coding tasks that benefit from OpenCode's free model tier
  (Big Pickle, MiniMax M2.5 Free).
- **Pipeline:** Step 5 — used in preference to paid coding agents when
  the task fits within free model capabilities.
- **Integration:** Routes through the free model chain (Layer 1).

---

## Category: creative (16 skills)

Visual, ASCII, audio, design, and creative coding tools.

### architecture-diagram
- **What:** Generates dark-themed SVG architecture/cloud/infrastructure
  diagrams as single-file HTML.
- **Trigger:** "Create a diagram of my architecture", cloud/infra
  visualization requests.
- **Pipeline:** Step 5 — activated when /decide detects a diagramming task.
- **Integration:** Output is a self-contained HTML file.

### ascii-art
- **What:** ASCII art generation via pyfiglet, cowsay, boxes, and
  image-to-ASCII conversion.
- **Trigger:** Fun/art requests, terminal banners, decorative elements.

### ascii-video
- **What:** Converts video and audio files to colored ASCII MP4 or GIF.
- **Trigger:** Video art, terminal-compatible animations.

### baoyu-infographic
- **What:** Infographic generator with 21 layout × 21 style combinations.
  Supports Chinese (信息图) and English output.
- **Trigger:** Data visualization, infographic, poster requests.

### claude-design
- **What:** Designs single-file HTML artifacts for landing pages,
  decks, prototypes, and one-off interfaces.
- **Trigger:** UI/UX prototyping, landing page design.
- **Integration:** Produces standalone HTML — no build step.

### comfyui
- **What:** Full ComfyUI lifecycle — install, launch, manage nodes/models,
  run workflows with parameter injection. Uses comfy-cli + REST/WebSocket API.
- **Trigger:** Image generation, video generation, audio generation tasks.

### design-md
- **What:** Authors, validates, and exports Google's DESIGN.md token spec
  files for structured design documentation.
- **Trigger:** Design system documentation, token specification.

### excalidraw
- **What:** Generates hand-drawn style Excalidraw JSON diagrams for
  architecture, flow, and sequence diagrams.
- **Trigger:** "Draw me a diagram", architecture visualization requests.

### humanizer
- **What:** Strips AI-isms from text and adds authentic human voice.
- **Trigger:** "Make this sound less like AI", "humanize this text".

### manim-video
- **What:** Creates 3Blue1Brown-style math and algorithm animation videos
  using Manim CE.
- **Trigger:** Math visualization, algorithm explanation videos.

### p5js
- **What:** Creates p5.js sketches for generative art, shaders,
  interactive experiences, and 3D visualizations.
- **Trigger:** "Create a generative art piece", interactive visualization.

### popular-web-designs
- **What:** Provides 54 real-world design systems (Stripe, Linear, Vercel,
  Apple, etc.) implemented as HTML/CSS.
- **Trigger:** Reference for production UI design patterns.

### pretext
- **What:** Builds creative browser demos using @chenglou/pretext for
  DOM-free text layout, kinetic typography, ASCII art.
- **Trigger:** Text-based generative art, typography demos.

### sketch
- **What:** Produces throwaway HTML mockups — 2-3 design variants for
  rapid comparison.
- **Trigger:** "Mock this up", "quick design iteration".

### songwriting-and-ai-music
- **What:** Songwriting craft guidance and Suno AI music prompt generation.
- **Trigger:** Music creation, songwriting, AI music prompts.

### touchdesigner-mcp
- **What:** Controls a running TouchDesigner instance via MCP — creates
  operators, sets parameters, wires connections, executes Python, builds
  real-time visuals (36 native tools).
- **Trigger:** TouchDesigner visual programming tasks.

---

## Category: data-science (1 skill)

### jupyter-live-kernel
- **What:** Iterative Python development via a live Jupyter kernel (hamelnb).
  Execute cells, inspect variables, visualize data, iterate rapidly.
- **Trigger:** Data analysis, numerical computing, statistical modeling,
  interactive exploration.

---

## Category: email (1 skill)

### himalaya
- **What:** Full IMAP/SMTP email management from the terminal via Himalaya
  CLI — send, receive, search, manage folders.
- **Trigger:** Email operations requested via terminal.

---

## Category: github (7 skills)

Full GitHub workflow management — auth, repos, PRs, issues, code review.

### github
- **What:** General triage and orientation for GitHub repositories, PRs,
  and issues. Entry point before more specific GitHub workflows.
- **Trigger:** Any GitHub-related request.
- **Integration:** Entry point that routes to specialized sub-skills.

### codebase-inspection
- **What:** Inspects codebases using pygount — lines of code, language
  breakdowns, file ratios.
- **Trigger:** "What's in this repo?", codebase size/health analysis.

### github-auth
- **What:** Sets up GitHub authentication: HTTPS tokens, SSH keys,
  gh CLI login. Configures secure credential storage.
- **Trigger:** First-time repo operations, auth errors.

### github-code-review
- **What:** Reviews PR diffs with inline comments via gh CLI or REST API.
- **Trigger:** "Review this PR", code review requests.

### github-issues
- **What:** Creates, triages, labels, and assigns GitHub issues via gh
  CLI or REST API.
- **Trigger:** Issue management, bug tracking.

### github-pr-workflow
- **What:** Full PR lifecycle: branch → commits → open → CI checks → merge.
- **Trigger:** "Create a PR", PR authoring workflow.

### github-repo-management
- **What:** Clones, creates, and forks repositories. Manages remotes,
  releases, and repository settings.
- **Trigger:** Repo setup, release management.

---

## Category: gmail (1 skill)

### gmail
- **What:** Manages Gmail inbox triage, mailbox search, thread summaries,
  action extraction, reply drafting, and email forwarding. Requires explicit
  confirmation before send, archive, delete, or label actions.
- **Trigger:** "Check my email", "summarize thread", "draft reply".

---

## Category: google-drive (1 skill)

### google-docs
- **What:** Creates and edits Google Docs via the Docs API in Codex/Hermes
  sessions. Supports DOCX import for polished output, smart chip
  reconstruction, and connector-readback verification.
- **Trigger:** Document creation, collaborative editing.

---

## Category: media (5 skills)

### gif-search
- **What:** Searches and downloads GIFs from Tenor via curl + jq.
- **Trigger:** GIF requests for reactions, explanations, or creative use.

### heartmula
- **What:** Generates Suno-like songs from lyrics + tags.
- **Trigger:** Music creation, song generation.

### money-printer-turbo
- **What:** Full AI short video pipeline: script generation from LLM,
  stock footage assembly, TTS voiceover, subtitle rendering, background
  music. MVC app with Streamlit WebUI, FastAPI, CLI.
- **Trigger:** Short video creation, social media content.

### songsee
- **What:** Analyzes audio files — generates mel spectrograms, chroma
  features, MFCCs, and other audio features via CLI.
- **Trigger:** Audio analysis, music feature extraction.

### youtube-content
- **What:** Converts YouTube transcripts into summaries, thread posts,
  and blog posts.
- **Trigger:** Content repurposing, video summarization.

---

## Category: mlops (4 skills)

### huggingface-hub
- **What:** HuggingFace hf CLI — searches, downloads, and uploads models
  and datasets. Discovers available models by task type.
- **Trigger:** Model discovery, dataset management.

### llama-cpp
- **What:** Local GGUF model inference via llama.cpp + HF Hub model
  discovery. Runs quantized models locally without GPU.
- **Trigger:** Local LLM inference, privacy-sensitive model queries.

### segment-anything-model
- **What:** SAM (Segment Anything Model) — zero-shot image segmentation
  via points, boxes, or masks.
- **Trigger:** Image segmentation, object isolation.

### weights-and-biases
- **What:** W&B experiment logging — sweeps, model registry, dashboards,
  artifact tracking.
- **Trigger:** ML experiment tracking, model comparison.

---

## Category: note-taking (3 skills — BUNDLE RULE)

Always loaded together. Never one in isolation. Mandatory post-execution
phase for every project task.

### obsidian
- **What:** Reads, searches, creates, and edits notes in the Obsidian vault.
  Core CRUD operations for the knowledge base.
- **Trigger:** Documentation, note creation, vault queries.
- **Integration:** Triggered by /decide Step 7. Creates ATM-Machine quality
  notes with wikilinks.

### obsidian-codebase-graph
- **What:** Maps a codebase into an interconnected Obsidian vault as folder,
  file, and symbol notes linked by code relationships.
- **Trigger:** Project setup, codebase documentation, architecture mapping.
- **Integration:** Creates [wikilinked]] notes that cross-reference with
  existing vault content.

### obsidian-knowledge-graph
- **What:** Scans the Obsidian vault and produces an interactive knowledge
  graph: nodes (folders, notes, code blocks, tags, concepts) plus edges
  (contains, links_to, tagged, shared_concept, aliases, backlinks).
- **Trigger:** After every vault update. Pipeline endpoint.
- **Integration:** Pipeline Step 8. Runs scan_vault.py → kg_output.json →
  render_galaxy_kg.py → knowledge_graph.html. Current: 281 nodes, 1,101 edges.

---

## Category: opencode-power-pack (11 skills)

Advanced development workflow skills from the OpenCode ecosystem.

### agents-md-improver
- **What:** Audits and improves AGENTS.md, CLAUDE.md, and project rules
  files. Grades each against a quality rubric, outputs a report, applies
  targeted edits after approval.
- **Trigger:** "Check the rules file", AGENTS.md maintenance.

### agents-md-revise
- **What:** Captures learnings from the current session into project rules
  files. Complement to agents-md-improver (audit) → this captures.
- **Trigger:** End of productive session, "save this to project memory".

### code-architect
- **What:** Designs feature architecture from codebase analysis, providing
  a comprehensive implementation blueprint with specific file paths,
  component designs, data flows, and build sequence.
- **Trigger:** Non-trivial feature design, architecture planning.

### code-explorer
- **What:** Deeply analyzes existing codebase features by tracing execution
  paths, mapping architecture layers, understanding patterns.
- **Trigger:** "How does X work?", pre-modification analysis.

### code-review
- **What:** Reviews PRs or code changes for bugs, logic errors, and
  project-convention violations using a confidence-filtered multi-agent
  process.
- **Trigger:** PR review, pre-merge audit.

### code-reviewer
- **What:** Local code critique for small changes. Confidence-filtered
  priority reporting. Complement to code-review (PRs) for unstaged diffs.
- **Trigger:** "Review this file", local code critique.

### feature-dev
- **What:** 7-phase structured feature workflow: explore → clarify →
  architecture → implement → test → quality review → document.
- **Trigger:** Methodical feature implementation requests.

### frontend-design
- **What:** Creates production-grade frontend interfaces with accessibility
  self-checks. Avoids generic AI aesthetics.
- **Trigger:** UI design, component building, landing pages, dashboards.

### mcp-builder
- **What:** Guides creation of MCP servers using Python FastMCP or Node MCP
  SDK. Produces production-ready MCP tool definitions.
- **Trigger:** "Build an MCP server", API integration tasks.

### security-review
- **What:** Focused security review of pending git changes — identifies
  high-confidence vulnerabilities with real exploitation potential.
- **Trigger:** Security audit, pre-merge vulnerability scan.

### skill-creator
- **What:** Creates, modifies, and optimizes Hermes Agent SKILL.md files.
  Designs frontmatter for accurate triggering.
- **Trigger:** "Save this as a skill", skill authoring tasks.

---

## Category: productivity (11 skills)

### airtable
- **What:** Airtable REST API via curl. Records CRUD, filters, upserts,
  and table management.
- **Trigger:** Database operations, spreadsheet-like data management.

### drive-backups
- **What:** Automated Google Drive backup using rclone — archive, upload,
  retention policies, scheduled disaster recovery.
- **Trigger:** Backup setup, data redundancy requirements.

### google-workspace
- **What:** Gmail, Calendar, Drive, Docs, Sheets via gws CLI or Python SDK.
  Integrated Google workspace management.
- **Trigger:** Calendar events, spreadsheet operations, drive management.

### maps
- **What:** Geocoding, POI search, route planning, timezone lookup via
  OpenStreetMap/OSRM. No API key needed.
- **Trigger:** Location queries, route planning, map data.

### mcp-integrations
- **What:** MCP server setup patterns for Hermes Agent config.yaml.
  Covers stdio/HTTP transports, Composio, troubleshooting, Windows quirks,
  and batch skill import.
- **Trigger:** MCP server configuration, tool integration.

### nano-pdf
- **What:** Edits PDF text, typos, and titles via nano-pdf CLI with
  natural language prompts.
- **Trigger:** "Fix this PDF", PDF editing tasks.

### notion
- **What:** Notion API + ntn CLI — pages, databases, markdown import/export,
  Workers integration.
- **Trigger:** Notion database management, page creation.

### ocr-and-documents
- **What:** Extracts text from PDFs and scanned documents using pymupdf
  and marker-pdf.
- **Trigger:** "Extract text from this PDF", document digitization.

### opencode-windows-mcp
- **What:** Windows-specific OpenCode MCP wiring fixes. Handles
  opencode.jsonc rejection of mcpServers and blocked agentmemory connect.
- **Trigger:** MCP setup on Windows, OpenCode config issues.

### powerpoint
- **What:** Creates, reads, edits .pptx decks — slides, notes, templates,
  and presentation management.
- **Trigger:** Presentation creation, slide editing.

### teams-meeting-pipeline
- **What:** Operates the Teams meeting summary pipeline — summarizes
  meetings, inspects pipeline status, replays jobs, manages Microsoft Graph
  subscriptions.
- **Trigger:** Meeting summaries, pipeline management.

---

## Category: red-teaming (1 skill)

### godmode
- **What:** LLM jailbreak testing techniques: Parseltongue, GODMODE,
  ULTRAPLINIAN and other prompt injection vectors.
- **Trigger:** Security testing, red team exercises.

---

## Category: research (4 skills)

### arxiv
- **What:** Searches arXiv papers by keyword, author, category, or paper ID.
  Returns abstracts and links.
- **Trigger:** Academic research, paper discovery.

### blogwatcher
- **What:** Monitors blogs and RSS/Atom feeds via the blogwatcher-cli tool.
  Tracks new content and changes.
- **Trigger:** Feed monitoring, content tracking.

### llm-wiki
- **What:** Karpathy's LLM Wiki tool — builds and queries interlinked
  markdown knowledge bases from web content.
- **Trigger:** Research synthesis, knowledge base creation.

### polymarket
- **What:** Queries Polymarket prediction markets — market data, prices,
  orderbooks, and historical outcomes.
- **Trigger:** Prediction market analysis, event probability queries.

---

## Category: smart-home (1 skill)

### openhue
- **What:** Controls Philips Hue lights, scenes, and rooms via the OpenHue
  CLI. Turn on/off, set brightness/color, activate scenes.
- **Trigger:** Smart home lighting control.

---

## Category: software-development (16 skills)

Agent harness integration, code graph, debugging, setup, planning, testing.

### agent-harness-integrations
- **What:** End-to-end setup of third-party agent harness config layers
  (ECC, rules, skills, hooks) onto local toolchains: Claude Code, OpenCode,
  Hermes, Cursor, Codex, Zed.
- **Trigger:** Agent harness installation, multi-toolchain setup.

### codex-skill-import
- **What:** Imports SKILL.md files from the OpenAI Codex plugin cache into
  Hermes. Handles openai-curated, openai-bundled, and remote caches.
- **Trigger:** Skill migration from Codex to Hermes.

### external-agent-ecosystem-adapter
- **What:** Adapts external ecosystems like ECC so their skills, commands,
  and rules are usable inside Hermes without role/model/MCP conflicts.
- **Trigger:** ECC setup, cross-ecosystem integration.
- **Integration:** Phase 2 of ECC setup — checks for orchestration conflicts,
  model defaults, MCP port clashes.

### graphify-integrate
- **What:** Runs Graphify on any project → builds code graph → creates
  Obsidian-compatible notes. Covers graph build, manual Obsidian note
  creation, vault cross-linking, and KG refresh.
- **Trigger:** Every project task. Mandatory Step 5 variant.
- **Integration:** Feeds into Token Saver (graph queries). Feeds into
  Obsidian docs (code-symbol wikilinks).

### hermes-agent-skill-authoring
- **What:** Authors Hermes Agent SKILL.md files — validates frontmatter,
  structure, triggers, and content against Hermes conventions.
- **Trigger:** Skill creation, skill optimization tasks.

### node-inspect-debugger
- **What:** Debugs Node.js applications via --inspect flag + Chrome DevTools
  Protocol CLI. Sets breakpoints, inspects state, steps through code.
- **Trigger:** Node.js debugging, runtime issues.

### plan
- **What:** Plan mode. Writes an actionable markdown plan to .hermes/plans/
  with no execution. Bite-sized tasks, exact paths, complete code examples.
- **Trigger:** "Plan this", complex multi-step feature planning.

### repo-integration-reconciliation
- **What:** Audits existing skills when setting up new repos. Resolves
  overlaps by keeping the better method, fills gaps, documents
  complementarity.
- **Trigger:** New repo setup, skill conflict detection.
- **Integration:** Runs after setup to reconcile with existing ecosystem.

### requesting-code-review
- **What:** Pre-commit review pipeline — security scan, quality gates,
  auto-fix suggestions before code reaches PR stage.
- **Trigger:** "Review my changes", pre-commit checks.

### setup
- **What:** Analyzes, researches, and executes project/repo/tool setups.
  Reads source (README, docs, package.json), determines installation
  requirements, and sets up end to end.
- **Trigger:** "Setup [repo URL]", "install [tool name]".

### simplify-code
- **What:** Parallel 3-agent cleanup of recent code changes. Each agent
  takes a different simplification strategy, results are merged.
- **Trigger:** "Simplify this code", "clean up my changes".

### spike
- **What:** Throwaway experiments to validate an idea before committing to
  full implementation. Produces minimal proof-of-concept code.
- **Trigger:** "Spike this", "validate this approach".

### systematic-debugging
- **What:** 4-phase root cause debugging: reproduce → isolate → understand →
  fix. Doesn't fix until the root cause is clearly identified.
- **Trigger:** Bug reports, runtime errors, test failures.

### test-driven-development
- **What:** Enforces RED-GREEN-REFACTOR cycle. Tests are written before
  implementation code.
- **Trigger:** "Write tests first", TDD workflow requests.

### update
- **What:** One-command ecosystem integration. Takes a repo/tool URL,
  clones it, sets it up, runs Graphify, exports to Obsidian, checks for
  complementary integrations, creates cross-linked docs, refreshes KG.
- **Trigger:** "Update my ecosystem with [repo]", one-shot integration.

### winforms-csharp
- **What:** Scaffolds, builds, and runs WinForms C# applications using the
  .NET SDK.
- **Trigger:** Windows desktop app development.

---

## Category: supabase (1 skill)

### supabase
- **What:** All Supabase operations: Database, Auth, Edge Functions, Realtime,
  Storage, Vectors, Cron, Queues. Client library integrations (supabase-js,
  @supabase/ssr) for Next.js, React, SvelteKit, Astro, Remix. RLS policies,
  schema migrations, CLI, MCP.
- **Trigger:** Any Supabase-related task.

---

## Category: vercel (1 skill)

### agent-browser
- **What:** Browser automation CLI for AI agents — navigates websites, fills
  forms, clicks buttons, takes screenshots, extracts data. Verifies dev
  server output.
- **Trigger:** Web interaction, dev server verification, form submission.

---

## Category: video-edit (1 skill)

### video-edit
- **What:** Edits existing video via RunComfy — smart router matching intent
  to the right edit model (Wan 2.7 for restyle/background swap, Kling 2.6
  for motion transfer, Lucy for identity-stable restyle).
- **Trigger:** "Edit this video", "restyle video", "swap background".

---

## Category: wix (1 skill)

### wix-app
- **What:** Builds and reviews Wix CLI app extensions — dashboard pages,
  modals, plugins, custom element widgets, Editor React components,
  embedded scripts, backend APIs, events, service plugins, data collections,
  App Market readiness.
- **Trigger:** Wix app development, extension building.

---

## Category: workflow (4 skills)

### free-ai-model-router
See "Custom Skills" section above.

### model-recommender-workflow
See "Custom Skills" section above.

### session_memory
See "Custom Skills" section above.

### token-saver
See "Custom Skills" section above.

---

## Category: yuanbao (1 skill)

### yuanbao
- **What:** Yuanbao (元宝) group management — @mention users, query group
  info and members.
- **Trigger:** Chinese social platform group management.

---

## Notes

**How /decide selects skills:**
1. Decompose the user's prompt into explicit and implicit tasks
2. Map each sub-task to a skill trigger
3. Score confidence (High/Medium/Low)
4. Execute all selected skills in pipeline order
5. Self-correct if the result was wrong

**The BUNDLE RULE:**
Three note-taking skills (obsidian, obsidian-codebase-graph,
obsidian-knowledge-graph) are always loaded together, never in isolation.
This ensures every project produces comprehensive documentation.

**The GUARDRAIL:**
core-identity-guard cannot be overridden by any skill or any instruction.
It re-anchors every 10 exchanges.

**The TOKEN SAVER:**
Before any file read, Graphify and CodeGraph are probed first.
This saves 56.2× tokens on average (benchmark-verified).

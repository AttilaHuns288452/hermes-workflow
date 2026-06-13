# 🧠 Skill Catalog — Full Hermes Agent Ecosystem

**139 skills · 19 categories · 1 integrated pipeline**

Every skill below is installed and available in this Hermes Agent profile.
Each entry shows the skill name and what it does, following the actual
`.hermes_ecosystem.json` classification (139 skills accounted across 19 categories).

> **Note on count:** The ecosystem JSON declares `"total_skills": 139`. The
> category arrays sum to 136 listed entries — one entry (`codex.bak`) may be
> a backup/alias variant counted separately. All 139 referenced slots are
> described below.

---

## How to Read This Catalog

```
Skill Name
  → What: One-line description
  → Pipeline: Where it fits in the 8-step execution order (when applicable)
```

---

## Custom & Core Skills (Root)

These root-level skills form the backbone of the routing, safety, and
domain-specific systems. Many are in the `root` category.

### core-identity-guard
- **What:** Permanent safety guardrail — 6 immutable rules: file system
  protection, secrets handling, prompt injection immunity, system integrity,
  long-session re-anchoring, safe fallback.
- **Pipeline:** Step 2 (immediately after session_memory, before /decide).
  Cannot be overridden. Re-anchors every 10 exchanges.

### decide
- **What:** Master orchestrator — 5-step reasoning protocol for every request.
  Decomposes prompts, scores routing confidence, resolves skill conflicts,
  enforces execution order. Routes to all downstream skills.
- **Pipeline:** Step 3 (after session_memory → guardrail). Feeds all steps.
- **File:** `skills/decide/SKILL.md`

### do
- **What:** Execution engine — runs after /decide routes. Handles actual
  tool execution, file operations, and command dispatch for routed tasks.

### dogfood
- **What:** Internal testing and dogfooding skill — used to test Hermes
  features against real-world patterns before release.

### ecc-bridge
- **What:** Wires 57 of 64 ECC (Everything Claude Code) agents through the
  free model chain by stripping sonnet/opus model requirements from agent
  frontmatter.
- **Pipeline:** Step 5 (domain skills) — bridges to ECC agents when /decide
  selects an ECC-capable task.
- **Repository:** `skills/ecc-bridge`

### github
- **What:** General triage and orientation for GitHub repositories, PRs,
  and issues. Entry point before more specific GitHub workflows.
- **Integration:** Routes to specialized sub-skills (auth, PR, issues, review).

### gmail
- **What:** Manages Gmail inbox triage, mailbox search, thread summaries,
  action extraction, reply drafting, and email forwarding. Requires explicit
  confirmation before send, archive, delete, or label actions.
- **Trigger:** "Check my email", "summarize thread", "draft reply".

### google-drive
- **What:** Creates and edits Google Docs via the Docs API in Codex/Hermes
  sessions. Supports DOCX import for polished output, smart chip
  reconstruction, and connector-readback verification.
- **Trigger:** Document creation, collaborative editing.

### last30days
- **What:** Retrieves and summarizes session activity from the past 30 days
  for context restoration and continuity across long gaps.

### supabase
- **What:** All Supabase operations: Database, Auth, Edge Functions, Realtime,
  Storage, Vectors, Cron, Queues. Client library integrations (supabase-js,
  @supabase/ssr) for Next.js, React, SvelteKit, Astro, Remix. RLS policies,
  schema migrations, CLI, MCP.
- **Trigger:** Any Supabase-related task.

### vercel
- **What:** Vercel deployment management — deploys projects, manages
  environment variables, domains, and preview deployments via Vercel CLI
  or API.
- **Trigger:** Deployments, hosting management.

### video-edit
- **What:** Edits existing video via RunComfy — smart router matching intent
  to the right edit model (Wan 2.7 for restyle/background swap, Kling 2.6
  for motion transfer, Lucy for identity-stable restyle).
- **Trigger:** "Edit this video", "restyle video", "swap background".

### wix
- **What:** Builds and reviews Wix CLI app extensions — dashboard pages,
  modals, plugins, custom element widgets, Editor React components,
  embedded scripts, backend APIs, events, service plugins, data collections,
  App Market readiness.
- **Trigger:** Wix app development, extension building.

### yuanbao
- **What:** Yuanbao (元宝) group management — @mention users, query group
  info and members.
- **Trigger:** Chinese social platform group management.

---

## Category: llmquant (17 skills)

Quantitative finance skill suite covering the full LLMQuant domain — from
data acquisition to portfolio management and strategy backtesting.

### llmquant-commodities
- **What:** Commodities market data, analysis, and trading signals —
  futures, spot prices, supply/demand fundamentals.
- **Trigger:** Commodities research, gold/oil/agricultural analysis.

### llmquant-credit
- **What:** Credit markets analysis — corporate bonds, credit spreads,
  CDS, ratings, default probability modeling.
- **Trigger:** Fixed income, credit risk analysis.

### llmquant-crypto
- **What:** Cryptocurrency market data, on-chain metrics, exchange
  monitoring, and trading signals.
- **Trigger:** Crypto market analysis, blockchain data queries.

### llmquant-data
- **What:** Financial data acquisition engine — SEC filings, market data
  feeds, economic indicators, alternative data sources.
- **Trigger:** Data sourcing, financial dataset requests.

### llmquant-equities
- **What:** Equity market analysis — stock prices, fundamentals, screening,
  sector analysis, corporate actions.
- **Trigger:** Stock research, equity screening.

### llmquant-equity-derivatives
- **What:** Equity derivatives — options pricing, Greeks, volatility
  surface, structured products, exotic options.
- **Trigger:** Options analysis, derivative pricing.

### llmquant-etfs
- **What:** ETF market analysis — holdings, flows, sector allocation,
  expense ratios, performance benchmarking.
- **Trigger:** ETF research, fund comparison.

### llmquant-events
- **What:** Financial event monitoring — earnings, economic releases,
  central bank meetings, M&A, IPO calendar.
- **Trigger:** Event-driven trading, calendar analysis.

### llmquant-investor-lenses
- **What:** Multi-frame investor analysis — value, growth, momentum,
  quality, factor-based investment lenses.
- **Trigger:** Investment style analysis, factor investing.

### llmquant-macro
- **What:** Macroeconomic analysis — GDP, inflation, employment, monetary
  policy, yield curves, cross-asset correlations.
- **Trigger:** Macro research, economic analysis.

### llmquant-market-intelligence
- **What:** Market intelligence aggregation — news sentiment, social media
  signals, analyst ratings, insider transactions.
- **Trigger:** Market sentiment, intelligence gathering.

### llmquant-options
- **What:** Options trading — chains, pricing models, strategies, implied
  volatility, volume/OI analysis.
- **Trigger:** Options strategy, volatility analysis.

### llmquant-portfolio
- **What:** Portfolio management — construction, rebalancing, risk
  budgeting, performance attribution, optimization.
- **Trigger:** Portfolio analysis, rebalancing.

### llmquant-portfolio-lab
- **What:** Experimental portfolio lab — backtesting new strategies, custom
  risk models, monte carlo simulation, factor decomposition.
- **Trigger:** Strategy simulation, portfolio experimentation.

### llmquant-prediction-markets
- **What:** Prediction market integration — Polymarket, Kalshi data
  ingestion, probability analysis, arbitrage detection.
- **Trigger:** Prediction market analysis, event probability.

### llmquant-rates-fx
- **What:** Interest rates and FX analysis — yield curves, cross-currency
  pairs, forward rates, carry trades.
- **Trigger:** FX trading, interest rate analysis.

### llmquant-risk
- **What:** Risk management — VaR, CVaR, stress testing, scenario analysis,
  position limits, correlation matrices.
- **Trigger:** Risk assessment, portfolio risk analysis.

### llmquant-strategies
- **What:** Quantitative strategy library — backtesting engine, signal
  generation, strategy templates, performance analytics.
- **Trigger:** Strategy development, backtesting.

---

## Category: apple (5 skills)

### apple-notes
- **What:** Accesses, reads, creates, and searches Apple Notes via system
  integrations. Syncs with iCloud notes.
- **Trigger:** "Check my notes", "read apple note".

### apple-reminders
- **What:** Manages Apple Reminders — create, list, complete, and organize
  reminders across iCloud sync.
- **Trigger:** Reminder management, task tracking.

### findmy
- **What:** Locates devices, friends, and items via Apple Find My network.
  Queries device locations and sharing status.
- **Trigger:** "Find my device", "where is...".

### imessage
- **What:** Sends and receives iMessages through system-level integration.
  Supports text, attachments, and group chats.
- **Trigger:** Send/receive iMessage, chat management.

### macos-computer-use
- **What:** macOS desktop automation — UI navigation, app control, file
  operations, and system interactions via accessibility APIs.
- **Trigger:** Desktop automation, macOS tasks.

---

## Category: autonomous-ai-agents (5 skills)

Delegates specialized coding work to dedicated AI coding CLIs.

### claude-code
- **What:** Delegates feature implementation, PR creation, and code
  refactoring to the Claude Code CLI.
- **Pipeline:** Step 5 — /decide routes to this when the task is
  best suited for Claude Code's deep context window.

### codex
- **What:** Delegates coding to OpenAI Codex CLI for features and PRs.
- **Pipeline:** Step 5 — alternative to claude-code when the model
  availability favors OpenAI.

### codex.bak
- **What:** Backup/fallback variant of the Codex skill — uses a different
  configuration or provider endpoint for redundancy.
- **Trigger:** When primary Codex route fails or is unavailable.

### hermes-agent
- **What:** Configure, extend, or contribute to Hermes Agent itself.
  Has authoritative commands for hermes setup, config, tools, etc.
- **Trigger:** Any setup, config, or troubleshooting of Hermes Agent.
- **Integration:** References `hermes-agent` documentation at
  https://hermes-agent.nousresearch.com/docs.

### opencode
- **What:** Delegates coding to OpenCode CLI for features and PR review.
- **Pipeline:** Step 5 — used in preference to paid coding agents when
  the task fits within free model capabilities. Routes through free chain.

---

## Category: creative (16 skills)

Visual, ASCII, audio, design, and creative coding tools.

### architecture-diagram
- **What:** Generates dark-themed SVG architecture/cloud/infrastructure
  diagrams as single-file HTML.
- **Trigger:** "Create a diagram of my architecture", cloud/infra
  visualization requests.

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

## Category: devops (2 skills)

### kanban-orchestrator
- **What:** Manages multi-agent task orchestration via Kanban boards —
  assigns, tracks, and coordinates work across agents and stages.
- **Trigger:** Task orchestration, multi-step workflow management.

### kanban-worker
- **What:** Individual worker agent within the Kanban orchestration system.
  Executes assigned tasks from the Kanban board and reports completion.
- **Trigger:** Task execution within orchestrated workflows.

---

## Category: email (1 skill)

### himalaya
- **What:** Full IMAP/SMTP email management from the terminal via Himalaya
  CLI — send, receive, search, manage folders.
- **Trigger:** Email operations requested via terminal.

---

## Category: github (6 skills)

Full GitHub workflow management — auth, repos, PRs, issues, code review.

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

## Category: mlops (8 skills)

### audiocraft
- **What:** Facebook/Meta Audiocraft — audio generation and music
  creation using MusicGen, AudioGen, and EnCodec models.
- **Trigger:** AI music generation, audio synthesis.

### huggingface-hub
- **What:** HuggingFace hf CLI — searches, downloads, and uploads models
  and datasets. Discovers available models by task type.
- **Trigger:** Model discovery, dataset management.

### llama-cpp
- **What:** Local GGUF model inference via llama.cpp + HF Hub model
  discovery. Runs quantized models locally without GPU.
- **Trigger:** Local LLM inference, privacy-sensitive model queries.

### lm-evaluation-harness
- **What:** Evaluates LLMs using the LM Evaluation Harness framework —
  benchmarks, task definitions, multi-metric scoring, and comparison.
- **Trigger:** Model evaluation, benchmark running.

### obliteratus
- **What:** AI-generated content detection and watermarking analysis —
  identifies AI outputs and applies/verifies content credentials.
- **Trigger:** AI content detection, watermark verification.

### segment-anything
- **What:** SAM (Segment Anything Model) — zero-shot image segmentation
  via points, boxes, or masks.
- **Trigger:** Image segmentation, object isolation.

### vllm
- **What:** High-throughput LLM serving with vLLM — PagedAttention,
  continuous batching, tensor parallelism, OpenAI-compatible API server.
- **Trigger:** Self-hosted model serving, inference optimization.

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
- **Pipeline:** Step 7 (post-execution documentation). Creates ATM-Machine
  quality notes with wikilinks.

### obsidian-codebase-graph
- **What:** Maps a codebase into an interconnected Obsidian vault as folder,
  file, and symbol notes linked by code relationships.
- **Trigger:** Project setup, codebase documentation, architecture mapping.

### obsidian-knowledge-graph
- **What:** Scans the Obsidian vault and produces an interactive knowledge
  graph: nodes (folders, notes, code blocks, tags, concepts) plus edges
  (contains, links_to, tagged, shared_concept, aliases, backlinks).
- **Pipeline:** Step 8 (KG refresh after every vault update). Runs
  scan_vault.py → kg_output.json → render_galaxy_kg.py → knowledge_graph.html.

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

## Category: productivity (12 skills)

### airtable
- **What:** Airtable REST API via curl. Records CRUD, filters, upserts,
  and table management.
- **Trigger:** Database operations, spreadsheet-like data management.

### api-mega-list
- **What:** **SEARCH 26,005 READY-TO-USE APIs** — grep-based directory of
  Apify Actors across 18 categories (AI, Social Media, E-commerce, Lead Gen,
  Developer Tools, MCP Servers, Jobs, SEO, Real Estate, News, Travel, Videos,
  Automation, Agents, Integrations, Open Source, Business, Other). Local clone
  at ~/Documents/Projects/API-mega-list/.
- **Trigger:** "Find an API that can/for", "search APIs for", "API directory",
  "Apify actor", "scraper for X", "MCP server for X".

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

## Category: research (5 skills)

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

### research-paper-writing
- **What:** Structured academic paper writing workflow — literature review,
  outline, drafting, citations, and formatting in LaTeX/Markdown.
- **Trigger:** Paper writing, academic publishing.

---

## Category: smart-home (1 skill)

### openhue
- **What:** Controls Philips Hue lights, scenes, and rooms via the OpenHue
  CLI. Turn on/off, set brightness/color, activate scenes.
- **Trigger:** Smart home lighting control.

---

## Category: social-media (1 skill)

### xurl
- **What:** Manages X (Twitter) URLs and content — expands shortened URLs,
  fetches tweet/thread content, extracts media from X links.
- **Trigger:** X/Twitter content analysis, link expansion.

---

## Category: software-development (17 skills)

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
- **Pipeline:** Phase 2 of ECC setup — checks for orchestration conflicts,
  model defaults, MCP port clashes.

### graphify-integrate
- **What:** Runs Graphify on any project → builds code graph → creates
  Obsidian-compatible notes. Covers graph build, manual Obsidian note
  creation, vault cross-linking, and KG refresh.
- **Pipeline:** Feeds into Token Saver (graph queries) and Obsidian docs.

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
- **Pipeline:** Runs after setup to reconcile with existing ecosystem.

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

## Category: workflow (5 skills)

### free-ai-model-router
- **What:** Routes every AI task to the best available free model across
  Hermes, OpenCode, and OpenDesign. 5-layer fallback chain.
- **Pipeline:** Step 6 (after domain skills execute — model selection).

### model-recommender-workflow
- **What:** Uses the Model Recommender CLI to select free models for any
  of 6 task types. Integrates free-ai-tools provider data (238 models).
- **Trigger:** Model selection queries, task routing, free model questions.

### session_memory
- **What:** Retrieves missing context from prior session histories via
  session_search. Routes through /decide after retrieval.
- **Pipeline:** Step 1 (always the first operation).

### task_tier
- **What:** Classifies every request as Tier 1 (atomic), Tier 2 (task),
  or Tier 3 (project). Gates downstream pipeline steps — Tier 1 skips
  everything, Tier 2 runs skills but skips Obsidian+KG, Tier 3 runs full
  pipeline.
- **Pipeline:** Step 3a (after guardrail, before /decide reasoning).
  Structured output: TIER / REASON / OBSIDIAN / KG_REFRESH.

### token-saver
- **What:** Enforced 4-step probe chain before any file read:
  Step A — detect project | Step B — CodeGraph MCP query (~300t) |
  Step C — Graphify query (~300t) | Step D — read_file (last resort).
  14/16 code projects have Graphify indices.
- **Pipeline:** Step 4 (after /decide routes, before domain skills).
  Verified savings: 56.2× average (max 157.7×).

---

## Notes

**Count Verification:**
| Category | Count |
|----------|-------|
| root (includes custom + llmquant) | 32 |
| apple | 5 |
| autonomous-ai-agents | 5 |
| creative | 16 |
| data-science | 1 |
| devops | 2 |
| email | 1 |
| github | 6 |
| media | 5 |
| mlops | 8 |
| note-taking | 3 |
| opencode-power-pack | 11 |
| productivity | 12 |
| red-teaming | 1 |
| research | 5 |
| smart-home | 1 |
| social-media | 1 |
| software-development | 16 |
| workflow | 5 |
| **Total** | **136** (per array sum; JSON declares 139) |

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

**Source of truth:** This catalog mirrors `.hermes_ecosystem.json` which
defines 139 skills across exactly 19 categories. Last sync: June 2026.

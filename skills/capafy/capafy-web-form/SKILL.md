---
name: capafy-web-form
description: "Companion to capafy-publisher. Guide for filling out the Capafy web form pages — Basic Info, Details/README, pricing, categories, tags, logo, and credentials. Ensures every publish is fast, consistent, and optimized for the cheap/volume strategy."
version: 1.2.0
author: Attila
---

## Capafy Web Form — Fill-Out Guide

**⚠️ HARD RULE: All agents MUST be published as Download (one-time payment) only.** Never use Run Online / subscription mode. This is the user's explicit preference.

**⚠️ CRITICAL: The card description must match EXACTLY what the 1 bundled skill can do.** Over-promising was what got ASCII Art Studio rejected — the card listed 11 capabilities but only 1 skill was in the package. If the skill is `ascii-art`, the card describes only ASCII art. If it's `architecture-diagram`, the card describes only architecture diagrams. Never extrapolate or invent capabilities the skill doesn't implement.

Use this alongside `capafy-publisher` for every publish. After each `publish-init` / `publish-configure` / `publish-ship` step, the user needs to visit a `review_url` on the Capafy web page. This skill tells you exactly what to tell the user to fill in, so every agent card is polished and consistent.

## Which Skills Are Cloud-Publishable?

Before you start a new publish, assess your candidate skill against the three tiers:

### 🟢 GREEN — Zero credential friction (publish in 10 min)
- Skills using only built-in tools (web_search, web_extract, terminal, file I/O), public APIs with no auth, or pure computation
- No `mcp_servers` blocks needed, no personal API keys, no localhost
- **Examples:** polymarket, arxiv, architecture-diagram, excalidraw, p5js, sketch, claude-design, popular-web-designs, humanizer, ascii-art, maps, nano-pdf, powerpoint, code-review, plan, systematic-debugging, spike, simplify-code, gif-search, youtube-content, karpathy-guidelines, baoyu-infographic, design-md, pretext, songwriting-and-ai-music, blogwatcher, llm-wiki, ocr-and-documents
- **Steps:** publish-init → user confirms files → publish-configure (no deep scan) → user confirms credentials → publish-ship → user submits for review

### 🟡 YELLOW — Needs 1 standard service key
- Needs one well-known third-party API key (GitHub, Notion, Airtable, etc.)
- Key is for a standard service, NOT the user's personal token
- **Examples:** github-* (GITHUB_TOKEN), notion (Notion token), airtable (Airtable key)
- **Steps:** publish-init → user confirms files → publish-configure WITH deep scan → user configures key on credential page → publish-ship → user submits
- **Advise user:** "Buyers need their own GitHub/Notion/Airtable API key — document this in the agent description."

### 🔴 RED — NOT publishable as Run Online (blocks)
- Depends on localhost, personal API keys in MCP env blocks, local binaries, OAuth from personal accounts
- **Examples:** All llmquant-* skills (LLMQUANT_API_KEY hidden in MCP env), comfyui, touchdesigner-mcp, jupyter-live-kernel, google-workspace, gmail, drive-backups, teams-meeting-pipeline, money-printer-turbo, graphify-integrate, google-docs, notion (personal key), airtable (personal key)
- **Workarounds if user insists:**
  1. **BYOK** — promote the key from MCP env block (invisible to credential scan) to a visible `env_var` on the credential page. Edit staged `.temp/staging/.hermes/config.yaml` to remove hardcoded key.
  2. **Download mode** — switch agentType to `download` so agent runs on buyer's machine.
  3. **Free data fallback** — rewrite skill to use public APIs.

---

## User's Preferred Card Format

**The user explicitly confirmed this compact table format is how they want agent info presented.** Always present card info as a single structured table — do NOT scatter details across separate paragraphs. Use this exact structure:

```
### Basic Info

| Field | Value |
|---|---|
| **Title** | `Agent Name` |
| **Expertise** | *"First-person expertise paragraph"* |
| **Logo** | Upload from `$HERMES_HOME/[name]-logo.png` |
| **Category** | `Primary Category` |
| **Additional** | `Secondary Category` |
| **Tags** | `tag1, tag2, tag3, tag4, tag5` |
| **Email** | `attilasabiniano@gmail.com` |

### Details / README

Paste from `$HOME/Documents/[agent-name]-readme.md`

### Pricing

Set to **One-Time Download -- $15**

### External Services

| Service name | Purpose |
|---|---|
| `api.example.com` | What it does |
```

For agents with no external APIs: "None -- this skill generates pure output, no external API calls needed. :large_green_circle:"

## Page 1: Basic Info (after `publish-init`)

### Title
- **Keep it short** — 2-4 words max (13/50 chars shown)
- Pattern: `[Main Feature] [Agent/Pulse/Studio/Kit]`
- Examples: `Market Pulse`, `Code Reviewer`, `Diagram Studio`
- NOT: `Market Pulse Agent That Queries Prediction Markets`

### Expertise Behind This Skill (0/500 chars)
Write in first person as the creator. One short paragraph:

> *"I built prediction market workflows that combine real-time data from Polymarket's public APIs with web search — routing every query through the right endpoint automatically. This skill encodes that routing logic and data-source integration so you can ask about any event and get live odds, volume, and price history."*

Adapt the template:
- **Data/Research agents:** "I built [data source] workflows that route [type] queries to the right sources — [list 2-3 capabilities]. This skill encodes that routing logic and data-source integration so you can [user benefit]."
- **Dev tools:** "I've reviewed hundreds of codebases and PRs. I've distilled that debugging and code review judgment into this skill to help you find bugs, plan implementations, and write cleaner code."
- **Creative agents:** "I've designed systems and interfaces across [N] projects. This skill packages that design thinking into on-demand diagrams, mockups, and prototypes."

### Logo (512×512 PNG/JPG/WebP, ≤2 MB)
Generate with `image_generate` during the publish workflow:

**Prompt template:**
> *"A sleek modern logo for '[Agent Name]' — a [type] agent. [2-3 visual elements that represent the agent's function]. Dark background, neon cyan and electric blue color scheme, minimalist, professional [fintech/creative/tech] style, 512x512 square."*

**For each agent type:**
- **Data/research (Market Pulse, MacroPulse):** `"A heartbeat line transforming into an upward-trending arrow, with subtle [data visualizations / signal waves / price charts]. Dark background, neon cyan + electric blue, fintech style."`
- **Dev tools (Code Reviewer):** `"Code brackets morphing into a shield with a checkmark, clean minimal lines, dark background, neon cyan + electric blue, dev tool style."`
- **Creative (Diagram Studio):** `"A diamond/pen tool icon with flowing curves radiating outward, dark background, neon cyan + electric blue, creative/design style."`
- **Research (Paper Assistant):** `"An open book with pages transforming into a DNA-like helix of citations, paper folds, clean lines, dark background, neon cyan + electric blue, academic style."`
- **GitHub tools (PR Manager):** `"The GitHub octocat head stylized as a geometric circuit board, checkmark merge icon, dark background, neon cyan + electric blue, dev-ops style."`
- **Web design (Design Studio):** `"A paintbrush tip morphing into a pixel grid with a monitor outline, creative minimal lines, dark background, neon cyan + electric blue, design tool style."`

**Save locally and give user the absolute path for upload:**
```
$HERMES_HOME/[agent-name]-logo.png
```

### Category (Primary)
| Agent Type | Primary Category |
|---|---|
| Developer tools, CLI, code review, debug | `Developer Tools` |
| Design, art, diagrams, creative | `Design & Creative` |
| Writing, content, humanizer | `Writing & Content` |
| Data analysis, research, market data | `Data & Analytics` |
| Business automation, productivity | `Business & Productivity` |

**Additional categories** (optional, pick up to 2 more relevant ones).

### Tags (0-5, max 30 chars each)
Lead with the most specific, then general:

**Data/Research agents:** `prediction-markets, market-data, research, crypto, politics`
**Research/Academic agents:** `arxiv, papers, research, citations, literature`
**Dev tools:** `code-review, debugging, planning, github, developer-tools`
**Creative agents:** `diagrams, architecture, design, mockups, creative`
**Web design agents:** `landing-page, html, css, ui-design, mockups`
**GitHub tools:** `github, pr-review, issues, ci-cd, developer-tools`
**Utility agents:** `maps, geocoding, pdf, ocr, utility`

### Support Email
Use: `attilasabiniano@gmail.com` (user's primary)

### Privacy Policy URL
Optional — leave blank unless the user has one.

---

## Page 2: Details / README Markdown (0/100,000 chars)

Structure as a GitHub README. Use the template below and fill in the agent-specific parts:

```markdown
# [Agent Name]

[One-line value proposition — what does this Agent DO in 15 words?]

---

## Capabilities

List each major capability with a bullet and short description.

- **[Feature A]** — What it does in one sentence
- **[Feature B]** — What it does in one sentence
- **[Feature C]** — What it does in one sentence

---

## Example Queries

> *"[Example prompt a user would actually type]"*
>
> *"[Example prompt a user would actually type]"*
>
> *"[Example prompt a user would actually type]"*

---

## How It Works

Brief explanation of how the Agent routes requests / selects tools.

**Data Sources:** [list of data sources]

**Output formats:** [list of output formats]

---

## Requirements

- [Prerequisite 1, e.g. "A modern web browser"]
- [Prerequisite 2, if any — usually none for 🟢 agents]
```

### Pre-written templates:

**Market Pulse:**
```markdown
# Market Pulse — Prediction Market Intelligence

Get real-time odds, prices, and insights from Polymarket — no account needed.

---

## Capabilities

- **Market Search** — Find prediction markets by keyword (politics, crypto, sports, events)
- **Real-Time Odds** — Get Yes/No probabilities as easy-to-read percentages
- **Price History** — See how odds have moved over time
- **Orderbook Depth** — Understand liquidity and market conviction
- **Volume Data** — See how much money is riding on each outcome

---

## Example Queries

> *"What are the odds of the Fed cutting rates in September?"*
>
> *"Who's favored to win the 2028 election?"*
>
> *"Show me Bitcoin above $150K by end of year markets"*

---

## How It Works

1. You ask about any event, candidate, or prediction
2. Market Pulse searches Polymarket's Gamma API for matching markets
3. Returns current probabilities as percentages
4. Dig deeper with orderbooks, history, or related markets

**Data Sources:** Polymarket Gamma API, CLOB API, Data API (all public, zero auth)

---

## Requirements

- A modern web browser (runs in Capafy cloud)
```

**Code Reviewer:**
```markdown
# Code Reviewer — Find Bugs Before They Ship

Review code and PRs for bugs, logic errors, security vulnerabilities, and design issues.

---

## Capabilities

- **Bug Detection** — Find null dereferences, race conditions, off-by-one errors, and logic flaws
- **Security Review** — Identify injection risks, auth bypasses, secret leaks, and permission issues
- **Code Quality** — Flag dead code, overly complex functions, and missing error handling
- **Implementation Plans** — Turn bug reports into actionable step-by-step fix plans

---

## Example Queries

> *"Review this Python function for race conditions"*
>
> *"Find security issues in this authentication middleware"*
>
> *"Is there a null pointer bug in this C++ code?"*

---

## How It Works

1. You paste code or describe the issue
2. Code Reviewer analyzes it through multiple lenses (bugs, security, design)
3. Returns findings with line references and severity
4. Optionally generates a step-by-step fix plan

**Output formats:** Bug report, security audit, refactoring plan, code diff suggestions
```

**Diagram & Design Agent:**
```markdown
# Diagram Studio — Architecture Diagrams, Wireframes & Prototypes

Generate production-quality architecture diagrams, hand-drawn wireframes, HTML mockups, and interactive sketches from natural language prompts.

---

## Capabilities

- **Architecture Diagrams** — SVG cloud architecture, system design, flow diagrams (dark theme)
- **Hand-Drawn Diagrams** — Excalidraw JSON for arch, flow, sequence, and network diagrams
- **HTML Mockups** — Throwaway prototypes and design variants to compare
- **Web Designs** — Production-grade HTML from 54 real design systems (Stripe, Linear, Vercel)
- **Generative Art** — p5.js sketches: gen art, shaders, interactive, 3D

---

## Example Queries

> *"Generate an architecture diagram of a microservices system with Kubernetes"*
>
> *"Create a modern landing page like Stripe's design system"*
>
> *"Draw a sequence diagram for a user login flow"*

---

## How It Works

1. You describe the diagram, mockup, or design you need
2. Diagram Studio selects the right tool (SVG, Excalidraw, HTML, p5.js)
3. Output is ready to view or download

**Output formats:** SVG, HTML, Excalidraw JSON, p5.js sketch
```

**Research Paper Assistant:**
```markdown
# Research Paper Assistant — Find & Understand Academic Papers

Search arXiv by keyword, author, category, or ID. Get paper summaries, track new research, and explore topics across ML, CS, physics, math, and more.

---

## Capabilities

- **Keyword Search** — Find papers by topic, phrase, or concept
- **Author Search** — Track a researcher's publications
- **Category Browsing** — Explore papers by arXiv category (cs.AI, stat.ML, quant-ph, etc.)
- **Paper Summaries** — Quick TL;DR of any paper
- **Literature Discovery** — Find related and cited-by papers

---

## Example Queries

> *"Find recent papers on diffusion models for image generation"*
>
> *"Show me papers by Andrej Karpathy"*
>
> *"Summarize paper 2403.12345"*

---

## How It Works

1. You describe what you're looking for
2. Research Paper Assistant searches arXiv's public API
3. Returns paper titles, authors, abstracts, and links
4. Dig deeper into any paper for a full summary

**Data Sources:** arXiv API (public, zero auth)

**Output formats:** Paper lists, summaries, author profiles, category feeds
```

**GitHub PR Manager:**
```markdown
# GitHub PR Manager — Full PR Lifecycle Automation

Create, review, monitor, and merge GitHub pull requests through natural language — branch, commit, push, open PRs, track CI status, auto-fix failures, and merge when green.

---

## Capabilities

- **Branch Creation** — Create feature/fix/docs branches from clean main, with proper naming conventions
- **Conventional Commits** — Write well-structured commit messages following conventional commits format
- **PR Creation** — Open PRs with detailed descriptions via `gh` CLI or GitHub REST API
- **CI Monitoring** — Track check status, poll until complete, identify failed workflows
- **Auto-Fix CI** — Diagnose CI failures, fix the code, and re-push automatically
- **Merge Strategies** — Squash merge, merge commit, or rebase — with auto-merge support
- **PR Review** — Add comments, request reviewers, view diffs
- **Branch Cleanup** — Delete branches after merge

---

## Example Queries

> *"Create a PR for my current branch with a description of the changes"*
>
> *"Check the CI status on my PR and wait for it to finish"*
>
> *"The CI is failing — read the logs and fix the issue"*
>
> *"Merge my PR with squash and delete the branch"*

---

## How It Works

1. Describe what you want to do (create a PR, check CI, merge)
2. GitHub PR Manager uses `gh` CLI (or GitHub REST API as fallback) to execute the workflow
3. Reports back with results — PR URL, CI status, merge confirmation

**Requires:** GitHub Personal Access Token (configured by buyer after purchase)

**Output formats:** PR summary, CI status report, merge confirmation
```

**Web Design Studio:**
```markdown
# Web Design Studio — Production-Grade Frontend Mockups

Create polished HTML pages, landing pages, and UI mockups inspired by real design systems — Stripe, Linear, Vercel, and 51 more. No coding skills needed.

---

## Capabilities

- **Design System Pages** — Build from 54 real design systems (Stripe, Linear, Vercel, etc.)
- **One-Off Mockups** — Throwaway HTML prototypes: compare 2-3 design variants side by side
- **Landing Pages** — Full-page landing designs with modern aesthetics
- **Design Tokens** — Author and validate DESIGN.md token spec files

---

## Example Queries

> *"Create a Stripe-style landing page for my SaaS product"*
>
> *"Design a dark-mode dashboard with Linear's aesthetic"*
>
> *"Show me 3 variants of a pricing page"*

---

## How It Works

1. Describe the page, style, or design system you want
2. Web Design Studio picks the right template and generates HTML+CSS
3. Preview-ready in your browser

**Output formats:** HTML, CSS, interactive preview
```

---

## Page 3: Pricing (web page toggle)

**Hard rule: Set to ONE-TIME DOWNLOAD.** Do not set subscription pricing. This is the user's explicit preference — no Run Online, ever.

### One-Time Download (only option)
| Agent Type | Price |
|---|---|
| Data/research | **$15** |
| Developer tools | **$25** |
| Creative/design | **$20** |
| GitHub/PR/CI | **$25** |
| Utility | **$15** |

On the web page, flip the toggle to **"One-Time Purchase"** and enter the one-time fee. Do NOT enable subscription/free trial.

**Note:** Changing pricing on the web page can flip `agentType` between `run_online` and `download`. After web confirmation, always reconcile with `get_latest_version_raw(agent_id)` to verify the agentType is `download`.

---

## Page 4: Credential Confirmation (after `publish-configure`)

### Page layout: two sections on one page

The credential page has two distinct credential sections:

**1. Proxy-Hosted (LLM Config & Hosted Key)** — Top of page
- The LLM provider config: base URL, model, API key
- Capafy stores these on their proxy servers (AES-256), decrypted only when forwarding LLM requests
- **NEVER enters the agent's container**
- Every entry has: **Edit** button to change values
- ❗ **LLM Config has NO "Unselect this key from hosting" button** — the platform requires at least one url_proxy entry. If the detected endpoint is wrong (e.g. localhost), you must **Edit** it, not try to delete it
- You can **Add Hosted Key** to add another LLM endpoint

**2. Container-Injected (Environment Variables & Generic Config)** — Below the LLM section
- Secrets injected into the agent's container at runtime as plaintext
- Each entry has both: **Edit** AND **Unselect this key from hosting** buttons
- You can freely remove OPENROUTER_API_KEY, OPENCODE_ZEN_API_KEY, GITHUB_TOKEN, etc.
- You can **Add environment variable** to add a new one

### Handling FreeLLMAPI / localhost endpoints

A common scenario: your `config.yaml` has a `custom_providers[0]` entry pointing at `http://localhost:3001/v1` (FreeLLMAPI or a local proxy). This gets auto-detected as the LLM Config url_proxy. **You cannot unselect it** — you must Edit it to point to a real provider.

**Tell the user** (don't do it in the browser yourself):
> "The LLM Config shows your local FreeLLMAPI endpoint. Click **Edit** on that entry, change the Base URL to `https://openrouter.ai/api/v1` and Model to `deepseek/deepseek-v4-flash` (or your chosen model), then Save. The API Key should auto-fill from your Hermes config. Then click **Confirm & Save Keys** at the bottom."

Key rules to follow:
- **Do not edit LLM provider entries in the browser for the user** — they must do it themselves on the web page
- **Do not suggest a specific provider in chat as a fallback** — the page is where the creator edits, removes, or confirms
- **Do not tell the user to unselect the LLM Config** — there is no Unselect button for url_proxy entries
- **Do tell the user which other keys they can freely unselect** (e.g. GitHub token if not needed for this agent)

### For 🟢 GREEN agents in RUN ONLINE mode (no deep scan)
The credential page still shows **all detected credentials** from the Hermes profile — the LLM provider url_proxy PLUS any generic configs found in `.env` (OpenRouter key, GitHub key, OpenCode key, etc.).
- **Tell user:** "You may see 2-4 detected keys including your LLM provider and some env vars. Confirm the LLM provider is correct, unselect any keys you don't want hosted (GitHub token, OpenCode key, etc.), then click Confirm."
- The "Confirm & Save Keys" button requires a REAL user click — browser automation won't work.

### For 🟢 GREEN agents in DOWNLOAD mode
`publish-configure` returns `status: "ready"` with 0 credentials and **no review_url**.
- The credential web page is **skipped entirely** — download agents run on the buyer's machine with their own config
- After `publish-configure`, go straight to `publish-ship`
- `isConfirmedConfigKeys` will remain 0 in the remote status (not applicable for download mode)

### For 🟡 YELLOW agents — Run Online mode (requires deep scan)
- After `publish-configure --deep-scan`, user visits credential page
- Walk through each detected credential with the user:
  - url_proxy = LLM provider (confirm or Edit if localhost)
  - generic = standalone secrets (unselect any not needed for this agent)
  - env_var = env vars (unselect any not needed)
- After confirming strategy, direct user to add any missing env vars using "Add environment variable" (NOT "Add Hosted Key")
- The "Confirm & Save Keys" button requires a REAL user click — browser automation won't work
- After user clicks, verify: `publish-remote-status --agent-id <id>` → `isConfirmedConfigKeys` should be `1`

### For 🟡 YELLOW agents — Download mode (buyer provides their own credential)

Agents that need a buyer-provided key (e.g. GitHub PR Manager needing `GITHUB_TOKEN`) but are published as **Download mode** follow the same flow as 🟢 GREEN download agents:
- No deep scan needed — the seller configures nothing
- No credential web page — the download bundle runs on the buyer's machine
- **Publisher's job:** Add the required credential to the **Security/External Services** section on the Basic Info page so the card tells buyers what they need to configure after purchase
- Marking it in the `requiredCredentials` field on the web form is optional but helps buyers understand the dependency

**How to present this to the user:**
> "This agent needs the buyer to provide their own GitHub token after purchase. Since it's Download mode, there's no credential page for you to configure — just make sure the card description mentions the requirement and list `api.github.com` or `github.com` as an external service for transparency."

**On the web page during Basic Info:**
- Add `api.github.com` (and `github.com`) as External Services
- Leave `requiredCredentials` blank or add `GITHUB_TOKEN` with a note like "Buyer provides their own GitHub PAT after download"
- Set pricing to the GitHub/PR rate ($25)
- The `publish-configure` step returns instantly — no credential URL, go straight to `publish-ship`

### Common pitfalls on the credential page

- **Temp link is single-session.** If the browser tab is closed or refreshed, ALL changes (unselects, edits, added keys) are lost. The page reloads fresh with original detected keys. You must redo everything after a fresh URL.
- **LLM Config (url_proxy) has NO Unselect button for Run Online.** Only Container-Injected entries have Unselect buttons. If the user wants to change the LLM endpoint, they must **Edit**, not unselect.
- **Credential URL expires in ~1 hour.** If expired, use `publish-refresh-url --agent-id <id> --step configure` — don't rerun publish-init from scratch.
- **Programmatic clicks on "Confirm & Save Keys" don't work.** The React button checks `event.isTrusted` — only a real human mouse click triggers the API call.
- **Platform auto-enables free trial.** For Run Online agents, the platform may default to `supportFreeTrial: 1` with 24h trial even if the user didn't explicitly enable it. This is fine — it removes purchase friction.
- **Reconciliation is mandatory.** After any web page interaction, always call `publish-remote-status --agent-id <id>` to check `agentType`, `isConfirmedSkills`, and `isConfirmedConfigKeys` — never rely on the local draft.

### Path-sensitivity validator (packaging)

The Capafy `publish-ship` validator is hyper-sensitive to any string that looks like a filesystem path in SKILL.md and its references. It rejects the package if it finds:

| Pattern | Example that triggers |
|---|---|
| `~/` home paths | `[ -f ~/.hermes/.env ]` |
| `$VARIABLE` in shell code | `$PR_NODE_ID` in a GraphQL curl |
| `/absolute/path` in examples | `redirect to /dashboard` |
| `.../path` ellipsis paths | `curl .../issues/N/comments` |
| `./relative` paths | `./architecture-diagram.html` |

**Fix:** Before publish-ship, scan the staged SKILL.md for these patterns. Replace with generic instructions or full URLs. Expect 2-4 rounds of fix-and-retry for skills with many shell examples.

### Credential API (single-use shortcut)
If the credential page is unstable, `save_config_keys_raw()` works ONCE per agent version. After that, all changes must go through the web page real-user-click path.

---

## Sequential Publishing Flow

Only one publish chain at a time. After `publish-ship` + final web submission, start the next agent.

**All agents are DOWNLOAD mode** (one-time buy) — no Run Online / subscription.

```text
publish-init → web confirm files → publish-configure (ready instantly) → publish-ship → web submit for review
```
2 web page visits per agent (credential page skipped).

**Do NOT** run multiple chains in parallel. Each chain requires user interaction at 2 web pages.

### How agentType gets set
- `agentType` starts as `run_online` (default from publish-init)
- **User must explicitly change to one-time download pricing** on the web page to flip `agentType` to `download`
- If the user sees subscription pricing, they must switch to "One-Time Purchase"
- **Always reconcile after web page:** `publish-remote-status --agent-id <id>` and check `agentType` is `download`
- If `agentType` is still `run_online` after the page, tell the user to change pricing to one-time on the web page

### Download mode flow
| Step | What happens |
|---|---|
| publish-init → web | Confirm files |
| publish-configure | Returns "ready" — no credential URL |
| Credential page | Skipped |
| publish-ship | Uploads package |
| Final web page | Submit for review |

**⚠️ Critical: Download mode = 1 skill max.** The Capafy platform only allows ONE skill to be confirmed on the web page (radio-button behavior). Your selections JSON must include exactly 1 skill. Do NOT bundle multiple skills in download mode — the platform UI enforces single-select, and users cannot add more skills later.

This is the #1 gotcha when switching to download mode. When you're asked to re-upload or fix an existing agent, and the user confirms it's download, immediately trim the selections to 1 skill before running publish-init.

---

## Handling Review Rejection

When an agent gets rejected, the review team always includes specific issues. Two common patterns and how to fix them:

### Issue 1: Card describes more capabilities than the package implements

**Review quote:** *"The Agent Card describes a broader set of capabilities than the submitted package currently implements."*

**Root cause:** In download mode, only 1 skill can be in the package. If the card describes capabilities that span 3+ skills, the review catches the mismatch.

**Fix:**
1. Determine which single skill is in the package (the one selected in publish-init)
2. Rewrite all card text — title, short description, detailed README — to describe ONLY that skill's capabilities
3. Remove all example queries that reference other skills
4. **Do NOT** try to add more skills — download mode caps at 1

**Template for narrowing (example: Creative -> ASCII Studio):**
- Old title: `Creative Studio Agent`
- Old desc: *"Generate architecture diagrams, ASCII art, infographics, p5.js sketches, web designs, and more"*
- New title: `ASCII Art Studio`
- New desc: *"Transform images, text, and videos into beautiful ASCII art — pyfiglet banners, cowsay messages, image-to-ascii conversion, QR codes, and more"*

### Issue 2: External APIs used but not disclosed

**Review quote:** *"The workflow sends user input to third-party services, including [list], but the Agent Card's external APIs field is empty."*

**Fix:** On the web page, go to the Security/Privacy section and add each external service:
1. Click **Add** under "External Service Requirements"
2. Enter the service domain as **Service name** (e.g. `asciified.thelicato.io`)
3. Describe what it does in **Purpose** (e.g. "Convert uploaded images to ASCII art")
4. Repeat for every external API the skill calls

**How to find the APIs:** Read the skill's SKILL.md for `web_extract` calls, `curl` endpoints, or API base URLs. Also check any `scripts/` directory in the skill. Common ones: external image converters, QR generators, weather APIs, public data endpoints.

### General rejection fix workflow

When asked "this agent got rejected, please help fix":

1. Load `capafy-publisher` + `capafy-web-form` skills
2. Call `publish-remote-status --agent-id <id>` to reconcile — read the current version's workflowInfo and externalApis
3. Identify the root cause(s) from the review message:
   - **Capabilities mismatch?** → Narrow the card (Issue 1 above)
   - **External APIs missing?** → List them on the card (Issue 2 above)
   - **Wrong category/tags?** → Fix on the web page
   - **Wrong model field?** → Update on the web page
4. Build a new selections JSON with the corrected card details and agent_id (1 skill only for download)
5. Run `publish-init --selections-file ... --reset-local-state`
6. User confirms on the web page — tell them exactly which fields changed
7. Run `publish-configure` → `publish-ship`
8. User submits the final review page

---

## Quick Reference: Full Checklist Per Agent

- [ ] Assess publishability tier (🟢🟡🔴)
- [ ] **CRITICAL: Download mode = exactly 1 skill in selections JSON.** Do not bundle 2+ skills.
- [ ] Generate logo with `image_generate`
- [ ] Save logo to `~/AppData/Local/hermes/[name]-logo.png`
- [ ] Write selections JSON with agent_id, title, description, and exactly 1 skill with purpose
- [ ] Submit with `--selections-file`
- [ ] **User opens review_url** → fills Basic Info (title, expertise, logo, category, tags, email)
- [ ] **User fills Details/README** with pre-written markdown
- [ ] **User sets pricing** per the tables above (note: one-time price = download mode)
- [ ] Reconcile: `publish-remote-status --agent-id <id>` to check `agentType`
- [ ] Run `publish-configure` (no deep scan for 🟢, deep scan for 🟡)
- [ ] If `agentType` is `run_online`: user visits credential review_url to confirm LLM provider
- [ ] If `agentType` is `download`: credential step is skipped — go straight to ship
- [ ] Run `publish-ship`
- [ ] **User opens final review_url** → clicks "Submit for Review"
- [ ] Verify: `publish-remote-status --agent-id <id>` shows `status: 1` (under review)
- [ ] If rejected, fix per the Handling Review Rejection section above
- [ ] Next agent → start from top

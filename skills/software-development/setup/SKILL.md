---
name: setup
description: "Analyze, research, and execute project/repo/tool setups. When the user says 'setup' followed by a repo URL, project name, or tool name, this skill reads the source (README, docs, package.json), determines what needs to be installed, and sets it up end to end."
version: 1.0.0
author: Hermes Agent
user-invocable: true
triggers:
  - setup
metadata:
  decide:
    keywords: [setup, install, configure, bootstrap, clone, initialize, scaffold]
    domain: software-development
    confidence: high
---

# /setup Skill

## Role
Automated setup agent for projects, tools, repos, and development environments. When the user says "setup" or asks to install/configure something, this skill takes over: clone → analyze → install → verify → report.

## Trigger Detection (for /decide)
The decide skill routes to `/setup` when any of these appear in the prompt:
- `setup <url|name>` — setup a repo or project
- `install <tool>` — install and configure a tool
- `clone and set up <repo>` — clone + full setup
- `bootstrap <project>` — initialize from scratch
- `configure <tool>` — configure an existing tool
- Any mention of `set up`, `installing`, `getting started` with a specific target

## Workflow

### Phase 0 — Environment Scan (New)
Before touching any setup target, **scan the existing environment** to understand what's already installed and where potential complements or conflicts lie.

1. **Scan existing projects**: Check `~/Documents/Projects/` for known repos:
   ```bash
   ls ~/Documents/Projects/
   # Look for: ECC/, free-ai-tools/, atm-machine/, or anything the user has worked on
   ```

2. **Check for complementary repos**: Does the target repo share a domain with anything already on disk?
   - Is this a model/provider repo? → It may complement **free-ai-tools**
   - Is this an agent framework repo? → It may complement **ECC** or need `external-agent-ecosystem-adapter`
   - Is this a Hermes plugin? → It integrates with **decide** skill routing
   - Is this a tool catalog? → It belongs near **free-ai-tools**

3. **Check for conflict vectors before they bite**:
   - **Model defaults**: Does the new repo have `agent.yaml` or `CLAUDE.md` with paid model defaults? (Will need free-model conversion)
   - **Orchestration claims**: Does `AGENTS.md` or `CLAUDE.md` claim orchestrator identity? (Will need role boundary)
   - **MCP servers**: Does the repo ship `.mcp.json` or `mcp-configs/`? (Check for port overlap with Hermes)
   - **Port competition**: Does it start a dev server on port 3000 or another common port?

4. **Record findings**: Add a note about complementary relationships to the eventual Obsidian doc. This data feeds Phase 2.5.

### Phase 0.5 — Classify the Project (before running anything)

Before reaching for a terminal command, determine **what kind of project this actually is** and whether it matches what the user is asking for. This prevents the "it started but doesn't do what I wanted" problem.

1. **Read the README** — keywords like "directory", "catalog", "list", "awesome list", "collection", "curated" mean it's a **reference/listing site**, not a running service.

2. **Scan for API routes** — does it have `app/api/*`, `pages/api/*`, or `routes/` directories? If not, there's no backend to call. Next.js apps with only `page.tsx` / component files are **static UI**.

3. **Check the data layer** — if data is imported from static `.ts`/`.json`/`.yaml` files (not a database, not HTTP endpoints), the project is **pre-compiled content**, not a live service.

4. **Check for server-side requirements** — does the README mention a database (Postgres, SQLite, MongoDB), external API keys, or a real backend? If not, there's no server-side processing.

5. **Mismatch detection triage** — If the user's ask and the repo's nature don't align, catch it *before* running any commands:
   - Does the user want a **live API/service** but the repo is a **directory/catalog/listing**? → Don't set it up. Build or offer a real alternative.
   - Does the user want a **running server** but the repo is a **CLI tool**? → Explain the project type mismatch and offer the correct approach.
   - Does the user want **offline/local** but the repo requires **cloud API keys**? → Flag this as a requirement mismatch.
   - **Multi-check rule**: If 2+ of checks 1-4 flag "not a live service", treat it as confirmed — don't find an excuse to run it anyway.

6. **Set expectations explicitly** — before running any commands, tell the user what they're getting:
   - *"This is a directory/listing website — it shows information but doesn't host an API you can call from the browser."*
   - *"This is an API server — once it's running you can make requests to `localhost:PORT/...`"*
   - *"This is a CLI tool — it's meant to be run in the terminal, not served on a port."*
   - *"This is a library/module — it needs to be imported into another project, not run standalone."*

7. **If the project is the wrong kind for the user's ask**: Don't just run it anyway. Offer a better alternative:
   - *"This project isn't what you're looking for. Instead, I can set up <real alternative> that actually provides <what you asked for>."*
   - Example from this session: user asked for a free LLM API → project was a directory site → built an Express proxy to OpenRouter free models instead (see `references/local-llm-proxy.md`).
   - **User asked for a local LLM API but the repo is just a directory?** → Build a lightweight Express proxy server that forwards to OpenRouter free models. This is faster and more useful than setting up the wrong project. Full pattern in `references/local-llm-proxy.md`.

### Phase 1 — Analyze the Target
1. If a **GitHub URL** is provided:
   - Extract the repo name and owner
   - Read the README.md — identify language, framework, build system, dependencies
   - Check for: package.json (npm), requirements.txt (Python), Cargo.toml (Rust), Gemfile (Ruby), CMakeLists.txt (C++), Dockerfile, Makefile, setup.py/pyproject.toml
   - Check for any CLI tools or global dependencies mentioned (e.g., `npm install -g ...`)
   - Check for environment variables, .env.example files, or secrets needed

2. If a **tool name** is provided:
   - Search for the tool's official docs or GitHub
   - Identify install method: package manager (npm/pip/apt/choco/brew), binary download, manual build
   - Check for post-install configuration steps

3. If a **project directory** exists locally:
   - Scan for config files, missing dependencies, broken symlinks
   - Compare installed versions vs required versions

### Phase 2 — Plan & Execute
1. **Produce a setup plan** — list the steps in order
2. **Execute each step** immediately using terminal:
   - `git clone` (if not already cloned)
   - Install system-level deps (Python, Node, etc.) if missing
   - Install project dependencies (npm install, pip install, uv sync, etc.)
   - Run build/compile step (npm run build, make, cargo build, etc.)
   - Set up environment file from .env.example if present
   - Verify the setup works (run a test, start the dev server briefly, check version)

### Phase 2.5 — Complementary Integration
After the target is installed and verified, **wire it to complement existing repos rather than compete**.
This phase may delegate to `software-development/graphify-integrate` (for code-graph exports)
and `software-development/update` (for full ecosystem onboarding).

1. **If it's an agent ecosystem (ECC, devfleet, etc.):**
   - Load `external-agent-ecosystem-adapter` and run Phase 2 (Conflict Resolution)
   - Check model defaults → convert to free models
   - Check AGENTS.md/CLAUDE.md → add role boundary
   - Check MCP configs → identify reference vs active, check for port overlaps
   - Link it in the Obsidian project note as a **resource/skill library** for the decide skill

2. **If it's a model/provider resource:**
   - Link to `free-ai-tools` as the model data source → new repo provides data, free-ai-tools catalogs it
   - Check `free-ai-model-router` skill for routing integration
   - Run `model-recommender-workflow` to test the model chain
   - Document the provider's free model count and rate limits

3. **If it's a standalone tool/utility:**
   - Check if it has a CLI (`--help`, `--version`) — if so, verify it works alongside existing tools
   - Check for shared dependencies (npm global, Python packages at different versions causing conflicts)
   - Add a workflow example showing how this tool fits with the user's existing stack

4. **Document cross-references in Obsidian:**
   - Always add `[[wikilinks]]` between the new project note and any existing complementary notes
   - Update the Knowledge Graph map in the main project note to show the new relationship
   - List the cross-reference in the "Related Files" section of each affected note

5. **If Graphify is available and the project has code files:**
   - Run `software-development/graphify-integrate` to build a code knowledge graph
   - Export to Obsidian vault: `graphify export obsidian --dir "<vault>/Projects/<name>/graphify"`
   - Register the `graphify-mcp` MCP server in Hermes config for code-level queries
   - Document the code graph metadata (nodes, edges, communities) in the Obsidian note

6. **If the user explicitly said `/update`:**
   - Route to `software-development/update` instead of doing Phase 2.5 inline
   - The update skill handles all integration, documentation, and cross-linking
   - Return to setup only if the update skill fails or reports unrecoverable issues

7. **If no complement found:** Add a note in the Obsidian doc: "Standalone — no known complementing repos" — future sessions can update this.

### Phase 3 — Verify
- **Build check**: `npm run build`, `python -m compileall`, `cargo check`, etc.
- **Quick smoke test**: run the app briefly, check for startup errors
- **CLI check**: if a CLI tool, run `--version` or `--help`
- **HTTP smoke test**: if it's a web server, curl the root endpoint or `/health` to confirm it's listening
- **Auth-gated endpoints**: A `401` or `403` on a server you just started is **proof of life** — the server is running and enforcing auth correctly. Don't report it as broken. Instead:
  1. Identify the auth mechanism (API key header, bearer token, session cookie, basic auth)
  2. Bootstrap credentials via the server's setup/login endpoints or admin creation APIs
  3. Re-test with proper credentials to confirm the endpoint works end-to-end
  4. Document the bootstrapped credentials in the setup report so the user knows what was configured
- **Report**: summary of what was installed, any issues, how to use/run it, and any bootstrapped auth credentials

### Phase 4 — Document
- If in a project directory, update the Obsidian vault with a setup note (see Obsidian bundle)

### Phase 5 — Wire into Hermes (if applicable)
If the setup produced a running OpenAI-compatible API server (proxy, local LLM, gateway), consider wiring it into Hermes as a custom provider:

1. Store the API key in `~/.hermes/.env` with a named env var (e.g., `MY_PROXY_API_KEY=…`)
2. Configure Hermes:
   ```bash
   hermes config set model.provider custom
   hermes config set model.default auto
   hermes config set model.base_url "http://localhost:<port>/v1"
   hermes config set providers.my-provider.base_url "http://localhost:<port>/v1"
   hermes config set providers.my-provider.key_env "MY_PROXY_API_KEY"
   hermes config set providers.my-provider.default_model auto
   hermes config set providers.my-provider.discover_models true
   ```
3. Verify a chat completion works: `curl` the `/v1/chat/completions` endpoint with the API key
4. Remember: a new `hermes chat` session picks up the config fresh — no restart needed

See `references/hermes-custom-provider.md` for the full schema, resolution internals, and auth-gated server patterns.

## Pitfalls
- **npm on Windows**: can hang on `npm install -g ...` — try `npx` or local install as fallback
- **Global installs on Windows**: MSYS path issues — prefer local installs when possible
- **Missing Python/pip**: Check for `uv` first (faster), fall back to pip
- **Lockfiles**: Never commit lockfiles that npm created outside the project dir
- **Version conflicts**: Check Node/Python version against project requirements before installing deps
- **Next.js 16 Turbopack root on Windows**: When building inside a subdirectory (e.g. `website/` of a monorepo), Turbopack detects the wrong root lockfile. Fix: add `turbopack: { root: __dirname }` to `next.config.ts`. See `references/nextjs-windows.md`.
- **Missing `@vercel/analytics`**: Next.js scaffolded projects often import from `@vercel/analytics/next` in layout.tsx but omit it from `package.json`. Install with `npm install @vercel/analytics`.
- **Port conflicts on Windows**: Port 3000 frequently has leftover Node.js processes. Check with `netstat -ano | grep ':3000' | grep LISTEN`. Kill with `taskkill //F //PID <pid>` (note `//F` not `/F` in git-bash — MSYS converts bare `/F` to `F:/`).
- **Next.js auto-detects existing dev servers**: If another `next dev` is already running, the new one exits with a message showing the existing server's port and PID. Kill the old one and retry.
- **Build errors from `.next/` auto-generated files**: Turbopack generates type validators in `.next/dev/types/` that can fail with spurious errors (e.g. "Declaration or statement expected"). These are Next.js internals, not the project's fault — clean `.next/` and retry, or skip the type-check phase.
- **Dev servers**: Verify they actually started by curling the endpoint (`curl -s http://localhost:3000 | head -5`). Check the process log if output is empty after 15s. Don't rely on background=true with no verification.
- **Shell quoting with API keys/secrets in bash**: API keys often contain `$`, `!`, `(`, `)`, or other special shell characters. Avoid `$()` command substitution or inline variable expansion with secret values. Safer approach: write the key to a temp file (`curl ... > /tmp/key.txt`), then read it with `python -c "import sys; print(open('/tmp/key.txt').read().strip())"` and export via `KEY=$(...)` only from the file — the file read doesn't trigger shell metacharacter expansion.
- **npm run dev via `concurrently` shows no process output**: When using `npm run dev` with `concurrently` (common in monorepos), the process log may show zero output even though both servers are running fine. This is because `concurrently` buffers/pipes output through the parent process. Don't interpret empty process log as failure — curl the endpoints directly to verify.

## Phase 2 Enhancement — GitHub API Directory Analysis

For GitHub repos, call the API to get the full file tree _before_ cloning:
```
https://api.github.com/repos/{owner}/{repo}/contents
```
This reveals hidden directories (e.g. `website/`, `packages/`) and config files the README may not mention. Especially useful for monorepos.

## Phase 3 Enhancement — Server Verification

When starting a dev server as a background process:
1. Check the process log for startup messages (`process(action='log')`)
2. Verify the server is responding: `curl -s http://localhost:3000 | head -5`
3. If no output after 15s, check if the port is already in use
4. Use `watch_patterns` like `["localhost:3000", "compiled successfully"]` for automatic readiness notification
5. **Auth-gated servers**: If the server requires auth for all endpoints (e.g. a proxy with unified API key, a dashboard with session auth), bootstrap auth first:
   - Create an admin account via the setup/register endpoint (check README or routes for `/setup`, `/register`, `/auth/setup`)
   - Login to get a session token or API key
   - Use that credential to test protected endpoints
   - A `401` at initial contact is normal; document what auth was bootstrapped

## CLI Tools with Browser OAuth

Some CLI tools (Freebuff, Supabase, Vercel, Linear, etc.) use **browser-based OAuth** rather than API keys or token files. Setup pattern:

1. Install via `npm install -g <tool>` or `brew install <tool>`
2. Run `<tool> login` — outputs a URL to open in a browser
3. Open the URL, complete the OAuth flow (typically GitHub, Google, or email magic link)
4. The CLI orchestrator stores an auth token in `~/.config/<vendor>/` or system keychain
5. Verify with `<tool> whoami` or `--version` (no auth prompt)

**Pitfall:** These tools cannot be set up without a browser session — there's no headless/token-only fallback. GitHub Personal Access Tokens (PATs) cannot be used as passwords for GitHub's web OAuth form. You MUST have a browser available to complete the flow. If working in a headless environment, generate the URL on the CLI then open it from a browser on another machine.

## Quick Reference

```bash
# Clone and setup a repo
git clone <url>
cd <repo>
# Check for deps
ls package.json && npm install
ls requirements.txt && pip install -r requirements.txt
ls pyproject.toml && uv sync
# Build
ls package.json && npm run build
# Start dev server
npx next dev --port 3000
# Install an OAuth-gated CLI tool
npm install -g <tool>
<tool> login   # must open URL in browser
```

## Related
- `github-repo-management` — for clone/fork/create operations
- `obsidian` — for documenting the setup in notes
- `software-development/graphify-integrate` — run Graphify code-graph + export to Obsidian
- `software-development/update` — full ecosystem onboarding (setup + graph + obsidian + cross-links)
- `software-development/repo-integration-reconciliation` — when setup includes auditing existing skills for overlap and resolving conflicts
- `references/nextjs-windows.md` — Next.js 16 on Windows: turbopack root fix, missing deps, and port conflict resolution
- `references/local-llm-proxy.md` — Build a lightweight Express proxy to OpenRouter free models when the user wants a live API but the repo is a directory/catalog site
- `references/hermes-custom-provider.md` — Wiring a local OpenAI-compatible server as a Hermes custom provider (model.provider=custom, providers dict with key_env, auth verification pattern)
- `references/codebuff-freebuff.md` — Setting up and using Codebuff/Freebuff: npm install, browser OAuth login, TUI usage, free tier limits, and Windows quirks.

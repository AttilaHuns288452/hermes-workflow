---
name: setup
description: "Analyze, research, and execute project/repo/tool setups. When the user says 'setup' followed by a repo URL, project name, or tool name, this skill reads the source (README, docs, package.json), determines what needs to be installed, and sets it up end to end."
version: 1.1.0
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

### Phase 0 — Environment Scan
Before touching any setup target, **scan the existing environment** to understand what's already installed and where potential complements or conflicts lie.

1. **Scan existing projects**: Check `~/Documents/Projects/` for known repos.
2. **Check for complementary repos**: Does the target repo share a domain with anything already on disk?
   - Model/provider repo? → may complement **free-ai-tools**
   - Agent framework? → may complement **ECC** or need `external-agent-ecosystem-adapter`
   - Hermes plugin? → integrates with **decide** routing
   - Tool catalog? → belongs near **free-ai-tools**
3. **Check conflict vectors**:
   - Paid model defaults in `agent.yaml` / `CLAUDE.md`
   - Orchestration claims in `AGENTS.md` / `CLAUDE.md`
   - MCP servers / port overlap with Hermes
   - Dev server port competition
4. **Record findings** in the eventual Obsidian doc.

### Phase 0.5 — Classify the Project (before running anything)

Before reaching for a terminal command, determine **what kind of project this actually is** and whether it matches what the user is asking for.

1. **Read the README** — keywords like "directory", "catalog", "list", "awesome list", "collection", "curated" mean it's a **reference/listing site**, not a running service.
2. **Scan for API routes** — `app/api/*`, `pages/api/*`, `routes/`? If not, it's likely static UI.
3. **Check the data layer** — static `.ts`/`.json`/`.yaml` files mean **pre-compiled content**, not a live service.
4. **Check for server-side requirements** — database, external API keys, real backend?
5. **Mismatch detection** — If 2+ checks flag "not a live service", treat it as confirmed. Don't run it anyway. Offer a better alternative.
6. **Set expectations explicitly** before running commands.

If the project is the wrong kind for the user's ask, offer a real alternative. Example: user wants a free LLM API but the repo is a directory site → build an Express proxy to OpenRouter free models instead. See `references/local-llm-proxy.md`.

### Phase 1 — Analyze the Target
1. If a **GitHub URL** is provided:
   - Extract repo name and owner
   - Read README.md — identify language, framework, build system, dependencies
   - Check for config files: package.json, requirements.txt, Cargo.toml, Gemfile, CMakeLists.txt, Dockerfile, Makefile, pyproject.toml
   - **Check for an agent-driven pipeline system** — `AGENT_GUIDE.md`, `PROJECT_CONTEXT.md`, `pipeline_defs/*.yaml`, `tools/tool_registry.py`. If found, read the guide first and follow the repo's pipeline; do NOT write ad-hoc scripts that bypass it. See `references/repo-pipeline-workflow.md`.
   - Check for environment variables, .env.example, or secrets needed
2. If a **tool name** is provided:
   - Search official docs or GitHub
   - Identify install method: package manager, binary download, manual build
   - Check post-install configuration
3. If a **project directory** exists locally:
   - Scan for config files, missing dependencies, broken symlinks
   - Compare installed vs required versions

### Phase 2 — Plan & Execute
1. **Produce a setup plan** — list steps in order
2. **Execute each step**:
   - `git clone` if needed
   - Install system-level deps if missing
   - Install project dependencies (`npm install`, `pip install`, `uv sync`, etc.)
   - Run build/compile step
   - Set up environment file from `.env.example` if present
   - **Check for OpenAI SDK hardcoding** — grep for `OpenAI(` calls and patch to support `OPENAI_BASE_URL`. See `references/openai-base-url-patch.md`.
   - Verify setup works (test, dev server briefly, version check)

### Phase 2.5 — Complementary Integration
After the target is installed and verified, wire it to complement existing repos rather than compete.

- **Agent ecosystem** → load `external-agent-ecosystem-adapter`
- **Model/provider resource** → link to `free-ai-tools` / `free-ai-model-router`
- **Standalone tool** → verify CLI, check dependency conflicts
- **Graphify available** → load `software-development/graphify-integrate`
- **User said `/update`** → route to `software-development/update`
- Document cross-references in Obsidian with `[[wikilinks]]`

For external repo → Hermes skill integration, see `references/external-repo-to-skill.md`.

### Phase 3 — Verify
- Build check
- Quick smoke test
- CLI check (`--version` / `--help`)
- HTTP smoke test with `curl` if it's a web server
- Auth-gated endpoints: `401`/`403` is proof of life; bootstrap credentials, then re-test
- Report: what was installed, issues, how to use/run it, bootstrapped credentials

### Phase 4 — Document
Update Obsidian vault with a setup note if in a project directory.

### Phase 5 — Wire into Hermes (if applicable)
If the setup produced a running OpenAI-compatible API server, wire it into Hermes as a custom provider. See `references/hermes-custom-provider.md`.

## Pitfalls
- **`git clone --depth 1` timeout on medium/large repos**: Repos with 100+ files can exceed the default 30s timeout on Windows. Always use `timeout=120` (or higher) when cloning repos with npm/yarn lockfiles, asset directories, or >50 files. The clone itself is fast — the checkout/unpacking phase hits the timeout.
- **npm on Windows**: can hang on `npm install -g ...` — try `npx` or local install as fallback
- **Vite build failing because root `index.html` points to a hashed asset**: If you previously copied a built `docs/index.html` to the repo root, Vite will try to resolve the hashed `/hermes-workflow/assets/index-XXXXXX.js` path as an entry point and fail with `Failed to resolve /hermes-workflow/assets/index-XXXXXX.js from .../index.html`. The root `index.html` must be the **source** version pointing to `/src/main.jsx` (or whatever Vite entry) before running `npm run build`. Only copy the built output *after* the build succeeds.
- **Interactive CLI tools hang in background mode on Windows**: Tools that expect interactive input (e.g. `input()` calls in Python) produce no output when started as a background process or PTY. Write config files directly instead of running interactive wizards. `curl` the expected ports directly; check `netstat`; run components separately if hung.
- **pnpm store corruption — only `.js.map` files present, no `.js`**: See `references/pnpm-store-corruption.md`.
- **Global installs on Windows**: MSYS path issues — prefer local installs
- **Missing Python/pip**: Check for `uv` first, fall back to pip
- **Lockfiles**: Never commit lockfiles that npm created outside the project dir
- **Writing ad-hoc scripts instead of using the repo's pipeline**: If the repo has an `AGENT_GUIDE.md`, follow it.
- **Version conflicts**: Check Node/Python version against project requirements
- **Next.js 16 Turbopack root on Windows**: See `references/nextjs-windows.md`.
- **Missing `@vercel/analytics`**: Install with `npm install @vercel/analytics` if imported.
- **Port conflicts on Windows**: Check `netstat -ano | grep ':3000' | grep LISTEN`. Kill with `taskkill //F //PID <pid>` (note `//F` not `/F` in git-bash).
- **Next.js auto-detects existing dev servers**: Kill the old one and retry.
- **Build errors from `.next/` auto-generated files**: Clean `.next/` and retry.
- **Dev servers**: Verify with `curl -s http://localhost:3000 | head -5`. Don't rely on `background=true` alone.
- **OpenAI SDK hardcodes `base_url`**: See `references/openai-base-url-patch.md`.
- **Hermes display masking hides API key values but DOES save them correctly**: See `references/hermes-env-key-masking.md`.

## Verification Commands

```bash
# GitHub API file tree (useful for monorepos)
curl -s https://api.github.com/repos/{owner}/{repo}/contents

# Dev server proof of life
curl -s http://localhost:3000 | head -5

# GitHub Pages asset 200 check (cache-bust)
curl -sI "https://<user>.github.io/<repo>/assets/index-XXXX.js?_$RANDOM"
```

## Related

- For SkillClaw-specific setup, see `references/skillclaw-setup.md`.
- `github-repo-management` — clone/fork/create operations
- `obsidian` — documenting setup in notes
- `software-development/graphify-integrate` — code-graph + Obsidian
- `software-development/update` — full ecosystem onboarding
- `software-development/repo-integration-reconciliation` — audit existing skills for overlap
- `references/nextjs-windows.md`
- `references/local-llm-proxy.md`
- `references/hermes-custom-provider.md`
- `references/openai-base-url-patch.md`
- `references/github-pages-vite-deployment.md`
- `references/skillclaw-setup.md` — SkillClaw proxy on Windows + Hermes integration
- `references/scroll-reveal-fallback.md`
- `references/app-centerpiece-integration.md` — register new apps in the launcher
- `references/autogpt-setup.md` — AutoGPT classic: OpenRouter config, Pydantic enum fix, centerpiece registry entry, serve mode

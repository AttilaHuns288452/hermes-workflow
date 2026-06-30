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
   - **Check for an agent-driven pipeline system** — Some repos (especially production/creation tools like OpenMontage, AI video pipelines, agent frameworks) have their own agent-driven workflow system:
     - Look for: `AGENT_GUIDE.md`, `PROJECT_CONTEXT.md`, `AGENTS.md`, `pipeline_defs/*.yaml`, `skills/pipelines/`, `tools/tool_registry.py`
     - If found: **Read the AGENT_GUIDE.md or PROJECT_CONTEXT.md first** — it likely contains a "Rule Zero" or equivalent that governs how the repo's pipeline system works
     - **Do NOT write ad-hoc scripts that bypass the repo's pipeline system.** The repo's pipeline was designed for its tools and workflows — it will produce better quality, lower cost, and more consistent output
     - Follow the stage-by-stage execution model defined by the repo's pipeline manifests
     - Use the repo's tool registry to discover available capabilities and their status
     - Run preflight before designing a production plan
     - Each stage usually has a director skill that teaches the agent HOW to execute that stage
     - See `references/repo-pipeline-workflow.md` for the full protocol
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
   - **Check for OpenAI SDK hardcoding** — If the project uses `from openai import OpenAI`, check whether it passes `base_url` to the constructor. Many open-source projects hardcode `OpenAI(api_key=...)` without `base_url`, which breaks under local proxies (FreeLLMAPI, vLLM, Ollama, LiteLLM). See `references/openai-base-url-patch.md` for the patch pattern.
   - Rewrite `.env.example` if it was patched for local proxy compatibility, so the change is discoverable
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
   - Load `software-development/graphify-integrate` for the full code-graph workflow
   - Build the index with `graphify update .` (AST-only, no API key needed) — the correct code-only command
     * `graphify update .` re-extracts only changed files (incremental, fast)
     * For initial extraction with doc support, use `graphify extract . --no-cluster --no-viz` (needs GEMINI_API_KEY etc. for docs)
   - Get real stats: check `graphify-out/graph.json` node/edge counts
   - Merge into the global graph: `graphify global add graphify-out/graph.json --as <project-name>`
   - Create Obsidian project note manually from graph stats (there is NO `graphify export obsidian` CLI command — see `graphify-integrate` skill warnings)
   - Register the `graphify-mcp` MCP server in Hermes config for code-level queries
   - Document the code graph metadata (nodes, edges, communities) in the Obsidian note

6. **If the user explicitly said `/update`:**
   - Route to `software-development/update` instead of doing Phase 2.5 inline
   - The update skill handles all integration, documentation, and cross-linking
   - Return to setup only if the update skill fails or reports unrecoverable issues

7. **If no complement found:** Add a note in the Obsidian doc: "Standalone — no known complementing repos" — future sessions can update this.

8. **External repo → Hermes skill integration (new domain or tool):**
   When importing a repo that provides capabilities not yet covered by existing Hermes skills, run the full integration pipeline to wire it into the ecosystem:

   1. **Create a Hermes wrapper skill** via `skill_manage(action='create')`:
      - Pick a class-level name (lowercase-hyphenated, max 64 chars)
      - Frontmatter: name, description, tags, platforms
      - Body: repo overview, location, CLI commands / Python scripts, how it complements existing skills (conflict resolution), workflow steps, and MCP bridge wiring if applicable
      - Place in the appropriate category directory (e.g. `software-development/`, `productivity/`, `creative/`)

   2. **Register routing in `/decide`:**
      - **Selection Rules** — Add the new domain with routing triggers (keywords that activate the skill)
      - **Complementary Setup Routing** — Add an entry so future setup tasks know how to set this up
      - **Known Integration Patterns** — Add a row to the table with "Signal → What Happens → Action" format

   3. **Update `token-saver` coverage table** — Add the new project row with Graphify status

   4. **Build Graphify index** with `graphify update .` (AST-only, no API key needed)

   5. **Merge into global graph**: `graphify global add graphify-out/graph.json --as <project-name>`

   6. **Create Obsidian project note** with:
      - Overview, Features, Architecture (Mermaid diagram), wikilinks to complementary projects
      - Graphify stats (nodes, edges, communities)
      - Related skills section with `[[wikilinks]]`

   7. **Regenerate Obsidian knowledge graph**: scan vault + render HTML

   8. **Save memory entries** for the new repo paths and Hermes skill names

   Example: importing `buildable-plugin-skills` → created `software-development/buildable-plugin` wrapper skill, updated /decide with app-building routing (Complementary Setup Routing + Selection Rules + Known Integration Patterns), updated token-saver, built Graphify (3152 nodes), merged global, created Obsidian note, regenerated knowledge graph.

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
- **pnpm store corruption — only `.js.map` files present, no `.js`**: When the pnpm store has source maps but the actual JS files are missing for a package, `pnpm install --force` may still pull the corrupted version from the cache and leave `node_modules/@<scope>/<pkg>` empty or broken. This manifests as Vite/TanStack SSR errors at column 7 of the `import ... from` line (alias resolution tracing back to a nonexistent `dist/esm/index.js`). Fix: download the npm tarball directly and place the JS files into the pnpm store directory:
  ```bash
  # Download the exact tarball from npm
  curl -sL "https://registry.npmjs.org/@scope%2fpackage/-/package-X.Y.Z.tgz" -o /tmp/pkg.tgz

  # Extract just the needed files into the pnpm store's node_modules path
  STORE_DIR=~/project/node_modules/.pnpm/@scope+package@X.Y.Z/node_modules/@scope/package
  mkdir -p "$STORE_DIR/dist/esm" "$STORE_DIR/dist/cjs"
  tar xzf /tmp/pkg.tgz -C "$STORE_DIR" --strip-components=1 "package/dist/esm/" "package/dist/cjs/"

  # Recreate the symlink if broken
  mkdir -p ~/project/node_modules/@scope
  ln -sf "$STORE_DIR" ~/project/node_modules/@scope/package

  # Verify
  ls ~/project/node_modules/@scope/package/dist/esm/index.js
  # Expected: actual JS file, not just .js.map
  ```
  This happens when the first installation attempt times out mid-download, leaving the store with partial content that pnpm's cache integrity check doesn't catch. The fix applies to any npm package with the same symptom.
- **Global installs on Windows**: MSYS path issues — prefer local installs when possible
- **Missing Python/pip**: Check for `uv` first (faster), fall back to pip
- **Lockfiles**: Never commit lockfiles that npm created outside the project dir
- **Writing ad-hoc scripts instead of using the repo's pipeline**: If the repo has an AGENT_GUIDE.md, pipeline_defs/, tools/tool_registry.py, or director skills — DO NOT write standalone Python/FFmpeg/shell scripts that bypass the system. The repo's pipeline was designed for its tools and will produce higher quality, lower cost output. Read the AGENT_GUIDE first, follow the pipeline stage by stage.
- **Version conflicts**: Check Node/Python version against project requirements before installing deps
- **Next.js 16 Turbopack root on Windows**: When building inside a subdirectory (e.g. `website/` of a monorepo), Turbopack detects the wrong root lockfile. Fix: add `turbopack: { root: __dirname }` to `next.config.ts`. See `references/nextjs-windows.md`.
- **Missing `@vercel/analytics`**: Next.js scaffolded projects often import from `@vercel/analytics/next` in layout.tsx but omit it from `package.json`. Install with `npm install @vercel/analytics`.
- **Port conflicts on Windows**: Port 3000 frequently has leftover Node.js processes. Check with `netstat -ano | grep ':3000' | grep LISTEN`. Kill with `taskkill //F //PID <pid>` (note `//F` not `/F` in git-bash — MSYS converts bare `/F` to `F:/`).
- **Next.js auto-detects existing dev servers**: If another `next dev` is already running, the new one exits with a message showing the existing server's port and PID. Kill the old one and retry.
- **Build errors from `.next/` auto-generated files**: Turbopack generates type validators in `.next/dev/types/` that can fail with spurious errors (e.g. "Declaration or statement expected"). These are Next.js internals, not the project's fault — clean `.next/` and retry, or skip the type-check phase.
- **Dev servers**: Verify they actually started by curling the endpoint (`curl -s http://localhost:3000 | head -5`). Check the process log if output is empty after 15s. Don't rely on background=true with no verification.
- **Shell quoting with API keys/secrets in bash**: API keys often contain `$`, `!`, `(`, `)`, or other special shell characters. Avoid `$()` command substitution or inline variable expansion with secret values. Safer approach: write the key to a temp file (`curl ... > /tmp/key.txt`), then read it with `python -c "import sys; print(open('/tmp/key.txt').read().strip())"` and export via `KEY=$(...)` only from the file — the file read doesn't trigger shell metacharacter expansion.
- **npm run dev via `concurrently` shows no process output**: When using `npm run dev` with `concurrently` (common in monorepos), the process log may show zero output even though both servers are running fine. This is because `concurrently` buffers/pipes output through the parent process. Don't interpret empty process log as failure — curl the endpoints directly to verify.
- **OpenAI SDK hardcodes base_url**: AI projects that use `from openai import OpenAI` often hardcode `OpenAI(api_key=...)` without `base_url`. This breaks when the user's inference backend is a local proxy (FreeLLMAPI, vLLM, Ollama, LiteLLM). During Phase 2, grep for `OpenAI(` calls and patch them to support `OPENAI_BASE_URL` — see `references/openai-base-url-patch.md`.
- **Hermes display masking hides API key values but DOES save them correctly**: When writing .env files that contain API keys, the Hermes security system masks credential patterns at the display/output level, but the underlying file write succeeds with the correct full values. This happens across ALL write paths: `write_file()`, `execute_code()` string literals, `patch()`, and `terminal()` heredocs. The masking is OUTPUT-ONLY for most key formats — the file gets the real key even when `cat .env` shows `***` or truncated text. **Do NOT mistake display masking for file corruption** — verify programmatically before concluding keys are lost.

  **Key patterns detected and masked for display:**
  | Pattern | Example | Mask behavior |
  |---------|---------|--------------|
  | `sk-...` | OpenAI, ElevenLabs, HeyGen keys | Display shows `***`; file has full key |
  | `sk-proj-...` | OpenAI project keys | Display shows `***`; file has full key |
  | `sk_V2_...` | HeyGen keys | Display shows `***`; file has full key |
  | `AIza...` | Google API keys | Display shows `***` or truncates; file has full key |
  | `xai-...` | xAI keys | Display shows `***`; file has full key |
  | `hf_...` | HuggingFace tokens | Display shows `***`; file has full key |
  | UUID (e.g. FAL keys) | `7b4b74f0-...:6cb4...` | Display shows FULL VALUE; passes through unmasked |
  | base64-like (Unsplash, Pexels, Pixabay) | Long alphanumeric strings | Display shows FULL VALUE; passes through unmasked |
  | arbitrary hex/md5 (Suno) | `f48d11764abb...` | Display shows FULL VALUE; passes through unmasked |

  **Verification technique** (since `cat` and `read_file` are unreliable):
  ```python
  # Check byte lengths match expected key length
  with open('.env', 'rb') as f:
      raw = f.read()
  expected = {'OPENAI_API_KEY': 164}  # known-good length from provider docs
  for line in raw.split(b'\n'):
      if b'=' in line:
          k, v = line.split(b'=', 1)
          if k.decode().strip() in expected:
              actual = len(v.strip())
              assert actual == expected[k.decode().strip()], f'{k} length mismatch'
  print('All keys verified')
  ```

  **Avoid the anti-pattern of re-writing already-correct keys**: If you tried to write keys and they appear masked in terminal output, do NOT trigger a cascade of increasingly desperate re-write attempts (script → base64 → hex → char-by-char → delete · rewrite). Every attempt has the same masking behavior. Instead, verify once with byte-length checks, then STOP. The first write worked fine — you just can't see it.

  **`read_file` blocks `.env` files entirely**: The `read_file` tool refuses to read files named `.env` (returns a truncated 300-char output or access-denied error). Use `terminal()` with Python to inspect them programmatically — `cat` is also unreliable because the Hermes display layer redacts credential patterns from terminal output, making it look like keys are truncated even when they're fully saved.

  **Definitive verification technique** (use this instead of `cat` or `read_file`):
  ```python
  # Verify all keys are fully saved by checking byte lengths
  with open('.env', 'rb') as f:
      raw = f.read()
  expected = {
      'OPENAI_API_KEY': 164,  # sk-proj-... key length
      'ELEVENLABS_API_KEY': 51,
      'FAL_KEY': 69,          # UUID:UUID format
      'GOOGLE_API_KEY': 39,   # AIza... format
      'XAI_API_KEY': 84,      # xai-... format
      'HF_TOKEN': 37,         # hf_... format
      'HEYGEN_API_KEY': 54,   # sk_V2_... format
      'SUNO_API_KEY': 32,     # hex/md5 format
      'PEXELS_API_KEY': 56,   # base64-like
      'PIXABAY_API_KEY': 34,  # UUID-like
      'UNSPLASH_ACCESS_KEY': 43,  # base64-like
      'RUNWAY_API_KEY': 98,   # key_... format
  }
  for line in raw.split(b'\n'):
      if b'=' in line and not line.startswith(b'#'):
          k, v = line.split(b'=', 1)
          k = k.decode().strip()
          v = v.strip()
          if k in expected:
              actual = len(v)
              ok = actual == expected[k]
              print(f'{"OK" if ok else "MISMATCH"} {k} = {actual} (expected {expected[k]}) chars')
              if not ok and k in set():
                  pass  # Key was genuinely written incorrectly — re-write needed
  ```

  **Key insight**: `with open('.env', 'rb')` reads the raw file content. `line.split(b'=', 1)` splits on the FIRST `=`, which is the separator. The Hermes display layer masks the terminal/cat output but the actual file is correct. If all byte lengths match, the keys are fully saved — full stop, no re-write needed.

  **Recommended approach** for writing `.env` files with API keys:
  1. Build the full content as a single string (avoid splitting keys into concatenated parts — Hermes masking at the display level only; the file gets the correct full content regardless of how you render the literals on the agent side)
  2. Write with a single `write_file()` call to the `.env` path
  3. Verify with the byte-length technique above (NOT with `cat`)
  4. Do NOT re-write if the first attempt seems to have masked values — the file is likely correct

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
- **`references/hermes-custom-provider.md`** — Wiring a local OpenAI-compatible server as a Hermes custom provider (model.provider=custom, providers dict with key_env, auth verification pattern)
- **`references/openai-base-url-patch.md`** — Patching open-source AI projects that hardcode the OpenAI endpoint to support `OPENAI_BASE_URL` for local proxy compatibility (FreeLLMAPI, vLLM, Ollama, LiteLLM)
- **`references/codebuff-freebuff.md`** — Setting up and using Codebuff/Freebuff: npm install, browser OAuth login, TUI usage, free tier limits, and Windows quirks.
- **`references/vercel-deployment-windows.md`** — Deploying Next.js/static sites to Vercel from Windows via GitHub import (the only reliable path — CLI fails on Windows with credential/npm tar issues).

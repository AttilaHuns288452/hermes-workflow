# Publishability Assessment — Which Skills to Publish on Capafy

Not every Hermes skill is suitable for Capafy cloud (Run Online) publishing.
Use this framework to assess publishability when the user asks "what should
I publish?" or "is this skill publishable?".

## The Three Tiers

### 🟢 GREEN — Fully publishable, zero credential friction
Skills that use only built-in tools (web_search, web_extract, terminal, file I/O),
public APIs with no auth, or pure computation (text generation, diagram drawing,
code generation). No personal API keys, no local services, no OAuth.

**Characteristics:**
- All data comes from public endpoints or the LLM itself
- No `mcp_servers` blocks in config.yaml needed
- No `custom_providers` entries needed (only the cloud LLM provider)
- No `.env` values that reference personal tokens

**Examples:** polymarket, arxiv, architecture-diagram, excalidraw, p5js, sketch,
claude-design, popular-web-designs, humanizer, ascii-art, maps, nano-pdf,
powerpoint, code-review, plan, systematic-debugging, spike, simplify-code,
gif-search, youtube-content, karpathy-guidelines

**Publishing steps:** publish-init → publish-configure (no deep scan needed) →
publish-ship. Just needs the LLM url_proxy (OpenRouter/etc.).

### 🟡 YELLOW — Publishable with standard service keys
Skills that need one well-known API key (GitHub, Notion, Airtable, etc.) that
users expect to provide. These are normal to host on Capafy's credential page.

**Characteristics:**
- Needs 1 standard third-party API key
- The key is for a well-known service, not the user's personal credentials
- No localhost endpoints
- No personal/tokenized credentials

**Examples:** github-* (need GITHUB_TOKEN), notion (Notion token), airtable
(Airtable key)

**Publishing steps:** publish-init → publish-configure (deep scan recommended
to capture the key) → configure on credential page → publish-ship.
Document for buyers that they need their own key.

### 🔴 RED — NOT publishable as Run Online (blocks)
Skills that depend on the user's personal infrastructure: localhost services,
personal API keys, local-only tools, private MCP servers, OAuth flows that
require a local browser session.

**Block characteristics:**
- `mcp_servers.*.env` with personal keys (these ship as PLAINTEXT — the
  publisher's rule scan does NOT detect keys inside MCP env blocks)
- `custom_providers` pointing to `localhost`, `127.0.0.1`, or LAN IPs
- Requires locally installed binaries (ComfyUI, TouchDesigner, Jupyter,
  Graphify, CodeGraph)
- OAuth tokens from personal Google/Microsoft accounts
- Personal `lqd_data_*`, `sk-or-*`, `sk-ant-*` keys the user doesn't want
  to expose

**Examples:** All `llmquant-*` skills (need LLMQUANT_API_KEY in MCP env,
not detectable by credential scan), comfyui, touchdesigner-mcp,
jupyter-live-kernel, google-workspace, gmail, drive-backups,
teams-meeting-pipeline, money-printer-turbo, graphify-integrate

**Options if user insists:**
1. **BYOK (Bring Your Own Key)** — promote the blocked key from MCP env
   (invisible to scan) to a visible `env_var` on the credential page that
   the buyer configures. Edit staged `.temp/staging/.hermes/config.yaml`
   to remove the hardcoded key and document the requirement.
2. **Download mode** — switch to `agentType: download` so the agent runs
   on the buyer's own machine with their own config. Pricing model changes.
3. **Free data fallback** — rewrite the skill to use public APIs instead.

## Pricing Guidelines

Pricing tiers consistent with a cheap/volume strategy:

| Agent Type | Subscription (500 req/cycle) | One-Time Download | Rationale |
|---|---|---|---|
| Data/research (market, paper, news) | **$3/mo** | **$15** | Casual use, volume play |
| Developer tools (code review, debug) | **$5/mo** | **$25** | Daily tool, higher willingness to pay |
| Creative/design (diagrams, mockups) | **$4/mo** | **$20** | Project-by-project, mid-value |
| GitHub/PR/CI tools | **$5/mo** | **$25** | Team tool, team budget |
| Utility (maps, PDF, OCR) | **$3/mo** | **$15** | Occasional use, low friction |

**Defaults:** 500 requests/cycle, no free trial, DeepSeek V4 Flash or equivalent
free model, 10 min estimated execution.

## Typical Publishing Flow for a New Agent

```
1. publish-list (check existing agents)
2. publish-init --skill-dir <path> --brief (Phase A discovery)
3. Confirm with user: title, description, pricing model
4. Write selections JSON → submit with --selections-file
5. User → web page: confirm file contents, set pricing, upload logo,
   paste description, pick category/tags
6. reconcile (get_latest_version_raw to confirm agentType)
7. publish-configure (no deep scan for 🟢, deep scan for 🟡)
8. User → credential page: confirm/configure env vars
9. reconcile → publish-ship
10. User → final page: submit for review
11. Next agent → start from step 2 (sequential, not parallel)
```

## Credential Pitfall: MCP Env Block Keys

The publisher's rule scan does NOT detect keys inside `mcp_servers.<name>.env`
blocks in config.yaml. They pass through to staging as plaintext. If they must
be hosted, manually flag them in the deep scan findings. If they must NOT be
exposed, edit the staged `config.yaml` before publish-configure.

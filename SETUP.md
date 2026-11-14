# Hermes Workflow — Full Setup Guide

> **Source of truth:** this repository publishes portable templates and workflow guidance. Your installed Hermes profile, `hermes mcp list`, `hermes config check`, and live runtime probes determine what is actually enabled and working.

> **10 steps** to get a configured Hermes workflow running. Optional provider and MCP steps are conditional.

---

> **Model choice: `config.yaml` is truth** — set your primary route in `model.default` and `model.provider`. This guide does not assume a specific vendor, model, quota, or billing plan. Verify the exact route with a fresh `hermes chat` probe. See Step 9.

---

## Step 1: Install Hermes Agent

```bash
# macOS/Linux
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | sh

# Windows PowerShell
irm https://hermes-agent.nousresearch.com/install.ps1 | iex

# Or via pip
pip install hermes-agent
```

Verify: `hermes --version`

---

## Step 2: Clone This Repo

```bash
git clone https://github.com/AttilaHuns288452/hermes-workflow.git
cd hermes-workflow
```

---

## Step 3: Configure Hermes

Do not overwrite an existing profile. Start from a copy or merge the portable
sections into your current config:

```bash
cp config.yaml.template /tmp/hermes-workflow-config.yaml
# Add HERMES_WORKFLOW_ROOT to the file returned by: hermes config env-path
hermes config check
```

The template uses `${ENV_VAR}` references and leaves the model/provider pair as
placeholders. Enable only MCP servers you have installed and authenticated. A
successful YAML parse does not prove a provider or server is reachable.

---

## Step 4: Configure Environment Variables

Run `hermes config env-path` to locate the active profile's environment file. Add only the variables required by the provider and MCP servers you enable. Do not overwrite an existing environment file or commit credentials; `.env.example` is a placeholder reference.

---

## Step 5: Install Optional Tools

The template's MCP examples are disabled by default. Install a tool only if you intend to enable its matching server; for example, CodeGraph is needed only for `mcp_servers.codegraph`:

```bash
npm install -g @colbymchenry/codegraph
codegraph --version
```

---

## Step 6: Optional Provider

This step is optional and provider-specific. The project template does not include third-party proxy URLs, model counts, or bootstrap credentials. If you choose a local or hosted OpenAI-compatible proxy, follow its current upstream documentation, configure its provider/model pair using the installed Hermes version, and store credentials in the active profile's environment file returned by `hermes config env-path` or in Hermes auth. Do not reuse published default credentials or expose development-only ports to untrusted networks.

---

## Step 7: Load the Skills

Do **not** copy skills into `~/.hermes/skills/` — point Hermes at the repo via `external_dirs` so skills stay synced with `git pull`:

```yaml
# ~/.hermes/config.yaml
skills:
  external_dirs:
    - /path/to/hermes-workflow/skills
```

Then reload and verify:

```bash
hermes -z "List five skills you can use from the hermes-workflow catalog"
```

> The repository carries a large SKILL.md library spanning many categories: the `/decide` routing brain, core identity guardrail, token-saver probe chain, LLMQuant finance skills, OpenDesign systems, creative/media/research workflows, and vendored upstream collections (claude-seo, superpowers, agent-skills).

---

## Step 8: Optional Obsidian Vault

Create or select a vault only if you intend to use the on-demand Obsidian skills. Hermes and this workflow repository work without one; follow Obsidian's current instructions for choosing a vault location.

---

## Step 9: Verify the Configured Route

The live config, not this document, decides the model chain. Verify the exact primary route and fallback behavior from a fresh process:

```bash
hermes config check
hermes config get model.default
hermes config get model.provider
hermes config get fallback_providers
hermes chat -Q -q "Reply with exactly: ROUTE_OK"
```

A successful chat proves the primary path can answer. It does not prove every fallback provider is available. Probe fallback pairs separately before relying on them, and never copy a model ID from this guide into production config without checking the provider's current catalog.

---

## Step 10: Test the Pipeline

After the route check succeeds, run a couple of real prompts through the installed workflow:

```bash
hermes -z "What does the decide skill do?"
hermes -z "Summarize this repo structure"
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Invalid API key" from selected provider | Check the configured key environment variable and provider base URL without printing the key. |
| No model available | Verify the configured provider/model pair and that the provider process is reachable. |
| Local provider UI won't load | Check the upstream service's current port, bind address, and logs. |

## Related Docs

- [`config.yaml.template`](config.yaml.template)
- [`.env.example`](.env.example)
- [`META_PROMPT.md`](META_PROMPT.md)
- [`SKILLS_CATALOG.md`](SKILLS_CATALOG.md)
- [`INTEGRATION.md`](INTEGRATION.md)
- [`SECURITY.md`](SECURITY.md)

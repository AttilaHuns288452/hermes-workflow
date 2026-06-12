# SETUP — Replicate the Hermes Workflow Stack

Step-by-step instructions to install and configure everything described in this repo.

---

## Prerequisites

- **OS:** Windows 10+ / macOS / Linux
- **Git:** `git --version` (must be 2.30+)
- **Node.js:** `node --version` (v18+ recommended)
- **Python:** `python3 --version` (3.10+)
- **uv:** `uv --version` (install from https://docs.astral.sh/uv/)

---

## Step 1: Install Hermes Agent

```bash
# macOS / Linux
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | sh

# Windows (PowerShell)
irm https://hermes-agent.nousresearch.com/install.ps1 | iex

# Or install via pip
pip install hermes-agent
```

**Verify:**
```bash
hermes --version
hermes status
```

**Set up the default profile:**
```bash
hermes setup
hermes setup tools  # configure web browser, MCP servers, image gen, etc.
```

---

## Step 2: Clone This Repo

```bash
git clone https://github.com/AttilaHuns288452/hermes-workflow.git
cd hermes-workflow
```

---

## Step 3: Install Skills

The skills in this repo need to be loaded into your Hermes Agent profile.

### Manual Installation

```bash
# Copy skills to your Hermes skills directory
# On macOS / Linux:
mkdir -p ~/.hermes/skills/workflow
cp skills/*.md ~/.hermes/skills/workflow/

# On Windows (Git Bash / MSYS):
mkdir -p ~/.hermes/skills/workflow
cp skills/*.md ~/AppData/Local/hermes/skills/workflow/
```

### Verification

```bash
# List installed skills
hermes skills list

# You should see:
# - workflow/decide
# - workflow/core-identity-guardrail
# - workflow/token-saver
# - workflow/model-router
# - workflow/obsidian-docs
```

### Configure the Decide Skill as the Router

In your `~/.hermes/config.yaml`, set `/decide` as the routing brain:

```yaml
# ~/.hermes/config.yaml
agent:
  routing: always
  default_skill: decide
  skills_path: ~/.hermes/skills

skills:
  workflow/decide:
    enabled: true
    priority: 1
  workflow/core-identity-guardrail:
    enabled: true
    priority: 2
  workflow/token-saver:
    enabled: true
    priority: 3
  workflow/model-router:
    enabled: true
    priority: 4
  workflow/obsidian-docs:
    enabled: true
    priority: 5
```

---

## Step 4: Install Graphify (Code Knowledge Graph)

Graphify builds an AST-based knowledge graph of your codebase. Used by the Token Saver probe chain.

```bash
# Install via uv (recommended)
uv tool install graphifyy

# Or via pip
pip install graphifyy

# Install as a Hermes skill (enables /graphify command)
graphify hermes install
```

**Verify:**
```bash
graphify --version
# Should show v0.8.x or later
```

**Build a code graph for a project:**
```bash
cd /path/to/your-project
graphify update .
```

**Run the benchmark:**
```bash
graphify benchmark
# Expected output: ~56.2× token reduction
```

---

## Step 5: Install CodeGraph (MCP Code Knowledge Graph)

CodeGraph provides a live MCP server for symbol search, caller tracing, and impact analysis. Used by the Token Saver probe chain (Layer 4-7).

```bash
# Install via npm
npm install -g @colbymchenry/codegraph@0.9.9

# Or use the install script:
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh

# Windows (PowerShell)
irm https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.ps1 | iex
```

**Verify:**
```bash
codegraph --version
# Should show v0.9.9
```

**Initialize CodeGraph for a project:**
```bash
cd /path/to/your-project
codegraph init -i
```

**Register CodeGraph MCP server in Hermes config:**
```yaml
# ~/.hermes/config.yaml
mcp_servers:
  codegraph:
    enabled: true
    command: npx
    args: ["-y", "@colbymchenry/codegraph", "serve"]
    env:
      CODEGRAPH_WATCH: "true"
```

**Verify MCP is working:**
```bash
codegraph query "main"
# Should return symbol locations
```

---

## Step 6: Install OpenCode (Free Model Layer 1)

OpenCode provides bundled free models (Big Pickle, MiniMax M2.5 Free).

```bash
# macOS / Linux
curl -fsSL https://opencode.ai/install.sh | sh

# Windows
# Download from https://github.com/opencode-ai/opencode/releases

# Or via npm
npm install -g opencode
```

**Note:** OpenCode has been archived and continued as [Crush](https://github.com/charmbracelet/crush). The latest `opencode` release (v0.0.55) still works for the Zen free tier.

**Verify:**
```bash
opencode --version
```

**Configure for free models:**
```json
// ~/.opencode.json
{
  "provider": "opencode-zen",
  "model": "big-pickle",
  "autoCompact": true
}
```

---

## Step 7: Install FreeLLMAPI (Free Model Layer 3)

FreeLLMAPI proxies 110+ free models from 16 providers behind a single `/v1` endpoint.

```bash
git clone https://github.com/tashfeenahmed/freellmapi.git
cd freellmapi
pip install -r requirements.txt
```

**Run the proxy:**
```bash
python main.py
# Starts on http://localhost:3001
```

**Register as a Custom Hermes Provider:**
```yaml
# ~/.hermes/config.yaml
custom_providers:
  freellmapi:
    type: openai
    api_base: http://localhost:3001/v1
    api_key: none
    default_model: auto
```

**Verify:**
```bash
curl -s http://localhost:3001/v1/models | python3 -c "import sys,json; print(len(json.load(sys.stdin)['data']), 'models')"
# Expected: 110+ models
```

---

## Step 8: Install Obsidian (Documentation Vault)

```bash
# Download from https://obsidian.md/download
# No CLI install — use the desktop app

# Set up your vault
# 1. Open Obsidian
# 2. "Open folder as vault" → choose ~/Documents/Obsidian Vault
# 3. Install the knowledge graph plugin (Community Plugins → "Obsidian Knowledge Graph")
```

**Configure the vault path in Hermes:**
```yaml
# ~/.hermes/config.yaml
obsidian:
  vault_path: ~/Documents/Obsidian Vault
```

---

## Step 9: Configure MCP Servers

Beyond CodeGraph, these MCP servers are useful:

### Graphify MCP
```yaml
# ~/.hermes/config.yaml
mcp_servers:
  graphify:
    enabled: true
    command: npx
    args: ["-y", "graphifyy", "mcp"]
```

### FreeLLMAPI MCP (for model queries)
```yaml
# ~/.hermes/config.yaml
mcp_servers:
  freellmapi:
    enabled: true
    type: openai
    base_url: http://localhost:3001/v1
```

---

## Step 10: Verify the Pipeline

### Run the Decide Skill Check

```bash
# Ask Hermes to route a simple query
hermes run "What does the decide skill do?"

# Expected: /decide should activate, run 5-step protocol,
# select the decide skill, and explain its role
```

### Run the Token Saver Probe Test

```bash
# Initialize Graphify and CodeGraph for a test project
mkdir -p /tmp/test-graph
cd /tmp/test-graph
echo 'def hello(): print("hello world")' > test.py

# Build knowledge graphs
graphify update .
codegraph init -i

# Now ask a code question — the token saver should probe
hermes run "How does the hello function work in /tmp/test-graph?"
```

### Run the Model Router Test

```bash
# Ask a simple question — it should use Layer 1 (OpenCode free) or Layer 2 (Freebuff)
hermes run "What is 2+2?" --debug

# Check debug output for model layer used
```

### Run the Full Pipeline

```bash
# This should trigger all 9 pipeline steps:
hermes run "Create a simple Node.js CLI tool that greets the user by name"
```

Expected execution:
1. ✅ session_memory — pulls context
2. 🛡️ Core Identity Guardrail — safety check
3. /decide — routes to coding skill
4. ⚡ Token Saver — probes Graphify/CodeGraph before reading files
5. 🧬 Graphify + CodeGraph — provides code context
6. 🎯 Domain Skills — creates the CLI tool
7. 🤖 Model Routing — uses OpenCode/Freebuff default
8. 📝 Obsidian Docs — creates ATM-Machine quality note
9. 🕸️ KG Refresh — updates the galaxy graph

---

## Optional: Galaxy Knowledge Graph

To set up the interactive galaxy-style knowledge graph visualization:

```python
# render_galaxy_kg.py — place in your Obsidian vault path
import json

# Dependencies: pip install pyvis
# Run after every Obsidian vault update

# 1. Scan the vault into a JSON graph
# (see scan_vault.py in the obsidian-knowledge-graph skill)

# 2. Render an interactive HTML visualization
# Nodes are vault notes, edges are wikilinks
# Uses force-directed layout + dark theme
```

The galaxy KG requires:
- Obsidian vault with wikilinks between notes
- `scan_vault.py` to extract the graph
- `render_galaxy_kg.py` to generate the HTML visualization

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `graphify: command not found` | Run `uv tool install graphifyy` or `pip install graphifyy`. The PyPI package is `graphifyy` (double y). |
| `codegraph: command not found` | Run `npm install -g @colbymchenry/codegraph` or use the install script from the repo. |
| Hermes can't find skills | Check skills path in `~/.hermes/config.yaml`. Skills must be `.md` files with valid frontmatter. |
| MCP server won't start | Check port conflicts. CodeGraph uses port 3100. FreeLLMAPI uses 3000-3001. |
| OpenCode free tier not working | Try `opencode --version`. If missing, the CLI may not be installed correctly. The Zen tier is bundled. |
| FreeLLMAPI refuses connection | Make sure the proxy is running (`python main.py`). Check that port 3001 isn't blocked by a firewall. |
| Obsidian vault not scanning | Verify `scan_vault.py` finds `.md` files. The vault must exist at the configured path. |
| Token Saver not activating | Ensure `/decide` is the default routing skill. The Token Saver is a sub-skill of the decide pipeline. |
| KG refresh failing | Check `scan_vault.py` and `render_galaxy_kg.py` are in the vault path. Verify Python dependencies (pyvis, etc.). |
| Model router always hits paid layer | Check each free layer independently (OpenCode CLI, FreeLLMAPI endpoint, OpenRouter API). If one is down, the router falls through. |

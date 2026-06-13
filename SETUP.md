# Hermes Workflow — Full Setup Guide

> **10 steps** to get the complete free-model AI agent pipeline running.

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

```bash
cp config.yaml.template ~/.hermes/config.yaml
# Edit ~/.hermes/config.yaml — replace YOUR_USERNAME and paths everywhere
```

Key things to change:
- `C:\Users\YOUR_USERNAME\Documents\Projects` → your project root
- `C:\Users\YOUR_USERNAME\AppData\Roaming\npm` → your npm bin path
- `C:\Users\YOUR_USERNAME\.local\bin` → your local bin path

---

## Step 4: Set Environment Variables

```bash
cp .env.example .env
# Edit .env — fill in your API keys and paths
source .env
```

---

## Step 5: Install Core Tools

| Tool | Purpose | Install Command |
|------|---------|-----------------|
| **OpenCode** | Free Model Layer 1 | `npm install -g opencode` |
| **Graphify** | Code Knowledge Graph | `uv tool install graphifyy` |
| **CodeGraph** | Live MCP Code Index | `npm install -g @colbymchenry/codegraph` |
| **FreeLLMAPI** | Free Model Layer 3 | (see Step 6) |

```bash
# Verify
hermes --version && codegraph --version && graphify --version
```

---

## Step 6: Install & Configure FreeLLMAPI

FreeLLMAPI aggregates **107 free models** from 16 providers behind one endpoint.

### 6a. Clone & Install

```bash
git clone https://github.com/tashfeenahmed/freellmapi.git ~/Documents/Projects/freellmapi
cd ~/Documents/Projects/freellmapi
npm install
```

### 6b. Start Both Services

```bash
npm run dev
# Starts: API on :3001, Dashboard on :5173
```

### 6c. Create Admin Account

1. Open **http://localhost:5173**
2. Click **Sign Up** (first signup = admin)
3. Default: `admin@freellmapi.local` / `freellmapi-admin`
4. Log in

### 6d. Add Provider API Keys

1. Go to **Keys** page in dashboard
2. Add keys: Google AI Studio, Groq, Together AI, DeepInfra, Cerebras, etc.
3. Providers appear as model sources automatically

### 6e. Get Your Unified API Key

1. Go to **Settings** page → copy **Unified API Key** (`freellmapi-<hex>`)
2. This single key authenticates everything

### 6f. Wire Into Hermes

```bash
# Option A: hermes auth
hermes auth add freellmapi --type api-key --api-key "your-unified-key-here"
```

```bash
# Option B: config.yaml
# custom_providers:
#   freellmapi:
#     type: openai
#     api_base: http://localhost:3001/v1
#     api_key: "your-unified-key-here"
#     default_model: auto
```

```bash
# Option C: .env
# FREELMAPI_API_KEY="your-unified-key-here"
```

### 6g. Verify

```bash
curl -s -H "Authorization: Bearer $FREELMAPI_API_KEY" http://localhost:3001/v1/models | \
  python -c "import sys,json; d=json.load(sys.stdin); print(f'{len([m for m in d[\"data\"] if m.get(\"available\")])} available / {len(d[\"data\"])} total')"
```

---

## Step 7: Install the Skills

```bash
for dir in ./skills/*/; do hermes skills install "$dir"; done
```

---

## Step 8: Set Up Obsidian Vault

```bash
mkdir -p ~/Documents/Obsidian\ Vault
```

---

## Step 9: Test the Pipeline

```bash
hermes run "What does the decide skill do?"
hermes run "Summarize this repo structure"
```

---

## Step 10: Verify the Model Chain

| Layer | Provider | Models |
|-------|----------|--------|
| 1 | OpenCode (Zen) | Bundled free models |
| 2 | Freebuff API | Kimi K2.6, MiniMax M3, MiMo 2.5 |
| 3 | **FreeLLMAPI** (:3001) | 107 models from 16 providers |
| 4 | OpenRouter :free | 29+ free models |
| 5 | Paid BYOK | Last resort |

```
hermes run "What model layer are you using?"
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Invalid API key" from FreeLLMAPI | Check `.env` for duplicate `FREELMAPI_API_KEY` lines. Shell uses LAST definition. |
| 0 available models | No provider keys added. Open `:5173` → Keys → add at least one. |
| Dashboard won't load | Ensure `npm run dev` is running. Server may have crashed. |
| `api_key: none` in template | **Replace it** with your real unified API key from Settings page. |
| Port 3001 in use | `kill $(lsof -ti:3001)` or change port. |

## Related Docs

- [`config.yaml.template`](config.yaml.template)
- [`.env.example`](.env.example)
- [`META_PROMPT.md`](META_PROMPT.md)
- [`SKILLS_CATALOG.md`](SKILLS_CATALOG.md)
- [`INTEGRATION.md`](INTEGRATION.md)
- [`SECURITY.md`](SECURITY.md)

# FreeLLMAPI Setup Reference

## Quick Start (Docker - Recommended)

## ⚠️ Security: Persistent Credential Leaks

FreeLLMAPI has **two recurring leak vectors** that every setup session should fix immediately:

### 1. `freellmapi_key.txt` — Plaintext Key File
The `get_key.py` utility writes the unified API key to `freellmapi_key.txt` in the project root. This file is **NOT in `.gitignore`** by default, making it a direct git leak hazard.

**Fix** (run after first key retrieval):
```bash
echo "freellmapi_key.txt" >> .gitignore
rm freellmapi_key.txt
```

### 2. `get_key.py` — Hardcoded Session Token
The `get_key.py` script has a dashboard session token hardcoded as a string literal (e.g. `token = "freellmapi_unified_api_key_here"`). If this script is committed or shared, anyone with the token can access the dashboard API.

**Fix**: Replace the hardcoded token with an environment variable:
```python
import os
token = os.environ["DASHBOARD_TOKEN"]  # Never hardcode
```
Then add `DASHBOARD_TOKEN=` to `.env` (and `.env` is already git-ignored).

### 3. Verification
```bash
# Confirm keyfile is gone and git-ignored
ls freellmapi_key.txt 2>/dev/null && echo "LEAKS STILL PRESENT" || echo "Keyfile removed"
git check-ignore freellmapi_key.txt && echo "Git-ignored" || echo "NOT git-ignored — add to .gitignore now"
```
```bash
curl -fsSL https://freellmapi.co/install.sh | bash
```
- Sets up `~/freellmapi`, generates encryption key, pulls image, starts container
- Opens on `http://localhost:3001` (bound to `127.0.0.1` by default)
- Dashboard at `http://localhost:5173`

## Manual Build from Source (This Session's Path)
```bash
# 1. Clone
git clone https://github.com/tashfeenahmed/freellmapi.git
cd freellmapi

# 2. Install dependencies
npm install  # 745 packages, ~5 min

# 3. Generate encryption key
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"

# 4. Create .env
cat > .env << 'EOF'
ENCRYPTION_KEY=<generated-key>
PORT=3001
HOST_BIND=127.0.0.1
EOF

# 5. Build server
npm run build:server  # compiles TypeScript to dist/

# 6. Start server
cd server && npm run start  # runs node dist/index.js
# Or background:
nohup npm run start > server.log 2>&1 &
```

## Dashboard Authentication (First Run)
```bash
# 1. Open http://localhost:5173
# 2. Sign up with email/password (creates first admin user)
# 3. Login to access dashboard

# API: POST /api/auth/setup with {"email":"...","password":"..."}
# Returns session token for subsequent /api/* calls
```

## Get Unified API Key (for Hermes/Clients)
```bash
# After login, get token from /api/auth/setup or /api/auth/login
TOKEN=<session-token>

curl -H "Authorization: Bearer $TOKEN" http://localhost:3001/api/settings/api-key
# Returns: {"apiKey": "freellmapi-<hex>"}
```

## Add Upstream Provider Keys (Required for Models to Work)
All 107 models show `"available": false, "unavailable_reason": "no_key"` until you add keys:

1. Open dashboard at `http://localhost:5173`
2. Go to **API Keys** page
3. Add keys for providers you want:
   - **OpenRouter** (covers 21 free models + many paid)
   - **Groq** (Llama 3.3, GPT-OSS, Qwen3, Compound)
   - **NVIDIA** (Nemotron, Llama, Mistral, GLM)
   - **Google** (Gemini 2.5/3.x)
   - **Mistral** (Large 3, Medium 3.5, Codestral, Devstral)
   - **Cloudflare** (Kimi K2.6, GLM, GPT-OSS, Llama 4)
   - **Cerebras** (Qwen3 235B, Llama 3.1 8B)
   - **HuggingFace** (Router to DeepSeek V4, Kimi, Qwen3)
   - **GitHub Models** (GPT-4.1, GPT-4o)
   - **Ollama Cloud** (GLM-4.7, Kimi K2, gpt-oss, Qwen3)
   - **Kilo Gateway** (free routes, anonymous OK)
   - **Pollinations** (GPT-OSS 20B, anonymous OK)
   - **LLM7** (GPT-OSS, Llama 3.1, GLM, anonymous)
   - **OVH AI Endpoints** (Qwen3.5, GPT-OSS, Llama)
   - **Cohere** (Command R+, Command-A – **avoid**, forbids personal use)
   - **Z.ai/GLM** (GLM-4.5, GLM-4.7 Flash – new entity, anti-redirect clause)

4. After adding keys, models for that provider become `"available": true`

## Hermes Integration

### Current Working Config (June 2026+)
FreeLLMAPI is configured as a **custom provider** — NOT a named provider section:

```bash
# Set provider type and endpoint
hermes config set model.provider custom
hermes config set model.base_url http://localhost:3001/v1
hermes config set model.default auto

# Add auth credential (this creates custom:freellmapi in Hermes auth)
hermes auth add freellmapi --type api-key --api-key freellmapi-<hex> --label "FreeLLMAPI Key"

# Verify
hermes auth list
# Should show: custom:freellmapi with your label
hermes status
# Should show: Provider — Custom endpoint, Model — auto
```

Note: The config.yaml itself only stores `mcp_servers:` by default. `hermes config set` stores model provider settings in Hermes state, not in config.yaml. This is by design — the runtime state survives restarts.

### Legacy Config (Will NOT Work — providers section not supported in current config)
```yaml
# DO NOT USE — there is no `providers:` section in config.yaml
# providers:
#   freellmapi:
#     base_url: http://localhost:3001/v1
#     key_env: FREELMAPI_API_KEY
```

### .env Setup
```bash
# ~/.hermes/.env — MUST have exactly ONE FREELMAPI_API_KEY line
FREELMAPI_API_KEY=freellmapi-<hex>

# CRITICAL — Check for duplicates:
od -A x -t c ~/.hermes/.env | grep -c "FREELMAPI"
# Must return 1. If 2+, remove stale duplicates.
```

## Testing
```bash
# List models (requires valid unified API key)
curl -H "Authorization: Bearer freellmapi-<hex>" http://localhost:3001/v1/models

# Test chat completion
curl -X POST http://localhost:3001/v1/chat/completions \
  -H "Authorization: Bearer freellmapi-<hex>" \
  -H "Content-Type: application/json" \
  -d '{"model":"auto","messages":[{"role":"user","content":"Hello"}]}'

# Via Hermes
hermes chat -q "Test via FreeLLMAPI"
```

## Troubleshooting

### "Invalid API key" on /v1/models
**3‑point diagnosis chain:**

1. **CHECK SERVER** — Is FreeLLMAPI server actually running?
   ```bash
   curl -s http://localhost:3001/v1/models
   # Empty response = server down. Restart: cd ~/Documents/Projects/free-llm-api && npm run build:server && npm run dev
   # "Invalid API key" = server IS running, auth error
   ```

2. **CHECK .ENV** — ~/.hermes/.env must have exactly ONE `FREELMAPI_API_KEY=` line.
   ```bash
   od -A x -t c ~/.hermes/.env | grep FREELMAPI
   # If 2 lines shown, the second (stale) key overwrites the first.
   # Fix: python -c "open(..., 'w').write(...)" to remove the duplicate.
   ```
   **Root cause pattern**: Regenerating the unified API key in the dashboard, then *appending* the new key to .env instead of *replacing* the old one. The stale key sits on line 2 and wins on load.

3. **CHECK AUTH CREDENTIAL** — `custom:freellmapi` in Hermes auth may have the old key.
   ```bash
   hermes auth remove custom:freellmapi 1        # Remove stale credential
   hermes auth add freellmapi --type api-key \    # Re-add with current key
     --api-key freellmapi-<hex> --label "FreeLLMAPI Key"
   ```

4. **CHECK CONFIG** — model.provider must be `custom`, not a named provider.
   ```bash
   hermes status
   # Should show: Provider — Custom endpoint, Model — auto
   # If it shows anything else: hermes config set model.provider custom
   ```

**After fixing any of the above → start a NEW Hermes session** (`/new` or exit/relaunch). Env vars and config snapshots are loaded at startup and NOT refreshed mid-session.

### "All models exhausted" (429)
- No upstream provider keys added for the requested model
- Add keys via dashboard → API Keys page
- Check provider status: healthy / rate_limited / invalid / error

### Server won't start
- Check `ENCRYPTION_KEY` in .env (must be 64 hex chars)
- Port 3001 free? `netstat -an | findstr 3001`
- Node version 20+ required
- `npm run build:server` must succeed first (compiles TypeScript → dist/)

### Dashboard not accessible
- Server runs on 3001, dashboard served by Express on same port at `/` (or 5173 in dev mode)
- In production build, dashboard is served statically from server
- Dev mode: `npm run dev` runs Vite on 5173 + server on 3001
- Login credentials: `admin@freellmapi.local` / `freellmapi-admin` (if no other admin exists, first signup creates the admin)

## Key Files
| File | Purpose |
|------|---------|
| `freellmapi/.env` | Encryption key, port, host bind |
| `freellmapi/server/data/freeapi.db` | SQLite DB (keys, sessions, settings) |
| `freellmapi/server/dist/index.js` | Compiled server entry point |
| `freellmapi/client/dist/` | Built dashboard assets (served by Express) |

## Model Catalog (107 total — 84 available with provider keys)
Run `curl -H "Authorization: Bearer <key>" http://localhost:3001/v1/models | jq '.data[] | select(.available)'` to see currently available models after adding upstream keys.

## Session Notes (June 12, 2026)
- Built from source on Windows (Node 22.14, npm 10.9.2)
- No Docker available, used `npm run build:server` + `npm run start`
- Dashboard auth: created test@test.com / password123
- Got unified key: `[REDACTED]`
- Added to Hermes via `hermes auth add freellmapi --type api-key --api-key <key> --label "FreeLLMAPI Key"`
- Verified: `hermes config` shows provider=freellmapi, model=auto
- All models show "no_key" - need upstream keys added via dashboard

## Session Notes (June 13, 2026 — Third Session: Dashboard Keys Already Stored, Env Fix)

- **Project path**: `~/Documents/Projects/free-llm-api`
- **Server status**: ✅ Running on port 3001 (Express) + port 5173 (Vite dashboard)
- **Dashboard login**: `admin@freellmapi.local` / `freellmapi-admin`
- **Unified API key**: `[REDACTED]`
- **Provider keys stored**: 13 (google, groq, openrouter, huggingface, opencode, github, cerebras, nvidia, mistral, cohere, zhipu, ollama, llm7 — all healthy)
- **Models**: 107 total (84 available, 23 unavailable with no_key reason)
- **Available model highlights**: deepseek-v4-flash-free, nemotron-3-ultra-free, qwen3-coder:480b, gemini-3.5-flash, gpt-oss-120b:free, kimi-k2.6, glm-4.7, mistral-large-3, and 77 more

### Fix Applied: Duplicate FREELMAPI_API_KEY in .env
- **Root cause**: `~/.hermes/.env` had TWO `FREELMAPI_API_KEY=` lines. The second (stale) key overwrote the first (correct) one at shell load time, causing all Hermes requests to FreeLLMAPI to fail with "Invalid API key".
- **Fix**: Removed the duplicate line. The correct key (`[REDACTED]`) is now the only one.
- **Prevention**: When regenerating the unified API key via the dashboard, also update `~/.hermes/.env` to replace the old key (not append a second line).
- **Verification**: `od -A x -t c ~/.hermes/.env | grep FREELM` should show exactly one occurrence. Test with `curl -H "Authorization: Bearer $FREELMAPI_API_KEY" http://localhost:3001/v1/models | python -c "import sys,json; d=json.load(sys.stdin); print(f'{len([m for m in d[\"data\"] if m.get(\"available\")])} available / {len(d[\"data\"])} total')"`
- **Project path on Windows**: `$HOME/Documents/Projects/freellmapi`
- **Database location**: `server/data/freeapi.db` (SQLite)
- **API keys table**: Empty initially — 0 rows, must add via dashboard at `http://localhost:5173` → API Keys
- **Settings table**: Stores `unified_api_key`, `catalog_applied_version`, `catalog_applied_json`, `active_profile_id`, `embeddings_default_family`
- **Users table**: 1 user created (test@test.com)

### Windows-Specific Fixes
- **curl Authentication Failed**: Windows bash heredoc escaping broke `Authorization: Bearer *** headers
- **Fix**: Use Python `requests` library for authenticated API calls:
  ```python
  import requests
  token = "freellmapi_unified_api_key_here"  # from /api/auth/login
  headers = {'Authorization': f'Bearer {token}'}
  requests.get('http://localhost:3001/api/settings/api-key', headers=headers)
  ```
- **npm install**: Required before `npm run build:server` (installs 745 packages)
- **Server start**: `cd server && npm run start` runs `node dist/index.js` (compiled output)
- **Background process**: `npm run start` in background with `notify_on_complete=true` works; foreground blocks

### Verified Working Commands
```bash
# Build (Windows PowerShell / Git Bash)
cd $HOME/Documents/Projects/freellmapi
npm install
npm run build:server
cd server && npm run start

# Get unified key via Python (bypasses curl issues)
python -c "
import requests
login = requests.post('http://localhost:3001/api/auth/login', json={'email':'test@test.com','password':'password123'})
token = login.json()['token']
headers = {'Authorization': f'Bearer {token}'}
key_resp = requests.get('http://localhost:3001/api/settings/api-key', headers=headers)
print(key_resp.json()['apiKey'])
"

# Test models with unified key
python -c "
import requests
key = '[REDACTED]'
headers = {'Authorization': f'Bearer {key}'}
resp = requests.get('http://localhost:3001/v1/models', headers=headers)
data = resp.json()
for m in data['data']:
    print(f\"{m['id']}: available={m['available']}, reason={m.get('unavailable_reason')}\")
"
```

### Model Catalog Verified (June 2026)
- **110 models** from **16 providers** in catalog
- **All models show `available=false, reason=no_key`** until upstream keys added
- **Keyless providers** (work without keys): Kilo Gateway, Pollinations, LLM7 (anonymous)
- **Credit-based** (NVIDIA): NIM models require credits, depleting trial
- **Key format quirks**: Cloudflare uses `account_id:token` format


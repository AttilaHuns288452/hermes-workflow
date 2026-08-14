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
- **Server**: Opens on `http://localhost:3001` (bound to `127.0.0.1` by default)\n- **Dashboard** (compiled/static): Same port at `http://localhost:3001` — Express serves the built dashboard\n- **Dashboard** (dev mode): `http://localhost:5173` — Vite dev server, started via `npm run dev` (uses `concurrently`)

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
# 1. Open http://localhost:3001 (compiled) or http://localhost:5173 (dev mode)
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

1. Open dashboard at `http://localhost:3001` (compiled) or `http://localhost:5173` (dev mode)
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
**5‑point diagnosis chain + SQLite verification:**

1. **CHECK SERVER** — Is FreeLLMAPI server actually running?
   ```bash
   curl -s http://localhost:3001/v1/models
   # Empty response = server down. Restart: cd ~/Documents/Projects/freellmapi && npm run dev -w server
   # "Invalid API key" = server IS running, auth error
   ```

2. **READ THE ACTUAL KEY FROM SQLITE** — The unified API key lives in the server's SQLite database. This is the single source of truth:
   ```bash
   python -c "
   import sqlite3
   db = sqlite3.connect(r'C:\Users\YOUR_USERNAME\Documents\Projects\freellmapi\server\data\freeapi.db')
   row = db.execute(\"SELECT value FROM settings WHERE key='unified_api_key'\").fetchone()
   if row: print('DB key:', row[0])
   db.close()
   "
   ```
   Compare this key to what's in `~/.hermes/.env`. If they differ, the .env has a stale key that the server no longer accepts. Update .env to match the DB key.

3. **CHECK .ENV** — ~/.hermes/.env must have exactly ONE `FREELMAPI_API_KEY=` line.
   ```bash
   od -A x -t c ~/.hermes/.env | grep FREELMAPI
   # If 2 lines shown, the second (stale) key overwrites the first.
   # Fix: python -c "open(..., 'w').write(...)" to remove the duplicate.
   ```
   **Root cause patterns**:
   - **Duplicate lines**: Regenerating the unified API key in the dashboard, then *appending* the new key to .env instead of *replacing* the old one. The stale key sits on line 2 and wins on load.
   - **DB/Env mismatch**: The key was rotated on the server (via dashboard or direct DB update) but `~/.hermes/.env` was never updated. The env file still has the old key that the server no longer accepts.
   - **Cross-contamination**: An old `freellmapi_key.txt` from `get_key.py` was read, or a key from a different FreeLLMAPI instance was copied.

4. **CHECK AUTH CREDENTIAL** — `custom:freellmapi` in Hermes auth may have the old key.
   ```bash
   hermes auth remove custom:freellmapi 1        # Remove stale credential
   hermes auth add freellmapi --type api-key \    # Re-add with current key
     --api-key freellmapi-<hex> --label "FreeLLMAPI Key"
   ```

5. **CHECK CONFIG** — model.provider must be `custom`, not a named provider.
   ```bash
   hermes status
   # Should show: Provider — Custom endpoint, Model — auto
   # If it shows anything else: hermes config set model.provider custom
   ```

   Compare this key to what's in `~/.hermes/.env`. If they differ, **sync the outdated side**:

   - **If .env has the old key** (most common — server DB is the source of truth):  
     Update .env to match the DB key. Replace the `FREELMAPI_API_KEY=` line, don't append a second one.

   - **If the DB has the old key** (less common — .env was updated but server wasn't):  
     Update the SQLite DB to match .env:
     ```python
     import sqlite3
     db = sqlite3.connect(r'C:\Users\YOUR_USERNAME\Documents\Projects\freellmapi\server\data\freeapi.db')
     db.execute("UPDATE settings SET value = ? WHERE key = 'unified_api_key'", ('freellmapi-<key-from-env>',))
     db.commit()
     db.close()
     ```
     Then restart the FreeLLMAPI server (kill old node process, re-run `node dist/index.js` from the `server/` directory).

   **After syncing either direction** → start a **new Hermes session** (`/new` or exit/relaunch). Env vars and config snapshots are loaded at startup and NOT refreshed mid-session.

   **If the DB key itself doesn't work** when tested with `curl -H "Authorization: Bearer <key>" http://localhost:3001/v1/models`, the server process may have been started before the key was written, or it's using a different database file. Restart the server after confirming the DB key: kill the old node process, then `cd ~/Documents/Projects/freellmapi && npm run dev -w server`.

### Key Regeneration on DB Recreation

**FreeLLMAPI generates a new unified API key every time `initDb()` is called on a fresh database.** This happens when:
- The server was started for the first time after a clean clone
- The DB files (`freeapi.db`, `freeapi.db-wal`, `freeapi.db-shm`) were deleted and recreated

**Symptom**: Hermes `.env` has `FREELMAPI_API_KEY=freell...ex>` but the server returns `"Invalid API key"` for that key.

**Quickest sync path** (no SQLite required — get key via API):
```bash
# 1. Login to FreeLLMAPI dashboard (no API key needed for auth)
TOKEN=*** -s -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@freellmapi.local","password":"admin12345"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['token']))

# 2. Get the server's current unified API key
curl -s -H "Authorization: Bearer *** http://localhost:3001/api/settings/api-key
# → {"apiKey": "freellmapi-<new-hex>"}

# 3. Update Hermes .env with the new key (replace existing line, don't append another)
# Use Python to safely do the find-and-replace:
python -c "
with open(r'C:\Users\YOUR_USERNAME\AppData\Local\hermes\.env', 'r') as f:
    content = f.read()
lines = content.splitlines()
new_key = 'freellmapi-022a52d486a05c12c5029bdd6173f41282c6b2fe03b72b37'
for i, line in enumerate(lines):
    if 'FREELMAPI_API_KEY' in line:
        old = line.split('=', 1)[1] if '=' in line else ''
        lines[i] = f'FREELMAPI_API_KEY=***        break
content = '\n'.join(lines) + ('\n' if not content.endswith('\n') else '')
with open(r'C:\Users\YOUR_USERNAME\AppData\Local\hermes\.env', 'w') as f:
    f.write(content)
print('Updated .env')
"
```

**Alternative: Sync the DB key to match .env** (if .env was intentionally set to a specific key):
```python
import sqlite3
db = sqlite3.connect(r'C:\Users\YOUR_USERNAME\Documents\Projects\freellmapi\server\data\freeapi.db')
db.execute("UPDATE settings SET value = ? WHERE key = 'unified_api_key'",
           ('freellmapi-<key-from-env>',))
db.commit()
db.close()
```

Then restart the FreeLLMAPI server.

**After syncing either direction** → start a **new Hermes session** (`/new` or exit/relaunch). Env vars and config snapshots are loaded at startup and NOT refreshed mid-session.

### Server starts then crashes with `ReferenceError: db is not defined`

**Symptom**: Server outputs "Server running on http://[::]:3001", then immediately crashes with:
```
file:///.../server/dist/routes/session-memory.js:165
db.close();
^
ReferenceError: db is not defined
```

**Root cause**: The `session-memory.ts` route handler has corrupted `finally` blocks where the LLM generating the code wrote garbled text like `if (db if (db if (db.open) db.close();if (db.open) db.close(); ...` instead of `if (db?.open) db.close();`.

**Fix** (three affected `finally` blocks in `/sessions`, `/sessions/:id`, and `/stats`):
1. Replace every `if (db if (db if (db.open) ...` garbled block with `if (db?.open) db.close();`
2. Also check for `use-after-close` bugs — `db.close()` called BEFORE a subsequent DB query. Move all DB reads before `res.json()`, keep `db.close()` only in the `finally` block.
3. Rebuild: `cd freellmapi && npm run build:server`
4. Restart the server

**Prevention**: When generating or patching `session-memory.ts`, review every `finally` block for correctness. The garbled pattern (`if (db if (db if (db.open) ...`) is a known LLM code-generation artifact from repeated edit cycles.

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
- **Compiled mode** (default): Server runs on 3001, dashboard served by Express on the same port at `/`
- **Dev mode**: `npm run dev` runs Vite on 5173 + server on 3001 via `concurrently`
- **Workspace names**: backend = `server`, frontend = `client` (NOT `web` — `npm run dev -w web` fails with `No workspaces found`)
- To start individually: `npm run dev -w server` (API only) or `npm run dev -w client` (Vite frontend only, serves on 5173)
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

## Session Notes (June 26, 2026 — Fourth Session: Full Setup & Testing)

### Complete FreeLLMAPI Setup From Scratch

**Project path**: `C:\Users\YOUR_USERNAME\Documents\Projects\freellmapi`

**Server status**: ✅ Running on port 3001 (Express) — compiled mode serves dashboard at `/`

**Dashboard login**: `admin@freellmapi.local` / `admin12345`

**Unified API key**: `freellmapi-022a52d486a05c12c5029bdd6173f41282c6b2fe03b72b37`

**Provider keys stored**: 13 (healthy: google, groq, openrouter, huggingface, opencode, github, cerebras, nvidia, mistral, cohere, zhipu, ollama, llm7 — all "healthy")

**Keyless providers working without keys**:
| Provider | Model ID | Platform | Status |
|----------|----------|----------|--------|
| **Kilo** | `stepfun/step-3.7-flash:free` | kilo | ✅ Working |
| **Pollinations** | `openai-fast` | pollinations | ✅ Working |
| **OpenCode Zen** | `deepseek-v4-flash-free` | opencode | ⚠️ Falls back to OpenRouter |
| **OpenCode Zen** | `big-pickle` | opencode | ⚠️ Falls back to OpenRouter |
| **OpenCode Zen** | `mimo-v2.5-free` | opencode | ⚠️ Falls back to OpenRouter |

**Verified working curl commands:**
```bash
# Kilo - WORKING
curl -X POST -H "Authorization: Bearer *** \
  -H "Content-Type: application/json" \
  -d '{"model":"stepfun/step-3.7-flash:free","messages":[{"role":"user","content":"hello"}]}' \
  http://localhost:3001/v1/chat/completions

# Pollinations - WORKING  
curl -X POST -H "Authorization: Bearer *** \
  -H "Content-Type: application/json" \
  -d '{"model":"openai-fast","messages":[{"role":"user","content":"hello"}]}' \
  http://localhost:3001/v1/chat/completions
```

**OpenCode Zen fallback behavior:** These models appear "available" in `/v1/models` but internally route through OpenRouter. If no OpenRouter key is configured, they fail with:
```
Provider error (GPT-OSS 120B (free)): OpenRouter API error 401: Missing Authentication header
```

Fix: Add a valid OpenRouter key via `/api/keys`.

### Process Management Learnings

- **Node process lock on DB**: `rm freeapi.db*` fails with "Device or resource busy" if server is running
- **Fix**: Kill node process on port 3001 first: `netstat -ano | findstr :3001` → `taskkill /PID <pid> /F` (Windows) or `kill -9 <pid>` (Linux/macOS)
- **Verification**: `netstat -ano | findstr :3001` should return empty

### Password Reset Procedure

1. Stop FreeLLMAPI server
2. Delete `server/data/freeapi.db*` (all three files)
3. Restart server
4. POST to `/api/auth/setup` with new credentials
5. POST to `/api/auth/login` to get session token
6. Use session token to call `/api/keys` for adding provider keys

### Hermes Config Changes That Fixed Issues

```yaml
# Primary model provider
model:
  base_url: http://localhost:3001/v1
  default: auto
  provider: freellmapi

# Auxiliary compression (was opencode-zen, now freellmapi)
auxiliary:
  compression:
    provider: freellmapi
    model: auto
    base_url: ''
    api_key: ''
    timeout: 120
    extra_body: {}

# Disable failing MCP servers
mcp_servers:
  agentmemory:
    enabled: false
  llmquant-data:
    enabled: false
  vscode:
    enabled: false
```

### Gateway Disconnection Root Causes

1. **Compression model rate limits** - `opencode-zen`/`deepseek-v4-flash-free` hitting free quotas → context compression fails → agent loop blocks → WebSocket stalls → disconnect
2. **MCP server connection storms** - Multiple failing MCP servers (`agentmemory`, `llmquant-data`, `vscode`) retry repeatedly, consuming event loop
3. **Missing provider registration** - Config uses `opencode-zen` but gateway only knows `opencode`

### Session Token vs Unified API Key

Two different tokens exist:
- **Session token** (from `/api/auth/login`): Gates the admin dashboard (`/api/keys`, `/api/settings`)
- **Unified API key** (from `/api/settings/api-key` or settings DB): Gates the `/v1` proxy for app clients

Use the unified API key for `Authorization: Bearer ***` headers on `/v1/*` endpoints.

### Database Path Issues

When running from different directories, use absolute paths for better-sqlite3:
```bash
# From project root
node -e "const db = new Database('C:/Users/YOUR_USERNAME/Documents/Projects/freellmapi/server/data/freeapi.db'); ..."
```

### Verification Commands
```bash
# Check FreeLLMAPI health
curl http://localhost:3001/v1/models

# Check Hermes model config
hermes config

# Test chat
hermes chat -q "Hello from FreeLLMAPI"

# Full doctor check
hermes doctor

# Automated verification script
python scripts/verify-freellmapi.py --key freellmapi-022a52d486a05c12c5029bdd6173f41282c6b2fe03b72b37 --test-chat
```

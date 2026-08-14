# FreeLLMAPI Setup for Hermes Agent

## Overview
FreeLLMAPI is a self-hosted OpenAI-compatible proxy that aggregates free tiers from 16+ LLM providers behind a single `/v1` endpoint. It runs locally and provides ~1.7B tokens/month across providers like Google Gemini, Groq, Cerebras, OpenRouter, GitHub Models, and more.

## Prerequisites
- Node.js 20+
- npm
- Hermes Agent installed

## Installation & Setup

### 1. Clone and Build FreeLLMAPI
```bash
cd ~/Documents/Projects
git clone https://github.com/tashfeenahmed/freellmapi.git
cd freellmapi
npm install
npm run build:server
```

### 2. Configure Environment
Generate encryption key and create `.env`:
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
# Copy output to .env
```

```env
# freellmapi/.env
ENCRYPTION_KEY=<generated-key>
PORT=3001
HOST_BIND=127.0.0.1
```

### 3. Start the Server
```bash
# Terminal 1 - start server
cd ~/Documents/Projects/freellmapi/server
npm run start
# Server runs on http://localhost:3001
```

### 4. Initialize Dashboard & Get API Key
```bash
# Create first admin user (one-time setup)
curl -X POST http://localhost:3001/api/auth/setup \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com","password":"your-password"}'

# Login to get session token
curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com","password":"your-password"}'
# Returns: {"token": "...", "email": "..."}

# Get unified API key using session token
curl -H "Authorization: Bearer <session-token>" \
  http://localhost:3001/api/settings/api-key
# Returns: {"apiKey": "freellmapi-..."}
```

### 5. Configure Hermes
```bash
# Add provider config to Hermes
hermes config set providers.freellmapi.base_url http://localhost:3001/v1
hermes config set providers.freellmapi.key_env FREELMAPI_API_KEY
hermes config set providers.freellmapi.default_model auto
hermes config set providers.freellmapi.discover_models true

# Add API key to Hermes credentials
hermes auth add freellmapi --key <freellmapi-xxx>

# Switch model provider to freellmapi
hermes config set model.provider freellmapi
hermes config set model.default auto

# Verify
hermes doctor
hermes chat -q "Test FreeLLMAPI connection"
```

## Configuration in Hermes config.yaml
```yaml
model:
  provider: freellmapi
  default: auto

providers:
  freellmapi:
    base_url: http://localhost:3001/v1
    key_env: FREELMAPI_API_KEY
    default_model: auto
    discover_models: true
```

## Adding Provider API Keys in FreeLLMAPI Dashboard
Once the server is running, open http://localhost:5173 (if client built) or use the API to add keys for each provider you want to enable:
- Google (Gemini)
- Groq
- Cerebras
- OpenRouter
- GitHub Models
- Mistral
- And others...

## Troubleshooting

### "Invalid API key" error
- Verify the key in `~/.hermes/.env` matches exactly what FreeLLMAPI returned
- Ensure FreeLLMAPI server is running (`curl http://localhost:3001/v1/models`)
- Check that Hermes reads the .env correctly: `hermes config` should show the key

### Port conflicts
- Default ports: 3001 (API), 5173 (dashboard)
- Change PORT in .env if needed

### Model discovery not working
- Ensure `discover_models: true` in config
- Restart Hermes after config changes: `/reset` in CLI or restart gateway

### Gateway disconnections / WebSocket stalls
**Root causes discovered (June 2026):**
1. **Rate limits on compression model** - The `opencode-zen` provider used for `auxiliary.compression` hits free-tier rate limits, causing context compression to fail and blocking the agent loop
2. **Failing MCP servers** - `agentmemory`, `llmquant-data`, `vscode` MCP servers failing to connect caused repeated connection attempts that stalled the gateway

**Fixes applied:**
```yaml
# In ~/.hermes/config.yaml - switch compression to freellmapi
auxiliary:
  compression:
    provider: freellmapi
    model: auto
    # (removed opencode-zen/deepseek-v4-flash-free)

# Disable problematic MCP servers
mcp_servers:
  agentmemory:
    enabled: false  # disabled due to connection errors
  llmquant-data:
    enabled: false  # disabled due to connection errors
  vscode:
    enabled: false  # disabled due to connection errors
```

### Dashboard login issues
- Existing user `test@test.com` created during testing may have unknown password
- **Workaround:** Delete `server/data/freeapi.db` and re-run setup to create fresh credentials
- The `/api/auth/setup` endpoint only works once; subsequent attempts return `setup_complete` error

### Working Keyless Providers (No API Keys Required)
The following providers work without API keys after adding them via `/api/keys`:

| Provider | Models (Available) | Status |
|----------|-------------------|--------|
| **Kilo** | `stepfun/step-3.7-flash:free` | ✅ Working |
| **Pollinations** | `openai-fast` (GPT-OSS 20B) | ✅ Working |
| **OpenCode Zen** | `deepseek-v4-flash-free`, `big-pickle`, `mimo-v2.5-free` | ⚠️ Falls back to OpenRouter (needs OpenRouter key) |

**Tested working calls:**
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

### OpenCode Zen Fallback Behavior
OpenCode Zen models appear "available" but route through OpenRouter internally. If no OpenRouter key is configured, requests fail with:
```
Provider error (GPT-OSS 120B (free)): OpenRouter API error 401: Missing Authentication header
```

**Fix:** Add a valid OpenRouter key (`sk-or-...`) via `/api/keys` or dashboard.

### OpenRouter Key Setup (Verified Working June 2026)
The OpenRouter key from Hermes `.env` (`OPENROUTER_API_KEY=*** was successfully added to FreeLLMAPI:

```bash
# 1. Get session token
curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@freellmapi.local","password":"admin12345"}'
# Returns: {"token": "...", "email": "..."}

# 2. Delete existing placeholder key (if any)
curl -X DELETE -H "Authorization: Bearer *** \
  http://localhost:3001/api/keys/1

# 3. Add real OpenRouter key
curl -X POST -H "Authorization: Bearer *** \
  -H "Content-Type: application/json" \
  -d '{"platform":"openrouter","key":"sk-or-v1-...","label":"OpenRouter"}' \
  http://localhost:3001/api/keys

# 4. Also add OpenCode Zen key (from Hermes .env OPENCODE_ZEN_API_KEY)
curl -X POST -H "Authorization: Bearer *** \
  -H "Content-Type: application/json" \
  -d '{"platform":"opencode","key":"sk-T50...","label":"OpenCode Zen"}' \
  http://localhost:3001/api/keys

# 5. Verify keys show "unknown" status (health check runs every 5 min)
curl -H "Authorization: Bearer *** \
  http://localhost:3001/api/keys
```

**Note:** The key is stored encrypted in FreeLLMAPI's SQLite DB using AES-256-GCM with the `ENCRYPTION_KEY` from FreeLLMAPI's `.env` (not Hermes's .env). The encryption key in FreeLLMAPI's DB must match the one used to encrypt the keys.

### Database Path Issues
When running from different directories, use absolute paths for better-sqlite3:
```bash
# From project root
node -e "const db = new Database('C:/Users/YOUR_USERNAME/Documents/Projects/freellmapi/server/data/freeapi.db'); ..."
```

### Session Token vs Unified API Key
Two different tokens exist:
- **Session token** (from `/api/auth/login`): Gates the admin dashboard (`/api/keys`, `/api/settings`)
- **Unified API key** (from `/api/settings/api-key` or settings DB): Gates the `/v1` proxy for app clients

Use the unified API key for `Authorization: Bearer` headers on `/v1/*` endpoints.

### Encryption Key Mismatch (Critical)
**Issue discovered June 2026:** FreeLLMAPI encrypts API keys using the `ENCRYPTION_KEY` from its own `.env` file. If you delete and recreate the database, a new encryption key is generated. Keys encrypted with the old key become undecryptable.

**Symptoms:**
- Keys show in `/api/keys` but return "DECRYPT ERROR" when FreeLLMAPI tries to use them
- Health checks fail with "Unsupported state or unable to authenticate data"

**Fix:** Ensure FreeLLMAPI's `.env` has a stable `ENCRYPTION_KEY` that persists across restarts:
```bash
# Generate once and keep forever
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
# Add to freellmapi/.env
ENCRYPTION_KEY=<generated-key>
```

The key is also stored in the DB at `settings.encryption_key` as a fallback, but the `.env` takes precedence.

### OpenRouter "Missing Authentication Header" Bug (Known Issue June 2026)
**Symptom:** Valid OpenRouter key is stored in FreeLLMAPI and shows "healthy" status, but requests fail with:
```
Provider error (Model Name): OpenRouter API error 401: Missing Authentication header
```

**Root Cause:** FreeLLMAPI's OpenAICompatProvider is not correctly passing the Authorization header when proxying to OpenRouter. The key decrypts correctly (verified via direct DB read with ENCRYPTION_KEY), and direct calls to OpenRouter with the same key work fine. The bug is in FreeLLMAPI's proxy/router layer.

**Workarounds:**
1. Use keyless providers (Kilo, Pollinations) for immediate testing
2. Specify models explicitly rather than using `auto` routing
3. Check FreeLLMAPI logs for the actual upstream request headers

**Debugging steps:**
```bash
# Check if key decrypts correctly
node -e "
const Database = require('better-sqlite3');
const db = new Database('C:/Users/YOUR_USERNAME/Documents/Projects/freellmapi/server/data/freeapi.db');
const keys = db.prepare(\"SELECT platform, encrypted_key, iv, auth_tag FROM api_keys WHERE platform = 'openrouter'\").all();
const crypto = require('crypto');
const ENCRYPTION_KEY = Buffer.from(require('fs').readFileSync('C:/Users/YOUR_USERNAME/Documents/Projects/freellmapi/.env').toString().match(/ENCRYPTION_KEY=([a-f0-9]+)/)[1], 'hex');
const decipher = crypto.createDecipheriv('aes-256-gcm', ENCRYPTION_KEY, Buffer.from(keys[0].iv, 'hex'), {authTagLength: 16});
decipher.setAuthTag(Buffer.from(keys[0].auth_tag, 'hex'));
let dec = decipher.update(keys[0].encrypted_key, 'hex', 'utf8');
dec += decipher.final('utf8');
console.log('Decrypted key:', dec);
"

# Test key directly with OpenRouter
curl -H "Authorization: Bearer <decrypted-key>" https://openrouter.ai/api/v1/auth/key
```

**Status:** Under investigation - appears to be a bug in `server/src/providers/openai-compat.ts` authHeader() method or request routing.

### Session Learnings (June 26, 2026)

### Process Management
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

## Verification Commands
```bash
# Check FreeLLMAPI health
curl http://localhost:3001/v1/models

# Check Hermes model config
hermes config

# Test chat
hermes chat -q "Hello from FreeLLMAPI"

# Full doctor check
hermes doctor
```

## Verification Commands
```bash
# Check FreeLLMAPI health
curl http://localhost:3001/v1/models

# Check Hermes model config
hermes config

# Test chat
hermes chat -q "Hello from FreeLLMAPI"

# Full doctor check
hermes doctor
```

## Related Skills
- `hermes-agent` - Main Hermes configuration skill
- `decide` → Complementary Setup Routing → FreeLLMAPI section
- `workflow/free-ai-model-router` - Free model chain routing (OpenCode → Freebuff → FreeLLMAPI → OpenRouter → Paid)
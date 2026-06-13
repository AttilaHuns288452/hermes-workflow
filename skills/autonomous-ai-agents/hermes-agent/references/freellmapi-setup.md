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
# Add provider config to Hermes (if not already present)
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
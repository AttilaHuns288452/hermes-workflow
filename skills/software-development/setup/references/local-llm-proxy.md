# Local LLM API Proxy (Express + OpenRouter)

When a user asks for a "free LLM API" running locally but the repo they pointed at is actually a directory/catalog site (not an API server), build a lightweight Express proxy instead.

## When to use this pattern

- User wants an API endpoint they can call from the browser or curl
- The repo they provided turns out to be a static listing/catalog/directory site
- User explicitly wants "free" models (no credit card, generous rate limits)
- Node.js is available on the target machine

## Architecture

```
Browser / curl  ──POST──►  localhost:3001/api/chat  ──►  OpenRouter API
                              │                           (free models)
                              ├── /api/models
                              ├── /api/providers
                              └── /  (HTML chat UI)
```

The server is a single Express JS file with no build step — `node server.js` starts it immediately.

## Quick scaffold

```bash
mkdir -p ~/Documents/Projects/free-llm-api
cd ~/Documents/Projects/free-llm-api
npm init -y
npm install express cors
```

### Core server structure

```
free-llm-api/
├── package.json    # express, cors
└── server.js       # single-file server
```

### Key endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | HTML chat UI (model selector, prompt input, streaming toggle) |
| `/api/chat` | POST | OpenAI-compatible chat completions proxy |
| `/api/models` | GET | List available free models |
| `/api/providers` | GET | List free LLM providers from directory |

### `/api/chat` request format

```json
{
  "model": "meta-llama/llama-3.3-70b-instruct:free",
  "messages": [{ "role": "user", "content": "Hello!" }],
  "stream": false,
  "apiKey": "sk-or-v1-..."
}
```

The server passes `apiKey` directly to OpenRouter. If not provided, falls back to `OPENROUTER_API_KEY` environment variable.

## OpenRouter free models

The user needs a **free API key** from https://openrouter.ai/keys (no credit card, 50 requests/day).

Confirmed working OpenRouter `:free` models:
| Model ID | Notes |
|---|---|
| `meta-llama/llama-3.3-70b-instruct:free` | Good general purpose |
| `openai/gpt-oss-120b:free` | Strong for coding |
| `nex-agi/nex-n2-pro:free` | Reliable, consistent |
| `qwen/qwen3-235b-awai:free` | Large context, good reasoning |
| `minimax/minimax-m2-5-awake:free` | Fast responses |

> **Known limitation**: Many OpenRouter `:free` models fail with server errors. The ones above are the most reliable from experience. See also the `opencode/` provider which has a separate set of working free models.

## Streaming support

The server proxies SSE (Server-Sent Events) directly from OpenRouter to the client when `stream: true` is set. The HTML chat UI includes a "Stream" button that reads the response incrementally.

```javascript
// Client-side streaming
const res = await fetch('/api/chat', { /* ... stream: true */ });
const reader = res.body.getReader();
const decoder = new TextDecoder();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  // Parse "data: ..." lines
  const lines = decoder.decode(value).split('\n')
    .filter(l => l.startsWith('data: ') && l !== 'data: [DONE]');
  for (const line of lines) {
    const json = JSON.parse(line.slice(6));
    output += json.choices?.[0]?.delta?.content || '';
  }
}
```

## Pitfalls

- **OpenRouter requires a key** even for free models. The user must create one at openrouter.ai/keys. Build the endpoint to accept `apiKey` in the request body AND check `process.env.OPENROUTER_API_KEY` — don't hardcode.
- **CORS**: Set `cors()` middleware (all origins) since the user will call from browser UIs on different ports.
- **Empty process logs on Windows**: `node server.js` in background mode may show 0 output lines even when running. Verify with `netstat -ano | grep ':3001' | grep LISTEN` and a curl test instead.
- **Port conflicts**: Check port availability before starting (`netstat -ano | grep ':3001'`). Avoid port 3000 which Next.js defaults to.
- **Streaming on older browsers**: SSE works in all modern browsers. For very old clients, fall back to non-streaming.
- **Server lifecycle**: The dev server never exits on its own. Use `taskkill //F //PID <pid>` to stop it. On restarts, the old PID may linger and cause EADDRINUSE on the new attempt.

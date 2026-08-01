# FreeLLM API Extension Patterns

## Adding a New API Route (Server-Side)

1. Create a new Express router in `server/src/routes/<name>.ts`
   - Import `Router` from `express`, `z` from `zod` for validation
   - Export the router (e.g. `export const myRouter = Router();`)
   - Define routes using `router.get('/')`, `router.post('/')`, etc.

2. Register the router in `server/src/app.ts`:
   ```typescript
   import { myRouter } from './routes/<name>.js'; // compiled output is .js

   // Before the proxy catch-all, with or without auth:
   app.use('/api/<name>', requireAuth, myRouter);   // protected
   // or
   app.use('/api/<name>', myRouter);                 // public
   ```

3. Build: `npm run build:server` (compiles TypeScript → `server/dist/`)

## Adding a New Client Page (Frontend)

1. Create a React page in `client/src/pages/<Name>Page.tsx`
   - Follow existing patterns: `@tanstack/react-query` for data fetching, `lucide-react` icons, shadcn/ui components
   - Match the layout of `AnalyticsPage.tsx` or `SessionMemoryPage.tsx` (sidebar breadcrumbs, top bar, content area)

2. Register the page in `client/src/App.tsx`:
   - Import the page component
   - Add a nav link: `{ to: '/<route>', label: 'My Page' }`
   - Add a route: `<Route path="/<route>" element={<MyPage />} />`

3. Build: `npm run build -w client` (compiles TypeScript via Vite → `client/dist/`)

4. Restart both services (server serves the updated static dashboard)

## Provider Key Management

All upstream provider API keys are stored **encrypted** in the SQLite database (`server/data/freeapi.db` → `api_keys` table). Keys are managed via:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/keys` | GET | List all keys (masked) |
| `/api/keys` | POST | Add a new key `{platform, key?, label?}` |
| `/api/keys/custom` | POST | Add a custom OpenAI-compatible provider `{baseUrl, model, apiKey?}` |
| `/api/keys/:id` | PATCH | Toggle enabled or update label |
| `/api/keys/:id` | DELETE | Remove a key |
| `/api/keys/platform/:platform` | PATCH | Toggle all keys for a platform on/off |

### Supported Platforms

```
google, groq, cerebras, nvidia, mistral, openrouter, github, cohere,
cloudflare, zhipu, ollama, kilo, pollinations, llm7, huggingface,
opencode, ovh, custom
```

### Keyless Providers

Some platforms (kilo, pollinations, llm7) work without API keys — they use anonymous gateways. Adding them just registers a sentinel row so routing sees them as configured.

### Custom Providers

The `POST /api/keys/custom` endpoint registers an OpenAI-compatible endpoint with one or more models. Each unique `baseUrl` gets its own key row. Models are bound to the endpoint's `key_id` and registered in the `models` table. Re-submitting the same `baseUrl` updates its key/label; re-registering a model ID re-binds it.

## All Routes Require Auth (by Default)

Most `/api/*` routes are gated by `requireAuth` middleware (checks for a valid dashboard Bearer token). To bootstrap access:
1. Create admin via `POST /api/auth/setup` with `{email, password}`
2. Login via `POST /api/auth/login` with `{email, password}` → returns a token
3. Use token as `Authorization: Bearer <token>` for all subsequent /api/* calls

The proxy endpoint `/v1/chat/completions` uses the unified API key (stored in `settings` table as `unified_api_key`), not the dashboard auth token.

## Server Crash/Auto-Restart Pattern

The FreeLLM API server (started via `node server/dist/index.js`) may exit after ~10 minutes of inactivity. On Windows, a different Node.js process may pick up port 3001 after the original process exits, or the port may stay bound in TIME_WAIT. Always verify the actual process owning the port via `netstat -ano | grep :3001` and compare PIDs against what you started.

If port 3001 is open but the server returns stale/incomplete responses, the running process may be a stale instance. Kill all Node.js processes and restart cleanly.

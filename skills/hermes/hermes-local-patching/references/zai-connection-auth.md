# Connecting Hermes to z.ai / ZCode (auth contract, credentials, provider quirks)

Companion to `zai-glm-429-fix.md` (that one is the 429/fingerprint patch; this
one is how the endpoint authenticates and where live credentials live). Learned
2026-07-31 while live-testing `hermes -z ... -m glm-5.2 --provider zai`.

## Auth contract — the ZCode plan endpoint wants Bearer, not x-api-key

`https://zcode.z.ai/api/v1/zcode-plan/anthropic` (Anthropic wire, `builtin:zai-start-plan`):

| Header sent | Result |
|---|---|
| `x-api-key: <plan JWT>` | `401 {"error":{"message":"token expired or incorrect"}}` — looks like an expiry but is actually the WRONG header |
| `Authorization: Bearer <plan JWT>` | auth passes → next gate is the captcha (`400 code 3007`) |

Diagnostic rule: **`400 code 3007 "captcha verify failed"` = your token is
valid** — the request just didn't clear the edge's bot check. Only chase the
token when you get a real 401.

Fix applied to this install: `agent/anthropic_adapter.py` `_requires_bearer_auth()`
gained `or "zcode.z.ai" in normalized` so the Anthropic SDK sends Bearer for
this host (same mechanism as MiniMax/Azure Foundry).

## Two-tier gate (auth → captcha)

z.ai's edge challenges scripted clients even with the full ZCode fingerprint
header set: node/undici `fetch` with all 10 fingerprint headers still gets
`400 code 3007`. TLS-level fingerprint (JA3/HTTP2) matters; headers alone
don't spoof it. The patched httpx path may behave differently — untested past
auth at time of writing.

## Where ZCode keeps its credentials (no headless refresh exists)

- Plan JWT: `~/.zcode/v2/config.json` → `provider["builtin:zai-start-plan"].options.apiKey`
  (HS256, no `exp`, server rejects once ~1 day old).
- OAuth tokens: `~/.zcode/v2/credentials.json` → `oauth:zai:access_token`,
  `zcodejwttoken` (also go stale).
- **Refreshed ONLY by the ZCode Desktop app** (`C:\Users\YOUR_USERNAME\AppData\Local\Programs\ZCode\ZCode.exe`)
  — no refresh_token is stored, no CLI exists (`zcode` not on PATH), and ZCode's
  own logs redact tokens (`eyJhbG...OGQ0`), so there is no headless refresh path.
  Stale tokens all return `401 token expired or incorrect`.
- The Electron session partition (`%APPDATA%\ZCode\session\`) holds the live
  session but the Cookies DB is locked while the app runs (device busy) —
  don't bother reading it mid-run.

Key extraction one-liner (never echo the key):
```bash
export ZAI_API_KEY=$(python -c "import json,os;print(json.load(open(os.path.expanduser('~/.zcode/v2/config.json')))['provider']['builtin:zai-start-plan']['options']['apiKey'],end='')")
```

## Hermes `zai` provider name is special-cased — config base_url is IGNORED

`plugins/model-providers/zai/__init__.py` (base `https://api.z.ai/api/paas/v4`)
and `hermes_cli/auth.py` coding-global (`https://api.z.ai/api/coding/paas/v4`)
override the endpoint when the provider is named `zai`; `agent.log` shows
`provider=zai base_url=https://api.z.ai/api/coding/paas/v4` regardless of
`providers.zai.base_url` in config.yaml. Also `hermes -z` requires the key as
an env var (`ZAI_API_KEY` / `GLM_API_KEY` / `Z_AI_API_KEY`) — the inline
`api_key:` field in config.yaml is NOT read for this path ("No usable
credentials found for provider 'zai'").

To use a custom z.ai-family endpoint with config-controlled base_url: **name
the provider something other than `zai`** (e.g. `zcode`) so the built-in
special case doesn't fire; the fingerprint/`zcode.z.ai` host triggers and the
Bearer fix still apply (they match on host, not provider name). Note: the
system_prompt brand rewrite gates on `provider == "zai"` — a renamed provider
loses that unless the gate is extended.

## Fingerprint injection trigger sites (all patched for zcode.z.ai, 2026-07-31)

`agent/auxiliary_client.py` — four `build_zcode_headers()` sites, each with
`base_url_host_matches(..., "api.z.ai") or (..., "zcode.z.ai") or (..., "open.bigmodel.cn")`:
~line 2000 (`_resolve_api_key_provider`), ~2046 (second `_resolve_api_key_provider`
block), ~4552 (`_to_async_client` sync branch), ~5141 (`resolve_provider_client`
headers dict). Plus `run_agent.py` `_apply_client_headers_for_base_url` and
`anthropic_adapter.py` `_requires_bearer_auth`.

## Test recipe

```bash
hermes -z "Reply with exactly: PONG" -m glm-5.2 --provider zai
```
- `PONG` → full win.
- `400 code 3007` → auth + headers fine; blocked at TLS edge (needs the real
  app or a proxied TLS fingerprint).
- `401 token expired or incorrect` → open ZCode Desktop once to refresh, retest.

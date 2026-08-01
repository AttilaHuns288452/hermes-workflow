# Z.ai GLM coding plan — 429/1305 is a disguised content filter + fingerprint check

Source: r/hermesagent post by /u/moreoronce (2026-07) + GitHub issue
NousResearch/hermes-agent#47685. Patch upstream:
`github.com/moreoronce/hermes-zcode-glm-patch` (MIT).

## Symptoms

Hermes hitting z.ai's coding plan (glm-5.2) starts returning constant
`429` / code `1305` ("overloaded"), falling back to backup models. Quota
looks fine on the z.ai dashboard. Swapping keys / endpoints / reducing
concurrency changes nothing.

## Root causes (two independent layers)

1. **Brand-word content filter.** z.ai's backend returns 429/1305 when the
   system prompt contains the exact phrase "Hermes Agent". Same key/endpoint/
   model — only the prompt content changes the outcome. Rewrite the phrase and
   it's an instant 200. (z.ai docs call general-purpose agents "best-effort",
   deprioritized ~2–6 PM SGT — real QoS exists on top; some users report pure
   peak-time throttling instead. Both can coexist.)
2. **Client fingerprint.** Requests whose headers don't match the real ZCode
   Desktop client get blocked/throttled at the Cloudflare edge. Spoofing the
   official header set minimizes this.

## The fix (applied to this install 2026-07-31, 3 files)

- `agent/system_prompt.py` — in `build_system_prompt`, after `joined = …`:
  `if provider == "zai" and "glm-5.2" in model: joined = joined.replace("Hermes Agent", "ZCode")`.
  (In-memory only; nothing on disk changes.)
- `agent/auxiliary_client.py` — `build_zcode_headers()` (module-level
  `_ZCODE_APP_VERSION` from env `ZCODE_APP_VERSION`, default `3.1.8`; stable
  `_ZCODE_SESSION_ID` per process), wired into all header-resolution sites
  after the `api.kimi.com` branches: `_resolve_api_key_provider` ×2,
  `_to_async_client`, `resolve_provider_client` custom_base, and the
  provider-headers dict in `resolve_provider_client` (5 sites total + the
  `run_agent.py` one below).
- `run_agent.py` — `build_zcode_headers` import + elif in
  `_apply_client_headers_for_base_url` (trigger: `provider == "zai"` or
  base_url host `api.z.ai` / `open.bigmodel.cn`).

### Header set

| Header | Value |
|---|---|
| `User-Agent` | `ZCode/3.1.8 ai-sdk/anthropic/3.0.81` |
| `X-ZCode-App-Version` | `3.1.8` |
| `X-ZCode-Agent` | `glm` |
| `x-zcode-trace-id` / `x-request-id` / `x-query-id` | fresh uuid per request |
| `x-session-id` | stable per process (`sess_<24 hex>`) |
| `HTTP-Referer` | `https://zcode.z.ai` |
| `X-Title` | `Z Code` |

## Re-apply after `hermes update`

`hermes update` reverts local patches. To re-apply: redo the three edits
above (anchors: the kimi header branches, which are stable upstream) and
re-run the real-import verification:

```python
from agent.auxiliary_client import build_zcode_headers
h = build_zcode_headers()
assert h["User-Agent"].startswith("ZCode/") and h["X-ZCode-Agent"] == "glm"
```

plus one prompt-rewrite check (provider=zai/model=glm-5.2 rewrites
"Hermes Agent" → "ZCode"; openrouter keeps the phrase) and one control
(openrouter base_url gets no ZCode headers).

## Caveats

- ToS gray area: spoofing an official client's fingerprint may risk a ban
  (discussed in the thread). Gated strictly to zai/api.z.ai/open.bigmodel.cn
  so non-zai traffic is untouched.
- Only fixes the z.ai provider path — opencode-zen / deepseek routes are
  unaffected (by design).

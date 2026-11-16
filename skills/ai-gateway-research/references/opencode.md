# OpenCode (opencode.ai) — key types, bases, and where free models actually live

`oc_sk_…` keys are OpenCode **service-account** keys (console → service account → API key); the same prefix is used for Go-integration keys. Two OpenAI-compatible inference bases:

| Base | Route | Requirements |
|---|---|---|
| `https://opencode.ai/zen/v1` | Zen pay-as-you-go + `-free` models | funded wallet for non-free ids |
| `https://opencode.ai/zen/go/v1` | Go subscription models | active Go subscription AND an `x-opencode-session` header on every request |

Catalog and gate notes:

- Free ids end in `-free` (`deepseek-v4.1-flash-free`, `glm-5.3-flash-free`, `mimo-v2.6-flash-free`, `minimax-m3.1-flash-free`, `longcat-2.5-preview-free`). The non-free twins share the name **without** the suffix and bill per token — confirm the suffix is in the id you wire.
- The `-free` tier is server-gated to the OpenCode client itself: 403 `FreeTierError "can only be used from within OpenCode"`, and a session header does not lift it. Third-party plugins impersonate the official CLI's origin headers to pass this; do not use that trick (SKILL.md pitfalls: entitlement gates are not puzzles).
- Error ladder on these bases: Go without `x-opencode-session` → 400 `MissingSessionID` (protocol, not auth); Go without a subscription → 403 "subscription required"; Zen without funds → 402 "Insufficient account funds".
- `/v1/models` on both bases answers 200 **without any auth header** — catalog presence proves nothing about a key.
- The console also exposes management APIs with these keys (usage export at `/console/api/v1/usage/export`), whose records distinguish `billing_source: managed-inference | byok | free` — useful when the user asks what a route bills.

External-app free hosts for the same DeepSeek models (rate-limited free tiers; free tiers may log prompts — say so when recommending):

- OrcaRouter: `https://api.orcarouter.ai/v1`, free ids `deepseek/deepseek-v4.1-flash-free` and `deepseek/deepseek-v4-flash-free` ($0), paid twins `deepseek/deepseek-v4-flash` / `deepseek/deepseek-v4-pro` at per-token prices. Same trap as OpenCode: the `-free` suffix is the whole difference between $0 and billed.

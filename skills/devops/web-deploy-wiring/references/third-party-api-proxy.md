# Third-Party API Serverless Proxy

A Vercel/Netlify function fronting a paid upstream (scrapers, market data, search).
The proxy is the only place the upstream secret exists, and the only place that
knows the upstream's real response shape.

## Contract discovery (do this before writing the adapter)

Do not build a normalizer from prose docs or from memory. Get the real paths,
params, and response field names first:

1. **Render the docs in a browser, not `curl`/`web_extract`.** Provider docs
   (Docusaurus and friends) load request/response examples as JS chunks, so a
   plain fetch returns the prose parameter tables but empty code blocks. Drive
   Playwright to the page, expand `<details>`, click any *Response* tab, then
   read `pre, code` innerText — that is where the endpoint path and the JSON
   field names actually live. Grep the rendered text for snake_case tokens to
   get the full field list in one pass.
2. **Probe route paths with a dummy key — but only to confirm a path EXISTS,
   never to rule one out.** A wrong path on a normal API returns 404; a right
   path with a bad key returns 401/403, so the status distinguishes them. The
   trap: gated marketplaces (RapidAPI) return `403 "not subscribed"` for EVERY
   path when the key lacks access, including nonsense paths — so a uniform 403
   proves nothing about the route. Do not burn turns probing a gated gateway for
   the suffix; make the base URL env-configurable and take the exact path from
   the provider's own playground **Code snippet** tab, which is the authoritative
   contract. Ship with the documented default and a one-line fix path for when
   the first live call 404s.
3. **Match the response envelope, not just field names.** Some APIs return a
   bare object; others wrap in `{code, msg, data}` where `code != 200` is an
   error even at HTTP 200. Detect the envelope explicitly and unwrap before
   normalizing — the shape-gate below assumes you already did.

## Handler shape

```
GET /api/<provider>/<action>?<params>
  1. method check            -> 405 Allow: GET
  2. key present?            -> 503 "search unavailable" (never name the missing var to the client)
  3. validate each param     -> 400 with the exact field that failed
  4. cache lookup            -> hit: return cached + X-Cache: hit (no upstream cost)
  5. fetch with timeout      -> AbortSignal.timeout(20000); timeout -> 504
  6. JSON.parse in try/catch -> bad JSON -> 502 (never surface the raw text)
  7. !upstream.ok            -> map error by stable code
  8. error-shaped 2xx?       -> map as error (see below)
  9. shape-gate the payload  -> missing expected keys -> 404 / 502
 10. normalize + return     -> stable internal shape + cachedAt
```

## Shape-gating (the step people skip)

A 2xx is not a success. Upstreams return `200` with `{"message":"Server Error"}` or
`{}`. Normalize first, then assert the result has the fields that make it real —
for a product, an id OR a title; for a search, a `products` array. If not, return
404 (not found) or 502 (bad response), never `200` with an all-null object.

Detecting an error-shaped body: has `code` + (`message`|`error`), OR has a
`message` string with NONE of the data keys (`products`, `count`, `product_id`,
`title`, `pricing`). Legit empty results carry the data keys with empty values.

## Error mapping

Branch on the upstream's stable `code`, never on its `message` (messages get
rewritten). Map to a safe client envelope; never leak the key, upstream body text,
or stack traces.

| upstream code | HTTP | client code |
|---|---|---|
| `missing_api_key` / `invalid_api_key` | 502 | `search_unconfigured` (never reveal which) |
| `quota_exceeded` | 429 | `quota_exceeded` + `renews_at` |
| `rate_limited` | 429 | `rate_limited` + `Retry-After` header |
| `subscription_*`, 402 | 502 | `search_unavailable` (hide plan detail) |
| >= 500 | 502 | `upstream_unavailable` |
| unparseable / shape-gate fail | 502 | `upstream_bad_response` |

## Safe diagnostics on the error path

Include only: numeric `upstreamStatus`, the upstream's stable `upstreamCode`, and
the TOP-LEVEL KEY NAMES of the body (`Object.keys(body)`). Optionally the reason
string truncated. Never the body values verbatim, never the key. This is what lets
you tell "invalid key" from "provider outage" from "wrong request" without a
redeploy loop — and it proved the upstream was returning `500 {"message":"Server
Error"}` while the same key's `/account/usage` call succeeded.

## Key validity probe

Every such provider has a free, non-consuming endpoint (OmkarCloud: `GET
/account/usage` on the same host, same `API-Key` header). Proxy it too. A healthy
response with quota numbers proves the key and host are correct, isolating the
fault to the paid endpoint — versus `invalid_api_key`, which points at the
credential. Run this first when a paid endpoint 5xx's.

## Split pure logic out of the handler

Put validation, normalization, envelope-unwrap, and error mapping in a pure
module (`lib/<provider>.js`, zero I/O) and keep the serverless handler thin:
validate → build URL → fetch → hand the body to the pure layer. This makes the
whole trust boundary unit-testable with `node --test` and mocked upstream
bodies — the assertions you want (price/rating coercion of missing and malformed
values, envelope accept/reject, shape-gate, error mapping, URL builders) run
offline in milliseconds, and the handler's only untested surface is the fetch.

Make the gateway host configurable and switch auth headers off it: direct
providers take `apikey:` (or `API-Key:`), while RapidAPI-style gateways take
`X-RapidAPI-Key` + `X-RapidAPI-Host` (bare hostname, not a full URL). Then a
provider migration is a config change plus one new normalizer, not a rewrite of
the handlers.

## Quota discipline

- Cache identical requests with a TTL (10 min is fine for search) and a hard size
  bound.
- Never auto-walk pagination; cap `page` and let the user request more.
- Return `cachedAt` + `cache: hit|miss` so stale data is never presented as fresh.
- Most automated tests use mocked upstream bodies; only a few live smoke calls.

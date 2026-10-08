# Production Domain Checklists (depth on demand)

Load only the sections the task touches. Each item is a question to answer, not a box to tick.

## Data & State

- What is authoritative for each fact? Where do derived/cached/UI copies live and how do they converge?
- Lifecycle entities: enumerated states? valid vs invalid transitions? who may transition? side effects? failure mid-transition?
- Invariants listed with their OWNING layer (DB constraint > server logic > client logic).
- FKs, unique/check constraints, indexes for access paths, nullability semantics, soft vs hard delete, archival, history preservation (financial/clinical/audit records).
- Migration safety: backward-compatible sequence, dual-read/write windows, backfill plan, rollback of both code AND schema, no deploy of incompatible app/db versions together.

## Concurrency, Idempotency & Async

- Every shared/scarce resource: simultaneous-operation test actually executed (not theorized).
- Locking/unique-constraint/transaction choice per conflict point; isolation level implications.
- Retryable operations (payments, creation, webhooks, jobs): idempotency keys or natural dedup; retries must not duplicate side effects.
- Async: stale closure capture? request cancellation on view change? out-of-order response handling? listener cleanup on unmount? reconnection semantics? no sleep-as-synchronization.
- Distributed: duplicate/delayed/lost/out-of-order messages, partial failures, compensating actions, retry storms.

## Security & Privacy

- Per-route/per-resource authz matrix (role × action × resource owner). IDOR probe: alter every ID in routes, params, bodies, file URLs.
- Input validation at every trust boundary (booking payloads, payments, chat, uploads, CRUD). Parameterized queries only.
- Secrets: env/secret manager, per-environment separation, rotation, least privilege; never in repo, bundles, logs, RAG, SOUL, or skills.
- Rate limits on: login, password reset, registration, messaging, uploads, expensive queries, public APIs.
- Supply chain: dependency count/versions/lockfiles, CI deps, third-party SDKs, external APIs; remove unused, review upgrades.
- Privacy: collected data × purpose × access × retention × deletion × export × log exposure. Minimize.
- Audit trail for critical actions (actor/action/resource/timestamp/delta) without sensitive values.

## Client, Cache & Network

- Back/Forward/refresh/hard-refresh/direct-URL/deep-link/new-tab/logout/expired-session all exercised per major route.
- Forward restores state; never repeats mutations (no resubmitted payment, no recreated records).
- Cache classes assigned per data type: static-safe / revalidate / never-cache-authority. Invalidation lists per mutation.
- Offline/slow/flaky network: partial completion states, retry duplication, stale UI honesty, success reported only when the authoritative call succeeded.

## Reliability & Operations

- Loading/success/empty/failure/retry/timeout/partial states per data view; errors actionable.
- Failure isolation + graceful degradation map: which features survive which dependency outages.
- Observability: structured logs, error tracking, correlation IDs, health checks, alerts on actionable indicators only.
- Backups: what, frequency, retention, encryption, storage independence, TESTED restore. RPO/RTO stated.
- Rollback: app, DB, config, assets — each has a path. Irreversible changes flagged and gated.
- Environments separated; CI gates: lint → types → unit → integration → security → build → E2E → staging smoke → prod.
- Feature flags for high-risk changes only: default-off, staged exposure, rapid disable.

## Performance & Scale

- Measure first: latency, bundle, N+1, render cost, memory. Optimize what measurement implicates.
- 10x/100x/1000x thought experiment: indexes, pagination/cursors, query complexity, async offload, connection/API limits.
- Load/stress critical paths (auth, hot reads, critical mutations, search, reports).

## Delivery & Maintenance

- Testing pyramid chosen per risk: unit/integration/component/API/E2E/regression/security/load — not E2E-only.
- Prod verification checklist: env config, routes, auth, DB, integrations, storage, critical flows, monitoring, rollback.
- Readiness lens for substantial systems: correctness · security · reliability · recovery · observability · operations · performance · data · UX · maintainability.
- Docs another engineer needs: architecture, setup, env vars, deploy, migration, recovery runbook, invariants, troubleshooting, known failure modes.
- Data export/portability: authorized, consistent, auditable, large-set safe.
- Incident lifecycle: detect → assess → contain → recover → communicate → investigate → remediate → prevent.

## Push Notifications & OS-Integrated Web Features

- Web Push key semantics: the VAPID PUBLIC key is public-by-design (embedding in the bundle is not a leak); only the private key is secret and must live server-side. A missing public key in a deployed bundle is a silent feature-off — verify the artifact carries it.
- Delivery is a side channel: the database notification row is authoritative; push dispatch is fire-and-forget and must never roll back or block the business transaction that triggered it.
- Subscription lifecycle: register server-side under the authenticated identity (never a client-supplied user id), revoke on logout and on permanent delivery failures (404/410), classify transient vs permanent before revoking.
- Automation of real push needs a real client binary and persistent profile: headless contexts deny notification permission, and ephemeral profiles fail subscription with a misleading "permission denied" that reads like an app bug. Unbranded Chromium builds lack the push service credentials entirely.
- Deep links from notifications: payload route + auth re-check at the destination; the link grants no access, and an id belonging to someone else's record must show nothing.
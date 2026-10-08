---
name: pwa-web-push
description: "Use when adding real OS-level push notifications to a PWA."
tags: [pwa, push, notifications, web-push, vapid, service-worker, supabase]
triggers: [push notifications, web push, PWA notifications, service worker push, VAPID, PushManager, push subscription, phone notifications, notification permission, push delivery, notification deep link]
---

# PWA Web Push Notifications

Real OS-level push for an installed web app: server event → persistent notification row → push delivery → service worker → phone notification → tap → correct screen. Never fake it with polling, toasts, in-page `new Notification()`, or badge-only updates — the acceptance bar is a notification the user sees with the app closed.

## Architecture (build in this order)

1. **Persistent notification row = source of truth.** Push is a delivery channel only. Every business event inserts one notification row (deterministic `dedupe_key`, nullable `route`); the in-app list works with push disabled, denied, offline, or failed.
2. **Delivery fires from the database, not the client.** AFTER INSERT trigger on notifications → queued HTTP call (pg_net-style) → internal dispatch function → Web Push. The trigger returns unconditionally and swallows exceptions: a push failure can never roll back the business transaction (payments, appointments, money rows never call push directly).
3. **Idempotency:** `dedupe_key` with a partial UNIQUE index + insert helper doing `ON CONFLICT DO NOTHING`. One logical event (`payment:{id}:paid`, `appt:{id}:{event}:{audience}`) = one notification = one push per active subscription. Dispatch runs on INSERT only, so retried business events cannot re-push.
4. **Subscriptions:** one row PER DEVICE (endpoint UNIQUE), owner-only RLS, columns `user_id, endpoint, p256dh, auth, last_success_at, revoked_at`. Upsert on endpoint with the session-derived `user_id`: a second device adds a row; an account switch on the same device reassigns the row; logout revokes THIS device's row.
5. **Identity is always server-derived.** Registration functions take the user from the verified token; a `user_id` in the request body is ignored. Dispatch is callable only with an internal shared secret (never a public authenticated endpoint).
6. **VAPID:** ES256 P-256 pair. Public key is public-by-design subscription info (frontend env, source fallback acceptable). Private key lives only in a server-only store (config table with RLS and no policies, or function secrets). Never in bundles, git, logs, or payloads.
7. **Service worker:** extend the EXISTING worker, never create a second one. `push` → `showNotification({title, body, icon, badge, data:{route}})`; `notificationclick` → close, then focus an existing client + navigate to `data.route`, else `openWindow(route)`.
8. **Permission UX:** request only on an explicit user gesture (Settings → "Enable phone notifications"). Never auto-prompt on load; never re-prompt a denial. Claim "enabled" only after subscribe AND server registration succeed. iOS/iPadOS 16.4+ supports Web Push ONLY from Home-Screen-installed web apps — detect and show Add-to-Home-Screen guidance instead of a broken enable button.

## Delivery lifecycle

- Send per active subscription; success → `last_success_at`.
- Permanent failures (HTTP 404/410/400/401/403 AND local crypto/validation errors) → `revoked_at`, never retried forever. Transient (5xx/timeout) → keep the subscription.
- Classify local validation errors by message: web-push libraries reject malformed stored keys BEFORE any network call and often throw without `statusCode`; treating those as transient makes one bad row poison every future send.

## Deep links

- Notification rows carry `route`; the push payload mirrors it. Entity-scoped routes (`/appointments?appt={id}`) beat generic lists — have the target screen honor the param (scroll/highlight the entity).
- Deep links grant nothing: unknown/foreign ids must render a normal, leak-free screen (the entity simply isn't in the user's data). Auth and RLS are unchanged by notification clicks.

## QA (the real chain, on the real stack)

Assert the end-to-end chain with NO polling by the app: create a business event server-side, then read `registration.getNotifications()` in the browser and check title/body/route. Cover: subscribe via the actual UI gesture, server persistence + ownership RLS, forged-user-id registration, unauthenticated dispatch, duplicate events → one row, dead + malformed subscription revocation, logout revocation, and multi-device (two profiles, one event, both show it).

**Reporting discipline:** "Automated Web Push chain: VERIFIED" and "Android/iOS physical: NOT PHYSICALLY VERIFIED" are separate claims. Never let desktop evidence stand in for device acceptance.

Browser/testing pitfalls live in `references/testing-web-push.md` — load it before writing push tests; the default Playwright setup cannot register push subscriptions at all.

## Output Pattern

[code] → skipped: [X], add when [Y].

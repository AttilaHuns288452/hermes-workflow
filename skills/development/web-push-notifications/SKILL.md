---
name: web-push-notifications
description: "Use when adding or testing Web Push notifications in a PWA."
tags: [pwa, web-push, notifications, service-worker, vapid, supabase]
category: development
triggers: [web push, push notifications, PWA notifications, VAPID, PushManager, service worker push, notification permission, notification click, deep link notification, app badge, multi-device push, push subscription, browser push test, phone notifications]
---

# Web Push Notifications for PWAs

OS-level notifications from server events to installed web apps — no native stack: Service Worker + Push API + Notifications API + VAPID + a server-side sender. The target chain is: business event → persistent notification row → server push → phone OS notification → tap → correct app screen, with the existing auth/RLS still authorizing everything.

## Architecture rules (always on)

1. **The persistent notification row is the source of truth; push is a delivery channel.** Every notification must exist in-app even when push is denied, offline, failed, or dismissed.
2. **Event pipeline:** business event → notification row (deterministic dedupe key, e.g. `appt:{id}:{event}:{audience}`; unique index on it; insert with ON CONFLICT DO NOTHING) → AFTER INSERT trigger queues the dispatch (pg_net/http from the DB) → sender function pushes to that user's active subscriptions. The trigger must be fire-and-forget and swallow its own errors — a push failure can NEVER block or roll back the business transaction that created the notification.
3. **Identity is server-derived** from the verified session. Never accept user_id/recipient from a client body; a forged one must be ignored.
4. **Subscriptions are per-device rows keyed by a unique endpoint** (one user = many devices). Upsert on endpoint REASSIGNS user_id to the current session — a shared device switching accounts must never keep delivering the previous account's notifications. Logout revokes the current device's row.
5. **VAPID private key and any dispatch shared secret are server-side only** (a service-role-only table — RLS enabled with NO policies — or function secrets). The VAPID PUBLIC key is safe in the browser. Never in the bundle: private key, service-role key, dispatch secret.
6. **Revocation policy:** permanent failures revoke the row (push-service 404/410/4xx AND local crypto-validation errors); transient failures (5xx, timeout) keep it. Malformed rows must be revoked too — they poison every future send.
7. **Permission UX:** request only on explicit user gesture, never auto-prompt on load, never re-prompt after denial, claim "enabled" only after server registration confirms, and show platform guidance (iOS/iPadOS Web Push works ONLY from Home-Screen-installed web apps — tell users to Share → Add to Home Screen).
8. **Privacy:** notification text goes to a lock screen — time, amount, generic category only; never clinical detail, message content, or payment credentials.

## Procedure

1. **Audit the existing service worker first** — there must be exactly one. Extend it with `push` + `notificationclick` handlers; leave caching logic untouched.
2. **Generate the VAPID keypair** from Node crypto: private = JWK `d` (raw P-256 scalar, base64url, 43 chars); public = `04 || x || y` (uncompressed point, base64url, 87 chars). Never extract the scalar via `DER.subarray(-32)` — it lands on the wrong bytes. Store private in the server config, public in a `VITE_`-style public env.
3. **DB:** subscriptions table (endpoint unique, p256dh, auth, user_agent, last_success_at, revoked_at; owner-only RLS) + server-only config table + notification `dedupe_key` (partial unique) and `route` columns + dispatch trigger on the notifications table.
4. **Edge functions:** authenticated register/unregister (upsert on endpoint) + an INTERNAL dispatch function guarded by a shared secret header, using the `web-push` npm package (it handles VAPID signing and aes128gcm payload encryption).
5. **Service worker handlers:** `push` → parse `{title, body, route, icon}` → `registration.showNotification(..., { data: { route } })`; `notificationclick` → focus an existing client and `navigate(route)` (fallback `openWindow(route)`).
6. **Settings UX** panel (enable/disable + status states) + app badge synced from the unread count (`navigator.setAppBadge` / `clearAppBadge`) + logout unregister.
7. **QA the real chain** (below) — permission flow is not proof of delivery.

## Verifying the real chain (the part that eats time)

Assert delivery WITHOUT faking: trigger the business event server-side with no browser polling, then read `registration.getNotifications()` in the page — if the service worker shows the pushed notification with the right title/route, the whole path (trigger → queue → sender → push service → SW) worked. One event must reach EVERY active device.

`PushManager.subscribe()` fails with the MISLEADING `AbortError: Registration failed - permission denied` for at least four causes: real permission denial, invalid `applicationServerKey` bytes, an ephemeral browser context, and a browser build without push-service (FCM) credentials. Diagnose by elimination: check `Notification.permission` → retry with a freshly generated keypair → switch to a PERSISTENT browser profile (`launchPersistentContext`; ephemeral contexts cannot register push at all) → switch to BRANDED Chrome (unbranded Chromium, Playwright Chromium, and Chrome for Testing ship without FCM credentials and can never subscribe; on Linux without sudo, unpack the Google Chrome .deb locally: `dpkg-deb -x chrome.deb ~/tools/google-chrome`, then use its binary as Playwright `executablePath`). Headless Chrome reports notification permission denied even after grants — run push QA headed.

Fixture rules for push tests: `web-push` rejects malformed keys locally with no `statusCode` (messages like "should be 65 bytes long" / "not valid for specified curve") — classify those as permanent-revoke; and random bytes are never a valid p256dh, so a "dead endpoint" fixture must carry a REAL P-256 point or the request never reaches the push service. Fresh browser-profile directory names per run (persistent profiles carry old subscriptions and hide the enable controls). Run destructive lifecycle tests (logout, revocation) LAST — they destroy fixtures later checks depend on.

RLS testing: UPDATE/DELETE denials are SILENT (0 rows affected, no error) — assert affected-row counts and post-state, not error presence. Scope isolation assertions by ownership: leftover rows from earlier runs belong to their owners and are not violations.

## Pitfalls

- A DB trigger calling the dispatcher must wrap the call in its own exception handler returning NEW — an unguarded trigger turns a push-provider outage into failed business writes.
- pg_net-style queueing can't be exercised through read-only SQL consoles (INSERT errors there and works fine from real write transactions) — test dispatch with a real application insert, not an ad-hoc SQL probe.
- Admin consoles running multi-statement SQL often return only the LAST result set — confirm earlier statements with single-statement queries before concluding they failed.
- When generated code must round-trip through tool output into a deploy payload, secret-looking literals (apikey/Authorization header values) get masked and corrupt the copy — author headers as a spread constant (`const svcAuth = { apikey: K, Authorization: 'Bearer ' + K }`) so nothing passes through a filter.
- Don't claim "push works" because the permission prompt appeared, a subscription object exists, or a page-context Notification displayed — the acceptance condition is a server event producing an OS-level notification via the service worker.
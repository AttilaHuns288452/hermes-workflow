# Testing Web Push (browser recipe)

The default Playwright setup cannot register push subscriptions at all. All three conditions below are required; missing any one produces the same misleading error.

## Browser requirements (all three, or subscribe() fails)

| Requirement | Why |
|---|---|
| **Persistent profile** (`launchPersistentContext`) | Ephemeral contexts fail `PushManager.subscribe()` with `AbortError: Registration failed - permission denied` — the text blames permission while the real cause is push-service registration state needing a persistent profile. |
| **Headed** | Headless Chromium reports `Notification.permission === 'denied'` even after `context.grantPermissions(['notifications'])`. |
| **Branded Chrome** (FCM credentials compiled in) | Unbranded Playwright Chromium and Chrome-for-Testing have no FCM credentials — subscribe fails regardless of profile/permission. No sudo: download the Google Chrome `.deb` and unpack it (`dpkg-deb -x chrome.deb ~/tools/google-chrome`), then pass `executablePath`. |

Also: `grantPermissions(['notifications'], { origin })` — omitting the origin grants it for the wrong one.

```js
const ctx = await chromium.launchPersistentContext(os.tmpdir() + '/profile-' + Date.now(), {
  headless: false,
  executablePath: process.env.QA_CHROME || undefined, // branded Chrome path
  permissions: ['notifications'],
})
```

Use a FRESH profile dir per device per run: a reused profile already holds a subscription, so the enable button disappears and the run silently stops testing subscription creation.

## Proving the real chain

After triggering a server-side business event, poll the service worker's own notification surface — no app polling involved:

```js
for (let i = 0; i < 15; i++) {
  await page.waitForTimeout(1500)
  const n = await page.evaluate(async () =>
    (await (await navigator.serviceWorker.ready).getNotifications()).map((x) => ({ t: x.title, r: x.data?.route })))
  if (n.length) break
}
```

Delivery is asynchronous (database trigger → queue → dispatch → push service → browser) — poll 15–20s, never a fixed sleep.

## Subscription fixtures

- **Dead endpoint (HTTP-404/410 path):** p256dh must be a REAL P-256 curve point — generate a keypair and use its uncompressed public point (`04 || x || y`, 65 bytes). Random bytes fail local curve validation and never reach the push service, so the HTTP cleanup path stays untested.
- **Malformed keys fixture:** a short/invalid p256dh exercises the local-validation revocation path — the library throws before any network call, usually WITHOUT `statusCode`; classify those permanent by error message (`should be|must be|invalid|not valid|curve`).
- Both fixtures must end REVOKED after one dispatch; a transient classification keeps them poisoning every future send.

## Multi-device

Two persistent profiles, same account, enable in both, clear both notification surfaces, fire ONE event, assert BOTH show it. Run this BEFORE any logout test — logout revokes the device subscription and silently turns the multi-device check into a single-device check.

## What cannot be automated

The literal OS notification click and lock-screen appearance are device-level. Open the notification's route URL in a fresh page to test what `openWindow(route)` lands on (scoped entity, refresh-safe, foreign id renders a leak-free screen), and report physical Android/iOS acceptance as NOT PHYSICALLY VERIFIED until a human does it on a device.

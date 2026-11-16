---
name: capacitor-mobile
description: Use when building or fixing a Capacitor app.
triggers:
  - capacitor
  - ionic
  - native app wrapper
  - mobile app
  - android app
  - ios app
  - apk
  - xcode
  - cap sync
  - webview
  - app store
  - appium
version: 1.0.0
metadata:
  source: https://github.com/Cap-go/capgo-skills
  upstream_license: MIT
  imported: "2026-11-16"
  note: reference bodies are verbatim upstream minus YAML frontmatter; sibling skill names below map to files in references/
---

# Capacitor mobile

Capacitor wraps an existing web build in a native iOS/Android shell. Most failures are
not app bugs: they are web-Dir/config drift, plugin/major version skew, a dev
`server.url` shipped to production, or edits made inside the generated native assets
folder instead of the web source.

## Why this exists here

No Capacitor/RN/Expo capability existed locally before this skill (verified 2026-11-16:
zero `capacitor.config.*` files on disk, zero Capacitor/Expo skills across 863 catalog
rows). The web apps that would ship this way are already Vite/Tailwind SPAs, so the
missing piece is exactly the native wrapper layer.

**Wrong skill?** If the app is React-native-first (native navigation, native lists) rather
than an existing web build in a wrapper, load `expo-mobile` instead. Rule of thumb: existing
Vite/web build → Capacitor; new React Native app → Expo.

## Workflow

1. **Read the project, not the docs.** Check `capacitor.config.ts|json`, then the
   installed `@capacitor/core` / `cli` / `ios` / `android` versions and every plugin's
   major. Version skew is the #1 cause of "plugin is not implemented" and half the
   build breaks.
2. **Route to the owning reference** (load one, not all):

| Situation | Reference |
|---|---|
| Codebase review, new setup, config audit, version alignment | `references/capacitor-best-practices.md` |
| Finding/installing a plugin, permission flows, web fallbacks | `references/capacitor-plugins.md` (+ `references/capacitor-plugins/` per-plugin files) |
| Secrets, storage, CSP, cert pinning, Xcode hardening | `references/capacitor-security.md`, `references/capacitor-ios-security-hardening.md` |
| Bundle size, startup time, memory, bridge profiling | `references/capacitor-performance.md` |
| Tests, plugin mocking | `references/capacitor-testing.md` |
| Major version upgrade | `references/capacitor-app-upgrades.md`, `references/capacitor-app-upgrade-v8-to-v9.md` |
| App Store / Play submission, review rejection preflight | `references/capacitor-app-store.md`, `references/capacitor-apple-review-preflight.md` |
| Push, deep links, keyboard, splash, intents, a11y, offline | `references/capacitor-push-notifications.md`, `references/capacitor-deep-linking.md`, `references/capacitor-keyboard.md`, `references/capacitor-splash-screen.md`, `references/capacitor-app-intents.md`, `references/capacitor-accessibility.md`, `references/capacitor-offline-first.md` |
| CI/CD builds | `references/capacitor-ci-cd.md` |
| UIScene / AppDelegate drift (iOS 18+) | `references/capacitor-uiscene-migration.md` |

3. **Verify by behavior, not by build success.** `npx cap sync` green + a running app
   that reaches the plugin is the bar. A white screen or a silent no-op on device is the
   usual failure mode; check `npx cap doctor` and the native logs before touching config.

## Hard rules

- Never edit files under `android/app/src/main/assets/public` or the iOS `public/` folder:
  `cap sync` overwrites them. Fix the web source and re-sync.
- `server.url` in a committed config means the app loads a dev server in production.
  Strip it for release builds.
- `webDir` must match the real build output (`dist`, `build`, `out`) or the app ships a
  stale or empty bundle.
- Plugin calls need an availability check plus a permission flow before use; matching on
  error message strings breaks on minor upgrades (match `error.code`).
- Treat the wrapper as a client: never place secrets in the web bundle. Native storage
  (`@capacitor/preferences`) is plain storage, not a keystore.

## Skipped on import

Capgo Cloud, organization management, release/workflow management, and live-update
migration references were left out: they only apply when paying for Capgo's service.
The CLI usage notes are inside `capacitor-ci-cd.md` when a build needs them.

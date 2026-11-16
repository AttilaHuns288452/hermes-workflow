---
name: expo-mobile
description: Use when building an Expo or React Native app.
triggers:
  - react native
  - expo
  - expo router
  - native app
  - mobile app
  - android app
  - ios app
  - list performance
  - reanimated
  - nativewind
  - expo go
  - dev client
version: 1.0.0
metadata:
  source: https://github.com/expo/skills
  upstream_license: MIT
  imported: "2026-11-16"
  note: reference bodies are verbatim upstream minus YAML frontmatter; nested files under references/<skill>/
---

# Expo mobile

Expo is the React Native path: one JS/TS codebase to iOS and Android with the native
project generated for you. Reach for it when the app is React-native-first (native
navigation, native lists, native gestures) rather than an existing web build in a
wrapper, which is `capacitor-mobile`.

## Why this exists here

Mobile tooling on this box (set up and build-verified 2026-11-16): `node v26.8.1`,
`openjdk 21.0.13`, `adb`, and an Android SDK at `~/Android/Sdk` with `platform-tools`,
`emulator`, `system-images`, `platforms;android-34/35/37`,
`build-tools;34/35/36/37`, `ndk;27.1.12297006`, `cmake`.

`ANDROID_HOME`, `ANDROID_SDK_ROOT` and PATH are exported in BOTH `~/.bashrc` and
`~/.profile` (bashrc returns early for non-interactive shells, so profile is the one that
matters for scripts). Verify before a build:

```bash
echo $ANDROID_HOME                       # /home/attila/Android/Sdk
command -v sdkmanager adb                # both resolve
npx expo run:android                     # gradle comes from the wrapper; no system gradle
```

Proven end to end: a fresh `create-expo-app` template passed `expo-doctor` 20/20,
`expo prebuild --platform android` generated the native project, and
`./gradlew assembleDebug` produced a working `app-debug.apk` (137 MB debug, minSdk 24,
targetSdk 36) in 6m29s on a cold `~/.gradle`. The first build is the slow one (gradle
pulls ~3.8 GB of cache once); after that builds are incremental.

Only AVD present: `Pixel_8_API_34` (android-34 google_apis x86_64). `npx expo start`
plus Expo Go on a phone needs none of the native toolchain.

## Workflow

1. **Establish the SDK contract first.** Read `package.json` for the `expo` version and
   run `npx expo-doctor` before writing code. Version skew between `expo`, `react-native`
   and native modules is the dominant failure mode.
2. **Route to the owning reference** (load one, not all):

| Situation | Reference |
|---|---|
| First contact with a codebase, or "what am I looking at" | `references/expo-overview.md` |
| Folder layout, entry point, app config, monorepo shape | `references/expo-project-structure.md` |
| Routes, tabs, stacks, typed params, deep links | `references/expo-router.md` |
| Building screens with native UI primitives | `references/expo-native-ui.md` |
| Design tokens, theming, dark mode, component library | `references/expo-design-system.md`, `references/expo-ui.md` |
| Fetching, caching, offline, auth-gated calls | `references/expo-data-fetching.md` |
| Animation, gestures, Reanimated, haptics | `references/expo-animation.md` |
| DOM components, sharing components with the web app | `references/expo-dom.md` |
| Porting an existing web app to native | `references/expo-web-to-native.md` |
| Writing a native module or config plugin | `references/expo-module.md` (+ `references/expo-module/`) |
| Native code inside an existing native app | `references/expo-brownfield.md` (+ `references/expo-brownfield/`) |
| Dev builds on a real device | `references/expo-dev-client.md` |
| iOS App Clip | `references/expo-app-clip.md`, `references/expo-app-clip/` |
| SDK upgrade | `references/expo-upgrade.md` (+ `references/expo-upgrade/`) |
| Copy-paste starting points | `references/expo-examples.md`, `references/expo-examples/` |
| Component/list/render performance rules, one file per rule | `references/react-native-performance/README.md`, then the matching rule file |

3. **Verify on a device or emulator, not in a browser.** Metro green plus the app running
   via `npx expo run:android` (or a dev client) is the bar. `npx expo start --web` proves
   nothing about native behaviour.

## Hard rules

- `expo-doctor` clean before debugging anything else. A version mismatch presents as a
  random runtime crash, not a version error.
- Anything requiring custom native code needs a **dev build**; Expo Go cannot load it.
  Do not spend time trying to make an incompatible package work in Expo Go.
- Prefer Expo Router file-based routes for new apps; don't mix in a second navigation
  library.
- Every native module added needs a rebuild of the dev client; reloading JS is not enough.
- Never put secrets in `app.json` `extra` or any `EXPO_PUBLIC_*` variable: they ship in the
  bundle.
- `app.json`'s `newArchEnabled` and the Android `compileSdk`/`targetSdk` come from the
  template; don't hand-edit the generated `android/` folder if you plan to keep using
  prebuild, because the next prebuild overwrites it.

## Reference: React Native performance rules

`references/react-native-performance/` holds 38 single-topic rule files from
vercel-labs/agent-skills (MIT), each with an incorrect/correct code pair: list
virtualization, item memoization, inline objects in lists, image loading, animation on the
UI thread, monorepo dependency rules, safe-area and Pressable patterns. Read the matching
file, not the whole folder.

## Skipped on import

The 7 EAS skills (`eas-app-stores`, `eas-hosting`, `eas-workflows`, `eas-observe`,
`eas-update`, `eas-update-insights`, `eas-simulator`) were left out: they exist to sell
Expo Application Services, and this box builds locally. Add them only if a project actually
pays for EAS. `expo-migrate-module` was skipped as upstream-experimental.

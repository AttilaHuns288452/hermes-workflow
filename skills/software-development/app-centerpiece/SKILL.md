---
name: app-centerpiece
description: Manage the App Centerpiece launcher — add, remove, and debug apps in the registry JSON, build with tsc, and validate before launch. Covers the Electron/TypeScript launcher at ~/Documents/Playground/src/launcher-centerpiece/.
tags:
  - centerpiece
  - launcher
  - electron
  - registry
  - playground
triggers:
  - app centerpiece
  - centerpiece launcher
  - add to centerpiece
  - apps.registry
  - launcher-centerpiece
  - compactgui
---

# App Centerpiece

The App Centerpiece is a custom Electron/TypeScript launcher at `~/Documents/Playground/src/launcher-centerpiece/` that displays app cards and lets you Start / Stop / Open each one.

## Project Layout

```
src/launcher-centerpiece/
├── apps.registry.json       # App definitions (JSON array)
├── types.ts                 # TypeScript types for registry entries
├── registry.ts              # Parser + validator (parseLaunch, parseApp, parseRegistryJson)
├── process-manager.ts       # Start/stop lifecycle
├── renderer.ts              # Frontend IPC calls
├── main.ts                  # Electron bootstrap + IPC wiring
├── electron-smoke.ts        # Smoke test helpers
├── renderer/
│   └── index.html           # App card shell
└── *.test.ts                # node --test test files
```

## Registry Entry Format

Each app is an object in `apps.registry.json` array. Full schema in `references/registry-format.md`.

### Quick template — native GUI app (like CompactGUI):

```json
{
  "id": "my-app",
  "name": "My App",
  "description": "What it does",
  "cwd": "C:\\Users\\Attila",
  "launch": {
    "shell": "powershell",
    "script": "Start-Process -WindowStyle Normal -FilePath \"C:\\path\\to\\app.exe\"",
    "windowStyle": "normal",
    "startupProbe": {
      "mode": "processMatch",
      "match": {
        "field": "name",
        "value": "app.exe"
      }
    }
  },
  "openTarget": { "type": "launch" },
  "stop": {
    "mode": "processTreeMatch",
    "match": { "field": "name", "value": "app.exe" }
  }
}
```

### Quick template — web dev server (like OpenCharts):

```json
{
  "id": "web-app",
  "name": "Web App",
  "description": "Vite/Next.js dev server",
  "cwd": "C:\\Users\\Attila\\Documents\\Projects\\web-app",
  "launch": {
    "shell": "powershell",
    "script": "Set-Location 'C:\\Users\\Attila\\Documents\\Projects\\web-app'\nnpm run dev",
    "windowStyle": "normal",
    "startupProbe": {
      "mode": "processMatch",
      "match": { "field": "commandLine", "value": "web-app" }
    }
  },
  "openTarget": { "type": "url", "value": "http://localhost:5173" },
  "stop": {
    "mode": "processTreeMatch",
    "match": { "field": "commandLine", "value": "web-app" }
  }
}
```

## Workflow to Add an App

1. **Locate the app** — binary path, repo URL, or install location
2. **Add registry entry** — edit `src/launcher-centerpiece/apps.registry.json` with the correct fields
3. **Validate the JSON** — before building:
   ```bash
   cd ~/Documents/Playground
   node -e "const r=require('./dist/launcher-centerpiece/registry.js'); \
     const reg=r.parseRegistryJson(require('fs').readFileSync('./src/launcher-centerpiece/apps.registry.json','utf8')); \
     console.log('OK —', reg.apps.length, 'apps');"
   ```
4. **Build** — `npm run build` (runs `tsc -p tsconfig.json`)
5. **Launch** — `npx electron dist/launcher-centerpiece/main.js`
   - Or for dev: `npm run centerpiece:dev`

## Shell Value Constraint

The `launch.shell` field **must** be `"powershell"`. Any other value (including `"cmd"`) crashes at runtime with:
```
Error: Invalid apps[N].launch.shell
```

For native GUI apps, use PowerShell's `Start-Process`:
```powershell
Start-Process -WindowStyle Normal -FilePath "C:\path\to\app.exe"
```

## When to Omit launch/stop

If the app is a URL link or library reference with no server to start (e.g. a GitHub repo link), set both to `null`:
```json
"launch": null,
"stop": null
```
The type system makes these `optional` — the parser and process-manager both handle `null` gracefully.

## App List (current as of July 2026)

11 apps registered: `crypto-radar`, `lds-clerk-bot`, `open-webui`, `llmfit`, `free-dev-tools`, `opencharts`, `tradingagents`, `tradingview-api`, `autogpt`, `compactgui`, `deeptutor`.

## Ponytail Notes

- Registry is JSON, not TypeScript — no type-checking at build time for this file. Always validate with `node -e require(...)` before launching.
- `startupProbe.match.field` accepts only `"name"` or `"commandLine"` — no custom fields.
- Multiple electron.exe processes is normal — each card can spawn its own.

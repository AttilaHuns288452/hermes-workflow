# App Centerpiece Registry Format Reference

## Full Schema

```typescript
interface AppRegistryEntry {
  id: string;              // kebab-case unique ID
  name: string;            // Display name
  description: string;     // Shown on the card
  cwd: string;             // Working directory (absolute path, double-escaped in JSON)
  launch?: LaunchDefinition | null;  // null for link-only apps (tradingview-api)
  openTarget: OpenTarget;  // What happens when user clicks "Open"
  stop?: StopDefinition | null;      // null for link-only apps
  notes?: string;          // Optional human note
}

interface LaunchDefinition {
  shell: "powershell";     // ⚠️ ONLY "powershell" is accepted
  script: string;          // PowerShell script to run (multi-line with \n)
  windowStyle: "normal" | "minimized" | "hidden";
  env?: Record<string, string>;  // Optional env vars
  startupProbe: {
    mode: "processMatch" | "processName" | "httpGet" | "tcpConnect";
    match: {
      field: "name" | "commandLine";  // Only these two fields accepted
      value: string;
    };
    initialDelayMs?: number;
    periodMs?: number;
  };
}

type OpenTarget =
  | { type: "launch" }              // Launch the app (same as Start)
  | { type: "url"; value: string }  // Open URL in browser
  | { type: "directory"; value: string };  // Open folder in Explorer

type StopDefinition = {
  mode: "processTreeMatch";
  match: {
    field: "name" | "commandLine";
    value: string;
  };
};
```

## Pitfalls (discovered during sessions)

### 1. `shell` must be `"powershell"` exactly
`"cmd"` or any other string crashes with `Error: Invalid apps[N].launch.shell`. Use `Start-Process` in PowerShell for native GUI apps instead of `start "" "..."`.

### 2. Literal `\n` in scripts
JSON `"script"` strings with literal `\\n` sequences (double backslash + n) render as literal `\n` text in PowerShell, not line breaks. Use actual newlines in the JSON string value.

### 3. `launch: null, stop: null` is valid
The type system now handles these as optional. Apps that are just URL links (like `tradingview-api` pointing to GitHub) should have both set to `null` to skip start/stop. Without this, the parser crashes on null values.

### 4. startupProbe.match.field is limited
Only `"name"` (process image name like `"electron.exe"`) or `"commandLine"` (substring of the command line like `"deeptutor_cli.main"`). No custom fields.

### 5. JSON is not type-checked at build time
The `apps.registry.json` file is plain JSON, not TypeScript. `npm run build` (tsc) compiles `*.ts` files only — it does not validate the JSON. Always run a validation check after editing:

```bash
cd ~/Documents/Playground
node -e "
const r=require('./dist/launcher-centerpiece/registry.js');
const reg=r.parseRegistryJson(require('fs').readFileSync('./src/launcher-centerpiece/apps.registry.json','utf8'));
console.log('OK —', reg.apps.length, 'apps validated');
reg.apps.forEach(a => console.log('  -', a.id, a.name));
"
```

## App Categories

| Category | Example | Notes |
|----------|---------|-------|
| **Native GUI** | CompactGUI | Use `Start-Process`, probe by `name` |
| **Web dev server** | OpenCharts, FreeDev Tools | Vite/Next.js on localhost, probe by `commandLine` |
| **Python server** | DeepTutor, AutoGPT | venv python -m module, probe by `commandLine` |
| **Electron app** | Crypto Watcher | Built from Playground monorepo |
| **Link-only** | TradingView API | `launch: null, stop: null`, `openTarget.type: "url"` |

## Quick Validation After Editing

```bash
# 1. Check JSON syntax
python -m json.tool src/launcher-centerpiece/apps.registry.json > /dev/null && echo "Valid JSON"

# 2. Check registry parser validates all entries
cd ~/Documents/Playground && node -e "
const r=require('./dist/launcher-centerpiece/registry.js');
const reg=r.parseRegistryJson(require('fs').readFileSync('./src/launcher-centerpiece/apps.registry.json','utf8'));
console.log(reg.apps.length, 'apps — all pass');
"
```

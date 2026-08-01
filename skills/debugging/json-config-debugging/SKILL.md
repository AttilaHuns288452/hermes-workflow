---
name: json-config-debugging
description: "Debug JSON config files with malformed string values, null-unexpected errors, encoding bugs, and type-mismatch crashes in config-driven TypeScript/Node apps."
---

# JSON Config File Debugging

## When to Use

- A JSON config file crashes the parser with obscure errors
- Scripts embedded in JSON strings don't execute correctly (commands run as one line)
- A field that should be an object is `null`, throwing `TypeError: Cannot read properties of null`
- Making a field optional in TypeScript produces cascading type errors across the codebase
- You need to inspect the actual parsed content of a JSON file vs. what the file looks like in an editor

## Diagnostic Protocol

### 1. Verify the Load Path

Check that the file you're editing is the same one the app actually loads:

```bash
# Trace the file path used at runtime
grep -rn "readFileSync\|loadConfig\|loadRegistry\|JSON.parse" src/
```

Sometimes the app loads a compiled copy in `dist/` while you're editing `src/`.

### 2. Parse the File Independently

Use Python to load the JSON and inspect parsed values:

```python
import json

with open('config.json', 'r') as f:
    entries = json.load(f)

for e in entries:
    if isinstance(e.get('launch'), dict):
        print(repr(e['launch'].get('script', '')))
```

**Key trick:** `repr()` shows the actual string content — real newlines show as `\n`, literal backslash-n shows as `\\n`.

### 3. Check for Null vs Object

If a field is expected to be an object but the JSON has `null`:

```python
for i, e in enumerate(entries):
    if e.get('someField') is None:
        print(f"Entry {i}: someField is null!")
```

Fix: either remove the field or the parser must handle null.

### 4. Raw Byte Inspection

When you can't trust what's in the JSON file:

```bash
python -c "
with open('config.json', 'rb') as f:
    raw = f.read()
idx = raw.find(b'script')
hex_str = ' '.join(f'{b:02x}' for b in raw[idx:idx+60])
print(hex_str)
"
```

Byte key:
- `5c 6e` (2 bytes) = `\n` in file → JSON.parse → real newline ✅
- `5c 5c 6e` (3 bytes) = `\\n` in file → JSON.parse → literal `\n` (NOT a real newline) ❌

### 5. Fix Embedded Script Newlines

When JSON strings have `\\n` (literal backslash-n) instead of real newlines:

```python
with open('config.json', 'r') as f:
    entries = json.load(f)

for e in entries:
    if isinstance(e.get('launch'), dict):
        s = e['launch'].get('script', '')
        if '\\n' in s:
            e['launch']['script'] = s.replace('\\n', '\n')

with open('config.json', 'w') as f:
    json.dump(entries, f, indent=2)
    f.write('\n')
```

This works because `json.dump` re-encodes real newlines as `\n` escape sequences (which all JSON parsers correctly decode).

## TypeScript Ripple Effects

When you change a field from required to optional in a TypeScript config type:

```typescript
// Before
launch: LaunchDefinition;

// After  
launch?: LaunchDefinition;
```

Every file that accesses `app.launch.X` will produce `Object is possibly 'undefined'` errors. The fix protocol:

1. **Fix the parser** — Guard with `isRecord()` or check for undefined
2. **Fix `buildPowerShellLaunchScript`** — Add early return/throw for undefined launch
3. **Fix `refreshStatuses`** — Skip entries with undefined launch, emit default status
4. **Fix `findMatchedProcess`** — Use optional chaining: `app.launch?.startupProbe`
5. **Fix test assertions** — Add `?.` or non-null assertions (`!`)
6. **Fix renderer** — Conditionally hide Start/Stop buttons when launch/stop is undefined

See `references/json-optional-field-ripple-effect.md` for a worked example.

## Protection Patterns

### Parser guard for null fields

```typescript
function parseApp(input: unknown) {
  if (!isRecord(input)) throw new Error('Invalid input');
  return {
    launch: isRecord(input.launch) ? parseLaunch(input.launch) : undefined,
    // ...
  };
}
```

### Runtime guard before using optional fields

```typescript
async start(appId: string) {
  const app = this.requireApp(appId);
  if (!app.launch) {
    return { id: appId, state: 'error' as const, detail: 'No launch definition' };
  }
  // ... safe to use app.launch
}
```

### Config assertion test

Add a test that loads the real config file and validates parsed field shapes against expected types — this catches both null crashes and encoding bugs:

```typescript
it('config scripts parse correctly', () => {
  const { apps } = loadConfigFile('config.json');
  for (const app of apps) {
    if (app.launch?.script) {
      assert.ok(app.launch.script.includes('\n'),
        `${app.id} script should have newlines`);
    }
  }
});
```

## Verification

- [ ] The JSON file loads without crashes
- [ ] All parsed strings have real newlines where expected (not literal `\n`)
- [ ] TypeScript compiles cleanly after optional-field changes
- [ ] Tests pass (including the config-loading integration test)
- [ ] Apps with missing launch definition don't show Start buttons in UI

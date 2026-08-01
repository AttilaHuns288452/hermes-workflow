# PowerShell Script Encoding in JSON — Debugging `\\n` vs `\n`

## The Bug

A JSON config file has PowerShell scripts embedded as string values, with `\\n` (double-escaped) instead of real newlines.

When you intended:
```
Set-Location 'C:\path'
command2
```

The file has:
```json
"script": "Set-Location 'C:\\path'\\ncommand2"
```

After `JSON.parse`, the string is: `Set-Location 'C:\path'\ncommand2` — a single line with literal `\n` chars. PowerShell treats `\n` as literal text, NOT a command separator.

## Diagnosis

### Python string inspection

```python
import json
entries = json.load(open('config.json'))
for e in entries:
    s = e.get('script', '')
    print(repr(s))  # \n = real newline (✅), \\n = literal chars (❌)
```

### Raw hex check

```bash
python -c "
with open('config.json', 'rb') as f:
    data = f.read()
# Look for the byte right after 'Playground"' before 'npm'
idx = data.find(b'script')
print(' '.join(f'{b:02x}' for b in data[idx:idx+60]))
"
```

Interpretation:
- `5c 6e` (`\n` in JSON) → real newline after JSON.parse ✅
- `5c 5c 6e` (`\\n` in JSON) → literal `\n` chars after JSON.parse ❌

## Fix

### Using Python's json module (recommended)

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

`json.dump` re-encodes real newlines as `\n` escape sequences, which round-trip correctly through any JSON parser.

## Verification

```python
with open('config.json', 'r') as f:
    fixed = json.load(f)
for e in fixed:
    if isinstance(e.get('launch'), dict):
        s = e['launch'].get('script', '')
        lines = s.split('\n')
        has_literal = '\\n' in s
        print(f'{e["name"]}: lines={len(lines)} literal_bn={has_literal} ok={len(lines)>1 and not has_literal}')
```

## Root Cause

Someone hand-edited the JSON file and wrote `\n` (which renders as a real newline in many editors) but the editor or toolchain escaped it to `\\n`. Or the JSON was written by a tool that applied double-encoding.

## Prevention

Add a config-loading integration test that validates all embedded scripts:

```typescript
it('all embedded scripts have real newlines', () => {
  const { apps } = loadConfig(CONFIG_PATH);
  for (const app of apps) {
    const script = app.launch?.script;
    if (script && script.includes('\\n')) {
      throw new Error(`${app.id} script has literal \\n instead of real newlines`);
    }
  }
});
```

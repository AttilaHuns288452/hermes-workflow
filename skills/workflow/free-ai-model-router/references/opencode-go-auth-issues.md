# OpenCode Go Auth — Trailing Whitespace & HTTP 400

## Root Cause

A trailing space in the `opencode-go` API key at `~/.local/share/opencode/auth.json` causes **HTTP 400 "Upstream request failed"** from the Console Go / OpenCode Go provider.

## Why It's Confusing

| Status | Meaning | Common at |
|--------|---------|-----------|
| **400** Bad Request | Server can't parse the request (malformed auth header) | Wrong API key format |
| **429** Too Many Requests | Rate limit exceeded | Free tier overload |
| **402** Payment Required | Quota exhausted | Paid credits used up |

Users conflate 400 with rate limits because both show as "request failed" in the provider error. The mental model should be: **400 = format, 429/402 = capacity**.

## Detection

```bash
python -c "
import json
with open('C:/Users/Attila/.local/share/opencode/auth.json') as f:
    d = json.load(f)
k = d['opencode-go']['key']
print(repr(k))
print('length:', len(k))
print('has trailing space:', k != k.strip())
"
```

Output when broken:
```
'sk-T50...uMpj '
length: 68
has_trailing_space: True
```

## Fix

```bash
python -c "
import json
path = 'C:/Users/Attila/.local/share/opencode/auth.json'
with open(path) as f:
    d = json.load(f)
d['opencode-go']['key'] = d['opencode-go']['key'].strip()
with open(path, 'w') as f:
    json.dump(d, f, indent=2)
print('fixed')
"
```

## Ponytail Plugin (Separate Issue)

`@dietrichgebert/ponytail` installed globally at `C:\Users\Attila\AppData\Roaming\npm` fails to load with:

```
ERROR service=plugin path=@dietrichgebert/ponytail error=path must be a string or a file descriptor
```

And causes `D.split is not a function` on direct `opencode run` invocations. Workaround: comment out the plugin in `opencode.jsonc`:

```jsonc
// "plugin": ["@dietrichgebert/ponytail"],
```

This is unrelated to the auth 400 issue.

# Setting Up Hermes `external_dirs` on Windows

A step-by-step recipe that avoids the pitfalls (two config files, list-value serialization, yaml.dump corruption).

## Step 1: Locate the Active Config

```bash
# Print the real config path
hermes config path
# Result: C:\Users\<user>\AppData\Local\hermes\config.yaml
```

This is the **only** file you should edit. The `~/.hermes/config.yaml` file (~1.4 KB) is a profile override stub and does not control `external_dirs`.

## Step 2: Read the Current Config

Check if `skills.external_dirs` already exists:

```bash
python -c "
with open('$HERMES_HOME/config.yaml') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'external_dirs' in line:
        print(f'Line {i+1}: {line.rstrip()}')
        # Show sibling lines
        j = i + 1
        while j < len(lines) and lines[j].startswith('  - '):
            print(f'  {lines[j].rstrip()}')
            j += 1
"
```

## Step 3: Edit the List (Safe Method)

Use string-based Python, NOT yaml.dump():

```python
import re

with open('$HERMES_HOME/config.yaml', 'r') as f:
    text = f.read()

# Replace: external_dirs: []  or  external_dirs: <string>
# With:    external_dirs:\n    - path1\n    - path2
# Build a fresh external_dirs multi-line string
# (replace paths below with your actual repos):
new_value = (
    'external_dirs:\n'
    '    - C:/Path/To/Repos/external-skills/superpowers/skills\n'
    '    - C:/Path/To/Repos/external-skills/agent-skills/skills\n'
    '    - C:/Path/To/Repos/external-skills/garden-skills/skills\n'
    '    - C:/Path/To/Repos/external-skills/claude-seo/skills'
)
text = re.sub(
    r'external_dirs:\s*\[.*?\]',
    new_value,
    text,
    flags=re.DOTALL
)

with open('$HERMES_HOME/config.yaml', 'w') as f:
    f.write(text)
```

If the value was already a string (not a list), use:
```python
text = re.sub(
    r'external_dirs:\s*.+$',
    new_value.replace('\n', '\n'),  # multiline replacement
    text
)
```

## Step 4: Verify

```bash
python -c "
with open('$HERMES_HOME/config.yaml') as f:
    import yaml
    cfg = yaml.safe_load(f)
ext = cfg.get('skills', {}).get('external_dirs', [])
if isinstance(ext, list) and len(ext) > 0:
    for p in ext:
        print(f'  {\"✓\" if os.path.isdir(p) else \"✗\"} {p}')
else:
    print(f'PROBLEM: external_dirs is {type(ext).__name__} = {ext}')
"
```

## Step 5: New Session

External_dirs is read at process startup. Start a new Hermes session:

```bash
hermes  # fresh session
```

`/reload-skills` does NOT refresh external_dirs — it only rescans local `~/.hermes/skills/`.

## Recovery: Config Was Corrupted by yaml.dump()

If you accidentally used `yaml.dump()` on the full config and lost MCP servers or other settings:

1. **Don't panic** — the file is valid YAML, just missing entries.
2. Reconstruct missing MCP server blocks using the known-good format. Each server entry looks like:
   ```yaml
   mcp_servers:
     <name>:
       command: <exec>
       args: [<arg1>, <arg2>]
       cwd: "C:\\path\\to\\workdir"
       env:
         KEY: "value"
       connect_timeout: 30
   ```
3. Insert the blocks right after the `mcp_servers:` line using Python string insertion:
   ```python
   with open('config.yaml', 'r') as f:
       text = f.read()
   block = '''  graphify:
       command: python
       args: ["-m", "graphify.serve"]
       ...
   '''
   text = text.replace('mcp_servers:', 'mcp_servers:\n' + block)
   with open('config.yaml', 'w') as f:
       f.write(text)
   ```

## Verification Script

Save this as a quick health check and run after any config edit:

```python
import yaml, os

with open('$HERMES_HOME/config.yaml') as f:
    cfg = yaml.safe_load(f)

print('=== MCP Servers ===')
for name, srv in cfg.get('mcp_servers', {}).items():
    cmd = srv.get('command', srv.get('url', '?'))
    status = '✓' if 'command' in srv or 'url' in srv else '✗'
    print(f'  {status} {name}: {cmd}')

print('\n=== External Dirs ===')
ext = cfg.get('skills', {}).get('external_dirs', [])
if isinstance(ext, list):
    for p in ext:
        exists = os.path.isdir(p)
        print(f'  {"✓" if exists else "✗"} {p}')
else:
    print(f'  ✗ NOT A LIST (is {type(ext).__name__}): {ext}')

print(f'\n=== Key Sections ===')
for key in ['model', 'terminal', 'display']:
    if key in cfg:
        print(f'  ✓ {key}')

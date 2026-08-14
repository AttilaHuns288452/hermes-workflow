# Adding external_dirs on Windows — Configuration Guide

Hermes has two config files on Windows. The **active** one lives at:

```
C:\Users\<username>\AppData\Local\hermes\config.yaml
```

The `~/.hermes/config.yaml` file is a **profile override** (~1.4 KB) — it does NOT control external_dirs.

## Methods for Adding a New external_dirs Entry

### Method A — hermes config set (recommended)

```bash
hermes config set skills.external_dirs '["C:/Users/YOUR_USERNAME/.agents/skills"]'
```

Pass the full list as a JSON array string. `hermes config set` stores it as a JSON-encoded YAML string which Hermes parses correctly.

**Merging with existing dirs:** Read the current config value first, then include the full combined list:

```bash
# Read current (returns a YAML list or JSON string)
grep -A5 'external_dirs:' /c/Users/<user>/AppData/Local/hermes/config.yaml

# Set with all paths
hermes config set skills.external_dirs '["C:/Users/YOUR_USERNAME/Documents/Repos/external-skills/superpowers/skills","C:/Users/YOUR_USERNAME/Documents/Repos/external-skills/agent-skills/skills","C:/Users/YOUR_USERNAME/.agents/skills"]'
```

### Method B — sed (Quickest)

```bash
sed -i "/some-existing-entry/a\\    - C:/path/to/new/skills" /c/Users/<user>/AppData/Local/hermes/config.yaml
```

Replace `some-existing-entry` with a unique substring from an existing `external_dirs` line (e.g., `claude-seo/skills`). The `a` command appends after the matching line.

### Method C — Edit the file directly

Open the active config in a text editor and add the new `- C:/path/to/skills` line under `skills.external_dirs:`.

## Reloading

Unlike local skills (`/reload-skills`), `external_dirs` is read **only at Hermes startup**. After editing the config, you must start a **new session** for external skills to appear.

## ⚠️ NEVER Use yaml.dump() on the Full Config

```python
# DESTRUCTIVE — loses anchors, flow styles, MCP servers
cfg = yaml.safe_load(open('config.yaml'))
cfg['skills']['external_dirs'] = [...]
yaml.dump(cfg, open('config.yaml', 'w'))
```

The Hermes config is complex (18+ KB, 676+ lines). `yaml.safe_load()` + `yaml.dump()` drops flow-style sequences, anchors, and nested structures — this **will lose MCP server configurations**.

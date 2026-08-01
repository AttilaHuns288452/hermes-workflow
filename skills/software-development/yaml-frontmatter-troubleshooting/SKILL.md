---
name: yaml-frontmatter-troubleshooting
description: Diagnose and fix YAML frontmatter issues in SKILL.md files. Covers YAML parse errors from unquoted colons, CRLF line endings corrupting platform detection, and platform-unsupported errors caused by trailing whitespace.
version: 1.0.0
author: Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [yaml, frontmatter, troubleshooting, skill-authoring]
    related_skills: [hermes-agent-skill-authoring, skill-creator]
---

# YAML Frontmatter Troubleshooting

## When to Use

- A `skill_view(name=...)` call returns "Skill 'X' is not supported on this platform" for a skill whose `platforms` lists the current platform.
- A skill's frontmatter YAML fails silently and the skill is invisible to `skills_list` or `skill_view`.
- You need to diagnose why a SKILL.md doesn't load despite appearing to have valid frontmatter.

## Trap 1: Unquoted description with colons

**Symptom:** Skill doesn't load. `cat -A SKILL.md | head -5` shows normal-ending lines but `skill_view` returns an error.

**Root cause:** YAML reads `description: foo bar: baz` where `bar: baz` has a space after the colon → interpreted as a new top-level mapping key, not part of the value.

**Fix:** Wrap `description` value in double quotes if it contains `: `:

```yaml
# Bad — YAML sees `kepano/obsidian-skills.` as a mapping key
description: Read, search, create... Upstream: kepano/obsidian-skills.

# Good
description: "Read, search, create... Upstream: kepano/obsidian-skills."
```

## Trap 2: CRLF line endings corrupting platform matching

**Symptom:** Skill reports "not supported on this platform" despite `platforms: [linux, macos, windows]` in the frontmatter.

**Root cause:** File has Windows `\r\n` (CRLF) line endings. YAML reads the platforms list as `windows\r` (with trailing carriage return) instead of `windows`, which never matches the actual platform string.

**Detection:**

```bash
cat -A SKILL.md | head -5
# Lines ending with ^M$ = CRLF (broken)
# Lines ending with $ = LF (correct)
```

Or programmatically:

```bash
python -c "print('CRLF:', b'\r\n' in open('SKILL.md','rb').read())"
```

**Fix:**

```bash
sed -i 's/\r$//' SKILL.md
```

Then verify:

```bash
python -c "print('CR count:', open('SKILL.md','rb').read().count(b'\r'))"
# Expected: 0
```

## Trap 3: Leading whitespace before `---`

The validator checks `content.startswith("---")`. Any blank line, BOM, or whitespace before the opening `---` causes the entire frontmatter to be missed.

**Fix:** Ensure the file starts with `---` on line 1, no preceding content.

## Trap 4: Description exceeds 1024 chars

Enforced by `MAX_DESCRIPTION_LENGTH`. `skill_manage(action='create')` refuses descriptions over the limit.

**Fix:** Shorten or move detail to the body. The description is a trigger label, not a summary.

## Trap 5: `platforms` omitted

When `platforms:` is absent, some Hermes runtimes treat the skill as unavailable on all platforms.

**Fix:** Always include `platforms: [linux, macos, windows]` or the subset your skill actually supports.

## Quick Diagnostic

```bash
# 1. Check raw frontmatter
python -c "
import yaml, pathlib
raw = pathlib.Path('SKILL.md').read_text()
parts = raw.split('---', 2)
if len(parts) >= 3:
    try:
        fm = yaml.safe_load(parts[1])
        print('Platforms:', fm.get('platforms'))
        print('Name:', fm.get('name'))
    except Exception as e:
        print('YAML ERROR:', e)
else:
    print('NO FRONTMATTER FOUND')
"

# 2. Check line endings
python -c "
raw = open('SKILL.md','rb').read()
print('CRLF endings:', b'\r\n' in raw)
print('Starts with ---:', raw.startswith(b'---'))
"
```

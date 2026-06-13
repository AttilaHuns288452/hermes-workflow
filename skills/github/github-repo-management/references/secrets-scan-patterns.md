# Secrets & Path Sanitization — Scan Patterns

Patterns used during the pre-flight sanitization phase when publishing a static site to GitHub Pages. Run these before any push to a public repo.

## Credential / Token Scan

```bash
# Generic credentials
grep -in -E "(api[_-]?key|token|secret|password)" files-to-scan.html

# GitHub tokens
grep -in -E "(ghp_|gho_|ghu_|ghs_|ghr_)" files-to-scan.html

# OpenAI / Anthropic / generic API keys
grep -in -E "(sk-[a-zA-Z0-9]{20,}|sk-ant-[a-zA-Z0-9]{20,})" files-to-scan.html

# Slack tokens
grep -in -E "(xox[baprs]-)" files-to-scan.html
```

## Local Path Scan

```bash
# Windows paths (leaks local username)
grep -in "C:\\\\Users\\\\" files-to-scan.html

# Unix paths
grep -in "/home/" files-to-scan.html
grep -in "/Users/" files-to-scan.html

# file:// protocol (only works on author's machine)
grep -in "file:///" files-to-scan.html
```

## Username Scan

```bash
# Check against common sources
grep -in "$(whoami)" files-to-scan.html
grep -in "$(echo $USERNAME)" files-to-scan.html  # Windows
grep -in "$(echo $USER)" files-to-scan.html       # Unix
```

## JS-Specific Vulnerability Points

HTML/JS files often embed paths in these patterns:

```bash
# iframe src
grep -in 'iframe.*src=' files-to-scan.html

# window.open calls
grep -in 'window.open(' files-to-scan.html

# clipboard writes (leaky in public repos)
grep -in 'clipboard.writeText' files-to-scan.html

# img src pointing to local files
grep -in 'img.*src="[A-Z]:' files-to-scan.html
```

## What to Replace

| Pattern Found | Replacement |
|---|---|
| `C:\Users\RealUsername\...` | Relative path (`./file`) or `~/` or just the filename |
| `file:///C:/Users/RealUsername/...` | Remove entirely or replace with descriptive text |
| Real API keys / tokens | `<YOUR_API_KEY>` placeholder |
| `file://` links in iframe/window.open | Remove iframe; replace open with relative path |

## Verification After Sanitization

```bash
# Re-run all scans — should return zero matches
grep -c -E "(api[_-]?key|token|secret|password|ghp_|gho_|ghs_|ghr_|sk-|xox[baprs]-)" index.html
# Expected: 0

grep -c "C:\\\\Users\\\\" index.html
# Expected: 0

grep -c "file:///" index.html
# Expected: 0 (unless a legitimate data URI context)
```

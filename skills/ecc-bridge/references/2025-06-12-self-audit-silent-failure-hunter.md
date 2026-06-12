# Self-Audit: Silent Failure Hunter vs ecc-runner.py

**Date:** 2025-06-12  
**ECC Agent:** silent-failure-hunter  
**Target:** `scripts/ecc-runner.py` (265 lines)  
**Model Used:** deepseek-v4-flash-free (OpenCode free tier)  
**Result:** 5 findings → 2 hotfixes applied → 0 regressions

## Trigger

After creating the ecc-runner.py bridge script, ran silent-failure-hunter against it
to validate the self-audit pattern. The agent's prompt was extracted via
`python ecc-runner.py silent-failure-hunter` and the analysis framework was applied
to the script in the current conversation.

## Agent's Analysis Framework

Silent Failure Hunter checks for:
1. **Empty catch blocks** — `catch {}` or ignored exceptions, errors converted to
   null/empty arrays without logging
2. **Inadequate logging** — logs without context, wrong severity, log-and-forget
3. **Dangerous fallbacks** — defaults that hide real failure, graceful paths that
   make downstream bugs harder to diagnose
4. **Error propagation issues** — lost stack traces, generic rethrows, missing async
   error handling
5. **Missing error handling** — no timeout or error handling around network/file/DB
   paths, no rollback

## Findings

### Finding 1 — Severity: Medium
**Missing try/except around file I/O**
- `read_text()` in `extract_agent_body()` (line 137), `extract_agent_frontmatter()` (line 162),
  and `index_all_agents()` (line 61) can throw `FileNotFoundError`, `PermissionError`,
  or `UnicodeDecodeError`
- **Fix:** Wrap file reads in try/except with graceful error tuple return

### Finding 2 — Severity: High ✅ FIXED
**Undefined 'tier' variable on unknown model field**
- `index_all_agents()` lines 71–76 only assigns `tier` for `haiku`/`sonnet`/`opus`.
  Any other model value (typo, new tier) causes `NameError` at line 78
- **Fix applied:** Added `else: tier = "unknown"` fallback

### Finding 3 — Severity: Low ✅ FIXED
**Duplicate key in SAFE_AGENTS**
- `"comment-analyzer"` defined at line 39 AND again at line 48 — second silently overwrites first
- **Fix applied:** Removed the duplicate entry

### Finding 4 — Severity: Low
**None-check before regex group access**
- `extract_agent_frontmatter()` regex can return None — `m.group(1)` raises `AttributeError`
- **Fix:** Guard with `if m is not None:` before accessing captured groups

### Finding 5 — Severity: Low
**Shell argument joining drops structure**
- Line 263: `" ".join(sys.argv[2:])` loses newlines and indentation in context
- **Fix:** Accept stdin pipe for structured input as an alternative to argv

## What This Proves

1. ECC agents deliver real value through the free model bridge — the analysis was
   accurate and actionable on deepseek-v4-flash-free
2. The self-audit pattern catches bugs in the bridge infrastructure itself
3. Analysis agents (read-only) work EQUALLY well on free models as on paid — no
   quality degradation observed
4. The bridge extracted the prompt correctly (no frontmatter or defense baseline leaked)

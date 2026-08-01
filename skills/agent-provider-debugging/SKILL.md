---
name: agent-provider-debugging
description: Diagnose opaque errors from agent providers (Console/OpenCode, OpenCode Go, etc.) where the surface error message doesn't match the root cause. Covers DB schema mismatches, plugin crashes, and other internal server failures that manifest as generic HTTP errors.
version: 1.0.0
---

# Agent Provider Debugging

## When to Use

- Hermes shows `HTTP 400: Error from provider (Console): Upstream request failed`
- OpenCode CLI crashes with `D.split is not a function`
- OpenCode server logs show `SQLiteError: no such column`
- The error message says "upstream request failed" but rate limits are fine
- Model requests fail generically without useful details

## Key Principle

**HTTP 400 ≠ rate limit.** Rate limits return 429 (Too Many Requests) or 402 (Payment Required). A 400 with "Upstream request failed" means the upstream server crashed before it could process the request.

## Known Patterns

### 1. OpenCode SQLite DB Schema Mismatch

**Scenario:** Hermes Console provider returns HTTP 400, or `opencode run` crashes with `D.split is not a function`.

**Root cause:** OpenCode v1.16.2 shipped with code referencing new DB columns that the auto-migration never added. The Bun SQLite server crashes at startup or on first message.

**Diagnosis:**
```bash
# Check the server log for SQLite errors
grep "SQLiteError" ~/.local/share/opencode/log/opencode.log
# Expected: "no such column: replacement_seq" or "no such column: revision"
```

**Fix:**
```sql
ALTER TABLE session_context_epoch ADD COLUMN replacement_seq INTEGER;
ALTER TABLE session_context_epoch ADD COLUMN revision INTEGER;
```

The DB is at `~/.local/share/opencode/opencode.db` on Windows. Always backup first.

### 2. `@dietrichgebert/ponytail` Plugin Crash

**Scenario:** Any `opencode run` command immediately fails with `D.split is not a function` or `path must be a string or a file descriptor`.

**Root cause:** The ponytail plugin's Node module doesn't load correctly on Windows with OpenCode v1.16.2.

**Fix:** Remove the plugin from `opencode.jsonc`:
```jsonc
// Remove or comment out:
// "plugin": ["@dietrichgebert/ponytail"],
```

The ponytail skills directory (the `ponytail/skills` entry in the paths array) is fine — only the npm plugin causes the crash.

### 3. OpenCode Go Weekly Usage Cap

**Scenario:** Hermes returns errors when using `opencode-go/` prefixed models, but `opencode/` (Zen) models work fine.

**Diagnosis:**
```bash
grep "Weekly usage limit" ~/.local/share/opencode/log/opencode.log
```

**Fix:** Wait for reset (~1 day) or add paid balance at the OpenCode workspace URL shown in the log. Use `opencode/` (Zen) tier models as fallback in the meantime.

## General Diagnostic Protocol

When facing opaque provider errors:

1. **Identify the provider.** Error messages usually include the provider name in parentheses: `(Console)`, `(Console Go)`, `(OpenRouter)`, etc.

2. **Check the provider's server logs.** OpenCode logs are at `~/.local/share/opencode/log/opencode.log`. Look for `ERROR` or `SQLiteError` entries.

3. **Test the provider directly.** Bypass Hermes and call the provider CLI directly:
   ```bash
   opencode run --model <provider/model> "test"
   ```
   This separates Hermes routing issues from provider issues.

4. **Confirm the symptom ≠ the cause.** Generic "upstream request failed" errors almost never mean what they literally say — they mean something crashed between the request and the response. Trace the actual error from the provider's own logs.

## Pitfalls

- Don't chase rate-limit fixes (key rotation, adding credits) when the error is HTTP 400. 400 = bad request/server crash, not quota.
- The `D.split is not a function` error looks like a code bug but is almost always the ponytail plugin crashing. Fix the plugin first before debugging OpenCode internals.
- DB schema mismatches recur after OpenCode updates. If a new version ships and the Console provider breaks, check for new SQLite columns first.

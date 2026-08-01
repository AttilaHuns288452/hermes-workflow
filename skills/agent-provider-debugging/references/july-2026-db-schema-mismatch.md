# Session: OpenCode DB Schema Mismatch (July 25, 2026)

## Initial Report

User saw: `HTTP 400: Error from provider (Console): Upstream request failed`

User clarified: the error happened on `opencode/mimo-v2.5-free` model, not DeepSeek V4 Flash. The free tier wasn't capped — they switched models to message the agent and ask for a fix.

## What Was Wrong

The OpenCode v1.16.2 Bun SQLite server had two missing columns in `session_context_epoch`:

- `replacement_seq` (INTEGER)
- `revision` (INTEGER)

This caused the server to crash with `SQLiteError: no such column: replacement_seq` / `no such column: session_context_epoch.revision` on every request, which Hermes surfaced as HTTP 400.

## Secondary Issue

The `@dietrichgebert/ponytail` plugin crashed on every `opencode run` with `D.split is not a function` / `path must be a string or a file descriptor`. This blocked CLI-based diagnosis and masked the real DB issue.

## Diagnostic Trail

1. `cat ~/.local/share/opencode/log/opencode.log` → showed `SQLiteError: no such column: replacement_seq`
2. `python -c "import sqlite3; ..."` → inspected DB schema, confirmed column missing
3. `cat migration` table → last migration ran June 22, v1.16.2 shipped after
4. Added missing columns with ALTER TABLE
5. Retested → next error was `no such column: revision`
6. Added revision column
7. Verified: `opencode run --model opencode/mimo-v2.5-free "say hi"` → responds

## DB Location

Windows: `C:\Users\Attila\.local\share\opencode\opencode.db`

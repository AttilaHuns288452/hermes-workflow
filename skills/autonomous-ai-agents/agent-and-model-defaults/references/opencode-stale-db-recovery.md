# OpenCode Stale DB Recovery

## Symptom

```
opencode run '...' --model opencode/deepseek-v4-flash-free

Error: {
  "name": "UnknownError",
  "data": {
    "message": "Unexpected server error. Check server logs for details.",
    "ref": "err_..."
  }
}
```

With `--print-logs` or `--log-level DEBUG`:

```
ERROR service=server ref=err_... error=no such column: replacement_seq
cause=SQLiteError: no such column: replacement_seq
    at prepare (unknown)
    at prepare (bun:sqlite:345:37)
    ...
```

## Cause

OpenCode uses a local SQLite database at `~/.local/share/opencode/opencode.db`. When OpenCode is upgraded (e.g. via `scoop update opencode`), the new version may expect new columns that the old schema doesn't have. The `replacement_seq` column was added in v1.16.x.

If the database is locked by a running opencode process, the migration fails silently and every subsequent `opencode run` returns a server error.

## Fix

1. Kill all running opencode processes:
   ```bash
   ps aux | grep opencode
   # or on Windows:
   powershell -Command "Get-Process opencode | Stop-Process -Force"
   ```

2. Delete the stale database files:
   ```bash
   rm -f ~/.local/share/opencode/opencode.db
   rm -f ~/.local/share/opencode/opencode.db-shm  # may not exist
   rm -f ~/.local/share/opencode/opencode.db-wal  # may not exist
   ```

3. Retry the `opencode run` command. OpenCode recreates the database fresh with the correct schema.

## Prevention

- Always kill stale opencode processes before running DB-affecting operations.
- If OpenCode starts failing after a version upgrade, assume the DB schema is stale before debugging anything else.

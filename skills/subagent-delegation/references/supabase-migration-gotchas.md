# Supabase Migration Gotchas (CashFlow OS Session)

## Trigger functions break when SQL is split by semicolon
Supabase REST API `/database/query` runs ONE statement. Naively splitting migration SQL by `;` cuts PL/pgSQL function bodies in half — `$$...$$` blocks contain semicolons. 

**Fix**: Move triggers to app code (server actions), or run multi-statement SQL through `DO $$` blocks with EXCEPTION handling. App-code entity creation (e.g., in `signUp`) is more reliable than DB triggers on `auth.users`.

## `CREATE POLICY IF NOT EXISTS` is NOT valid PostgreSQL
PostgreSQL does not support `IF NOT EXISTS` on CREATE POLICY statements.

**Fix**: `DO $$ BEGIN CREATE POLICY "name" ON table FOR SELECT USING (...); EXCEPTION WHEN duplicate_object THEN NULL; END $$;`

## Auth trigger requires SECURITY DEFINER
Triggers on `auth.users` (Supabase-managed schema) require `SECURITY DEFINER` and may fail silently if permissions are insufficient.

**Fix**: Move entity creation to app code. The `signUp` server action inserts into `entities` after `auth.signUp()` succeeds. This avoids all auth-schema permission issues.

## Migration execution via REST API
The Supabase Management API endpoint `POST /v1/projects/:ref/database/query` runs ONE statement per call. Batch execution requires splitting by semicolons carefully (avoiding `$$` blocks), or using Python scripts with the `requests` library.

## CHECK constraints add AFTER table creation
`ALTER TABLE table ADD CONSTRAINT name CHECK (condition)` is safe and idempotent. Use `IF NOT EXISTS` for indexes: `CREATE INDEX IF NOT EXISTS`.

## Default values
`ALTER TABLE t ADD COLUMN IF NOT EXISTS c BOOLEAN DEFAULT false` — safe for idempotent migrations. New columns with defaults don't lock large tables in Postgres 11+.

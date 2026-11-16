# Encrypted secret storage & admin-configurable integrations

Use when an admin must set/rotate a third-party API key (or any credential) through the app UI: the secret must NOT be stored plaintext, must NOT reach the browser, and a new value must take effect without a redeploy. This is the `app_settings` + AES-256-GCM + runtime-lookup pattern.

## Why not just an env var
Env vars are frozen into the serverless function's snapshot at deploy time, so changing one needs a redeploy, and only a deployer (not an in-app admin) can set it. Storing the secret encrypted in a table and reading it per-request lets an admin rotate it live. Keep the env var as the fallback source.

## Pattern (pieces)

**1. Table (ciphertext only, never plaintext):**
```sql
create table app_settings (
  key text primary key,
  ciphertext text not null,
  iv text not null,
  tag text not null,
  updated_by uuid,
  updated_at timestamptz default now()
);
alter table app_settings enable row level security;
-- admin-only, all verbs (is_admin() gate lives in the DB):
create policy admin_read  on app_settings for select using (is_admin());
create policy admin_write on app_settings for insert with check (is_admin());
create policy admin_edit  on app_settings for update using (is_admin()) with check (is_admin());
```
(See `admin-role-gate.md` for the `is_admin()` function + the DB-enforced privilege rule.)

**2. Encrypt on write (Node, AES-256-GCM):** master key lives ONLY in a server env var (e.g. `SETTINGS_ENCRYPTION_KEY`, 32 bytes / 64 hex chars). Random 12-byte IV per write; return `{ciphertext, iv, tag}` base64; `decryptSecret` must verify the GCM tag.
```js
const key = Buffer.from(process.env.SETTINGS_ENCRYPTION_KEY, "hex"); // 32 bytes
function encryptSecret(plain) {
  const iv = crypto.randomBytes(12);
  const c = crypto.createCipheriv("aes-256-gcm", key, iv);
  const ciphertext = Buffer.concat([c.update(plain, "utf8"), c.final()]);
  return { ciphertext: ciphertext.toString("base64"), iv: iv.toString("base64"), tag: c.getAuthTag().toString("base64") };
}
function decryptSecret({ ciphertext, iv, tag }) {
  const d = crypto.createDecipheriv("aes-256-gcm", key, Buffer.from(iv, "base64"));
  d.setAuthTag(Buffer.from(tag, "base64"));
  return Buffer.concat([d.update(Buffer.from(ciphertext, "base64")), d.final()]).toString("utf8");
}
```

**3. Runtime lookup helper (DB-first, env fallback):** the serverless functions call this per request so a saved key applies immediately:
```js
export async function getLazadaKey() {
  // service-role client reads app_settings, decryptSecret(row) -> value
  if (dbValue) return { key: dbValue, source: "database" };
  return { key: process.env.LAZADA_API_KEY || "", source: "environment" };
}
```

**4. Admin config endpoint (service-role backed):**
- `GET` returns status only: `{configured, source, fingerprint: "ab12…xyz"}` — never the value.
- `POST` accepts the new value, `encryptSecret` + upsert. Return the same masked fingerprint.
- Auth: resolve the caller with their bearer JWT (`supabase.auth.getUser(token)`) AND `select is_admin()` — never trust a client-sent role/user id.

## Pitfalls
- **Master key lives only in server env, never in the DB.** A DB leak alone must not reveal any secret. Gitignore the local `.env.local` copy.
- **The master key is effectively immutable.** Losing/rotating it orphans every stored ciphertext (undecryptable). If you must rotate it, re-encrypt all rows in the same change.
- **Never echo the full secret** — not in GET responses, logs, or error messages. Masked fingerprint (`first4…last3`) only. A read-back after a write returns no value (providers mask it); trust the write's `200` + live behavior, not a value comparison.
- **Enforce admin at the DB boundary** (`is_admin()` RLS + the endpoint's server-side check), not just a hidden/absent button in the UI.
- **A toast over a state-only "save" is a silent lie** (see react-patterns Data Honesty): the write must hit the encrypted store and the consuming function must read it back at runtime before you report "saved".
- **Before debugging an integration failure "at the provider", probe the configured credential class.** A config row can hold test/sandbox credentials (`pk_test_…`/`sk_test_…` key prefixes, `mode: 'test'`) while the user exercises the real client — sandbox artifacts (payment QRs, redirect URLs) are rejected by the real thing exactly like an app bug would be. Read the key prefix and mode column first (a prefix is not a secret, so this probe is safe to display); when switching test→live, also retire pending sandbox rows — a create path that reuses a pending row hands back the stale test artifact instead of minting a live one.

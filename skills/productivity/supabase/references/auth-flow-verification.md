# Verifying Supabase Auth flows

## Redirect allow-list: where it is enforced

The OAuth `/auth/v1/authorize` endpoint 302s to the provider with whatever `redirect_to` was supplied — the redirect allow-list is enforced at the **callback**, not at authorize. A successful 302 (even with a foreign `redirect_to`) proves nothing about redirect safety. Verify by driving the callback: a foreign `redirect_to` must be rejected/dropped and a listed one must complete. Judge the config by what the callback does, never by the authorize response.

## Symptom: OAuth signs in but lands on localhost (or the wrong host)

When a provider (Google, etc.) completes sign-in and the app lands on `http://localhost:3000` or any host that is not the deployed one, the client's `redirect_to` was not in the allow-list, so the callback fell back to the **Site URL**. This is config-side — the sign-in code is usually already sending the correct `redirect_to`; diagnose the URL config before touching client code.

The setting lives only on the Dashboard at **Authentication → URL Configuration**:
- **Site URL** — the fallback when `redirect_to` is missing or unmatched. Set to the production origin (`https://<app>.vercel.app`). No wildcards here.
- **Redirect URLs** — the allow-list that makes `redirect_to` stick. Add the production origin with a wildcard (`https://<app>.vercel.app/**`). Wildcards ARE allowed here.

Access path: this is a dashboard **form** and is NOT editable via the project API keys (PostgREST exposes only `public`, never the `auth` config), not reliably via MCP `execute_sql` (often permission-denied), and only via a fresh management PAT (`sbp_…`, frequently stale/401). When those are unavailable, edit it through the owner's logged-in dashboard using the desktop-automation coordinate recipe in `live-database-access.md` Path 1 (it generalizes to any dashboard form: click the input, `ctrl+a`, type the value, Save). Verify by re-driving the OAuth flow and confirming it now lands on the production host.

## PKCE probes: false negatives

`signInWithOAuth({ skipBrowserRedirect: true })` on a client built WITHOUT `flowType: 'pkce'` returns a URL with no `code_challenge` and stores no verifier — which reads as "PKCE is broken". Build probe clients with `auth: { flowType: 'pkce' }` explicitly and assert `code_challenge_method=s256` in the returned URL before concluding anything about the auth flow.

## Sign-out scope and phantom sessions

`supabase.auth.signOut()` defaults to `scope: 'global'` — it revokes every server-side session the user has, not just the signing-out client's. With per-tab session storage (each tab holds its own session copy), the other tabs become phantoms: their JWT is still unexpired so PostgREST/RLS reads keep returning 200, but `auth/v1/user` returns `403 session_not_found`, so any flow that resolves the caller server-side (edge functions checking `auth/v1/user`) rejects with "invalid session". The shape is a split-brain: same user, same token — data reads work, identity-checked calls fail.

- **Discriminate the two auth layers with one probe pair.** Call `auth/v1/user` (session validity) and a PostgREST read (JWT validity) with the same token: 200/200 = healthy; 403/200 = phantom session (the user's exact "invalid session" report); 401/401 = dead token. Judge which layer failed before touching function code.
- **Match revocation scope to intent.** `signOut({ scope: 'local' })` revokes only the current session and keeps other tabs/clients alive; `scope: 'global'` is for "sign out everywhere". Per-session client storage + the global default is what manufactures phantoms.
- **Clear in-memory state on the `SIGNED_OUT` auth event.** A session/role context that learns about sign-outs only through its own `logout()` keeps rendering a logged-in shell after the server session is gone; subscribe to `onAuthStateChange` and drop user state on sign-out events.
- **Dead sessions need user-facing recovery.** A money/identity flow whose server call returns a session error must show "your session ended — sign in again" with a recovery action, never a spinner or a dead end; the error body's `code`/`message` is the discriminator (session errors vs validation errors), not the HTTP status alone.

## Test-harness auth hygiene

Supabase clients persist the session in `localStorage` by default — `context.clearCookies()` in Playwright does NOT log out: the next navigation auto-resumes the previous account, and role assertions silently test the wrong user. Clear `localStorage` + `sessionStorage` and re-navigate before each role's login in a multi-role E2E run. Also mind label collisions on auth screens: a landing page often has both a "Sign in" tab and a "Sign in" submit button, so a role/name locator matches the tab first — target the submit explicitly (scope to the form or take the last match).

## Origin changes

After any origin/domain change, drive signup, login, password reset, and OAuth end-to-end: emails still send when the landing origin is wrong, so delivery is not evidence. See `web-deploy-wiring` → `references/domain-migration.md` for the rename checklist.
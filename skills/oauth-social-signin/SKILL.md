---
name: oauth-social-signin
description: Use when adding or debugging third-party OAuth sign-in.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [web-development, auth, oauth, supabase, signin, google, verification]
    related_skills: [prototype-to-production, productivity/supabase, development/supabase-mcp-workflows, vercel-deployment]
---

# Third-Party Social Sign-in (OAuth)

Wire a social login button (Google/GitHub/Apple/Facebook) and get it to complete end-to-end against the identity provider (IdP). Two things cost the most time: (1) the redirect-callback the IdP validates is NOT your app URL, and (2) a rendered button is not proof the flow works. Verify by clicking through to the IdP, not by DOM presence.

## When to use
- Adding "Sign in with Google/GitHub/Apple/Facebook" to an app (usually alongside existing email auth).
- A social button redirects to the IdP but bounces back with an error (`redirect_uri_mismatch`, `unauthorized_client`).
- Verifying a social login actually completes before calling the feature done.

## Procedure
1. **Confirm the provider is enabled in the auth backend first.** For Supabase: Auth → Providers → Google must have a Client ID + Secret set. If it's not enabled server-side the app button is dead. Probe: hit the backend authorize endpoint (`/auth/v1/authorize?provider=google`) and confirm it 302-redirects to the IdP (`accounts.google.com`) rather than erroring.
2. **Register the AUTH BACKEND's callback URI in the IdP's console** — the #1 failure. For Supabase add `https://<project-ref>.supabase.co/auth/v1/callback` to the IdP's "Authorized redirect URIs" (Google Cloud Console → APIs & Services → Credentials → your OAuth client). The app's own URL is the post-login `redirectTo`, a DIFFERENT thing.
3. **Configure where the auth backend sends the user AFTER the IdP round-trip** — the other half of the redirect chain, and the #1 cause of "the sign-in lands on localhost." For Supabase: Authentication → URL Configuration → set **Site URL** to the deployed app URL (the out-of-box default is `http://localhost:3000`) and list every allowed return origin under **Redirect URLs** (`https://<app>/**`, plus `http://localhost:<port>/**` when you test locally). The frontend `redirectTo` must match a Redirect-URL pattern; if it does not, the backend silently falls back to Site URL.
4. **Wire the frontend button** to `auth.signInWithOAuth({ provider, options: { redirectTo: window.location.origin } })`. Reuse the existing auth client; do not build a parallel one. Give the button the app's secondary/outline style (e.g. `btn-ghost`) plus the provider's brand mark.
5. **Clean up stale auth copy.** If auth is real-only (no demo fallback), remove any "Demo mode / no account is created" copy — it misleads.
6. **Verify by clicking through, not by button presence.** Click the button, follow the redirect, and confirm you land on the IdP sign-in WITHOUT an error page. Decode any IdP error (below) before concluding the flow works.

## Diagnosing redirect errors
- The IdP bounces back with an error URL that encodes the cause. Google puts it in a base64 `authError` param — decode it to read the exact error code AND the `redirect_uri` the IdP saw. (`authError=<base64>` → e.g. `redirect_uri_mismatch` + the callback URI at issue.)
- `redirect_uri_mismatch` means the callback URI from step 2 is missing or wrong in the IdP console. Fix it there; no app code change is needed.
- Compare the decoded `redirect_uri` character-for-character against the IdP console entry (scheme, host, path; watch for trailing-slash and http/https drift).

## Pitfalls
- **Registering the app URL instead of the auth backend's callback** is the classic mismatch — the IdP validates the backend callback (Supabase `/auth/v1/callback`); the app URL is only the post-login redirect.
- **A completed sign-in lands on `http://localhost:3000`** — the auth backend's post-login **Site URL** is still the out-of-box default and the app origin isn't in its **Redirect URLs** allowlist, so the backend falls back to Site URL after the IdP round-trip. Fix the backend URL config (step 3), not the app code; the IdP side is fine.
- **A rendered OAuth button that goes nowhere** — presence in the DOM is not proof. Click it and follow the redirect to confirm it reaches the IdP cleanly.
- **Provider wired in the app but not enabled in the auth backend** — `signInWithOAuth` fires but the authorize step errors. Enable it server-side first (step 1).
- **A `skipBrowserRedirect` probe returns a URL with no `code_challenge`** when the auth client isn't built with `flowType:'pkce'` — a false negative that reads as "PKCE is broken." Build the probe client with PKCE explicitly before concluding anything about the auth flow.
- **Clicking the button in QA can land on an IdP error page (not the sign-in form)** — assert on the final URL/redirect target, not on the button's existence or the click succeeding.

## See also
- `prototype-to-production` (making auth real + honest states)
- `productivity/supabase`, `development/supabase-mcp-workflows` (backend auth/provider config via MCP)
- `vercel-deployment` (env vars + redeploy to ship the change)
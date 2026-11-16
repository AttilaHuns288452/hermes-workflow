# Domain / product rename

Every layer that holds an origin or a brand string has to move together. Order: host config → auth config → code sweep → deploy → live verification.

## Checklist

1. **Host**: add the new domain, keep the old one redirecting to it (307/308 at the host level). Verify the redirect response itself before anything else.
2. **Auth config**: add the NEW origin to the auth provider's Site URL and redirect allow-list (keep the old origin listed until cutover is confirmed — old links carrying tokens still land there). Same for the OAuth provider's console: authorized origins AND redirect URIs.
3. **Code sweep** for hardcoded origins and brand strings: page titles, meta/OG tags, manifest and service-worker scope, payment description strings, email templates, CORS origins, QA/script base URLs, docs. Grep source AND the deployed bundle — a string baked into an old build is not fixed by a source edit.
4. **Deploy**, then verify the LIVE build (cache-bust query param). Deploy status success is not proof the new build serves: poll the deployment whose commit SHA matches the push, then confirm bundle markers on the live URL.
5. **Auth flows last**: signup, login, password reset, OAuth. Redirect allow-list enforcement and PKCE probe pitfalls live in the `supabase` skill → `references/auth-flow-verification.md`.

## Pitfalls

- A host-level redirect for the old domain does not move auth callbacks: the auth server redirects to the origin in its own allow-list, so a rename that updates only the host leaves reset/OAuth emails pointing at an origin nobody listed.
- Reset and magic-link flows break silently on an origin change — the email still sends, the landing page 404s or drops the token hash. Drive the flow end-to-end after the rename, never infer it from config.
- QA fixtures and smoke scripts that hardcode the production origin silently retarget the old host after a rename and keep passing against whatever still answers there. Grep test/QA trees for the old origin and make the base URL an explicit input.
- Verify rename completeness in the minified bundle with brand/origin strings plus identifier markers (see `web-deploy-wiring` step 6) — label copy alone is unreliable evidence.
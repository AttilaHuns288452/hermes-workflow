# Supabase Auth Quirks

Auth gotchas specific to Supabase (the auth backend behind this user's web
apps). General auth rules live in the SKILL.md.

## PKCE recovery redirect: a hash route swallows the token

`resetPasswordForEmail(email, { redirectTo })` makes Supabase append its recovery
token **to whatever URL you pass**. If that URL ends in a hash route
(`origin + "/#/login"`), the token is appended inside the fragment, where
`detectSessionInUrl` never looks. No recovery session is created and the
"choose a new password" screen never appears - the user reports the reset link
"doesn't work".

Fix: redirect to the origin root (or a dedicated path with no hash) and let the
app route from there once the session is established.

## Email confirmation needs its own redirect

`signUp` takes `options.emailRedirectTo`. Without it the confirmation link uses
the project's dashboard Site URL, so a preview or secondary deployment sends
users to the wrong host. Set it explicitly per deployment origin.

## `signInWithOAuth({ skipBrowserRedirect: true })` false-negatives PKCE

On a client built without `auth: { flowType: 'pkce' }` this returns an OAuth URL
with **no `code_challenge` and no stored verifier** - a probe that reads like
"PKCE is broken" when the probe client is the problem. Build probe clients with
`flowType: 'pkce'` explicitly and assert `code_challenge_method=s256` before
concluding anything about the auth flow.

## `signUp` on a shared client auto-switches the session

A successful `signUp` on the same client used for other writes switches that
client's session to the new user, so any role/profile row written afterwards
fails RLS (`new row violates ... policy`) because it is now the brand-new,
unprivileged identity. Create accounts through an isolated anon client and do
the privileged writes from the client that owns them.

## Provider rate limits surface as raw error text

`resetPasswordForEmail` is throttled (roughly one per address per interval),
and the built-in email service (no custom SMTP) sends only **2 emails per hour,
best-effort** — that cap is the whole E2E email budget, shared across signup
confirmation and every recovery/resend attempt. Budget the sends across the
test plan, and stop parallel QA workers from triggering emails mid-run or they
consume the quota before the real test starts.

The raw message (`email rate limit exceeded`) is not actionable. Translate it
at the auth seam: say what is limited and that retrying later works. Do not
disable or bypass the limit.

`resetPasswordForEmail` also returns success for addresses with no account
(enumeration protection) — "accepted" never proves an email was sent, so
delivery is confirmable only from a mailbox.

## Recovery email: link vs code decides the whole recovery UX

Template variables: `{{ .Token }}` is a **one-time code whose digit length
follows the dashboard's "Email OTP length" setting** (commonly 6, some projects
8) - read the setting instead of assuming a length, `{{ .TokenHash }}` its
hashed form for building custom links, `{{ .ConfirmationURL }}` the classic
reset link. GoTrue's default recovery mail has shipped both link-only and
"follow this link ... Alternatively, enter the code: {{ .Token }}" variants,
so **read one really delivered email** before designing recovery UI around a
code length - the docs describing the variable do not tell you which template
your project's mail actually uses.

When inspecting the template from a logged-in dashboard session, trust the
editor's own content, not the page HTML: the dashboard renders a list of
"available variables" that includes `{{ .Token }}` on the same page even when
the template body never uses it. The template editor is Monaco - read
`window.monaco.editor.getModels()` (pick the model whose value contains
`{{ .ConfirmationURL }}`) and confirm the token in THAT value before claiming
the email carries a code.

Editing templates is blocked in the dashboard until a custom SMTP server is
configured ("emails will be sent using the default templates"). Without SMTP,
the only template-edit path is the Management API
(`PATCH /v1/projects/{ref}/config/auth` with a personal access token — the
project's anon/service keys do not authenticate it). If the default mail shows
no code, same-tab OTP recovery cannot be completed by users until one of those
is configured: report it as a configuration blocker with exact manual steps
rather than working around it in app code.

## Dashboard-side configuration (handoff items, not code)

- **Site URL** and **Redirect URL allowlist** must include every deployment
  origin (production, preview, local dev). Symptoms when wrong: OAuth and email
  links land on the wrong host or error - and a 400 from the recovery request
  before any email is sent.
- **Email templates** (confirmation, recovery) contain the link the user
  actually clicks - they cannot be verified without mailbox access.
- **Auth policy settings** (email OTP length, password requirements, require
  current password when updating) are the source of truth the app code must
  mirror - see SKILL.md step 1.
- Report both as explicit handoff items; they cannot be changed from the repo.

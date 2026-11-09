---
name: auth-flows
description: "Build or fix web auth: sign-in, sign-up, reset, OAuth."
---

# Auth Flows

Build and harden the authentication surface of a web app: sign-in, sign-up,
password reset, email confirmation, and OAuth, then verify each flow against the
real provider. Triggers: adding auth to an app, "sign in is not behaving", broken
reset or confirmation links, auth form complaints. Provider-specific quirks live
in `references/supabase-auth-quirks.md`.

Audit/verification method for auth (role walkthroughs, cross-user isolation,
live token probes) belongs to `webapp-release-qa`; this skill is about building
the flows correctly in the first place.

## Procedure

### 1. Establish the provider's real policy before writing form rules

Read the auth provider's configured policy (password length/complexity, whether
email confirmation is mandatory, redirect allowlist) and mirror it exactly in the
form's `minLength`, hint copy, and client validation. A form that advertises one
rule and the backend enforces another sends users into a dead end on submit.
Put the mirrored rules in ONE shared validation helper called by every password
form (sign-up and all password-set screens): separate copies drift the next
time the provider setting changes, and only one of them gets fixed.

### 2. Forms carry their machine semantics

Every auth input gets an `autoComplete` token. Without them password managers
fill the wrong field or nothing at all, and users read the form as broken:

| Field | autoComplete |
|---|---|
| Email / username | `email` / `username` |
| Display name | `name` |
| Password (sign-in) | `current-password` |
| Password (create / change) | `new-password` |
| OTP code | `one-time-code` |

Password creation always gets a **confirm** field; password change gets current
+ new + confirm. Validate the mismatch client-side and return **before any
provider call** - a mismatch must never create an account, consume a reset
token, or burn a rate-limit slot.

### 3. Normalize at one seam, not per form

Trim the identifier where the auth client is invoked (sign-in, sign-up, reset),
not in each page's submit handler. Pasted whitespace is the most common
user-side failure and one seam covers every caller and every future form.

### 4. Error copy is generic and actionable, never enumerating

- One message for wrong password AND unknown account. Any wording that
  distinguishes them ("no user with that email", "not registered") is account
  enumeration and belongs in neither the message nor the response shape.
- Translate provider error text at the same normalization seam into something a
  user can act on (a rate limit says what to wait for and how long), while
  stripping the provider's internal phrasing.
- Emit a success message only after the provider returns success - never from
  the click handler. A gated or slow call that later fails leaves a false
  "check your email" on screen.

### 5. Redirect targets are derived, never hand-assembled

Build `redirectTo` from `location.origin` (or a configured absolute base URL).
Never append a hash route to it - see the reference for why that silently
breaks the recovery handoff. Email confirmation needs its own redirect option;
without one the provider's default Site URL wins and the user lands on the
wrong deployment. The Site URL and redirect allowlist are dashboard-side and
are the user's to configure - name them explicitly as a handoff item.

### 6. Authorization lives at the resource layer

Hiding admin UI is not access control. Enforce role checks where the data is
served (RLS policy, `is_admin()` RPC, server middleware) and verify by acting as
the unprivileged identity against the same endpoint. See
`webapp-release-qa` -> `references/backend-trust-boundaries.md`.

### 7. Same-tab OTP recovery

Prefer the staged same-tab flow (enter email → enter code → set new password →
success → sign in) over the emailed reset link whenever the provider's email
can carry a code. Rules that hold for every implementation:

- Verify every submitted code with the provider's RECOVERY verification call
  (`verifyOtp({ email, token, type: 'recovery' })` in Supabase). The
  passwordless sign-in OTP call is a different flow — never substitute it. A
  code is never accepted by shape (length/digit count alone), not even
  optimistically while typing.
- The set-password form renders only after the provider confirms verification.
  Password change happens on the authenticated recovery session via the
  provider's user-update call, and "password updated" is emitted only from that
  awaited result.
- A verified recovery session is a real session: generic "already signed in"
  redirects fire on it. Recovery state must outrank them until the password is
  actually changed and must survive a refresh (persist the stage keyed to the
  recovery session) or the user is bounced into the app mid-flow.
- Every stage carries: the masked destination email, resend with cooldown, a
  way back to correct the email, and the same generic non-enumerating copy as
  the request stage.
- Confirm the delivered email actually SHOWS a code before promising a
  code-entry experience (see `references/supabase-auth-quirks.md` — the default
  recovery mail may be link-only), and match the input to the code format the
  email really delivers.

### 8. Admin-created accounts yield a handover credential

When an admin form creates another user's login (staff, dentist, team member),
the result must include a **temporary password shown once** with a copy button
and handover guidance — the admin needs a credential they can say out loud.
Pair it with a forced password change at first sign-in (`must_change_password`
gate or the provider's equivalent), so the shared secret is short-lived.
Invite-email-only provisioning hides any credential and dead-ends the admin
when email delivery is slow or untrusted; an invite email may be an ADDITIONAL
channel, never the only one. Create the account with the temp password first,
then any convenience email — never let the email path suppress the display.

## Verification (runnable, real provider)

1. **One isolated browser context per scenario.** Shared contexts leak the
   session: a second scenario's page bounces to the app's home as "already
   signed in", and the probe reports the wrong flow as broken.
2. **Test validation without creating accounts.** Guards that return before the
   provider call (mismatch, too-short password) can be exercised on throwaway
   emails with zero side effects. Only create an account when the flow under
   test is account creation itself, and clean it up.
3. **Assert feedback on the form's own alert element** (`[role=alert]` scoped to
   the form), not on `body` text. Brand/marketing panels contain copy that
   false-matches success and error phrases and turns a correct failure into a
   reported "success".
4. **Sign-in success is a protected surface rendering**, not "no error shown":
   a signed-in indicator or sign-out control plus a route that only authenticated
   users reach.
5. **Password recovery is verifiable to the provider boundary — and for OTP
   flows that boundary is reachable.** The recovery credential exists only in
   the delivered email (link or code). With a readable mailbox, read the
   emailed code and complete the flow end to end; without one, the provider's
   own admin API can issue a real recovery token for a controlled test account
   — report which leg was exercised. Always report the honest subset (request
   returns success and the app shows its confirmation state; expired, used and
   malformed codes degrade honestly; the new-password form rejects a mismatch
   before any provider call). Never insert tokens into storage or "verify" in
   client state to simulate the leg.
6. **Route guards must be tested cold** (`page.reload()` or a fresh tab). In-app
   navigation keeps an already-resolved session and hides a guard that decides
   before the session has settled.

## Pitfalls

- **A password-reset link that "does nothing" is usually the redirect URL, not
  the token.** Appending a hash route to `redirectTo` makes the provider append
  its token inside the fragment, where a hash router's session detector never
  reads it - so no recovery session is established and the "set a new password"
  screen never appears. Redirect to the origin root instead.
- **Success copy rendered from the click handler is a lie by construction.**
  Every auth outcome message must come from the awaited provider result. The
  same holds for fire-and-forget background writes: a local-first save with an
  un-awaited sync mirror must await that mirror and report its failure
  distinctly ("saved here, could not sync"), or the toast claims a write the
  database never received.
- **An auth wrapper that discards the provider's returned result turns every
  caller's failure branch into dead code.** A `signOut`/`signIn` helper that
  awaits the SDK call and returns nothing leaves callers checking
  `res && res.error` against forever-undefined — a failed logout still navigates
  away and renders as success. Return the `{ error }` object from the wrapper
  and let callers navigate only on the non-error path.
- **Confirm fields must live on the form that creates the secret**, not only on
  the form that resets it. A missing confirm on sign-up turns one typo into a
  locked-out account.
- **`autoComplete` belongs on the field, not the form.** Autofill heuristics key
  on the input; a form-level attribute is ignored.
- **Never weaken a generic error to "help" the user.** "We couldn't find that
  email" is the enumeration bug, however friendly it reads.
- **Recovery/reset routes render the auth layout only — zero app nav — even for
  an authenticated user.** Route gates exempt recovery links (so the deep link
  can establish its session), and the exemption lets a signed-in session fall
  through to the full app shell, navbars included. Every nav item is an escape
  hatch out of the token-consuming flow: one click walks the user away mid-reset
  and the flow dies with it. Land recovery routes on the auth chrome regardless
  of session state, and verify the chrome-free state while SIGNED IN, not just
  signed out.
- **Browser QA: `clearCookies()` does not clear a localStorage-persisted
  session.** Supabase (and similar) keep the session token in localStorage
  (`sb-*` keys), so a Playwright context that only clears cookies silently
  auto-resumes the previous user and every role assertion tests the wrong
  identity. Clear `localStorage` + `sessionStorage` and re-navigate before
  each role's sign-in.
- **`signOut()` defaults to `scope: 'global'` — it revokes every server session
  the user has, not just the current tab's.** With per-tab session storage
  (sessionStorage), the other tabs keep a JWT that passes data-layer reads but
  fails the provider's user check ("invalid session") — a phantom signed-in
  shell that dead-ends on the next authenticated call, with no error until
  then. Use `scope: 'local'` for ordinary logout, and subscribe the provider's
  auth-state listener (`onAuthStateChange`) in whatever store holds in-memory
  user state, so an external revocation (another device, admin kill) clears the
  shell instead of leaving it logged in.

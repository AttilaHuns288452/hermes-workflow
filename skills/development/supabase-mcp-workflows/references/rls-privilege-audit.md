# RLS & Privilege Audit Rules (Postgres/Supabase)

Rules for auditing or hardening a backend's privilege surface. Each: the trap, then the mechanism.

## Policy semantics

- **Permissive policies OR together** — adding a restrictive policy NEVER
  neutralizes an existing permissive one. To deny a role you must drop/fix the
  permissive policy; audit by enumerating ALL policies (`pg_policies`) and
  reasoning about their OR, never by looking at the policy you just added.
- **Dropping a bundled `ALL` policy silently drops its SELECT half too** —
  `INSERT ... RETURNING` then fails with the MISLEADING "violates row-level
  security policy" (rows are RLS-filtered on return), and plain reads return
  empty without error. When an insert-with-returning suddenly fails, check for
  a missing SELECT policy before doubting the insert check. `UPDATE` needs
  SELECT for the same reason.
- Deny-by-default beats deny-policy: revoking role privileges entirely and
  granting one explicit path is auditable; a policy tangle is not.

## SECURITY DEFINER functions

- **The real boundary of a definer function is EXECUTE grants, not table
  RLS.** A SECURITY DEFINER function callable by client roles runs with its
  owner's rights and bypasses every table policy — a checked-forgeable audit
  path through the table can be re-opened through the RPC. After any RLS
  lockdown, enumerate callable functions (`has_function_privilege`) and revoke
  client EXECUTE on privileged helpers; grant to `service_role` explicitly
  (see the `REVOKE FROM public` trap in the parent skill).
- Definer functions must do their own input authorization (assert the acting
  role inside the body), not rely on the caller's table access.

## Verification

- **Adversarial checks must ATTEMPT the operation with a real role session**
  (raw REST/SQL as anon/authenticated), never conclude from reading policies —
  privilege bugs live in the gap between the intended and the granted set.
- Verify that a revocation bites: call the RPC as the client role and expect
  the permission error; verify that legitimate server-side callers still work.

---
name: confirmation-and-feedback
description: Use when adding confirm dialogs and truthful feedback.
---

# Confirmation And Feedback

Give every meaningful user action the right amount of friction and the truth
about its outcome. Triggers: "add confirmation dialogs", destructive-action
safety pass, "the app says saved but it wasn't", false-success or silent-failure
complaints, action-safety audits.

## Procedure

### 1. Inventory before wiring

Enumerate every state-changing action (mutations, auth calls, localStorage
writes, admin CRUD) with: call site (file:line), what happens today, loading
state, success message, error handling. Two questions per action:

| Question | Confirm dialog? |
|---|---|
| Irreversible or expensive to undo (deletes, clears of user data, privilege grants, sign-out with unsaved work, credential rotation, account closure) | YES |
| Ordinary reversible toggle (wishlists, compare lists, filters, approve/reject that can be flipped back) | NO |

Confirmation is friction: a reversible action gated behind a dialog reads as
tedium, and users learn to click through dialogs, which defeats the ones that
matter.

### 2. One shared primitive, built on the app's existing modal

Do not hand-roll per-action dialogs. Wrap the existing modal component (which
should already own focus trap, Escape, focus restore) in a `ConfirmDialog`:

- Props: `title`, `message`, `confirmLabel`, `cancelLabel`, `danger`, `busy`,
  `error`, `onConfirm`, `onClose`. Context-specific action labels ("Delete",
  "Sign Out", "Grant admin"), never a bare "OK".
- `danger` variant uses the destructive button style; neutral otherwise.
- **`busy` disables BOTH buttons AND swallows Escape/backdrop close** (pass a
  no-op as the modal's onClose while busy) — a running operation must not be
  double-submitted or abandoned half-way with a stale UI.
- `error` renders inline in the dialog (role="alert"), so a failed confirm
  explains itself where the user is looking instead of a toast that vanishes.
- The message names the item and the consequence ("Permanently delete
  <name>? This cannot be undone"), not just "Are you sure?".

For especially consequential operations (credential rotation, mass delete),
type-to-confirm is justified; for ordinary deletes it is tedious.

### 3. Execute for real, report the real result

- `onConfirm` awaits the actual operation. Success copy and navigation happen
  ONLY on the awaited success path; failure keeps the dialog open (or shows the
  inline error) with user input preserved.
- Duplicate-submission prevention: the busy state starts before the call.
- A confirmation dialog is NOT a security boundary — permissions stay enforced
  at the resource layer regardless of what the UI gates.

### 4. Truthful feedback everywhere else too

- Success toast fires after the write lands. A local-first write with a
  background sync must await the sync and report its failure distinctly
  ("saved on this device, could not sync"), never a flat "Saved".
- Feedback colors are semantic: **success = green, caution = amber** (data/API
  warnings, degraded or quota-limited states), **destructive = red**. Confirmed
  destructive account actions (sign-out) use the muted-red destructive button
  treatment even when nothing failed. Color/icon must match the message class —
  the default success styling on a failure message trains users to ignore both.
- Buttons whose label encodes state ("Add to Wishlist" / "In your Wishlist")
  must re-read the state after the action; a static label lies after the click.
- In-flight guards belong on the button (`disabled={busy === row.id}`); state
  that is set but never read is not a guard.
- Copy that narrates a workflow ("Submit for moderation", "reservation fee",
  "pending approval") goes stale the moment the workflow changes. Whenever
  enforcement moves (auto-approve at insert, fee removed), grep the UI for the
  old workflow's words and fix the copy in the same change — the button label
  is what users read first.
- Derived aggregates next to an action (counts, averages, totals) must refresh
  from the mutation's result within the same interaction; a stale count beside
  a just-created item reads as the write failing.
- Copy names the concrete object of the action ("Paying for: Tooth Filling"),
  not a generic explanation of what the action is for. Benefit/exposition
  sentences ("this payment is the full service payment which confirms your
  slot") are deleted on sight; the label of the thing being acted on is what
  the user wants to read.
- A preview must show the COMPLETE effect of the current configuration. A
  windowed view (month calendar, carousel page, paginated list) hides most of a
  generated schedule and reads as "only one item exists" — pair the window with
  the full computed list (e.g. "All N session dates" chips under the calendar)
  so every configuration change is visible at a glance.

### 5. Unsaved-changes guards (dirty forms)

Where an edit form can hold meaningful work (admin CRUD forms, profile
editors, multi-field settings), a Cancel or close must not silently eat it:

- Snapshot a `pristine` copy of the form object when the editor opens
  (`openForm(f) => { setForm(f); setPristine(f); }` — one opener helper so
  every open path records the snapshot).
- Dirty = `JSON.stringify(form) !== JSON.stringify(pristine)` plus any
  out-of-band state (pending photo upload, remove-photo flag, added rows).
- Route the close through ONE guard used by every exit (Cancel button,
  backdrop click, Escape): dirty opens a discard confirm, clean closes
  immediately — an unedited form cancelling through a prompt is the tedium
  this skill exists to avoid.
- The discard dialog uses context-specific labels: confirm "Discard
  changes", cancel "Keep editing" (a bare "Cancel" inside a cancel flow is
  unreadable). Confirming discards and closes; keeping editing restores
  focus to the form with input intact.
- Navigation-away guarding is separate and weaker: browser `beforeunload`
  can only warn, never offer a choice, and client routers without blockers
  (HashRouter) cannot intercept in-app route changes at all. Guard the
  in-app close paths and say plainly which exits stay unguarded rather than
  implying protection that does not exist.

## Verification (real browser)

Exercise the dialog journeys, not just the build: open → Cancel keeps state
unchanged; Escape closes and state unchanged; confirm runs the real operation
and success appears only after it; a forced failure (invalid input, revoked
session) shows the error and does NOT navigate or claim success; rapid
double-click on confirm submits once. Screenshot the dialog itself.

## Pitfalls

- A wrapper that discards the operation's returned `{ error }` makes every
  caller's failure branch dead code — the failure path exists in the UI and can
  never fire. Return the result from the wrapper seam.
- Multiple entry points to the same action (header, profile page, admin shell)
  must ALL confirm; wiring one and leaving the others instant is the most common
  half-done result of this pass.
- Dialog state lives in the component that RENDERS the dialog. A patch that
  inserts `useState`/handlers into one component and the dialog JSX into its
  parent or sibling compiles green and throws `x is not defined` at render the
  first time the flow opens — one broken dialog takes the whole screen down
  through the error boundary. Give each owning component its own state, or lift
  state and JSX together.
- Migrating an existing hand-rolled confirm modal to the shared primitive is
  part of the job: two subtly different dialogs for the same class of action
  drift immediately.
- Optimistic UI without a rollback path: if the mutation fails and the list
  already changed, restore it — or do not optimistically update at all.
- Two dialogs at once (a discard confirm over an edit modal) stack by DOM
  order at equal z-index: the one rendered FIRST is painted UNDER the
  later modal's backdrop and its buttons are unreachable. Render the new
  dialog after the existing one, or wrap it in a `relative z-[95]` stacking
  context above the modal's z-90. Tell: "the confirm appeared but clicking
  it did nothing" = it is under another overlay.
- Nested dialogs also confuse name-scoped locators in tests: `getByRole(
  'dialog').last()` picks the wrong one when the new dialog renders earlier
  in the DOM. Filter by the dialog's own copy (`hasText: "Discard"`).

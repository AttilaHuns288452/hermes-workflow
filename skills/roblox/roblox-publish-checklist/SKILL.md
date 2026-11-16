---
name: roblox-publish-checklist
description: "Use before publishing or updating a Roblox experience to run evidence-backed release gates and a pre-release audit"
---


# Roblox Publish Checklist

## When to Load

Load before publishing or updating a live experience. Test the surfaces and risks the change introduces.

## Quick Reference

### 1. Define the release

Record the changed places, scripts, assets, configuration, schemas, products, supported devices, and rollback path. Classify each gate as required, conditional, or not applicable before testing.

### 2. Block on high-consequence failures

- **Persistence changed:** load, save, migration, duplicate-session, disconnect, and shutdown behavior. Load `roblox-data` or `roblox-server-data`.
- **Remotes or authority changed:** validate types, bounds, state, ownership, replay, and abusive frequency. Load `roblox-networking` and `roblox-security`.
- **Purchases changed:** test durable, idempotent receipt grants and retries. Load `roblox-monetization`.
- **Cloud auth or webhooks changed:** verify secrets, scopes, callback state, retries, signatures, and deduplication. Load `roblox-cloud`.

A failed high-consequence gate means NOT READY. Do not average it into a percentage. Precedence: user approval authorizes an otherwise permitted action; it does not satisfy a mandatory policy and does not turn a failed or unverified gate into PASS.

### 3. Exercise the shipped surface

- Run one normal flow plus failure, retry, leave/rejoin, and rapid-input cases relevant to the change.
- Test every supported input mode and representative viewport/device tier.
- Measure errors, memory, frame/network cost and streaming.
- Verify focus, touch targets, readable contrast, non-color state cues, reduced motion, and localized overflow where applicable.
- Confirm Dashboard metadata, permissions and policy.

### Prove the publish actually landed

A closed dialog is not a publish. Verify in this order, and never stop at step 1:

1. **Timestamp.** Poll the public games API and require the `updated` field to MOVE past the value you read before publishing:
   `curl -sS "https://games.roblox.com/v1/games?universeIds=<id>"` → `data[0].updated`. Unchanged timestamp means nothing shipped, whatever the UI showed.
2. **Source marker readback.** Read a script's `Source` back out of the PUBLISHED place (bridge/MCP `script_read`) and grep for a string that only exists in this change. A live place can be several publishes stale while the editor shows your newest code.
3. **Behaviour.** Only then run the player-facing check.

Publishing from Studio's own dialog, before anything else:

- **Stop play mode (`shift+F5`).** With a playtest running the dialog binds to the Client datamodel and every Overwrite click is a silent no-op. Studio's log says so: `StudioPublishServiceDependencies: setComponents: not the edit data model, nothing to do`.
- **Dismiss stray child windows first.** An open modal (shortcuts dialog, leftover file picker, an "Invalid path" alert) eats the keystrokes and clicks aimed at the publish dialog while `getactivewindow` may already report the right window. Enumerate every visible window and look for unexpected extras.
- **Never conclude from the dialog closing, and never `windowkill` a Studio child window** to get rid of one — it can take the parent Studio process with it and lose the session's unsaved work.

Driving the overwrite sequence (the path that actually ships over an existing place):

1. `alt+p` while the viewport has focus. If nothing appears, a stray modal is eating it — see above; fix that before retrying.
2. Click **"Update existing experience…"** at the bottom-left of the dialog. Plain `alt+p` alone starts a NEW experience, which is how a build silently goes to the wrong place.
3. Pick the experience card, then the first place row (the radio must show selected before Overwrite enables).
4. Click **Overwrite**, then verify by the `updated` timestamp — never by the dialog.

Button coordinates rot between sessions and window states. Locate the primary button on *every* attempt by sampling its fill colour in the dialog's own geometry (`#3359FF`-ish blue) and clicking the centre of the returned bounding box, rather than reusing an offset that worked once. A click 70px high in a dialog with a large empty body hits nothing and reports no error at all.

### 4. Require evidence

Every PASS cites a test, log, profiler capture, readback, screenshot, or dashboard inspection. UNVERIFIED if unavailable; approval is not evidence.

### Output

`READY`, `NOT READY`, or `READY WITH ACCEPTED RISK`; blockers first, then warnings, unverified gates, evidence, rollback plan, and skipped gates with reasons.

> Details: [references/full.md](references/full.md)

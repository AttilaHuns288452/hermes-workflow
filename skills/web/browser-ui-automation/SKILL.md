---
name: browser-ui-automation
description: "Use when driving a web app UI via browser tools, no API."
---

# Browser UI Automation

Drive a web app UI through `browser_exec` (local browser) when no usable API/CLI path exists but the user's browser is logged in — creating Google Forms, filling SaaS wizards, operating web dashboards. Also the fallback when API auth is missing for an otherwise API-covered surface. The technique rests on three things: trusted clicks (not synthetic events), hit-tested coordinates (not assumed targets), and verification in a read-only surface (not the editor's own DOM).

## Procedure

1. **Route check first.** If an API or CLI with auth exists, use it instead (e.g. `google-workspace` for Google surfaces). Probe auth (`setup.py --check`-style) before choosing — the fallback decision must be evidence-based, not assumed.

2. **One tab per document.** Open the editor exactly once; list open targets (`cdp('Target.getTargets')`) and close duplicate editor tabs (`Target.closeTarget`) before editing. Two editors on one document clobber each other's autosaves and edits silently revert.

3. **Foreground the tab** with `cdp('Page.bringToFront')` before every interaction batch. Whenever clicks or menus misbehave, check `document.visibilityState` first — a backgrounded tab freezes CSS/WAAPI animations, so dropdowns render at zero height and coordinate clicks silently miss.

4. **Map the page** before acting: `document.body.innerText` for true app state (toasts, dialogs, modes), plus JS enumeration of roles/aria-labels with `getBoundingClientRect()`.

5. **Click via coordinates.** Compute the rect in JS, click with `click_at_xy`. Hit-test first with `document.elementFromPoint(x, y)` to confirm the intended element (not a toast, scrim, or floating toolbar) receives the point; transient toasts hover over buttons and swallow clicks — click an exposed point of the button or wait for the toast to clear. Synthetic `.click()` on component-framework widgets (Material, JSX handlers) often silently no-ops; do not build workflows on it.

6. **Text entry:** `<input>`/`<textarea>` → `fill_input`. Contenteditable fields → `focus()` + `document.execCommand('selectAll')` + `execCommand('insertText', ...)`, then read back `textContent` — `fill_input` scrambles contenteditable text.

7. **Menus must be open before selecting.** Click the trigger, assert the target option's `getBoundingClientRect().height > 0`, then click the option. Clicking a collapsed menu's "option" just re-clicks the trigger.

8. **Never index-pair two element lists** (items[i] ↔ actionButtons[i]) — app editors hoist the ACTIVE item's toolbar in the DOM (often at index 0) and hide the rest, so list indices do not correspond. Click the item to activate it, then use its toolbar action. "Add item" inserts AFTER the active item, not at the end — activate the intended anchor first.

9. **Verify in a read-only surface** (preview/viewer/public page), never in the editor DOM: editor aria-checked flags and labels can lie. Assert the spec there — item count, order, input types, required markers, absence of fields the spec does not want (e.g. an email gate).

10. **Extract outputs from input values.** After publish/share flows the destination URL often exists only in an input `value` — regex `[value*="http"]` rather than links or innerText. To copy page text out, use `xclip -selection clipboard` from terminal; page-JS clipboard writes throw NotAllowedError.

11. **Finish with a fresh load of the public URL** and assert the full spec once end-to-end. A successful edit sequence is not proof the artifact is correct.

## References

- `references/google-forms.md` — Google Forms editor: selectors, defaults, publish flow, verification checklist.

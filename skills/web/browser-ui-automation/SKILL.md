---
name: browser-ui-automation
description: "Use when driving a web app UI via browser tools, no API."
---

# Browser UI Automation

Drive a web app UI through `browser_exec` (local browser) when no usable API/CLI path exists but the user's browser is logged in — creating Google Forms, filling SaaS wizards, operating web dashboards. Also the fallback when API auth is missing for an otherwise API-covered surface. The technique rests on three things: trusted clicks (not synthetic events), hit-tested coordinates (not assumed targets), and verification in a read-only surface (not the editor's own DOM).

## Procedure

1. **Route check first.** If an API or CLI with auth exists, use it instead (e.g. `google-workspace` for Google surfaces). Probe auth (`setup.py --check`-style) before choosing — the fallback decision must be evidence-based, not assumed. If `browser_exec` cannot open the logged-in profile (another process holds its profile data), fall back to the desktop driver (`computer_use` capture/click/type) plus `xdotool` for hotkeys against the already-open tab — same procedure below, coordinates instead of DOM.

2. **One tab per document.** Open the editor exactly once; list open targets (`cdp('Target.getTargets')`) and close duplicate editor tabs (`Target.closeTarget`) before editing. Two editors on one document clobber each other's autosaves and edits silently revert.

3. **Foreground the tab** with `cdp('Page.bringToFront')` before every interaction batch, and keep a multi-step edit (open dialog → fill → save) atomic in a single `browser_exec` call on a freshly-loaded page. The tab's DOM and login session are not guaranteed to survive into the next call (it can reset to `about:blank` or hit the site's login wall mid-flow, silently discarding earlier steps), and in the user's LIVE profile the active tab can be a different site entirely because the user is using that browser between calls — so every batch starts with `goto_url` to the target and asserts `location.href` before clicking anything. Never run a broad action on whatever page happens to be open, and never dump `body.innerText` from personal surfaces (mail, billing, dashboards) — scope reads to the task-relevant element and keep what leaves the page minimal. A dialog trigger that opened on a fresh DOM can stop responding to `.click()` after intermediate saves/re-renders — reload, then click + fill + save together. Whenever clicks or menus misbehave, check `document.visibilityState` first — a backgrounded tab freezes CSS/WAAPI animations, so dropdowns render at zero height and coordinate clicks silently miss.

4. **Map the page** before acting: `document.body.innerText` for true app state (toasts, dialogs, modes), plus JS enumeration of roles/aria-labels with `getBoundingClientRect()`.

5. **Click via coordinates.** Compute the rect in JS, click with `click_at_xy`. Hit-test first with `document.elementFromPoint(x, y)` to confirm the intended element (not a toast, scrim, or floating toolbar) receives the point; transient toasts hover over buttons and swallow clicks — click an exposed point of the button or wait for the toast to clear. Synthetic `.click()` on component-framework widgets (Material, JSX handlers) often silently no-ops; do not build workflows on it. When the desktop driver's element map returns only the window frame (webviews and Electron canvases expose no inner elements), there is no index to click: locate the button with `vision_analyze` for its pixel center, then click those screenshot coordinates scaled by the reported `bounds_scale` (native ≈ 1.1× screenshot px) — confirmation modals (e.g. a dashboard's "this query includes destructive operations" gate) need that second click before anything runs.

6. **Text entry:** `<input>`/`<textarea>` → `fill_input`. When a framework-controlled field ignores it (the value does not stick, or repeated attempts accumulate duplicated text), set it through the native setter and fire the event: `Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(el, v)` then `el.dispatchEvent(new Event('input',{bubbles:true}))`. Contenteditable fields → `focus()` + `document.execCommand('selectAll')` + `execCommand('insertText', ...)`, then read back `textContent` — `fill_input` scrambles contenteditable text. For a large payload (SQL, code) into a code editor (Monaco/CodeMirror), put the file on the OS clipboard (`xclip -selection clipboard < file`) and send the paste hotkey to the focused editor, then capture and confirm the TAIL of the payload landed — X11 typing of multi-KB text is slow and drops characters, and the editor can hold a truncated buffer while looking populated.

7. **Menus must be open before selecting.** Click the trigger, assert the target option's `getBoundingClientRect().height > 0`, then click the option. Clicking a collapsed menu's "option" just re-clicks the trigger. For an **autocomplete / combobox** (MUI, Radix, Downshift) a visible, correctly-hit option can still dismiss the popup without committing, so drive it by keyboard: focus the input, clear it (an uncleared field accumulates the query as `abcabcabc`), send characters as `cdp('Input.dispatchKeyEvent', type='char', text=ch)`, wait for the option list, then `ArrowDown` + `Enter`. Confirm the committed value in the DOM (a chip in the permissions list, a filled value) before continuing, because the popup closing is not evidence of selection.

8. **Never index-pair two element lists** (items[i] ↔ actionButtons[i]) — app editors hoist the ACTIVE item's toolbar in the DOM (often at index 0) and hide the rest, so list indices do not correspond. Click the item to activate it, then use its toolbar action. "Add item" inserts AFTER the active item, not at the end — activate the intended anchor first.

9. **Verify in a read-only surface** (preview/viewer/public page), never in the editor DOM: editor aria-checked flags and labels can lie. Assert the spec there — item count, order, input types, required markers, absence of fields the spec does not want (e.g. an email gate).

10. **Extract outputs from input values.** After publish/share flows the destination URL often exists only in an input `value` — regex `[value*="http"]` rather than links or innerText. To copy page text out, use `xclip -selection clipboard` from terminal; page-JS clipboard writes throw NotAllowedError.

11. **Finish with a fresh load of the public URL** and assert the full spec once end-to-end. A successful edit sequence is not proof the artifact is correct. The same rule governs saved settings on an admin page: after clicking Save, reload and re-read that exact field. A value that appears to save and then reverts on reload was never persisted, and every downstream action built on it fails later for a reason that looks unrelated. One reload diagnoses it; retrying the save a dozen times does not.

## References

- `references/google-forms.md` — Google Forms editor: selectors, defaults, publish flow, verification checklist.

## The user's own browser (extension plugin)

When the task must run inside the user's real sessions (their logins, their open tabs), use the `hermes-browser-extension` plugin's `tab_*` tools instead of a fresh automated browser. They report unavailable until the extension is attached, so check `browser_control_status` first and fall back to `browser_exec` only for anonymous work.

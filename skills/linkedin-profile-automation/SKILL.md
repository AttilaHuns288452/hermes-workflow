---
name: linkedin-profile-automation
description: Edit a LinkedIn profile via the saved patchright browser.
---

# LinkedIn Profile Automation

The LinkedIn MCP server (`mcp-server-linkedin` v4.22.0, wired via mcporter) is **read-only for profiles**. Its tools: `get_my_profile`, `get_person_profile`, `search_people`, `search_jobs`, `get_saved_jobs`, `get_feed`, `get_inbox`, `send_message`, `connect_with_person`. **No profile-write tools exist.** To edit the profile, drive the browser directly with patchright using the saved login profile.

## Environment (Attila's machine)

- Browser profile with live LinkedIn session: `C:\Users\Attila\.linkedin-mcp\profile` (patchright Chromium, headless launch works)
- Venv: **mangled path** `/c/c/Users/Attila/.linkedin-mcp-venv` (i.e. `C:\c\Users\Attila\.linkedin-mcp-venv`) — artifact of an Aug 2026 setup bug; it is real and works. The python there is a uv shim: **absolute MSYS paths passed to it get double-mangled** (`C:\c\Users\...`), so always `cd` first and pass relative script paths.
- Working scripts on disk (reuse by editing the `HEADLINE`/`ABOUT` constants):
  - `~/.linkedin-mcp/edit_profile.py` — headline (via `/edit/intro`) + about (via pencil click)
  - `~/.linkedin-mcp/edit_about.py` — About only (last verified working)
  - `~/.linkedin-mcp/diag_profile.py`, `scan_about.py` — DOM diagnostics when selectors miss
- Run: `cd /c/Users/Attila/.linkedin-mcp && /c/c/Users/Attila/.linkedin-mcp-venv/Scripts/python.exe edit_about.py`
- Verify: `export PATH="$HOME/.local/bin:$PATH"; mcporter call linkedin.get_my_profile` — read back the `sections.main_profile` text.

## The technique (LinkedIn 2026)

1. **Headline**: `goto <profile-url>/edit/intro` opens the "Edit intro" modal. The headline field is a **TipTap/ProseMirror contenteditable** div (`div.tiptap.ProseMirror[contenteditable="true"]`), NOT an input — `fill()` silently fails. Sequence: `locator.click()` → `page.keyboard.press("Control+a")` → `page.keyboard.type(text, delay=4)` → click Save button (find by exact inner text `"Save"`).
2. **About**: `/edit/about/` is a **404**. Open the About modal from the profile page: scroll down (wheel ~10-12 × 900px), then JS-click the pencil: find the `section` whose `h2/h3` text is exactly "About", then click its `button[aria-label*="edit" i]` (label is "Edit about"). Same TipTap typing sequence, then Save.
3. **Save button**: try `button[aria-label="Save"]` first, else scan all buttons for exact text `"Save"`. After save, expect a "Your intro is saved" / "Save was successful" confirmation.
4. **Verification is via MCP read-back, not screenshots.** Screenshots can show display-truncated text (long headlines render cut in the card view — looks like data loss, isn't). `get_my_profile` returns the full stored value.

## Pitfalls

- Authwall check: after `goto`, bail if URL contains `authwall`/`login`/`checkpoint` — session expired. Re-login via the MCP server's own login flow (opens browser, 30-min manual auth window), which regenerates `profile/` cookies.
- Field IDs are obfuscated (`«r3o»`-style) — never target by ID. Locate by current value (input) or by ProseMirror class (editors).
- Scroll is required before the About pencil exists in a clickable state; the pencil is icon-only (no text) with `aria-label="Edit about"`.
- The intro modal is scrollable; the headline editor can be below the fold in the modal — `locator.click()` auto-scrolls.
- Don't touch anything with 2FA/password/verification walls; stop and ask the user.

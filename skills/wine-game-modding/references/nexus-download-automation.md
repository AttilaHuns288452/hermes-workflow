# Nexus Mods download automation (free account)

Fetch many exact-version files from nexusmods.com hands-off, using the user's existing login.

## Session setup
- Login lives in the user's browser and Chromium encrypts cookie values with an OS-keyring key — do NOT try to decrypt them. Copy the browser profile and run a second instance against the copy: `brave-origin --user-data-dir=<copy> --remote-debugging-port=9333 about:blank`, then Playwright `chromium.connectOverCDP('http://127.0.0.1:9333')`.
- Delete `Singleton*` from the copied profile first — the copied lock file makes the instance abort at startup.
- Cloudflare: headless never clears the "Just a moment..." challenge on nexusmods.com; run the instance HEADED (DISPLAY=:0). The copied profile's cf_clearance carries over.
- NEVER call `browser.close()` on a CDP connection: it closes the last window, the browser auto-exits, and any sibling script dies mid-run. Close your page and leave the browser running.

## Finding the exact file
- Files tab DOM rows: `dt.file-expander-header` carrying `data-id` (file_id), `data-name`, `data-version`, `data-date` (upload epoch).
- Match order: `data-date == epoch` parsed from old package names (exact), then normalized version equality, then nearest date within ~30 days.
- Authors delete old versions when uploading new ones. When the exact file is gone, pick the closest surviving row, preferring rows whose name carries the game-version compat label (e.g. "(v1.2.x)"), and record every substitution for user review — do not silently swap versions.

## Downloading a file
1. Navigate to `?tab=files&file_id=<fid>`.
2. Click the `Slow download` button (role/name match; Playwright locators pierce the `mod-download-modal` shadow DOM where the button lives).
3. After the countdown the site POSTs `Core/Libs/Common/Managers/Downloads?GenerateDownloadUrl` and pulls a signed `files.nexus-cdn.com` URL. Capture the browser `download` event and `saveAs` to the target dir. Listen for downloads on `popup` pages too — some flows open one.

Pitfalls:
- Bound every await. `saveAs` has no timeout and hangs forever on a stalled stream; wrap it and the download-event wait in explicit races, plus a per-item budget (~12 min) so one bad file cannot freeze the queue.
- Free accounts get a short countdown per download; serial downloads are fine. Multi-hundred-MB files are normal and look like stalls — check the progress log before killing anything.
- Keep a resumable JSONL progress log keyed by package name (status/file/size/how matched); reruns skip completed entries and re-try misses.
- Direct curl of nexusmods.com pages is Cloudflare-blocked even with a browser UA; use the real browser session for pages. Signed CDN URLs work from curl afterwards.
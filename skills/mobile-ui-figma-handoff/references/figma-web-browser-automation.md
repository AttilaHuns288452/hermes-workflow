# Driving Figma web with a cloned Chrome profile (CDP automation)

Context: user entrusts the agent to import/fix screens in their Figma file ("do what is necessary,
i permit everything"). The REST API is read-only, plugins need the Figma client, so the remaining
lever is automating Figma WEB in the user's logged-in Chrome via Playwright + CDP.

Verified 2026-08-12 (Guardian Alert 13-screen import). Half-works — the login does NOT survive the
profile clone; the user must log in once in the automation window. Everything else (CDP attach,
page load, DOM drive) works.

## What fails (don't retry these)

1. **Relaunching the user's Chrome with `--remote-debugging-port`**: kill all chrome → launch with
   the flag + same `--user-data-dir` → port never binds. The relaunch races a second instance which
   forwards args to the first and exits; the surviving main process ends up WITHOUT the flag
   (`wmic process where "name='chrome.exe'" get CommandLine` shows no `remote-debugging`). Chrome on
   Windows also requires the flag on the FIRST browser process of the profile.
2. **Playwright `launchPersistentContext` on the real default profile**: Chrome refuses —
   `DevTools remote debugging requires a non-default data directory. Specify this using --user-data-dir`.

## What works: clone the profile, launch with CDP

```bash
taskkill /F /IM chrome.exe 2>/dev/null; sleep 2   # repeat until `tasklist | grep -ci chrome` == 0
SRC="/c/Users/YOUR_USERNAME/AppData/Local/Google/Chrome/User Data"
DST="/c/Users/YOUR_USERNAME/AppData/Local/Temp/figma-chrome"
rm -rf "$DST"; mkdir -p "$DST/Default/Network"
cp "$SRC/Local State" "$DST/" && cp "$SRC/Default/Network/Cookies" "$DST/Default/Network/" \
   && cp "$SRC/Default/Preferences" "$DST/Default/" && cp "$SRC/Default/Login Data" "$DST/Default/"
# launch (background, long-lived):
"/c/Program Files/Google/Chrome/Application/chrome.exe" --user-data-dir="$DST" --remote-debugging-port=9222 --no-first-run about:blank
# poll until: curl -s http://127.0.0.1:9222/json/version  (binds in <60s)
```

Then connect: `chromium.connectOverCDP('http://127.0.0.1:9222')`, `ctx.pages()[0]`, `page.goto(file URL)`.

## The hard caveat

**The Figma session does NOT survive the clone** (cookies are App-Bound-encrypted; the copy lands
on a "Sign up for Figma" wall even though the page title shows the file name). The file opens but
login blocks it. Handling that works: keep the automation window headful, ask the user to log in
once in that window ("Continue with Google", 2FA included), then continue driving — the CDP
session stays attached and the login completes inside it.

## Figma web DOM notes (for the drive step)

- Canvas loaded = toolbelt testids present (`design-toolbelt-wrapper`, `Move-tool`, …) — the old
  `[data-testid="canvas"]` selectors no longer match.
- Cookie banner: `[data-testid="cookie-dismiss-button"]` → click to dismiss.
- Plugins/resources: Shift+I opens the Resources modal but slowly on first use; a plain
  `[role="dialog"]` dump is the reliable check for what's actually open.
- Plugins render in `plugin-sandbox` iframes; the plugin modal container testid is
  `pluginModalWindow`.
- Identify screens in the Figma DOM by TEXT signatures, never by position/order (see
  references/figma-import-qa.md).

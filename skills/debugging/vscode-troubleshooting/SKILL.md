---
name: vscode-troubleshooting
description: Use when VS Code extensions don't work or error at startup.
---

# VS Code Troubleshooting

## Golden rule: `code --list-extensions` lists INSTALLED, not ENABLED
An extension can be in VS Code's global **disabled** list and still show up in `code --list-extensions`. This is the #1 cause of "the extension is installed but does nothing" — every config fix is moot until it's re-enabled. Check disabled state:

```bash
P="C:\Users\YOUR_USERNAME\AppData\Local\Programs\Python\Python311\python.exe"
"$P" -c "
import sqlite3, os, json
con = sqlite3.connect(os.path.expandvars(r'%APPDATA%\Code\User\globalStorage\state.vscdb'))
print([r for r in con.execute(\"SELECT key, value FROM ItemTable WHERE key LIKE '%disabled%'\")])"
```

## Re-enabling a disabled extension
- Modern VS Code REMOVED the `--enable-extension` CLI flag (`code --enable-extension X` passes through to Electron as a no-op — warning printed, nothing happens).
- Supported path: Extensions panel → Enable button (UI only).
- Scripted path (works, safe): `UPDATE ItemTable SET value='[]' WHERE key='extensionsIdentifiers/disabled'` on `state.vscdb` (SQLite, transactional). VS Code has the DB open in WAL mode; the write sticks and is read at next window start. **Requires full restart of VS Code** — reload window alone keeps the stale in-memory state.

## Did the extension actually activate? Check the logs, don't guess
```bash
ls -td "$APPDATA/Code/logs/"*/ | head -1          # latest session
# per-window: window1/exthost/exthost.log — every activation event + errors
grep -E "activate|error" "$LATEST/window1/exthost/exthost.log"
```
If a language event fired (e.g. `onLanguage:javascriptreact`) and your extension has NO activation line and NO error line → it never tried → disabled or corrupt. If there's an error line → read it; it names the cause.

## Startup error toasts = failed activations (duplicate-extension conflicts)
The classic: `Activating extension X failed: Error: command 'foo' already exists` — two extensions register the same command; the loser throws. Also `Chat model provider for vendor Y is already registered`, `ENOENT ... .wasm` (corrupt/broken install). Fix: uninstall the loser/duplicate via `code --uninstall-extension <id>`. Pattern: users accumulate 5+ near-identical AI completion extensions (ollama-copilot clones, opencode providers) that step on each other. Keep the actively-configured one (check settings.json for which has live config keys), uninstall the rest.

## Tailwind IntelliSense specifically
- Tailwind v4 project (`tailwindcss: ^4` in package.json) requires extension ≥ 0.14; CSS-first config is detected via `@import "tailwindcss"` in a CSS file — no tailwind.config needed.
- `editor.quickSuggestions` gotchas (user settings `%APPDATA%/Code/User/settings.json`):
  - `strings: off` → NO picker inside `className="..."` (Tailwind classes live in strings). Must be `"strings": "on"`.
  - `other: offWhenInlineCompletions` → picker suppressed whenever an AI inline ghost (Copilot/localaipilot) is active. Set `"other": "on"` if the user wants the picker always.
- `cn()` helper (tailwind-merge) needs `tailwindCSS.experimental.classRegex` for suggestions inside it:
  `[["cn\\(([^)]*)\\)", "[\"'`]([^\"'`]*).*?[\"'`]"]]`
- **v4 detection timeout — the #1 "everything else is fixed but it still doesn't work" cause.** The extension's startup *project detection* is a workspace-wide file search that can time out; the LSP never boots → ZERO completions, no errors anywhere except the extension's output channel: `Server was not started. Search for Tailwind CSS-related files was taking too long.` Deterministic fix: pin the entry per project in `.vscode/settings.json` (skips the search entirely):
  ```json
  { "tailwindCSS.experimental.configFile": "src/app/globals.css" }
  ```
  v4 → the CSS file containing `@import "tailwindcss"`; v3 → tailwind.config.js path. Add to EVERY project the user works in, not just the reported one (the timeout is flaky — it will hit other projects later).
- Extension output channels live at `%APPDATA%\Code\logs\<session>\window1\exthost\output_logging_*\N-<Name>.log` (e.g. `9-Tailwind CSS IntelliSense.log`) — this is where "search took too long" and LSP server messages appear.

## Maxed completion settings (this user wants ALL of it)
`editor.quickSuggestions` {other/comments/strings: on}, `editor.tabCompletion: on`, `editor.inlineSuggest.enabled: true`, `editor.suggestSelection: first`, `editor.suggestOnTriggerCharacters: true`, `editor.acceptSuggestionOnEnter: smart`, `editor.acceptSuggestionOnCommitCharacter: true`, `editor.suggest.matchOnWordStartOnly: false`, `editor.wordBasedSuggestions: matchingDocuments`, `editor.parameterHints.enabled: true`, `editor.suggest.showWords: true`, `editor.suggest.showStatusBar: true`, `editor.suggest.snippetsPreventQuickSuggestions: false`, `editor.quickSuggestionsDelay: 1`, `editor.inlineSuggest.showToolbar: always`, `editor.suggest.preview: true`, `tailwindCSS.emmetCompletions: true`, `tailwindCSS.classAttributes` [class, className, ngClass], `tailwindCSS.includeLanguages` {typescript/typescriptreact → javascript}. Dead keys to skip: `github.copilot.nextEditSuggestions.*` when Copilot extension isn't installed.

## Corrupt / partial installs (LSP crash loops, startup spam)
- Symptom: Output panel repeats `Cannot find module '...\<ext>\dist\server\server.js'` / `Server initialization failed` / `The X LSP server crashed 5 times in the last 3 minutes. The server will not be restarted.` — the extension's `main` may exist while its LSP server files are missing (interrupted update, antivirus quarantine).
- VS Code keeps the previous version dir — **delete the broken version dir** (`~/.vscode/extensions/<id>-<ver>`) and it falls back to the older working version. Same for stale duplicate version dirs of the same extension id (safe cleanup, frees disk).
- Audit installs with **Node-style resolution**: package.json `main` values like `./out/src/extension` resolve to `extension.js` — a naive `os.path.exists(main)` check reports false positives for dozens of healthy extensions. Check main, main+'.js/.cjs/.mjs'. Re-runnable audit: `scripts/audit-extensions.py`.
- Deleting an extension dir while VS Code runs leaves a stale index entry → one `ENOENT` line in exthost.log at next startup; harmless, self-heals.

## Pitfalls
- Empty newest `%APPDATA%\Code\logs\<session>` dir = window crashed/closed instantly (e.g. 12-line exthost.log, no activations) — check the PREVIOUS session dir for the real evidence.
- Never grep `renderer.*.log` for extension activity — it can contain multi-MB extension-cache invalidation dumps; use exthost.log.
- settings.json edits apply live; Tailwind config changes need Reload Window (extension LSP restart), extension enable/disable needs FULL restart.
- `main.log` `ERR_CONNECTION_REFUSED localhost:PORT` = preview pane pointing at a dead dev server, not an extension problem.
- Don't chase `github.copilot.*` settings if the Copilot extension isn't installed — orphan keys.

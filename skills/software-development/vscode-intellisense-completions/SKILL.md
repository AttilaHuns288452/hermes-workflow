---
name: vscode-intellisense-completions
description: Fix VS Code suggestions not showing (Tailwind, TS, inline).
---

# VS Code IntelliSense & Completion Fixes

When "suggestions don't show" in VS Code, 90% is user settings, not the project.

## Diagnostic chain (in order)

1. **Extension installed?** `code --list-extensions | grep -i -E "tailwind|css"` — Tailwind IntelliSense is `bradlc.vscode-tailwindcss`.
2. **Extension version vs Tailwind major.** Tailwind **v4** needs the extension **≥ 0.14.0**. Older versions silently no-op on v4 projects (no error, no suggestions). Check version: `ls "$APPDATA/Code/User/extensions/" | grep -i tailwind`.
3. **v4 CSS-first detection.** v4 has no `tailwind.config.js` — the extension detects `@import "tailwindcss"` in a CSS file (e.g. `src/app/globals.css`). Verify that import exists.
4. **THE #1 killer — `editor.quickSuggestions`.** Check `$APPDATA/Code/User/settings.json` (Windows; `%APPDATA%\Code\User\settings.json`):
   - `"strings": "off"` → no picker inside `className="..."` (where Tailwind classes live). Must be `"on"`.
   - `"other": "offWhenInlineCompletions"` → every time an inline AI pilot (Copilot, localaipilot, ollama pilots) draws a ghost, the whole suggestion picker is suppressed. Must be `"on"`.
5. **Workspace override?** `.vscode/settings.json` in the project overrides user settings — check it before blaming the global file.
6. **Apply:** settings apply live, but if the language server was in a dead state, `Ctrl+Shift+P` → **Developer: Reload Window**.

## Tailwind settings block (global user settings)

```json
"editor.quickSuggestions": { "other": "on", "comments": "on", "strings": "on" },
"tailwindCSS.emmetCompletions": true,
"tailwindCSS.classAttributes": ["class", "className", "ngClass"],
"tailwindCSS.experimental.classRegex": [
  ["cn\\(([^)]*)\\)", "[\"'`]([^\"'`]*).*?[\"'`]"]
],
"tailwindCSS.includeLanguages": { "typescript": "javascript", "typescriptreact": "javascript" }
```

The `classRegex` entry is what makes suggestions fire inside `cn(...)` helpers (tailwind-merge) — check the project uses `cn(` first (`grep -rln "import { cn }" src/`); if it does, add it.

## Max-completions block (user wants everything on)

```json
"editor.tabCompletion": "on",
"editor.inlineSuggest.enabled": true,
"editor.suggestSelection": "first",
"editor.suggestOnTriggerCharacters": true,
"editor.acceptSuggestionOnEnter": "smart",
"editor.acceptSuggestionOnCommitCharacter": true,
"editor.suggest.matchOnWordStartOnly": false,
"editor.wordBasedSuggestions": "matchingDocuments",
"editor.parameterHints.enabled": true,
"editor.suggest.showWords": true,
"editor.suggest.showStatusBar": true,
"editor.suggest.snippetsPreventQuickSuggestions": false,
"editor.quickSuggestionsDelay": 1,
"editor.suggest.preview": true
```

## Pitfalls

- **Dead `github.copilot.*` keys**: this user has NO GitHub Copilot extension — only local ollama pilots (`localaipilot`, `ollama-copilot-*`). Those `github.copilot.nextEditSuggestions.*` settings do nothing; don't bother flipping them. Verify which AI pilot extension is actually installed before tuning its keys.
- **AI pilot ghost vs picker conflict**: with inline pilots active, `other: "offWhenInlineCompletions"` suppresses the classic picker — this is the most common "no suggestions when typing" report.
- **User preference**: Attila's "fix suggestions" = max everything (tab completion, inline, auto-accept, fuzzy). Apply the full blocks, don't ask which ones.
- Patch `settings.json` with the `patch` tool; lint check confirms JSON validity. Never rewrite the whole file (it's 280+ lines of unrelated config — java, ollama, emulator paths).

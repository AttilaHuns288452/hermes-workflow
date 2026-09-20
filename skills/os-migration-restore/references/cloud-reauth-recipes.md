# Cloud Re-auth Recipes (post-migration)

Browser-bound credentials never survive a Windows → Linux move: OAuth tokens,
`rclone.conf` remotes, Composio/connected-account logins. Re-auth them on Linux
with the recipes below. Field-tested on a Hermes restore (rclone + Google Drive,
Composio), 2026-09.

## rclone: reconnect a drive remote headlessly

1. Run `rclone authorize "<type>"` **bare on the machine that has the browser**
   (e.g. `rclone authorize "drive"`). It prints a URL — open it, approve, paste
   the resulting JSON back into that same terminal.
2. **Never relay the auth blob through chat.** Chat truncates long base64 with
   `...`, and the elided blob fails with
   `decode simple map: illegal base64 data`. A blob containing `...` is corrupt
   by definition — re-run the authorize step instead of retrying the paste.
3. If the headless box has no terminal sharing (`tmux`/`socat` absent), drive
   `rclone config` with a small PTY script (stdlib `pty` + `os.fork`): feed
   answers when prompts appear, write the auth blob to a sentinel file
   (`auth_request.txt`), and block until the user drops the result into
   `auth_result.txt`. Match prompts loosely (regexes) — wording and order
   vary across rclone versions (`Use auto config?` vs `Use web browser?`,
   `Edit advanced config?`, `Configure as Team Drive?`). Delete partial
   remotes between attempts (`rclone config delete <name>`).
4. Recreate the crypt remote from the migrated key file — never invent a
   new password, old backups stay readable only with the original key:
   `OBS=$(rclone obscure "$(cat ~/.hermes/backup.key)") && rclone config create <crypt-name> crypt remote "<drive-remote>:<dir>" password "$OBS"`
5. Inject the OAuth token non-interactively:
   `rclone config update <drive-remote> token "$(cat token.json)"`
6. Verify both layers before declaring done: `rclone listremotes` must show the
   drive remote, and `rclone lsjson <crypt>: --files-only` must list the
   encrypted backups (proves key + token + crypt all agree).

## Composio / OAuth-PKCE scripts (general pattern)

`register client → PKCE challenge → print AUTH_URL → localhost callback
listener → exchange code → save token JSON`. Run the script in background,
pop the URL on the user's machine (`xdg-open "$AUTH_URL"`), user approves,
script completes alone. Save tokens under `~/.hermes/` (Linux home — audit
migrated scripts for hardcoded `~/AppData/...` token paths), `chmod 600`.

## Pitfalls

- **YAGNI against the source system.** Before building wiring the new box
  "should" have (e.g. passing a fresh Composio token into MCP headers), check
  whether the old system ever had it: if the old `config.yaml` had the entry
  `enabled: false` and nothing consumed the token file there either, match the
  source (disable) instead of building. Port behavior, not aspirations.
- **Hermes config edits go through the CLI.** File-edit tools refuse
  `~/.hermes/config.yaml`; use `hermes config set <dotted.key> <value>`
  (e.g. `hermes config set mcp_servers.figma.enabled false`). Note `hermes mcp`
  has no `disable` subcommand — the config-set path is the toggle.

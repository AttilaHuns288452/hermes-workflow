# Figma: MCP install + REST QA of imported design files

Verified 2026-08-12 on the Guardian Alert 13-screen handoff. Covers (a) wiring the official Figma
MCP server into Hermes, (b) QA-ing a user's Figma file (frames imported via html.to.design) purely
through the REST API when MCP tools aren't in the current session.

## Figma MCP install (official server)

```bash
# 1. token: user generates in Figma → Account settings → Security → Personal access tokens (scoped read-only is enough)
echo 'FIGMA_API_KEY=figd_...' >> ~/AppData/Local/hermes/.env

# 2. pre-warm the npx package (first-run download can exceed the connect timeout)
npx -y figma-developer-mcp --help

# 3. register — CRITICAL: --env BEFORE --args; --args must be LAST (argparse nargs* swallows everything after it)
echo y | hermes mcp add figma-dev --command npx --connect-timeout 90 --env FIGMA_API_KEY=figd_... --args -y figma-developer-mcp --stdio

hermes mcp test figma-dev   # → "2 tools enabled" means the connection succeeded at add time
```

Pitfalls (all hit live):
- **`hermes mcp add --args ... --env ...` mangles the config**: the saved entry had the whole
  `-y figma-developer-mcp --stdio` as ONE arg string plus `--env`/`--connect-timeout` orphaned
  inside `args`. Order matters: options before `--args`.
- **MCP child processes do NOT inherit `~/.env`** — without the key in the server's `env:` block,
  figma-developer-mcp prints `Either FIGMA_API_KEY or FIGMA_OAUTH_TOKEN is required` and exits →
  `hermes mcp test` reports `Connection closed`. Pass it via `--env KEY=VALUE` (lands in
  `mcp_servers.<name>.env` in config.yaml). The token then sits in config.yaml — acceptable, it's
  the documented mechanism.
- **The interactive "Save config anyway? [y/N]" prompt** hangs a non-interactive shell; pipe
  `echo y |`. On EOF it defaults to N and saves nothing.
- The pre-existing `figma` entry (`https://connect.composio.dev/mcp`, Composio-hosted) is
  **401-dead without a Composio API key** — `hermes mcp test figma` fails; ignore it or disable.
- Tools appear in NEW sessions only (`hermes mcp list` shows ✓ enabled; current session can't use
  them until `/reset`).

## REST QA workflow (works in-session, same token)

Token: `grep FIGMA_API_KEY ~/AppData/Local/hermes/.env | cut -d= -f2`. Header `X-Figma-Token`.

```python
GET /v1/files/<key>?depth=2            # document → children: pages → frames (names, ids, sizes)
GET /v1/files/<key>/nodes?ids=<id1>,<id2>&depth=N   # subtree of specific nodes (NOT /files/<key>?ids= — wrong endpoint, returns nothing)
GET /v1/images/<key>?ids=...&format=png&scale=1     # renders nodes to PNG URLs (download, then vision-QA)
```

Steps that worked:
1. Dump the page's children — identify the "Imported HTML" frames (plus any user's own frames; the
   file may contain chat/notes TEXT nodes — ignore them).
2. **Identify each imported frame by TEXT signature**: walk the node tree collecting
   `characters` from TEXT nodes; first ~4 non-empty strings identify the screen ("Reset password",
   "Account management", …). Never map by position/order — the user pastes in arbitrary order and
   html.to.design drifts sizes (390×866, widths up to 459).
3. Render frames via `/images`, download, run the standard vision-QA prompt on each.
4. **Dropped-content detector**: sibling frames whose renders are byte-identical (same md5/size) =
   the overlay content never imported (seen: 3 dialog frames all 18,139 bytes of plain Account page).
5. Compare render signatures against the source screenshots when naming disagreements arise.

Rate limits (free tier): 429s hit within minutes of bursty calls — the quota is SHARED with the
user's browser + html.to.design plugin usage on the same account. Pace calls, sleep 30–60 s between
groups, retry on 429 with backoff. Python sandbox loops burn the 5-min budget on retry sleeps —
prefer one `curl` call per node from terminal when limits are tight.

## html.to.design import behavior (observed)

- Single-file boards: 13 frame-wraps import as one 1920×12006 board; overlays inside may be
  missing (see static-flow rule in SKILL.md).
- Board node structure: `Imported HTML` → `board` → `frame-wrap` → `frame` (ids like `24:2728`).
- Dialogs centered with `transform: translate(-50%,-50%)` + `position:absolute` do NOT import;
  plain-absolute overlays (toast at `top:16px`) and static-flow overlays DO.
- One-file board with 13 wraps: wraps 10–12 rendered byte-identical Account pages (dialogs gone),
  wrap 13's static toast present — consistent with static-flow being the fix. NOTE (2026-08-13):
  even in-flow `rgba` scrims imported as a black screen for the user — the operative rule is now
  NO scrim at all (see SKILL.md pitfall "Drop the rgba scrim entirely").

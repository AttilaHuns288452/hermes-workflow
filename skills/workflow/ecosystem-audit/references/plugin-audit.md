# Plugin layer audit

How to tell whether an installed plugin is actually working, and what to do about each class.

## Inventory (parseable forms only)

```
hermes plugins list --json        # name, status, version, source — the only reliable roster
hermes plugins list --plain       # counts: grep -c '^enabled' / '^disabled'
hermes plugins list --user        # user-installed only (catalog + git), excludes bundled
hermes tools list                 # 'Plugin toolsets' block: enabled/disabled per plugin
```

`hermes plugins list` as a Rich table wraps every description across lines and makes columns
unreadable — never parse it. `hermes plugins doctor <dir>` needs a **directory path**, not a plugin
name, and then it is the most informative single command: it prints per-stage `OK` lines for
`runtime discovery, manifest parsing, import, and registration` plus a `WARN` when the manifest
declares a hook the code never registered. `hermes plugins doctor <name>` (a bare name) and
`hermes plugins doctor .` only report "no plugin manifest", which is a usage miss, not absence.

## Failure modes, in the order they bite

1. **Registered without metadata.** `ctx.register_skill(name, path, description="", frontmatter=None)`
   is the API; plugins that omit the optional fields produce a bare `plugin:skill` row in the prompt
   index. Symptom: `- hermes-security:security-audit` with no `: description`, so the router has no
   trigger. Fix at the registrar (hydrate from the SKILL.md frontmatter) rather than patching N
   vendored plugins, and verify with a fresh-process check that runs real discovery:
   `python3 ~/.hermes/scripts/check_plugin_skill_descriptions.py` (exit 0 = every plugin skill has one).
2. **Failed to load.** One WARNING per discovery in `agent.log` (`Failed to load plugin '<name>': ...`),
   usually a requirement the plugin cannot resolve on its own (profile secret scope, owned state home).
   The toolset still shows enabled in `hermes tools list`, but nothing registered. Try the config fix
   below before disabling; disable only when the plugin exposes no settings path.
   `hermes plugins disable <name>` hot-unloads and says so; hooks it already wired stay until a
   gateway restart.
3. **Credential-gated.** `requires_env` in `plugin.yaml` lists the key. The tools register anyway and
   fail at call time. That is "blocked", not "broken" — report the exact key needed.
4. **Alternatives by design.** Bundled backends (image, video, web, platform adapters, dashboard auth)
   are a registry; only the one named by config runs. They cost nothing while idle. Disabling them
   removes options from the model/provider pickers.

## Binding-requirement failures (the non-obvious class)

A plugin can refuse to register with a message like `... requires an owned profile variable binding`.
In a multiplexed process Hermes deliberately does not hand a plugin the process-wide env secrets, and
the plugin also needs to know which store it owns. It is refusing to guess, not crashing. Before
disabling:

1. Read the raise site and the home resolver:
   `grep -rn "requires an owned\|_configured_home" ~/.hermes/plugins/<name>`. Most of these plug-ins
   read their own settings from `plugins.entries.<name>.settings.<key>` (for the OMH bridge the key is
   `omh_home`); a settings value short-circuits the secret-scope probe.
2. Pin it: `hermes config set plugins.entries.<name>.settings.<key> <absolute path>`, then
   `yaml.safe_load` the config and confirm `plugins.entries` exists.
3. Reload: `hermes plugins disable <name>` then `hermes plugins enable <name>`. The enable output names
   the deferred surfaces ("tools (next session)") — a plugin that failed once stays failed in the
   running gateway until a reload, so never conclude anything from the current session.
4. Prove it with a call, not by reading source: a NEW single-query session must run the tool.
   `hermes chat -q "call tool_search for <tool>; if present, tool_call it with {} and print the raw result; else reply ABSENT"`.
   An agent session that greps the plugin source can report "0 tools available" while the tool is in
   fact registered — absence is only proven by a failed call.
5. Isolated repro when you need the traceback: fresh interpreter, force multiplex, discover, list tools:
   `PYTHONPATH= python3 -c "import sys;sys.path.insert(0,'<repo>');from agent.secret_scope import set_multiplex_active;set_multiplex_active(True);from hermes_cli.plugins import discover_plugins,get_plugin_manager;discover_plugins();pm=get_plugin_manager();print([n for n in pm._plugin_tool_names if n.startswith('<prefix>')])"`.

Two cautions:

- Check what the plugin ALSO provides before turning it on. One that provides a memory provider can
  displace the file-backed memory that is the system of record; leave `memory.provider` unset unless
  the user explicitly asks for it.
- These settings are per-profile (each profile reads its own `config.yaml`). If the plugin appears in
  only one profile's `plugins.enabled`, one setting is enough; add it to every profile that lists it.

## Utilization classes and how to prove each

| Class | Proof | Action |
|---|---|---|
| Active | The config selector names it (`web.search_backend`, `image_gen.provider`, `browser.cloud_provider`, delegation strategy) AND calls exist in `state.db` | none |
| Ready | No `requires_env`, registers tools/skills, zero calls | add a pointer from the skill that loads when the capability matters |
| Blocked | `requires_env` key absent from the profile env | report the key; leave installed unless the user says otherwise |
| Alternative | Named by a `<thing>.provider` selector family, not the selected value | leave enabled |

**Counting caveat:** plugin tools are usually deferred, so invocations are recorded under
`tool_call`, not their own name. `tool_name` counts undercount to zero. On a `tool_call` row the
`tool_calls` column is NULL and the invoked name lives in `content` as
`tool_call to '<name>'` (the rest of the row is the result or the schema error), so extract it with a
regex, not a JSON parse and not a `"name"` substring — measured on the same database, the
`'%"name": "<tool>%'` shape matched zero plugin calls while `tool_call to '…'` matched 1,648:

```python
import sqlite3, re, collections
c = sqlite3.connect('file:state.db?mode=ro', uri=True)
cnt = collections.Counter()
for (ct,) in c.execute("select content from messages where tool_name='tool_call'"):
    m = re.search(r"tool_call to '([a-z0-9_]+)'", ct or "")
    if m:
        cnt[m.group(1)] += 1
```

A substring prefix matches prose everywhere — match on the quoted name shape and group by exact name.

**Dep probe must use the live interpreter.** A plugin's `pip_dependencies` are satisfied or not
*for the process serving the session*, and `python3 -c "import x"` answers for the shell's default
tier instead — a mismatch that reads as "plugin is broken" when it is installed, or the reverse.
Take the interpreter off the running process:

```bash
GW=$(ps aux | grep -m1 "[t]ools/python-" | grep -oP '/home/[^ ]+/\.hermes/tools/[^ ]+/bin/python3')
"$GW" -c "import apify_client"   # ModuleNotFoundError here is the real answer
```

A plugin can still pass `plugins doctor <dir>` with its SDK absent (it imports lazily and only needs
the SDK once configured), so treat "doctor says OK" and "dependency present" as separate facts.

## Making a "ready" plugin fire

A registered tool nobody knows about is not a capability. Put one line in the skill that loads at the
moment of need, naming the plugin tools and when they beat the default:

- teammates → delegation skill (standing roster vs one-shot children)
- browser extension → browser-automation skill (the user's own logged-in tabs vs an anonymous browser)
- connectors (ClawLink et al.) → integrations skill (OAuth plane vs bespoke per-app credentials)

## Reload semantics

- `hermes plugins enable/disable` reloads the plugin manager in the running gateway.
- A patch to core Python (`hermes_cli/*`) does NOT hot-reload; new CLI processes pick it up
  immediately, the desktop app only after a restart. Verify with a fresh CLI process and say which
  surface is stale instead of claiming the fix is live everywhere.
- A newly registered MCP server is picked up by `hermes mcp list` and `hermes mcp test` immediately
  (both spawn their own process), but its tools do not enter a live session until `/reload-mcp` or an
  app restart. The gateway's `cache/mcp_schema_cache.json` gaining the server name proves the gateway
  has seen it; a `tool_search` miss in the current session does not contradict that.

## Two shapes that look like plugins but are not

- **A directory with no `plugin.yaml`.** Leftover state from a removed plugin (scan JSON, `state.json`).
  `hermes plugins show <name>` answers "not found" while the directory sits in every scan and gets
  re-flagged as UNLISTED forever. Confirm no `plugin.yaml`, check nothing live references it
  (`grep -rl <name> --include=*.yaml --include=*.py ~/.hermes`), then move it to
  `~/.hermes/archive/` — reversible, and it stops polluting the roster.
- **`Emits:` / `Listens:` in `hermes plugins show`.** Both print `(none)` for plugins that demonstrably
  work (a prompt-section injector, a mode injector), because the field is unpopulated in this build.
  Never read `(none)` there as "the plugin is dead"; use `plugins doctor <dir>` for registration facts.

## Hook overlap: what overlapping plugins actually cost

Inventory the hook graph before calling overlap harmless (parse `hooks:` and `provides_hooks:` from
every enabled `plugin.yaml`, invert to hook → owners):

- **Tool-name collisions are the thing to check first, and they are usually absent.** No two enabled
  plugins exposing the same tool name means a call cannot be misrouted. Say that explicitly instead
  of warning about "conflicts" in the abstract.
- **Hooks compose, they do not overwrite.** Hermes runs every callback for a hook rather than
  electing a winner, so overlap costs latency and ordering, not correctness.
- **The staged hooks are where it bites.** `pre_llm_call` and `pre_tool_call` run on every model /
  tool call. With five and three owners respectively, a slow callback produces
  `WARNING hermes_cli.plugins: Hook 'pre_tool_call' callback pre_tool_call skipped after previous
timeout or while still running` and Hermes then **skips the remaining callbacks of that hook** — so a
  gate or approval another plugin provides silently does not run. Grep for that line before and after
  any change to hook owners; it is the only observable consequence.
- **Cheapest risk reduction:** disable the plugin that contributes per-call hooks and cannot function
  anyway (no credential, no provider slot). That removes a hook owner from every call and loses no
  working capability — a strictly better cut than disabling one that merely duplicates a tool.
- **The one unsafe overlap** is two memory providers writing the same facts. The framework already
  forbids it (one provider slot, `hermes memory status`), so leaving several installed is safe as
  installed; it turns unsafe only if two are ever activated, which config will not allow.

Behavioural overlap is the softer cost and worth naming: two plugins can inject instructions that
pull in opposite directions on every turn, and the model arbitrates non-deterministically. Report the
count of per-turn injected sections alongside their owners.

## Memory plugins share one slot

Several memory plugins can be installed and `enabled` at once while **none** is running:
`hermes memory status` prints `Provider: (none — built-in only)` plus the installed list. Enabled is
not active, and only one external provider can be active, so a plugin that declares a session hook
will register nothing until it is the selected provider — `plugins doctor <dir>` states this exactly
(`manifest declares hook '…' but registration did not add it`). Report the slot as empty rather than
reporting three working memory systems, and never set `memory.provider` on the user's behalf.

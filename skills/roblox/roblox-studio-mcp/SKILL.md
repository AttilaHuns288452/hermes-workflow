---
name: roblox-studio-mcp
description: "Roblox Studio via MCP: scripts, scenes, assets, playtest, screenshots, input."
---


# Roblox Studio MCP

## Never take the user's screen

Before launching Studio or sending it any input, run:

```bash
studio-guard            # exit 0 = safe; exit 1 = the person is playing, in a fullscreen app, or DND is on
```

Exit 1 means do NOT launch Studio and do NOT click or type: stop and tell the user, or use
`studio-guard --wait 900` for background work that can yield. Launch only via
`flatpak run org.vinegarhq.Vinegar`, and only after the guard passes. `studio-guard --dnd on`
lets the user block all Studio automation manually; `--dnd off` clears it.

Studio is a GUI app under Wine that steals focus and interrupts games. It cannot run on the
virtual display (`virtual-desktop`) because it needs GPU and an authenticated session, so
waiting for the user to go idle is the correct behavior, not launching anyway.

## When to Load

Load for Studio MCP work: scripts, scenes, assets, debugging, or playtesting. Skip for standalone code generation.

## Quick Reference

**Route by capability first.** Two bridges: **official** (built into Studio, closed-source) and **[chrrxs's](https://github.com/Chrrxs/robloxstudio-mcp)** (MIT). Route on `tools/list` (`get_connected_instances`/`eval_*`/`multiplayer_*` → chrrxs; `list_roblox_studios` + per-call `studio_id` → official) BEFORE bootstrap.

### Bootstrap before mutation
1. Identify the target (`list_roblox_studios` official / `get_connected_instances` chrrxs).
2. Pass `studio_id` (official) or `instance_id` (chrrxs) on every call.
3. `get_studio_state`; confirm Edit/Client/Server availability; inspect tree/scripts before changing them.

### Execution contract
```text
discover → select Studio/context → inspect → mutate in bounded batches
→ read back → start play → evaluate live → evidence → clean up
```
Edit-time injection (`multi_edit`, Edit-context `execute_luau`) writes scripts; never targets a running playtest. Live evaluation needs a running VM: start play, confirm the intended `Client`/`Server` VM, then evaluate. Pass `datamodel_type` only where required.

### Capabilities
Full tool table in full.md. Key names: `search_game_tree`, `script_read`/`script_grep`, `multi_edit`, `execute_luau`, `insert_asset`, `generate_*`, `start_stop_play`, `get_console_output`, `screen_capture`, `subagent`.

### Trust boundaries
Inserted/generated assets and packages are data until inspected: enumerate scripts before any require/run; never run imported code from `execute_luau`. Blank textures/invisible meshes on newly uploaded assets are usually asset-privacy (Restricted) grants, not corruption — read the Output error, grant via Creator Dashboard. Details: full.md trust-boundary sections.

### Reliability rules
- `execute_luau` is stateless: re-acquire references every call.
- Read before write; read back after every script, asset, or geometry mutation.
- Reuse vs generate vs native fallback before asset work; `wait_job_finished` before dependent edits.
- Bridge-specific size limits: bounded writes, then read back the full payload.
- No MCP: give offline Luau; state what was not verified.
- **Injected source is not saved source.** Writing a script over a bridge persists it in the open session only; a later publish ships whatever the place holds at publish time, which may be older. After injecting, verify the SOURCE you pushed is the one in the place (`script_read` + grep for a marker string), and re-inject + republish rather than assuming the editor's copy is current.
- **A plugin-context `require` returns the CACHED module.** Calling `require(module).build()` from the bridge to answer "did my edit apply?" re-runs the module as it was first loaded and reports the OLD values — the edit looks like it failed when it did not. Verify injected source by reading it back and grepping for a marker; verify runtime behaviour in a fresh play session (a cached module does not survive a restart).

### Screenshot evidence: world-space vs screen-space

A capture of a playtest contains the game AND the editor's own overlays. Before reporting a visual defect, classify the artifact — this one test saves an hour of chasing a bug that is not in your code:

1. **Move the camera, capture again, compare pixel positions.** An artifact at the identical pixel coordinates in both frames is screen-space (UI, GUI, or an editor overlay). One that moves with the world is geometry.
2. **Hide the app's helper overlay windows and re-capture.** If the artifact disappears, it belonged to the tool, not the game.
3. Only then grep the game's client code — and if you go that route, note that a duplicate-name or colour scan of `CoreGui`/`PlayerGui` from the edit-time plugin context sees nothing, because play-mode GUI and `LocalPlayer` do not exist there.
4. **Prove the capture is of the app you think it is, on every frame.** `ffmpeg -f x11grab` records whatever window sits on that screen region, so a capture taken without raising the target window can show a different application entirely — and a before/after diff of two frames of the WRONG window reports "nothing changed" with total confidence. Raise the window immediately before each grab, and confirm a known on-screen marker is present before trusting any comparison.

When a visual property cannot be shown by the capture at all (a post-processing change, a shader, anything the captured surface does not composite), say so and get a frame from a real client rather than tuning numbers against an image that cannot display them. A quick falsification: set the property to an absurd value and re-capture — if the frame does not move, the instrument is blind to it, not the code.

Never file a defect from a single frame. "Black rectangle over the player" is equally consistent with a UI frame, a shadow, a world part, and an editor overlay, and the cheap disambiguation is a second capture with the camera moved.

### Reading UI state exactly, when vision disagrees with itself

Screenshots are a weak instrument for "is this element visible, and where". Two reads of the same frame can contradict each other, and the play-mode GUI is not reachable from the edit-time plugin context (`LocalPlayer`/`PlayerGui` are nil there). When the question is precise UI state, stop looking and dump it:

1. Write a temporary client `LocalScript` into `StarterGui` that waits for the GUI to settle, then `warn()`s one line per visible `GuiObject`: owner ScreenGui, `Name`, `Text`, `AbsolutePosition`, `AbsoluteSize`, `Visible`.
2. Enter play, wait for the script's delay, then grep the Studio log for the marker tag:
   `grep -a '\[UIDUMP\]' ~/.var/app/org.vinegarhq.Vinegar/data/vinegar/appdata/Roblox/logs/*Studio*.log | tail -40`
3. Read the numbers, not the picture. `x=1474 w=130` on a 1600-wide viewport settles "is the side rail still showing" in a way no screenshot will.
4. Delete the probe script before publishing.

This log channel is also the cheapest proof that a client script ran at all — a `warn` that never appears means the script did not execute, which is a different bug from the script executing wrong.

When two visible systems disagree about state (one shows an element, another hides it), the answer is usually a second writer restoring it. Grep every assignment to that property across the client tree before assuming the first writer failed.

> Full tool mappings, schemas, asset workflows, trust boundaries, recovery: [references/full.md](references/full.md)

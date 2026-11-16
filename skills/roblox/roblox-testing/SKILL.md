---
name: roblox-testing
description: Testing Roblox code - testable modules with dependency injection, Jest Lua (runCLI, .spec files), legacy TestEZ, running tests in Studio, via Studio MCP, run-in-roblox, or CI with Open Cloud Luau Execution, Lune for pure Luau, multi-client playtests, QA checklist. Use when adding tests, setting u...
---

# Testing Roblox games

## Make code testable first

- Keep game rules in **pure ModuleScripts** (inputs → outputs, no services, no yields): damage formulas,
  inventory operations, shop pricing, state machines, serialization, validation. These are trivially testable.
- Services take their dependencies as parameters (**dependency injection**) so tests can pass fakes
  instead of real DataStores, remotes, or `Players`.
- **Read every duration through one virtualisable clock.** Cooldowns, combo windows, and reward gaps that call `os.clock()`/`os.time()` directly while the harness advances simulated time never expire during a test: the feature looks broken when it is not, and a test that pumps virtual time still fails. Use a clock the harness can drive (`tick()` is virtualised by a scheduler-driven harness; an explicit `Clock` module is the general form) and keep the window length in `Config` so a test advances past it with a pump instead of sleeping.

```luau
--!strict
-- ReplicatedStorage/Shared/Inventory.luau — pure logic, no Roblox services.
export type Inventory = { [string]: number }

local Inventory = {}

function Inventory.add(inventory: Inventory, itemId: string, amount: number, maxStack: number): (boolean, string?)
	if amount <= 0 or amount ~= math.floor(amount) then
		return false, "invalid amount"
	end
	local current = inventory[itemId] or 0
	if current + amount > maxStack then
		return false, "stack full"
	end
	inventory[itemId] = current + amount
	return true, nil
end

return Inventory
```

```luau
--!strict
-- A service that receives its data store, so tests can inject an in-memory fake.
type Store = {
	GetAsync: (self: Store, key: string) -> any,
	SetAsync: (self: Store, key: string, value: any) -> (),
}

local function newCurrencyService(store: Store)
	local service = {}
	function service.award(userId: number, amount: number): number
		local key = `User_{userId}`
		local balance = (store:GetAsync(key) or 0) + amount
		store:SetAsync(key, balance)
		return balance
	end
	return service
end

-- In tests: a fake store backed by a table.
local fakeData: { [string]: any } = {}
local fakeStore: Store = {
	GetAsync = function(_self, key)
		return fakeData[key]
	end,
	SetAsync = function(_self, key, value)
		fakeData[key] = value
	end,
}
print(newCurrencyService(fakeStore).award(1, 50))

return newCurrencyService
```

## When your change fails an existing test

A red test is evidence, but it is evidence about two different things. Decide which before editing either side:

- **The test is guarding a real invariant you just broke.** Read the assertion and its comment first. A threshold like `brightness >= 1.2` is usually not a style opinion — it is the tombstone of an earlier "the room read as a black void" bug, and lowering it to make your tuning pass re-opens that bug silently. Fix the real conflict instead (move the light rather than dim the room), keeping the invariant intact.
- **The test encodes a design you deliberately replaced.** Then the assertion is the stale artifact, and the correct move is to flip it to the new contract *inverting the check where the new rule is the opposite of the old one*, with a comment saying why it reversed. A test that still demands "six different button colours" after the design moved to a single accent is not protecting anything — it is enforcing the old look.

The failure to avoid is the middle path: loosening a number until it passes, which leaves a test that no longer protects the invariant and no longer documents the design. Either keep the invariant and change the code, or change the assertion and say which design it now enforces.

## Jest Lua (recommended framework)

Port of Jest (`describe`/`it`/`expect`, mocks, snapshots). TestEZ is legacy; Jest Lua 3 includes a
migration guide.

```toml
# wally.toml
[dev-dependencies]
Jest = "jsdotlua/jest@3.10.0"
JestGlobals = "jsdotlua/jest-globals@3.10.0"
```

```luau
-- src/shared/Inventory.spec.luau
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local JestGlobals = require(ReplicatedStorage.DevPackages.JestGlobals)
local Inventory = require(ReplicatedStorage.Shared.Inventory)

local describe, it, expect = JestGlobals.describe, JestGlobals.it, JestGlobals.expect

describe("Inventory.add", function()
	it("stacks items up to the limit", function()
		local inventory = {}
		expect(Inventory.add(inventory, "Apple", 3, 5)).toBe(true)
		expect(inventory.Apple).toBe(3)
		local ok, reason = Inventory.add(inventory, "Apple", 3, 5)
		expect(ok).toBe(false)
		expect(reason).toBe("stack full")
	end)

	it("rejects fractional amounts", function()
		expect(Inventory.add({}, "Apple", 0.5, 5)).toBe(false)
	end)
end)
```

- Put a `jest.config.luau` (`return { testMatch = { "**/*.spec" } }`) in each test root.
- Runner script (Studio command bar, a test place Script, or cloud task):
  `require(ReplicatedStorage.DevPackages.Jest).runCLI(root, { ci = true }, { root }):awaitStatus()` →
  inspect `result.results.numFailedTests`.
- Jest Lua 3 needs the fast flag `FFlagEnableLoadModule = true` in Studio's `ClientAppSettings.json`
  when run locally.
- Map `DevPackages` into the DataModel only for test builds (separate Rojo project, e.g. `test.project.json`).

## Where tests run

| Runner | Use |
| --- | --- |
| Studio (command bar / test Script) | Local development. |
| Studio MCP (`execute_luau`, `start_stop_play`, `get_console_output`) | Agents running tests and playtests against the open place — see `roblox-studio-mcp`. |
| `run-in-roblox` | CLI that opens Studio, runs a script, pipes output (needs Studio installed; local/Windows/mac CI runners). |
| **Open Cloud Luau Execution** | Headless CI: runs a script in a real Roblox server for a published place version. |
| Lune | Pure-Luau modules with no Roblox API dependencies (fast, runs anywhere). |

Open Cloud Luau Execution flow (details and a script: [references/cloud-test-runner.md](references/cloud-test-runner.md)):
1. Build the test place (`rojo build test.project.json -o test.rbxl`) and upload it as a **Saved** version
   of a dedicated test place.
2. `POST /cloud/v2/universes/{u}/places/{p}/versions/{v}/luau-execution-session-tasks` with `{ "script": ... }`
   (API key scope `universe.place.luau-execution-session:write`; rate limit ≈ 5 tasks/min per key owner).
3. Poll the task `path` until `state` is `COMPLETE`/`FAILED`; read `output.results` and `.../logs`.

## Playtesting in Studio

- **Test** tab: Play (you + server), Run (server only, no character), **Clients and Servers** with 2+
  players to test replication, trading, and PvP. Most multiplayer bugs only appear with ≥ 2 clients.
- **Device Simulator** toolbar (Test → Device Simulator, top of the viewport): switch phone/tablet/console
  mid-playtest, with touch-control hints; its **Network Simulator** applies 3G/4G/Wi-Fi/wired or custom
  inbound/outbound latency, jitter, and packet loss to test lag compensation and loading/retry UX.
  Controller Emulator for gamepad input.
- Streaming: test with `StreamingTargetRadius = 64`.
- DataStores in Studio: enable API access and use a separate test universe or data store names.

## Visual evidence you can trust

Screenshots are the only way to judge look and feel, and they lie in specific, repeatable ways.

- **Raise the window before you capture.** A rootless screen grab copies whatever is composited on
top. Two frames taken "before" and "after" a change can both be your terminal — the diff comes back
near-zero and you conclude the change had no effect. `xdotool windowraise <id>; xdotool windowactivate
--sync <id>` then `ffmpeg -f x11grab -video_size WxH -i :0+X,Y -frames:v 1 out.png`.
- **Prove a rendering change with a pixel diff, not with prose.** Capture state A, capture state B,
`ImageChops.difference(...)`, and report the mean channel delta. A whole-frame mean under ~1/255 means
the two states rendered identically, whatever they claim in code. That is also how you test whether
effects are reaching the screen at all: flip saturation to its extremes, or destroy every post-effect,
and diff. If a controlled extreme produces a flat diff, the capture path is not showing that layer —
verify it on a real client before tuning values you cannot see.
- **Rule out the tool's own overlays before reporting a visual bug.** Studio keeps small child windows
that paint onto captures (a 100x100 helper window reads as a solid black rectangle over the game).
Enumerate windows, hide everything but the main one, re-capture, and only then decide. A defect that
vanishes with an overlay hidden was never in the game.
- **Do not read exact UI state from a vision description.** "Is that button visible, and where" comes
back inconsistent between two reads of the same frame. Probe the live tree instead: a client
`LocalScript` that walks `PlayerGui` and `warn()`s each visible `GuiObject`'s name, text and
`AbsolutePosition`, then grep the Studio log for that marker. The plugin/MCP context has no LocalPlayer,
so it cannot read PlayerGui — the client-side probe is the only way in.
- **Re-requiring a rewritten script returns the cached module.** After changing a script that is
already loaded, restart the play session (stop, then play) — calling the module's function again from
the same session exercises the old code and makes a correct fix look like a no-op.
- **A guard that early-returns can disable everything below it.** A "already built / already registered"
check placed above the rest of an initialiser silently skips lighting, props and effect setup once
whatever it guards exists — the properties look right in the file and never run. Assert the observable
side effect (a property that only the initialiser sets), not that the call was made.

## QA checklist before shipping a feature

- [ ] Works for a player who joins **after** the feature started (late joiners), and after respawn.
- [ ] Works with 2+ clients; server state is authoritative; UI updates on all clients.
- [ ] Player leaving mid-action (trade, purchase, round) leaves no broken state or leaked tables.
- [ ] Remotes rejected when spammed or sent malformed arguments.
- [ ] Data saves and reloads (rejoin), including teleports between places.
- [ ] Mobile, gamepad, and keyboard all work; UI readable on a phone.
- [ ] No errors/warnings in Output (server and client).

## Related skills

`roblox-tooling` (CI, Rojo), `roblox-studio-mcp` (agent-driven playtests), `roblox-open-cloud`,
`roblox-code-review`.

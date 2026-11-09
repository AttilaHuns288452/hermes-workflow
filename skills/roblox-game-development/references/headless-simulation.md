# Headless simulation of a real Roblox project

Use when Studio is unavailable (or before spending Studio time) and you still need evidence that the
server and client actually RUN. The harness executes the shipped modules — not copies, not rewritten
logic — against a mock Roblox API.

## Why this beats lint

`luau-lsp` proves types. It cannot catch: a service function called before data loads, a reset that
leaves a table empty, a remote whose argument order drifted, a reward double-paying on replay, a loop
that dies on the first player without a character, or an economy that takes 66 hours to prestige. The
simulator catches all of those in seconds, deterministically.

## Layout

```
tests/sim/
  build.py     # stages src/ -> .sim/ with rewritten requires (gitignore .sim/)
  mock.luau    # Roblox API surface + deterministic scheduler
  run.luau     # boots Bootstrap, drives every Request kind, asserts
  client.luau  # boots the same server, adds PlayerGui/LocalPlayer, loads client modules
```

`.sim/env.luau` is generated and must be the SINGLE mock instance both the sim and the staged modules
bind to. Whatever the sim reads (`M.services`, `M.tags`, `M.pushes`) must be the same objects the
modules mutated; otherwise the tests silently observe a different world. Assert it:

```lua
assert(require("../../.sim/env").game == M.game, "mock env split across require paths")
```

## Re-stage after EVERY `src/` edit — `.sim/` is a copy

`.sim/` is a snapshot of `src/`, not a live view. Edit a module and run the sim without rebuilding and you are
testing the PREVIOUS code, and the failure is indistinguishable from a real bug: a newly added Config table
reads nil, a part the builder now creates is absent, a renamed seat still answers to its old name. Always
invoke the pair as one chain — `python3 tests/sim/build.py && luau tests/sim/run.luau` — and when something you
just wrote "does not exist", rebuild before debugging it. This is the single most common way to lose an hour
in this harness, and it happened repeatedly in one session even knowing the rule.

## The staging transform

| Written for Roblox | Staged to plain Luau |
|---|---|
| `require(script.Parent.X)` | `require("./X")` |
| `require(script.Parent:WaitForChild("X"))` | `require("./X")` |
| `require(ReplicatedStorage.Shared.X)` | `require("../shared/X")` |

Two non-obvious extras:

- **Inject a prelude of locals.** The CLI's `_G` is READONLY, so `_G.game = mock` throws
  "attempt to modify a readonly table". Prepend to each staged file:
  `local __env = require("../env")` then `local game, workspace, Instance, Vector3, CFrame, Color3, UDim, UDim2, NumberRange, TweenInfo, Random, Enum, task, warn, tick, time = __env.game, ...`.
  Locals shadow the (absent) globals cleanly.
- **Append `return true` to `.server.luau` / `.client.luau`.** Scripts return nothing in Roblox, but
  `require` demands exactly one value; without this every Script fails as
  "module must return a single value" — which reads like a game bug and is not.

Check the rewrite is total: after substituting, abort if any `require(script` or
`require(ReplicatedStorage` survives in a staged file.

## Mock surface (ordered by what server code touches first)

`Instance` tree · `Vector3` · `CFrame` · `Color3` · `UDim`/`UDim2` · `NumberRange` · `TweenInfo` ·
`Random` · `Enum` · `task` · `game:GetService` · `Players` · `ReplicatedStorage` · `Workspace` ·
`Lighting` · `DataStoreService` · `CollectionService` · `RunService` · `MarketplaceService` ·
`TweenService` · `BindableEvent` · `RemoteFunction`/`RemoteEvent`.

## Mock implementation traps (each one costs an hour if missed)

- **Dot-access resolves CHILDREN.** `Workspace.Map.CentralPark` is normal Roblox. Implement child
  lookup by name in the proxy's `__index`, after property lookup; without it the map builder dies on
  `attempt to index nil`.
- **A local is not in scope inside its own initializer.**
  `local proxy = setmetatable({}, { __newindex = function() ... proxy ... end })` captures a GLOBAL
  `proxy` (nil), so parenting silently inserts nil. Write `local proxy: any` on one line and
  `proxy = setmetatable(...)` on the next.
- **One metatable only.** Setting a second `setmetatable(proxy, methods)` discards the property
  `__index` you installed first (every field then reads nil). Merge: property lookup falls through to
  a `methodLookup(key)` function.
- **`rawget` needs raw fields.** If helpers read `rawget(inst, "_props")`, also `rawset(proxy, "_props", props)`
  and `rawset(proxy, "_children", children)`; an `__index` branch returning props does not satisfy raw access.
- **Events must exist on demand.** `__index` returns a lazily created `Signal()` for known event names:
  `Touched`, `Activated`, `MouseButton1Click/Down/Up`, `Triggered`, `PromptTriggered`, `Seated`,
  `Died`, `HealthChanged`, `Changed`, `ChildAdded`, `Event`, plus `OnServerEvent` and `Fire` for
  BindableEvent/RemoteEvent. A missing one surfaces as "attempt to index nil with 'Connect'".
- **RemoteFunction `InvokeServer` must inject the player.** Server code sees `OnServerInvoke(player, kind, payload)`;
  client code calls `InvokeServer(kind, payload)`. In the mock, if a `localPlayer` is registered prepend it,
  else treat the first argument as the player.
- **Characters need `Head` + `Humanoid`.** Client code `WaitForChild("Head")` for name tags; a root-only
  mock times out.
- **`RunService:IsStudio()` gates real behaviour.** Shutdown saves are commonly skipped in Studio.
  Expose a `studio` flag and flip it false to test the live-server path.
- **Signal handlers must run in their OWN coroutine.** Roblox starts each handler synchronously up to its
  first yield, then resumes it later. A mock that calls handlers inline makes any handler containing
  `task.wait` throw "thread yielded unexpectedly" — which reads as a game bug. Fire each handler via
  `coroutine.create` + `coroutine.resume`; the injected `task.wait` already queues the resume.
- **`FireClient` must DELIVER, not just record.** A mock that appends to a `pushes` list and stops leaves the
  entire server→client half of the game untested: snapshots never reach `ClientState`, panels never re-render.
  Fire the remote's `OnClientEvent` in the same call (headless, "the client" is this process). Same for
  `BindableEvent`: `Fire` and `Connect` must share one signal table, or `onState` silently delivers nothing.
- **Provide engine DEFAULTS, not just assignments.** Code reads properties it never set: `ScreenGui.DisplayOrder`
  (0), `Frame/TLabel/Button.ZIndex` (1), `Visible`. Return those from a per-class defaults table in `__index`,
  otherwise a draw-order assertion compares against `nil` and crashes or, worse, passes vacuously.
- **`PivotTo` on a Model must move its parts.** Server code teleports characters/models with `model:PivotTo(cf)`;
  a mock that only stores the CFrame leaves every part where it was, so proximity checks read the old position.
  Walk the children and set each `BasePart.Position`.
- **Parent created players to `Players`.** Real Roblox parents every player; join hooks guard `while player.Parent
  and not DataLoaded do`. A mock that leaves `Parent` nil makes every one of those hooks return immediately — the
  feature silently never runs and the test reports success for code that never executed. This is the highest-cost
  class of mock defect: a fidelity gap that reads as a passing test. When a feature "works but does nothing",
  check whether its entry condition is ever true in the mock before touching the feature.
- **Add value types and instance classes as the code grows into them.** Cosmetics, particles and welds pull in
  `Vector2`, `ColorSequence`, `NumberSequence`, `NumberRange`, `WeldConstraint`, `Motor6D`, `Attachment`. A missing
  constructor surfaces as "attempt to index nil with 'new'" from deep inside a service, which reads like a game bug.
  Add them to both the mock and the injected prelude list at the same time — a local in the prelude with no mock
  value underneath it is an equally confusing nil.
- **Value-type metatables still need `__index = MT`.** `setmetatable({...}, Color3MT)` without
  `Color3MT.__index = Color3MT` leaves every method invisible — `attempt to call missing method 'Lerp'` from a
  deep service line that reads like a game bug. Implement the methods the code actually calls (`Color3:Lerp`
  for colour blending) on that table.
- **Engine defaults include `BasePart.Color` and `Player.AccountAge`.** Every real part is born with a colour
  (medium stone grey); appearance code that remembers an original colour and restores it later reads nil
  without one. Build that default with `Color3.new(...)`, not a raw `{R=,G=,B=}` literal, so it carries the
  metatable above. `AccountAge` is read by anti-alt logic — default it to an established account (e.g. 400)
  and override per test, or every player looks brand new and the social multiplier silently halves.
- **Scripts run outside the staged tree have no injected prelude.** A helper like `dump_ui.luau` is plain Luau:
  `warn`, `task` and the rest exist only in modules `build.py` staged. A bare `warn(...)` there throws AFTER the
  real output and interleaves the error into the piped JSON, corrupting it — use `print`. Likewise `Enum` values
  serialize as `table: 0x…`; write `.Name` when dumping them.
- **`Instance:Play` / `Stop` / `Pause` on Sound.** Audio wiring calls `sound:Play()`; without a method the call site
  throws. Make it RECORD the sound and its `SoundId` so an assertion can prove which effect fired.

## Boot only once

The sim and Bootstrap must not both build the world. `require("Bootstrap")` already calls
`MapBuilder.build()` and starts every service; calling `build()` again in the harness doubles every zone,
prompt and collectible, and assertions then pass or fail against a duplicate map. Boot through Bootstrap
only — and give `MapBuilder.build()` a guard that warns and returns if `Workspace.Map` already exists, so a
second call can never silently double the world in production either.

## Write assertions that cannot lie

- **Never trust `os.clock()` in a fast run.** Rate limits use real time while `pump()` advances virtual
  time, so a 30-request burst arrives "within one second" and correctly trips. Wrap request calls in a
  retry that busy-waits ~1.05s once on a `rate` failure, and test the limiter itself with RAW calls
  (the wrapper would hide it).
- **Poll phase-dependent loops, don't pump once.** Autosave/achievement/cycle loops start at boot, so
  "pump exactly one interval" lands wherever the phase happens to be. Loop until the expected state
  appears, bounded by 2-3 intervals, and fail on the timeout.
- **Isolate players between sections.** Other joined players standing in the same zone legitimately
  count toward Social Energy and will make a "solo" assertion read as a social tick. Leave everyone
  else before a solo measurement.
- **Strip reward spikes.** Achievement/journal payouts can land on any tick and only ever ADD. Take the
  minimum of several samples to recover the clean rate, then compare against the expected value
  computed from Config — a ±0.5 tolerance catches a real regression without flaking on a bonus.
- **Search the right root.** `MapBuilder` may parent folders to `Workspace` directly (`Hill`, `Campsite`)
  while other geometry lives under `Workspace.Map`. Look both up; a zero count usually means wrong root,
  not a missing feature.
- **Match the real contract for duplicates.** If the service treats a re-register as idempotent success
  (`true, "already registered"`), assert the message AND that no second reward was paid — not `ok == false`.
- **Assert the world is joinable**: a `SpawnLocation` exists, zones are tagged, every spawn part of a
  family carries its `ProximityPrompt`, and the species/collectible count equals the Config table length.
- **Assert the world is WALKABLE, not just populated.** Point samples prove a coordinate has ground; a player
  walks a line. Sample every real route every 4-6 studs and report the first gap with coordinates, sweep the
  full width of each opening (not the centre line), require ground under every prompt host, and check distance
  from standing height against the prompt's activation range. This is the only class of test that catches
  "the third firewood log spawned past the campsite patch and floats over the void" — a defect that passes
  every teleport-based assertion while making a whole activity unfinishable.
- **Assert the hint matches reality.** If a config string tells the player where something is (`habitat =
  "Forest at night"`, a collectible `hint`), compare it to the spawn's actual zone in the test. Text that
  points at the wrong place is worse than no text: it sends the player on a failed walk. Prefer giving every
  undiscovered entry a location lead at all — `???` plus `undiscovered` across fourteen entries gives a new
  player nothing to act on.
- **Assert discovery is reachable AND discoverable.** Register every species and collectible in one run, and
  for a condition-gated entry (night-only, weather-only) assert it is REFUSED outside the window and accepted
  inside it — a gate nobody can satisfy and a gate that never closes are both bugs.
- **Assert the payoff exists, not just the counter.** If a stat accumulates (friendship, streak, mastery),
  assert crossing its threshold actually pays and that re-crossing cannot pay twice. A counter with no reader
  passes every increment test.
- **Test the interruptions, not just the happy path.** Respawn mid-session (character destroyed, new one loaded,
farming resumes, GP retained), leaving mid-activity (slide started, camp half-done, no explicit save — the
departure save must still hold it), a mass disconnect, and a multi-minute soak with several players where GP
never regresses. These are where per-character hooks, save paths and loop guards actually get exercised.
- **Fuzz every request kind.** Send `nil`, numbers, strings, booleans and malformed tables to all kinds and
require no handler returns an "internal error" — a handler that throws inside the dispatcher's pcall has
failed to validate, not merely rejected input. Repeat mid-session after a legitimate start so early-return
guards ("not started") do not shield the payload path, and assert hostile calls create or destroy no currency.

## Coverage that pays for itself

Join + DataLoaded gate → farming rate and off-zone stop → upgrade purchase → journal proximity and
idempotency → settings clamping → quest claim → rebirth refusal and success (upgrades reset, journal
kept) → shop → receipts (grant, replay, unknown id, absent player, boost expiry) → failed-load no-save
→ autosave → BindToClose → rejoin persistence → activities (camp steps, slide bounds, run gate) → pets
→ tutorial → Social Energy exact multipliers → security (unknown kind, non-string kind, cross-map claim,
rate limit) → economy pacing bands.

Client side: every module loads, ≥8 ScreenGuis build, every panel opens by button AND by keybind, and
`ClientState.request` round-trips into the real dispatcher.

### Persona passes

A single happy-path player hides the two things that decide whether a game lives: whether a lone newcomer
can get going, and whether bringing friends is worth it. Write one scenario per persona and assert the
NUMBERS, not just that nothing errors.

- **Solo newcomer, ten minutes.** Join → streak fires → earn in the starter area → reach the hub → earn →
afford and buy the first upgrade. Assert time-to-first-purchase against the design band.
- **Small group.** Three fresh players standing together must each earn AND collectively out-earn a solo
  player per tick. Assert social ticks are generated, and that a group activity pays more than doing it alone
  — a campfire that pays identically for one person and five gives nobody a reason to organise.
- **Veteran beside a newcomer.** Give one account prestige levels, currency and upgrades; assert the veteran
  visibly out-earns while the newcomer still progresses from the company. This is the only test that catches
  a progression curve that either flattens (veteran gains nothing) or wallpapers (newcomer cannot participate).
- **Clean the arena between personas.** Leaving earlier players joined keeps their Social Energy contribution
  alive and silently inflates or deflates the solo baseline.


## Boundary

Reports as a server/client runtime test — never as a playtest. It says nothing about pixels, layout,
touch input, physics, animation, or streaming. Those stay `Not tested` until a Studio session exists.

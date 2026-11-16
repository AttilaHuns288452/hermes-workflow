# Making a repeatable activity feel like a game

A loop that pays currency for an action is a chore. What makes it read as a minigame is a
scoreboard, a clock, and a payoff moment — three small additions that reuse one another.

## 1. One result card, N activities (client)

The server decides the copy; the client renders it. Then a new activity needs no client change and
every activity feels like part of the same game.

```lua
-- server: the returned table is authoritative; the push is for the card
local result = { gp = reward, distance = ..., streak = ..., isBest = ..., best = ... }
remotes.Push:FireClient(player, "activityResult", {
  title = if isBest then "NEW BEST SLIDE" else "SLIDE",
  value = ("%d studs"):format(result.distance),
  meta  = table.concat({ ("+%d GP"):format(reward), ("%d studs/s"):format(speed) }, "  ·  "),
})
return true, result
```

```lua
-- client: one handler, whatever the activity
if event == "activityResult" then showResult(payload); return end
```

Rules that keep it working:

- Return the same table you push. The headless test asserts on the return value, and copy drift
  between the card and the tested path is invisible otherwise.
- Keep the card to three fields: a short title, one big number, one metadata line joined with `·`.
  Four fields and it becomes a panel nobody reads.
- Pop it in and fade it out on a timer; a card that stays is a modal.

## 2. Every activity needs a scoreboard

Without one, two runs are interchangeable and there is no reason to try again.

- **Personal best**, persisted, shown on the card, and used to change the card's *title* (`NEW BEST RUN`).
- **Combo**: N consecutive completions inside a window multiply the payout (`+15%` per step, capped).
  Put the window in `Config` so a test can advance past it instead of sleeping.
- **Pace**: for a timed run, emit a split per checkpoint (`CP 3/5 · 12.4s · on pace`) and colour it
  against the best time. A count alone is a checklist; a count with a clock is a race.
- Read the *previous* value before overwriting the timestamp the window compares against — computing
  the delta after assigning `lastEnd = now` makes every run a combo.

## 3. Give the session a clock

A depleting resource is the cheapest way to give a session a shape and to put a natural ceiling on
idle income.

- Store the deadline as an **absolute timestamp attribute on the world object**
  (`fire:SetAttribute("FuelUntil", tick() + burnSeconds)`), so the loop carries no per-object state.
- Drain in one guarded tick loop; pay every participant in range on each tick; extinguish at zero and
  tell the players nearby.
- Let players feed it: adding a log pushes `FuelUntil` forward, which turns "gather" into a decision
  rather than a chore.
- Show the remaining time in the HUD. An invisible countdown motivates nobody.

## 4. Cap the faucet, not the price

- Duplicate rewards (re-collecting a unique item) need a **daily cap** in `Config`; otherwise the
  repeatable action out-earns active play and the activity tier becomes pointless.
- An empty instance pays nothing but still expires — otherwise players park an alt and farm.
- Every cap belongs in `Config` with a comment naming what it protects, so tuning does not require
  reading the service.

## 5. Test the contract, not the feel

- Assert the scoreboard, not the number: "first completion sets a personal best", "an equal run does
  not beat it", "a second run inside the window builds a combo", "payouts stop at the daily cap",
  "lighting the fire starts a burn timer" and "the timer runs out".
- Assert the *returned* result table so a client-only regression cannot pass.

## Design constraint worth remembering

Duplicate collection items must be fuel, never waste: fuse N duplicates into the next tier or pay a
reduced reward plus progression currency. A collection whose fifth copy of the common item is
worthless is the failure mode, not the edge case — and item spawns that never despawn make that the
most common interaction in the game.

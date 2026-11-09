# Publishing a Roblox experience and activating monetization

Paths, gates and verification for moving a completed Rojo build onto Roblox and turning `id = 0` placeholders
into live products. Everything here is checked against the public Roblox web APIs, not against dashboard prose.
Substitute the project's own universe/place/product IDs.

## Paths to a new published place

| Path | Requirement | Notes |
|---|---|---|
| Studio, Publish | a working Studio session | the only path that also yields a real playtest |
| Open Cloud versions endpoint | API key with `universe-places:write` | scriptable, no GUI |
| Creator Hub | nothing | **no place-file upload exists here**; it manages the experience shell only (name, icon, maturity, products) |

A new experience ships as a template baseplate. Nothing built locally reaches players until one of the first
two paths succeeds, so report publish state from the API (below), never from a green local build.

## Gate 1: content maturity questionnaire

Until it is submitted, the overview carries a red **"Game unplayable"** banner and the game cannot be played
publicly. It is a one-question-at-a-time wizard (`No`/`Yes` radios, `Preview rating`, `Back`, `Cancel`): there
is no `Continue`, the forward action is **Preview rating**, then **Submit**.

Answer honestly per category (violence, blood, fear, crude humor, gambling-related, social hangout). A
social-hangout `Yes` moves audience reach to 16+, which is a product decision, not a bug to click around. A
clean quiz previews as **Minimal** and clears the banner immediately.

The radios are Radix buttons; clicking the `<label>` frequently does not register. Click the
`button[role=radio]` element itself at its measured centre, then confirm `aria-checked` before advancing.

## Gate 2: Open Cloud place upload

```
POST https://apis.roblox.com/universes/v1/{universeId}/places/{placeId}/versions?versionType=Published
x-api-key: <key>
Content-Type: application/xml
<body: the .rbxlx bytes>
```

Success returns `{"versionNumber": N}`. Resolve `universeId` and `rootPlaceId` from the public games API
rather than guessing which of two IDs on a dashboard page is which.

### Reading the error codes

| Status | Body | Meaning |
|---|---|---|
| 401 | `Invalid API Key` | the key string itself is wrong or truncated, see the capture section |
| 403 | `Scope not authorized` | key is valid, the required scope is not actually attached |
| 200 | `{"versionNumber": N}` | published |

Treat 401 and 403 as different faults. Conflating them sends you re-creating keys when the real problem is a
missing scope, or debugging scopes when the key was simply mangled.

## Capturing an API key without corrupting it

Roblox API keys are **standard base64**, so they contain `/` and `+` and may end with `=` padding. A scrape
pattern like `[A-Za-z0-9_-]{200,}` silently splits the key at the first `/`: the result is a plausible
~960-character string that fails with 401 and reads like a permissions problem.

- Match the full set: `[A-Za-z0-9_\-+/]{200,}={0,2}`.
- Prefer an element's `textContent` with all whitespace stripped over `innerText`; the rendered key wraps
  across lines and `innerText` can cut it at the wrap.
- Never overwrite a stored working secret with a read you have not validated. A stale clipboard read will
  happily clobber a good key. Check length AND charset before writing.
- Validate by authenticating, not by eyeballing length.

## Verify what is actually live

Two unauthenticated endpoints answer "is it live" without trusting any UI:

```
# live experience state: name, updated timestamp, visits, creator
GET https://games.roblox.com/v1/games?universeIds=<universeId>

# a game pass: price and sale state
GET https://apis.roblox.com/game-passes/v1/game-passes/<passId>/product-info
```

`updated` is the decisive field for publishing: if it predates your build, the place is still the template no
matter what any deploy flow reported. `PriceInRobux` + `IsForSale` is the decisive pair for a pass. There is no
equivalent public read for developer products, so keep their IDs in `Config` as the record of what was created.

## Creator Hub automation notes

The dashboard is MUI/Radix. Native `.click()` often fails to commit state: hidden inputs ignore it, autocomplete
options dismiss instead of selecting, and a save can look successful while the value is dropped.

- Set text through the native setter plus events, never by assigning `.value`:
  `Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(el, v)` then dispatch `input`.
- Commit an autocomplete through the **keyboard**: focus the input, clear it, type with
  `Input.dispatchKeyEvent type='char'`, then `ArrowDown` + `Enter`. Clicking the popup option often just closes
  the list without selecting anything.
- Toggle switches by clicking the Radix `button[role=switch]` at real coordinates, not the hidden checkbox.
- **After any save, reload and re-read the value.** A permission chip that comes back as "No permissions added
  yet" was never persisted, and every later API call will 403. One reload tells you this; retrying the save a
dozen times does not.

## Confirm the universe before you create anything

Products and passes are scoped to ONE universe. Creating them under the wrong experience is silent: the
dashboard shows them as live, the IDs are real, and the published game's shop is empty because it asks a
different universe.

Resolve the live universe first, from outside the dashboard:

```
GET https://games.roblox.com/v1/games?universeIds=<candidate>   # name, rootPlaceId, updated, creator
```

A running Studio session also logs the truth for the place it has open — grep its session log for
`[telemetryLog] universeid:` and `placeid:`; those come from the file actually being edited, so they cannot
disagree with what will publish. Do this before the maturity questionnaire and before any product creation:
both are per-universe work you would otherwise redo.

Old placeholder experiences stay in the account and keep real-looking IDs. When a publish lands on a new
experience, re-point `Config.Monetization` and re-create anything that lived on the old one rather than
assuming the IDs carried over.

## Activation checklist

1. Maturity questionnaire submitted, no "Game unplayable" banner.
2. Live universe confirmed; every product and pass created under THAT universe.
2. Products and passes created; IDs read from the dashboard list.
3. IDs written into `Config.Monetization`; `configured = true`.
4. Pass verified via `product-info` (price and `IsForSale`).
5. Place published via Studio or the versions endpoint; the games API `updated` now postdates the build.
6. Purchase path exercised in the sim harness against the real IDs: grant, replay rejection, unknown-ID refusal.

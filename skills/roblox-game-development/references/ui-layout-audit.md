# UI layout audit without a renderer

Studio is blocked, but layout is not unknowable: the client modules are just code, and code can print its
own geometry. Dump the built GUI tree, render the rects to PNGs to look at, and audit them numerically in
the same pass.

Proves: element rects, colours, text content, wrap/truncate flags, draw order, touch-target sizes, panel
fit against the design viewport.
Does NOT prove: real font metrics, `UIScale` interaction, animation, actual pixels, touch ergonomics.
Label it a layout audit, never a playtest.

## Layout of the harness

```
tests/sim/dump_ui.luau    # boots Bootstrap + all client modules, prints the layout as JSON
 tests/sim/render_ui.py    # JSON -> one PNG per panel + contact sheet (PIL)
tests/sim/audit_ui.py     # JSON -> exit 1 on the defect classes below
```

Pipeline: `python build.py && luau dump_ui.luau | sed -n '/UI_JSON_BEGIN/,/UI_JSON_END/p' | sed '1d;$d' >
/tmp/ui_layout.json && python3 render_ui.py && python3 audit_ui.py`.

The dump must print JSON between sentinel lines and the caller redirects it: **the Luau CLI has no `io`
library**, so `io.open(...)` is `attempt to index nil with 'open'`. Print, then `sed` the markers off.

## Driving the client so there is something to dump

`dump_ui.luau` mirrors `client.luau`: create a player, `LoadCharacter`, `join`, pump, build a `PlayerGui`
Folder parented to the player, register `localPlayer`, then `pcall(require, ...)` all client modules. Panels
are built at module load; rows are built on `render()`, which runs on open.

**Populate `ClientState.state` with a complete save before dumping** (gp, ep, nt, level, upgrades, species,
collectibles, stats, achievements, titles, cosmetics, pet, quests, enlightenment). A half-filled state makes
panels render `nil`/blank rows and the audit then reports layout defects that are really missing test data.

## Geometry rules for the collector

- Accumulate each descendant's offset up to its panel by walking ancestors: `offset += scale(child) *
  parentRect + child.offset`. UDim fields can be missing on mocked objects — guard every read and default to 0;
  `num()` returning two values inside an arithmetic expression silently uses only the first and will be `nil`
  on a field that was never set.
- Emit per element: `kind`, `name`, `x/y/w/h`, `color`, `transparency`, `visible`, `text`, `textColor`,
  `textSize`, `wrapped`, `truncate`, `listed`.
- **`listed` is mandatory.** Children of a `UIListLayout`/`UIGridLayout` have `Position = (0,0)` until Roblox
  lays them out at runtime. Overlap-checking them produces ~100 false "buttons overlap" findings on a clean
  layout. Set `listed = true` when ANY ancestor holds a layout, not just the immediate parent (a row button
  inside a row Frame inside a list is still list-managed), and skip those in the overlap check.

## The audit's defect classes

| Check | Rule | Why it matters |
|---|---|---|
| Text overflow | `maxLineLen * textSize * 0.55 > boxWidth` AND not `wrapped` AND `truncate == None` | Roblox TextLabels do not ellipsize: the text is simply cut mid-word, no error |
| Panel fit | panel rect inside the design viewport (0,0)-(W,H) | a panel wider than the screen clips silently |
| Child containment | label/button rect inside its panel rect | absolute offsets drift when copy-pasted |
| Overlap | two absolutely-positioned buttons intersect | two clickable rects on top of each other |
| Touch target | any button < ~28px in design space | fine on desktop, unusable on a phone |

`CHAR_W = 0.55` (fraction of font size per character) is a deliberate over-estimate so the check fails on
the safe side. Only apply the wrap check to single-line strings — a `\n` string is already wrapped by
construction.

## Prove the audit bites

An audit that passes on everything is decoration. Inject two defects into a COPY of the JSON — set a label's
`wrapped = false` and lengthen its text, shrink a button to 12x12 — run the audit, confirm exit 1 and the
right messages, then restore and confirm exit 0. Cheap, and it is the only evidence the gate is real.

Note the touch-target check must sit OUTSIDE the text branch: buttons with no label (`X` close buttons,
bare icon buttons) have no text and were skipped entirely by a naive "for each labelled element" loop.

## Rendering to look at

`render_ui.py` draws a game-like backdrop, then every rect in draw order (`depth`, then descending area so
panels sit under their children), with a truncated single-line label approximation and `\n` split into
lines clipped to the box. Output one PNG per panel plus a contact sheet labelled with the panel names.

This is an approximation of Roblox text, not a screenshot — use it to judge spacing, hierarchy, crowding and
missing content. Never claim pixel fidelity from it.

## Interview the numbers, not the prose

When a layout gate reports dozens of findings, check the FINDING CLASS before editing anything: 100 "buttons
overlap" on a layout you just built is almost always a harness artifact (list positioning, per-frame
transforms), while 3 "text clipped with no wrap" is almost always real. Confirm by inspecting one element's
raw dump entry, then fix the harness or the code — never bulk-edit UI to satisfy a broken probe.

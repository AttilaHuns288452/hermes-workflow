---
name: roblox-gui
description: "Use when building or fixing Roblox menus, HUDs, shops, dialogs, or UI that must work on phones, tablets, desktop and console"
---


# roblox gui

## When to Load

HUDs, menus, shops, dialogs, world UI, and layout bugs on phone, tablet, desktop or TV.

## Quick Reference

- Mobile first: design on the smallest landscape phone with touch controls, then grow (full.md §11).
- Reserve top bar, thumbstick, jump, chat; interactive UI in `CoreUISafeInsets`; place by measured `AbsolutePosition`/`AbsoluteSize`.
- Check every element pair that can show together; reflow, don't shrink.
- Gamepad: one `SelectedObject` owner, `SelectionGroup` bounds, restored focus, layered Back (§8).
- Console: TV-safe area, `ViewportDisplaySize`, no chat window.
- Layouts own repeated layout; UI shows server state; a button is not an authority boundary.
- Reactive UI: per-screen cleanup; repeat open/close to test leaks. Loading UI in `ReplicatedFirst`.
- TextBox submit, grids, truncation, RichText safety, deprecated APIs: full.md.
- **HUD text sits OVER the world with no panel behind it, so it needs paper text + a full ink stroke — never ink-on-transparent.** Ink reads fine on a pale wall and disappears on grass, and the only symptom is somebody squinting at a screenshot. Apply the stroke to every bare label (caption, meta line, clock), not just the big number.
- **Guard it in the headless suite, and prove the guard.** Walk every TextLabel under the HUD: if no ancestor paints a background (`BackgroundTransparency < 1`), the label must have `TextStrokeTransparency < 1`. A guard that has never failed is not yet evidence — reintroduce the bug once, confirm the assertion fails, revert it.

> Details: [references/full.md](references/full.md)

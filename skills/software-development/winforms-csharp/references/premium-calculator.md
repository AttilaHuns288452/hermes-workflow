# Premium Calculator UI Reference

## Verified Color Palette (RGB)

- Form background: `#1E1E1E` <=> `RGB(30, 30, 30)`
- Display background: `#141414` <=> `RGB(20, 20, 20)`
- Display text: white, Segoe UI 28pt Bold
- Number/decimal buttons: `#323232` <=> `RGB(50, 50, 50)`, white bold
- Function buttons (Clear/±/%): `#969696` <=> `RGB(150, 150, 150)`, black text
- Operator buttons: `#FF9500` <=> `RGB(255, 149, 0)`, white text
- Equals button: `#007AFF` <=> `RGB(0, 122, 255)`, white text

## Layout Rules

- Standard 4-col x 5-row grid.
- `0` button spans 2 columns.
- Operators are right-hand column.
- Flat borderless, padding 4px.
- For premium look, keep minimum button W/H 64x54.

## Proven Implementation Notes

- Target framework: `net8.0-windows`.
- Minimum button visual contrast: button Fill must differ from Form BackColor.
- Never use near-black button fill (`#1A1A1A`) on a dark form (`#1E1E1E`).
- Hover state: lighten button base color 15-20%.
- Windows/MSYS shell paths: use POSIX `/c/Users/YOUR_USERNAME/...` or live with current cwd inside project dir.

## Failure Modes to Avoid

- Loading skill without editing Program.cs => Boilerplate workspace form is not a calculator.
- Using literal Windows backslash paths in MSYS-like shell without converting to POSIX form.
- Missing hover feedback => feels dead and unresponsive.
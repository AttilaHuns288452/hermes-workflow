# Calculator Pattern Notes

## Verified Implementation Shape
- Single partial `Form` class in one file when starting from scratch.
- `AddButton` span control is a `bool`, not an integer count.
- Correct call shape:
  - `AddButton("0", 0, 4, ..., spanColumns: true);`
- Incorrect call shape that triggers `CS1503`:
  - `AddButton("0", 0, 4, ..., spanColumns: 2);`

## Dark Theme Defaults
- Form: `RGB(30, 30, 30)`
- Display: `RGB(20, 20, 20)`
- Digits: `RGB(50, 50, 50)`
- Operators: `RGB(255, 149, 0)`
- Equals: `RGB(0, 122, 255)`
- Functions: `RGB(150, 150, 150)`

## Operator Symbols
Use `÷` and `×` when the UI should expose familiar calculator glyphs.

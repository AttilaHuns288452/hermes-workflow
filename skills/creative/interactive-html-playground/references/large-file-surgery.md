# Safely Editing Large Single-File HTML Playgrounds

When a playground reaches 2000+ lines, `patch()` (fuzzy find-and-replace) breaks
on template-literal-heavy JS — backtick strings (`html += `...``) confuse string
boundaries. Use Python to read → transform → write the file instead.

## Procedure

```python
import os

path = os.path.expanduser('~/project/index.html')
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# lines is a 0-indexed list, each item is "line content\\n"

# --- Insert lines at a specific position ---
insert_line = 210  # line number (1-indexed) minus 1
new_lines = [
    "      { id: 'components', name: 'Components', icon: '🧩' },\n"
]
lines[insert_line:insert_line] = new_lines

# --- Reorder blocks (move preview block above controls) ---
controls = '\n'.join(lines[1232:1292])   # extract
preview  = '\n'.join(lines[1292:1307])
# Build new order
new_block = [preview, '', controls]
# Replace old block
old_block = '\n'.join(lines[1229:1321])
new_content = html.replace(old_block, '\n'.join(new_block), 1)

# --- Write back ---
with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)
```

## Verify After Edit

```python
with open(path, 'r') as f:
    content = f.read()

# Count balanced punctuation
print('Backticks even:', content.count('`') % 2 == 0)
print('Braces balanced:', content.count('{') == content.count('}'))
print('Parens balanced:', content.count('(') == content.count(')'))
print('</html> count:', content.count('</html>'))  # should be 1
```

## When to Use This Instead of `patch()`

| Use `patch()` | Use Python surgery |
|---|---|
| < 500 lines | 2000+ lines |
| No template literals | Template literals with backtick strings |
| Single targeted edit | Reordering/moving blocks |
| Known exact strings | Dynamic index-based manipulation |

## Caveats

- Line numbers shift after each edit. Re-read between operations.
- Template literals inside `html += `...`` use backticks — don't match on backtick
  boundaries, match on the comment header before each block.
- Always verify syntax balance before writing.

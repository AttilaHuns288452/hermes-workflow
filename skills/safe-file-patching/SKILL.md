---
name: safe-file-patching
description: Guides when to use patch vs complete rewrite, especially for syntax-sensitive files (JSX, JSON, Python, YAML). Use when editing existing files in codebases, fixing build errors, or applying changes that involve structured/parsed content.
---

# Safe File Patching

## Overview

The `patch` tool is fast and convenient, but its fuzzy matching (9 strategies) can consume more content than the old_string describes — especially in syntax-sensitive files like JSX, JSON, Python, or YAML. This skill teaches when to patch safely and when to rewrite entirely.

## When to Patch

| Situation | Recommend |
|---|---|
| Single-word or single-line change with unique context | Patch |
| Whitespace normalization | Patch |
| Adding/removing import lines at the top of a file | Patch (with care) |
| Changing a CSS class name or attribute value | Patch |
| Adding a new section at the end of a file | Patch |
| Replacing function body while keeping signature | Patch |
| **3+ structural changes in a JSX/TSX file** | **Rewrite** |
| **File has already been patched 2+ times this session** | **Rewrite** |
| Error moves to different location after each fix | **Rewrite → full file rewrite** |
| Change involves tag nesting (opening/closing mismatches) | **Rewrite, especially JSX** |

## Patch Pitfalls by File Type

### JSX / TSX (Most Dangerous)

JSX is the most fragile target for fuzzy patching because:

```jsx
// If you target this line to remove:
<time className="text-gray-500 text-sm mb-4 block">Published Jan 1, 2026</time>
<h1 className="text-3xl font-bold">Title</h1>
```

The fuzzy matcher may consume:
- The `</time>` closing tag (leaving a dangling `<time>`)
- The next line's `<h1` opening tag (leaving bare text + `</h1>`)
- The `<` character from the next element

**Signs of consumed content:**
- "Expected '</', got 'jsx text'" — unclosed parent tag upstream
- Missing `<` at start of a JSX element line
- "Unexpected token 'default'" — missing `};` on metadata block

**Safe approach for JSX:**
```
├── For 1-2 simple changes → Patch with UNIQUE surrounding context (3+ lines)
├── For 3+ changes to the same component → write_file the full file
└── For structural changes (adding/removing wrappers, changing nesting) → ALWAYS write_file
```

### JS Arrays in HTML `<script>` Tags

Inserting entries into an existing JS array via string replacement is fragile because:

- The **last entry before the insertion point may lack a trailing comma** — the original `];` closed the array, so `} } }` was valid. After inserting new entries, that line becomes the second-to-last element and needs `} } },`.
- **JSON-formatted objects (`{"id":...}`) are valid JS** and work fine inside arrays alongside single-quote JS objects, but the missing comma between them causes an immediate parse error.
- **`sectionCard()` returns a DOM element, not an HTML string.** Using it in `sec.innerHTML = '...' + sectionCard(...)` coerces the element to `[object HTMLDivElement]`. Use `sectionCard(...).outerHTML` or `appendChild()` instead.

**Signs of the missing-comma bug:**
- "Unexpected token '{'" at the first inserted entry
- The entire JS-driven page fails to render (sidebar, buttons, all)
- `node --check` on the extracted script content pinpoints the line

**Safe approach for JS-array insertion:**
```
├── Check the last existing entry for a trailing comma BEFORE applying the patch
├── After patching, validate with node --check on the script content
├── Or use execute_code (Python) for programmatic array element insertion
└── Brace/paren balancing (Python: count `{` vs `}` in the array) catches misses
```

### JSON / YAML (Fragile)

Fuzzy matching thinks it found the target but replaces the wrong key:

```yaml
# Target: change key "timeout"
old_string: "timeout: 30"
new_string: "timeout: 60"
# May also match "request_timeout: 30" → "request_timeout: 60"
```

**Safe approach:**
```
├── Patch with the ENTIRE line (indentation included) as unique context
├── Or use execute_code (Python json/yaml libs) for programmatic edits
└── Or write_file the full config file
```

### Python

Fuzzy matching can consume up to the next function/class definition:

```python
# old_string targets a small block
old_string: "def helper():"
# May match the FIRST "def" in the file, not the one you meant
```

**Safe approach:**
```
├── Include the function's entire signature + docstring as context
├── For function body changes, include def line + return statement
└── For multi-method changes → write_file the full file
```

### Repeated Pattern Match Failures (HTML Files)

HTML files with repeated patterns (same `class="section-card ..."` block, same `switchCodeTab` code blocks, same `copy-btn` markup) cause the patch tool to find 8+ matches for a short `old_string`. The tool refuses to apply.

**Fix**: include enough unique surrounding context (3+ lines above/below) that only ONE match exists. The function name, unique ID attribute, or a specific section comment (`<!-- ===== CLAMP ===== -->`) is the best anchor. If `read_file` shows `"` characters in the file, pass `"` in old_string — don't backslash-escape them.

```
├── If old_string matches 2+ times → add more context lines until exactly 1 match
├── Anchor on unique IDs, function names, or section comments
├── Use replace_all=true only if you WANT every instance changed
└── escape-drift error = file has `"` but you passed `\"` — re-read file, copy raw text
```

### replace_all=true Specific Risks

`replace_all=True` replaces EVERY match of old_string in the file, not just the first one. Common surprises:

- **Function definitions get renamed too.** If you `replace_all('sectionCard(', 'sc(')` it renames the function keyword, the definition, and every call site — not just call sites.
- **After replace_all, always verify with grep:**
  ```
  grep 'sectionCard' file.html   # should show function def + wrapper, not call sites
  grep 'sc(' file.html           # should show only intended call sites
  ```
  If the function definition was renamed, patch it back first, then re-verify no other unintended changes remain.

## The "Stop Patching" Checklist

Stop using patch and switch to write_file if ANY of these is true:

```
[ ] The file is JSX/TSX and you're changing the wrapper/nesting structure
[ ] The file has already been patched 2+ times in this session
[ ] A build/test error moved to a different line after the last patch
[ ] You need `replace_all=True` on a structured file
[ ] The old_string is < 40 characters (too short for uniqueness)
[ ] You're targeting a line that contains special characters ({, }, <, >, &)
[ ] The edit crosses multiple indentation levels
```

## Patch Alternatives

Use these instead of patch for structured edits:

| Tool | Best for |
|---|---|
| `write_file` | Full file rewrite (preferred for 3+ edits) |
| `execute_code` (Python) | Programmatic edits via json/yaml/ast libraries |
| `terminal` (sed/awk) | Line-based edits in plain text files |
| `terminal` (git apply) | Applying complete diffs |
| `terminal` (Python script) | Multi-line string replacements where patch's fuzzy matching or escape handling fails |

### JS Template Literal Trap in HTML `<script>` Tags

When patching JS inside an HTML `<script>` tag (not a standalone `.js` file), `\n` passes through **two** escaping layers: **patch-tool JSON → HTML file → JS template literal**. Each layer re-interprets `\n`:

| Patch JSON contains | Written to HTML file | Meaning in JS template literal |
|---|---|---|
| `\n` | `\n` (real newline) | Real newline — correct |
| `\\n` | `\n` (two chars: `\` + `n`) | Literal text `\n` — **the bug** |

The bug: writing `\\\\n` in the patch JSON (intending to produce `\n` text) instead produces `\n` as literal characters in the JS string.

**Rule of thumb**: inside template literals in HTML `<script>` tags, use a single `\n` in the patch JSON to get a real newline. For multi-line CSS code examples, prefer `escapeHtml('line1\nline2')` instead of raw newlines in the template literal — it avoids the escaping chain entirely.

**Signs of the bug:**
- CSS code displayed as `property: value;\nanother: value;` with visible `\n` text
- HTML output shows literal backslash-n in `<code>` or `<pre>` blocks

#### Extended Trap: Apostrophes & Backticks in `onclick` & Template Literals

JS template literals inside HTML `<script>` tags that contain **both** template interpolation (`${...}`) **and** attribute event handlers with single quotes (`onclick="fn('arg')"`) cause a double escaping hazard:

```
<button onclick="flexUpdate('dir','${s}')">${s}</button>
```

The problem: the `'` (apostrophe + single-quote wrapping) in the `onclick` handler gets misread by the patch tool's JSON serialization. The tool emits the "escape-drift detected" error because `old_string` contains escaped apostrophes differently than the file stores them.

**Workaround sequence when patch fails on JS template literals:**

1. **First attempt:** use `patch` with `old_string` taken directly from a re-read of the target lines (no hand-typed escaping). If the re-read shows `'` in the file, pass `'` — not `\'`.

2. **Python script bypass:** If patch still fails with "escape-drift detected" or the match is ambiguous (backticks confuse the fuzzy matcher), write a Python script to disk via `write_file` and run it via `terminal`:

   ```python
   # _edit.py — written via write_file, run via terminal
   with open('target.html', 'r', encoding='utf-8') as f:
       content = f.read()

   old = '<div class="old-exact-content">...</div>'
   new = '<div class="new-content">...</div>'

   assert content.count(old) == 1, f"old appears {content.count(old)} times"
   content = content.replace(old, new)

   with open('target.html', 'w', encoding='utf-8') as f:
       f.write(content)
   print(f"OK: replaced {len(old)}c -> {len(new)}c")
   ```

3. The `assert ... count(old) == 1` guard prevents accidental multi-replace.

4. Clean up with `rm _edit.py` after successful run.

This approach bypasses the patch tool's escaping layer entirely: the Python script handles exact string matching, and `terminal` passes the bytes through without serialization or fuzzy matching.

**When to use the Python-script approach over patch:**

| Symptom | Fix |
|---|---|
| `escape-drift detected` even with exact copy-paste | Python script |
| Patch suggests fuzzy match but region looks correct | Python script |
| Content contains both backticks `` ` `` and `${}` inside template literals | Python script (or write_file the whole section) |
| JSX/TSX nesting changes | write_file the whole file |
| `\"` in file but match fails | Re-read and copy-paste exact content into old_string (fixes most cases) |
| `\\d` or `\s` in regex literal inside JS string | Verify with `od -c`, then patch with correct backslash count |

The Python-script approach is heavier than patch but is the **only reliable path** when the patch tool's escaping chain breaks down on deeply nested template literals.

See also `references/regex-literal-escape-ambiguity.md` for the `\\d`/`\\s` double-backslash trap inside regex literals in HTML+JS files.

### Shell Escaping Trap: Multi-Line in `python -c "..."`

When using `python -c "..."` for multi-line string replacement, the escaping chain is **shell → Python → file**. A `\n` inside a shell double-quoted string becomes `\n` (two chars) in Python, which Python interprets as a **literal newline** — not the escape sequence.

**The bug:** `python -c "s.replace('>','>\\n')"` — shell passes `>\n` to Python, Python sees `\n` as actual newline, writes a real newline into the file instead of `\n`.

**Fix:** use `\\\n` (triple-escaped) in `-c`, or avoid `-c` entirely and use a Python script file or execute_code.

## Red Flags

- Using `replace_all=True` on a JSX file — almost certainly matches unintended content
- Patching the same file more than 3 times in one session — rewrite instead
- `old_string` that's just a tag name like `<p>` or `</div>` — way too short
- Error message changes after each patch — cascading corruption underway
- Close-but-not-exact match suggested by the fuzzy matcher — trust the suggestion means your old_string too loose

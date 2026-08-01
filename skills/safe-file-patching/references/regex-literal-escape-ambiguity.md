# Regex Literal Escape Ambiguity in HTML+JS Files

## The Problem

When `read_file` displays a JS regex literal inside an HTML `<script>` tag, escaped backslashes may appear as `\\` — but you can't tell if the **file actually has two backslash characters** or if `read_file` is displaying a single `\` as `\\` for terminal-safe output.

```js
// read_file shows:
box.className = box.className.replace(/z-\\d+/g, '')

// This could mean EITHER:
// (a) File has:  /z-\d+/g    (single \, regex digit class)  ✓
// (b) File has:  /z-\\d+/g   (double \\, literal \d)        ✗ wrong!
```

Case (b) is a bug: `\\d` in a JS regex literal means literal `\` followed by `d` — it matches `\d` text, NOT digits.

## Diagnosis

Use `od -c` on the actual file byte content:

```bash
sed -n 'LINEp' FILENAME | grep -oP '/z-.+?/' | od -c
```

| `od -c` Output | Meaning | Correct? |
|---|---|---|
| `z - \ d +` (single `\`) | File has `/z-\d+/g` — regex digit class | ✅ |
| `z - \ \ d +` (two `\` chars) | File has `/z-\\d+/g` — literal `\d` text | ❌ bug |

## Fix

Change the regex literal in the file from `\\d` to `\d` (and `\\s` to `\s`).

**Patch parameters** (raw JSON values, no extra escaping):
- old_string: `z-\\d+` (file has two backslashes)
- new_string: `z-\d+` (file should have one backslash)

## Propagation

The `\\d` vs `\d` bug is NOT isolated to one section. If one regex literal in an HTML file has double-backslash, EVERY regex literal in that file likely does too (same author, same editor encoding). Grep across the whole file:

```bash
grep -c '\\\\d' index.html   # count of \\d patterns — if >0, all are broken
```

The visual symptom is insidious: Tailwind's last-class-wins means the CSS appears correct even though old classes accumulate in the DOM. Only a `node --check` on the extracted JS or a direct byte check reveals it.

## Prevention

When writing JS regex literals in a `read_file` argument or patch tool call:

- In a JS regex literal (`/.../`), `\d` is the digit class. Always use one backslash.
- If `read_file` shows `\\` and you're editing JS regex, verify with `od -c`.
- The same ambiguity affects `\\s`, `\\w`, `\\S`, `\\W`, `\\b` — every backslash escape inside regex literals.

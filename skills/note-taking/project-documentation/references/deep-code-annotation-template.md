# Deep Code Annotation Style — Reference Template

> Use this style when embedding code blocks in project documentation.
> The user expects every unfamiliar concept to be explained relative to
> C# CRUD experience (basic classes, if/else, loops, try/catch, switch).

## Style Template

```python
# ═══════════════════════════════════════════════════════════════════════════
# 📦 WHAT IS THIS? (concept introduction)
# Explain in 1-2 sentences what the code does at a high level.
# Anchor to C# if relevant.
# ═══════════════════════════════════════════════════════════════════════════

# ── METHOD SIGNATURE ──
# `def method_name(param: type) -> ReturnType:`
# Like C#: `public ReturnType MethodName(Type param)`
#
# `param: str` — TYPE HINT (optional in Python, unlike C# which enforces it)
# `-> bool` — return type hint (like `bool` return type in C#)
# ─────────────────────────────────────────────────────────────────────────
def some_function(param: str) -> bool:
    # ── LOGIC BLOCK ──
    # In plain terms: what this loop/if/check does.
    # Example: "Loop through each transaction and add to total.
    #          Same as `foreach (var txn in transactions)` in C#."
    for item in items:
        # `condition or default` — Python idiom.
        # If item.name is empty string (falsy), use "Unknown" instead.
        # Like C#: `item.Name ?? "Unknown"` (null-coalescing)
        name = item.name or "Unknown"
        process(name)

    # `raise ValueError(...)` — like `throw new ArgumentException(...)` in C#
    if not valid:
        raise ValueError("Invalid input")
```

## What MUST Be Explained

Every concept in this table needs an inline comment when it appears:

| Concept | C#/Java Equivalent to Reference |
|---------|--------------------------------|
| `@dataclass(frozen=True)` | C# `record class` with init-only props / read-only struct |
| `def __init__(self)` | Constructor — `self` = `this` |
| Type hints `: str`, `-> None` | Optional, doc-only — like C# type annotations |
| f-strings `f"{name}"` | C# `$"{name}"` or Java `String.format` |
| `Optional[X]` | C# `X?` nullable |
| `raise ValueError` | C# `throw new ArgumentException()` |
| `try/except` | C# `try/catch` |
| `dict.get(key, default)` | C# `TryGetValue` |
| `"".join(str(x) for x in xs)` | C# `string.Concat()` / StringBuilder |
| `isinstance(x, Type)` | C# `is` keyword |
| Lambda/arrow `() => {}` | C#/Java lambda |
| `interface` / TypeScript | C# interface |
| Destructuring `{ a, b } = obj` | C# 12 deconstruction |
| Spread `...obj` | C# 12 spread `..` |
| `useState()` in React | C# WPF `INotifyPropertyChanged` |
| `.find(q => ...)` | LINQ `.FirstOrDefault()` |
| `.map(q => ...)` | LINQ `.Select()` |
| `.sort((a,b) => ...)` | LINQ `.OrderByDescending()` |
| `Math.pow()` | C# `Math.Pow()` |
| `Math.sqrt()` | C# `Math.Sqrt()` |
| `Math.abs()` | C# `Math.Abs()` |
| `Math.min/max` | C# `Math.Clamp()` |
| `//` comment | Same as C# |
| `"""docstring"""` | C# `///` XML comment |
| `import` / `from X import Y` | C# `using X;` |

## Display Conventions

- Use **`═══` separator lines** with 📦/💡/ℹ️ emoji headers for major sections
- Use **`─ ` with emoji (💡/🛠️/⚠️)** for inline callouts
- Use **`💡 WHY THIS MATTERS:** ` for design rationale
- Use **`═` table separators** for ASCII comparison tables
- Put the C# equivalent in **parentheses** or after a **→** arrow

# JS Array Insertion Pitfalls When Patching

## The Missing-Comma Bug

When you insert entries into an existing JS array via `content.replace()` or `patch`, the
original last entry ends without a trailing comma because the `];` was the array closer.
The inserted entries sit between that entry and `];`, so the entry needs a trailing comma.

### Symptom

```
SyntaxError: Unexpected token '{'
    at the first line of your inserted entries
```

### Root Cause

Original:
```js
const compDefs = [
  { id: 'nav', ... },
  { id: 'card', ... },
  { id: 'dropdown', ... } } }  // NO comma — was last before ];
    ];
```

After naive insertion:
```js
const compDefs = [
  { id: 'nav', ... },
  { id: 'card', ... },
  { id: 'dropdown', ... } } }  // NO comma — now syntax error
{"id": "tabs", ...},            // parser sees two objects without separator
    ];
```

### Fix

Add `,` to the last original entry: `} } },`

### Prevention Checklist

- [ ] Check the last entry before insertion point for trailing comma
- [ ] After patching, run `node --check` on the extracted `<script>` content
- [ ] Or use Python with brace counting as a quick sanity check

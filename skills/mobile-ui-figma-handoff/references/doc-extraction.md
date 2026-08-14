# Extracting text from legacy .doc binaries (WPS/UTF-16LE)

## Symptom

`antiword file.doc` fails with "I can't open ... for reading" while `file` shows:
`Composite Document File V2 Document ... Code page: 1200 ... Name of Creating Application: WPS Of`.

Code page 1200 = UTF-16LE text inside the OLE2 WordDocument stream. WPS Office
writes these; antiword can't handle the encoding.

## Recipe (no extra tools — stdlib Python)

```python
import re
data = open(path, 'rb').read()
text = data.decode('utf-16-le', errors='ignore')
runs = re.findall(r'[\x20-\x7e\u00a0-\uffff]{3,}', text)
out = '\n'.join(runs)   # printable runs, headers/footers interleaved with garbage
```

The output mixes real body text with OLE metadata garbage (binary runs decode
to CJK-looking noise). Body text is contiguous and readable — slice around
known headings (e.g. find "1. Introduction" and print a window) to pull the
content out. `strings` may be absent on git-bash; this needs no external
binary at all.

## Pitfalls

- The decode is lossy for the whole file; the first ~2000 chars are usually
  header garbage — print from the first recognizable title onward.
- `\r\n` survive; keep them for paragraph boundaries.
- Works for any OLE2 .doc whose strings are UTF-16LE; for ANSI (codepage
  1252) .doc files, prefer `antiword -m cp1252` first.

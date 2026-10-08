#!/usr/bin/env python3
"""guide_builder.py — skeleton generator for a self-contained offline docs handbook.

Usage: fill SECTIONS (id, title, group, source-md), SNIPPETS (path, s, e + metadata),
and optional DIAGRAM_ASCII (mermaid fence replacements), then run:
    python3 guide_builder.py  ->  HANDBOOK.html (no external resources).
Key guarantees:
- output has zero <script src>/<link>/<img>/fetch — all CSS/JS inline
- code snippets are sliced from real source at build time
- search/theme/copy/drawer all work from file://
"""
import re, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / 'HANDBOOK.html'

SECTIONS = [
    # (id, title, nav-group, source markdown filename or None)
    ('start', 'Start Here', 'Overview', 'index.md'),
]

# Replace ```mermaid fences (not offline-safe) with ASCII per source file.
DIAGRAM_ASCII = { 'index.md': ["""
 [browser] -> [backend] -> [database]
"""] }

SNIPPETS = [
    # dict(path='src/file.js', s=1, e=30, lang='javascript',
    #      what=..., concept=..., why=..., depends=..., tested=...)
]

def esc(s): return html.escape(s, quote=False)

def inline(s):
    s = esc(s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    def link(m):
        t, u = m.group(1), m.group(2)
        if u.startswith('http'):
            return f'<a class="ext" href="{u}" target="_blank" rel="noopener">{t} ↗</a>'
        stem = u.split('/')[-1].replace('.md', '')
        return f'<a href="#{stem}">{t}</a>'
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, s)

def md_to_html(md):
    md = re.sub(r'^---\n.*?\n---\n', '', md, flags=re.S)
    out, i, lines = [], 0, md.split('\n')
    in_code, code_buf, code_lang, table_buf = False, [], '', []

    def flush_table():
        nonlocal table_buf
        if len(table_buf) >= 2:
            rows = [[c.strip() for c in r.strip().strip('|').split('|')] for r in table_buf]
            t = ['<div class="table-wrap"><table><thead><tr>' +
                 ''.join(f'<th>{inline(c)}</th>' for c in rows[0]) + '</tr></thead><tbody>']
            for r in rows[2:]:
                t.append('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>')
            t.append('</tbody></table></div>')
            out.append('\n'.join(t))
        table_buf = []

    while i < len(lines):
        ln = lines[i]
        if in_code:
            if ln.strip().startswith('```'):
                out.append(f'<div class="code" data-lang="{code_lang}"><button class="copy" type="button" aria-label="Copy code">Copy</button><pre><code>{esc(chr(10).join(code_buf))}</code></pre></div>')
                in_code, code_buf = False, []
            else:
                code_buf.append(ln)
            i += 1; continue
        if ln.strip().startswith('```'):
            flush_table(); in_code = True; code_lang = ln.strip()[3:] or 'text'; i += 1; continue
        if ln.strip().startswith('|'):
            table_buf.append(ln); i += 1; continue
        flush_table()
        if ln.startswith('#### '): out.append(f'<h5>{inline(ln[5:])}</h5>')
        elif ln.startswith('### '): out.append(f'<h4>{inline(ln[4:])}</h4>')
        elif ln.startswith('## '):
            hid = re.sub(r'[^a-z0-9]+', '-', ln[3:].lower()).strip('-')
            out.append(f'<h3 id="h-{hid}">{inline(ln[3:])}</h3>')
        elif ln.startswith('# '): out.append(f'<h2>{inline(ln[2:])}</h2>')
        elif ln.strip() == '---': out.append('<hr>')
        elif ln.startswith('> '):  # merge consecutive quote lines into ONE blockquote
            q = []
            while i < len(lines) and lines[i].startswith('> '):
                q.append(lines[i][2:]); i += 1
            out.append(f'<blockquote>{inline(" ".join(q))}</blockquote>'); continue
        elif re.match(r'\s*[-*] ', ln):
            items = []
            while i < len(lines) and re.match(r'\s*[-*] ', lines[i]):
                m = re.match(r'(\s*)[-*] (.*)', lines[i])
                items.append((2, m.group(2)) if (m.group(1) and items and items[-1][0] == 1) else (1, m.group(2)))
                i += 1
            buf, open_sub = [], False
            for lvl, txt in items:
                if lvl == 2 and not open_sub: buf.append('<ul>'); open_sub = True
                if lvl == 1 and open_sub: buf.append('</ul>'); open_sub = False
                buf.append(f'<li>{inline(txt)}</li>')
            if open_sub: buf.append('</ul>')
            out.append('<ul>' + ''.join(buf) + '</ul>'); continue
        elif re.match(r'\d+\. ', ln):
            ol = []
            while i < len(lines) and re.match(r'\d+\. ', lines[i]):
                item = re.sub(r'^\d+\. ', '', lines[i])   # hoisted: no backslash in f-string expr
                ol.append(f'<li>{inline(item)}</li>'); i += 1
            out.append('<ol>' + ''.join(ol) + '</ol>'); continue
        elif ln.strip() == '': out.append('')
        else: out.append(f'<p>{inline(ln)}</p>')
        i += 1
    flush_table()
    return '\n'.join(out)

def get_snippet(path, s, e):
    ls = (ROOT / path).read_text().split('\n')[s-1:e]
    while ls and not ls[-1].strip(): ls.pop()
    return '\n'.join(ls)

def snippet_cards():
    cards = []
    for sn in SNIPPETS:
        code = esc(get_snippet(sn['path'], sn['s'], sn['e']))
        cards.append(f'''<details class="snippet" open>
<summary><span class="file">{sn["path"]}</span><span class="badge">{sn["lang"]}</span></summary>
<div class="code" data-lang="{sn["lang"]}"><button class="copy" type="button" aria-label="Copy code">Copy</button><pre><code>{code}</code></pre></div>
<div class="meta"><p><strong>What this code does:</strong> {sn["what"]}</p>
<p><strong>Concept used:</strong> {sn["concept"]}</p><p><strong>Why we use it:</strong> {sn["why"]}</p>
<p><strong>What depends on it:</strong> {sn["depends"]}</p><p><strong>Tested by:</strong> {sn["tested"]}</p>
<p><strong>Source:</strong> <a class="ext" href="https://github.com/OWNER/REPO/blob/main/{sn['path']}#L{sn['s']}-L{sn['e']}" target="_blank" rel="noopener">{sn['path']} L{sn['s']}-{sn['e']} ↗</a></p>
</div></details>''')
    return '\n'.join(cards)

def build_section(sid, title, src):
    if sid == 'code':
        return f'<section id="{sid}" data-title="{title}"><h2>{title}</h2>{snippet_cards()}</section>'
    md = (ROOT / 'docs' / src).read_text()
    for ascii_d in DIAGRAM_ASCII.get(src, []):
        md = re.sub(r'```mermaid\n.*?\n```', lambda m: f'```text\n{ascii_d.strip()}\n```', md, count=1, flags=re.S)
    return f'<section id="{sid}" data-title="{title}">{md_to_html(md)}</section>'

# The proven inline UI shell (CSS + JS) lives in DentalVibe's build_guide.py:
# sidebar nav, DOM search, copy fallback (execCommand for file://), single-pass
# tokenizer (comments|strings|keywords|numbers), theme via localStorage,
# drawer <860px, overflow-wrap:anywhere on inline code (pre code stays normal),
# version badge hidden <640px. Reproduce those blocks with modifications.
sections_html = '\n'.join(build_section(sid, title, src) for sid, title, _g, src in SECTIONS)
print('sections built:', len(SECTIONS), '- wrap sections_html in the UI shell before writing', OUT.name)

#!/usr/bin/env python3
"""build_docs.py — portable handbook generator skeleton.
Merges docs/*.md + real source-code slices into ONE self-contained HTML file.
Reproduce with modifications: set SECTIONS, DOCS dir, ROOT, and SNIPPETS.

Pitfalls baked in: f-string braces doubled in CSS/JS; no backslashes inside
f-expressions (py3.11 SyntaxError — hoist to variables first); no fetch();
copy uses execCommand fallback (clipboard API is blocked on file://).
"""
import re, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
DOCS = ROOT / 'docs'
OUT = ROOT / 'HANDBOOK.html'

# (id, title, group, source md) — order defines nav + prev/next
SECTIONS = [
    ('start', 'Start Here', 'Overview', 'index.md'),
    ('architecture', 'Architecture', 'Overview', 'architecture.md'),
    # extend per the content architecture in SKILL.md
]

# real code slices extracted at build time — they stay current because the
# verifier re-checks every path; re-pin line ranges after refactors
SNIPPETS = [
    # dict(path='src/example.py', s=10, e=40, lang='python', what='...',
    #      concept='...', why='...', depends='...', tested='...'),
]

def esc(s): return html.escape(s, quote=False)

def inline(s):
    s = esc(s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    def link(m):
        t, u = m.group(1), m.group(2)
        if u.startswith('http'):
            return f'<a class="ext" href="{u}" target="_blank" rel="noopener">{t} &#8599;</a>'
        return f'<a href="#{u.split("/")[-1].replace(".md", "")}">{t}</a>'
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
            out.append(''.join(t) + '</tbody></table></div>')
        table_buf = []

    while i < len(lines):
        ln = lines[i]
        if in_code:
            if ln.strip().startswith('```'):
                code = esc(chr(10).join(code_buf))
                out.append(f'<div class="code"><button class="copy" type="button">Copy</button><pre><code>{code}</code></pre></div>')
                in_code, code_buf = False, []
            else:
                code_buf.append(ln)
            i += 1; continue
        # raw block-HTML passthrough (collapsible prompt cards etc.) — a line-based
        # converter must pass these through unescaped or the tags render literally
        if ln.lstrip().startswith(('<details', '</details>', '<summary', '</summary>', '<div', '</div>')):
            out.append(ln)
            i += 1; continue
        if ln.strip().startswith('```'):
            flush_table(); in_code = True; code_lang = ln.strip()[3:] or 'text'; i += 1; continue
        if ln.strip().startswith('|'):
            table_buf.append(ln); i += 1; continue
        flush_table()
        if ln.startswith('## '):
            slug = re.sub(r'[^a-z0-9]+', '-', ln[3:].lower()).strip('-')
            out.append(f'<h3 id="h-{slug}">{inline(ln[3:])}</h3>')
        elif ln.startswith('### '): out.append(f'<h4>{inline(ln[4:])}</h4>')
        elif ln.startswith('# '): out.append(f'<h2>{inline(ln[2:])}</h2>')
        elif ln.strip() == '---': out.append('<hr>')
        elif ln.startswith('> '):
            q = []
            while i < len(lines) and lines[i].startswith('> '):
                q.append(lines[i][2:]); i += 1
            out.append(f'<blockquote>{inline(" ".join(q))}</blockquote>'); continue
        elif re.match(r'\s*[-*] ', ln):
            items = []
            while i < len(lines) and re.match(r'\s*[-*] ', lines[i]):
                m = re.match(r'(\s*)[-*] (.*)', lines[i]); items.append((2 if m.group(1) else 1, m.group(2))); i += 1
            buf, open_sub = [], False
            for lvl, txt in items:
                if lvl == 2 and not open_sub: buf.append('<ul>'); open_sub = True
                if lvl == 1 and open_sub: buf.append('</ul>'); open_sub = False
                buf.append(f'<li>{inline(txt)}</li>')
            if open_sub: buf.append('</ul>')
            out.append('<ul>' + ''.join(buf) + '</ul>'); continue
        elif ln.strip() == '': out.append('')
        else: out.append(f'<p>{inline(ln)}</p>')
        i += 1
    flush_table()
    return '\n'.join(out)

def snippet_html():
    cards = []
    for sn in SNIPPETS:
        code = esc('\n'.join((ROOT / sn['path']).read_text().split('\n')[sn['s']-1:sn['e']]))
        meta = ''.join(f'<p><strong>{k}:</strong> {v}</p>' for k, v in
                       [('What', sn['what']), ('Concept', sn['concept']), ('Why', sn['why']),
                        ('Depends on', sn['depends']), ('Tested by', sn['tested'])])
        cards.append(f'<details class="snippet" open><summary><span>{sn["path"]}</span></summary>'
                     f'<div class="code"><button class="copy" type="button">Copy</button><pre><code>{code}</code></pre></div>'
                     f'<div class="meta">{meta}</div></details>')
    return '\n'.join(cards)

def build_section(sid, title, src):
    if sid == 'code':
        return f'<section id="{sid}" data-title="{title}"><h2>{title}</h2>{snippet_html()}</section>'
    return f'<section id="{sid}" data-title="{title}">{md_to_html((DOCS / src).read_text())}</section>'

sections_html = '\n'.join(build_section(s, t, f) for s, t, _g, f in SECTIONS)
nav, last = [], None
for sid, title, group, _s in SECTIONS:
    if group != last: nav.append(f'<div class="nav-group">{group}</div>'); last = group
    nav.append(f'<a href="#{sid}" data-nav="{sid}">{title}</a>')
nav_html = '\n'.join(nav)

# NOTE: every brace below is DOUBLED (this is an f-string). Keep it that way.
HTML = f'''<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Engineering Handbook</title>
<style>
:root {{ --bg:#0d1117; --bg2:#161b22; --border:#30363d; --text:#e6edf3; --muted:#8b949e;
  --accent:#58a6ff; --code-bg:#0b0f14; --mono:ui-monospace,Menlo,monospace }}
[data-theme="light"] {{ --bg:#fff; --bg2:#f6f8fa; --border:#d0d7de; --text:#1f2328; --muted:#656d76; --accent:#0969da; --code-bg:#f6f8fa }}
* {{ box-sizing:border-box }}
body {{ margin:0; background:var(--bg); color:var(--text); font-family:system-ui,sans-serif; line-height:1.65 }}
a {{ color:var(--accent); text-decoration:none }}
header.top {{ position:sticky; top:0; display:flex; gap:10px; align-items:center; padding:10px 16px;
  background:var(--bg2); border-bottom:1px solid var(--border); z-index:50 }}
#search {{ flex:1; max-width:320px; background:var(--bg); color:var(--text); border:1px solid var(--border);
  border-radius:8px; padding:7px 10px }}
.layout {{ display:grid; grid-template-columns:250px minmax(0,1fr); max-width:1300px; margin:0 auto }}
nav.side {{ position:sticky; top:53px; height:calc(100vh - 53px); overflow-y:auto; padding:14px 10px; border-right:1px solid var(--border) }}
.nav-group {{ font:700 11px/1 var(--mono); color:var(--muted); letter-spacing:.8px; margin:14px 8px 4px; text-transform:uppercase }}
nav.side a {{ display:block; padding:6px 9px; border-radius:8px; color:var(--text); font-size:14px }}
nav.side a.active {{ background:var(--bg2); color:var(--accent) }}
main {{ padding:24px clamp(14px,4vw,48px) 100px; min-width:0 }}
section {{ margin:0 0 64px }}
h2 {{ font-size:25px }} h3 {{ font-size:19px; border-top:1px solid var(--border); padding-top:10px; margin-top:28px }}
code {{ font-family:var(--mono); font-size:.88em; background:var(--bg2); border:1px solid var(--border); padding:1px 5px; border-radius:6px }}
.code {{ position:relative; margin:12px 0; border:1px solid var(--border); border-radius:10px; background:var(--code-bg) }}
.code pre {{ margin:0; padding:26px 12px 12px; overflow-x:auto }}
.code code {{ background:none; border:none; padding:0; font-size:12.6px }}
.copy {{ position:absolute; top:5px; right:6px; background:var(--bg2); color:var(--muted);
  border:1px solid var(--border); border-radius:7px; padding:2px 9px; font-size:11px; cursor:pointer }}
button.copy {{ position:static }}
.table-wrap {{ overflow-x:auto; margin:12px 0; border:1px solid var(--border); border-radius:10px }}
table {{ border-collapse:collapse; width:100%; font-size:13.5px }}
th,td {{ text-align:left; padding:8px 12px; border-bottom:1px solid var(--border); vertical-align:top }}
th {{ background:var(--bg2); color:var(--muted); font-size:12px; text-transform:uppercase }}
blockquote {{ margin:12px 0; padding:9px 14px; border-left:3px solid var(--accent); background:var(--bg2); color:var(--muted) }}
.snippet {{ margin:16px 0; border:1px solid var(--border); border-radius:12px }}
.snippet summary {{ cursor:pointer; padding:10px 13px; background:var(--bg2); font-family:var(--mono); font-size:12.5px }}
.snippet .meta {{ padding:4px 14px 10px; font-size:13.5px; color:var(--muted) }}
@media (max-width:860px) {{ .layout {{ grid-template-columns:minmax(0,1fr) }}
  nav.side {{ position:fixed; left:0; top:53px; bottom:0; width:260px; background:var(--bg2);
    transform:translateX(-102%); transition:transform .18s; z-index:40 }}
  nav.side.open {{ transform:translateX(0) }} }}
</style>
</head>
<body>
<header class="top">
  <button class="copy" id="menuBtn" aria-label="Open navigation">Menu</button>
  <strong>Engineering Handbook</strong>
  <div style="flex:1"></div>
  <input id="search" type="search" placeholder="Search\u2026" aria-label="Search documentation">
  <button class="copy" id="themeBtn" aria-label="Toggle theme">Theme</button>
</header>
<div class="layout">
  <nav class="side" id="sideNav">{nav_html}</nav>
  <main>{sections_html}</main>
</div>
<script>
(function () {{
  const $$ = (s, r=document) => Array.from(r.querySelectorAll(s));
  const sections = $$('main > section');
  const themeBtn = document.querySelector('#themeBtn');
  let theme = null; try {{ theme = localStorage.getItem('doc-theme'); }} catch (e) {{}}
  if (theme) document.documentElement.dataset.theme = theme;
  themeBtn.addEventListener('click', () => {{
    const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    try {{ localStorage.setItem('doc-theme', next); }} catch (e) {{}}
  }});
  const side = document.querySelector('#sideNav');
  document.querySelector('#menuBtn').addEventListener('click', () => side.classList.toggle('open'));
  side.addEventListener('click', (e) => {{ if (e.target.tagName === 'A') side.classList.remove('open'); }});
  document.addEventListener('click', (e) => {{
    const btn = e.target.closest('.copy');
    if (!btn || btn.id === 'menuBtn' || btn.id === 'themeBtn') return;
    const code = btn.parentElement.querySelector('code');
    if (!code) return;
    const ta = document.createElement('textarea'); ta.value = code.textContent;
    ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select();
    try {{ document.execCommand('copy'); btn.textContent = 'Copied';
          setTimeout(() => btn.textContent = 'Copy', 1400); }} catch (e) {{}}
    ta.remove();
  }});
  const navLinks = $$('nav.side a[data-nav]');
  const obs = new IntersectionObserver((es) => {{
    const v = es.filter(e => e.isIntersecting).sort((a,b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
    if (v) navLinks.forEach(a => a.classList.toggle('active', a.dataset.nav === v.target.id));
  }}, {{ rootMargin: '-56px 0px -70% 0px' }});
  sections.forEach(s => obs.observe(s));
  document.querySelector('#search').addEventListener('input', (e) => {{
    const q = e.target.value.trim().toLowerCase();
    sections.forEach(s => {{
      const hit = q.length >= 2 && (s.textContent || '').toLowerCase().includes(q);
      s.style.opacity = q.length >= 2 && !hit ? '.35' : '1';
    }});
  }});
}})();
</script>
</body></html>'''

OUT.write_text(HTML)
print(f'wrote {OUT.name}: {len(HTML):,} bytes - {len(SECTIONS)} sections - {len(SNIPPETS)} snippets')

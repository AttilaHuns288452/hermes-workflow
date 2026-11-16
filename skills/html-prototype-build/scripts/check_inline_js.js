#!/usr/bin/env node
// Syntax-gate inline scripts of one HTML file: node check_inline_js.js <file.html>
// Each block is checked on its own - classic blocks as .js, type=module as .mjs (so
// `import` parses); src= and JSON/importmap blocks are skipped (data, not executable).
const fs = require('fs');
const os = require('os');
const path = require('path');
const cp = require('child_process');

const file = process.argv[2];
if (!file) { console.error('usage: check_inline_js.js <file.html>'); process.exit(2); }
const html = fs.readFileSync(file, 'utf8');
const blocks = [...html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)];
let checked = 0, failed = 0;
for (const [i, m] of blocks.entries()) {
  const attrs = m[1], body = m[2];
  if (/\bsrc\s*=/.test(attrs)) continue;
  const type = (attrs.match(/\btype\s*=\s*["']?([^"'\s>]+)/i) || [])[1] || '';
  if (type === 'importmap' || /^application\/(json|ld\+json)$/.test(type)) continue;
  const isModule = type === 'module';
  const tmp = path.join(os.tmpdir(), `html-inline-${process.pid}-${i}${isModule ? '.mjs' : '.js'}`);
  fs.writeFileSync(tmp, body);
  const r = cp.spawnSync(process.execPath, ['--check', tmp], { encoding: 'utf8' });
  checked++;
  if (r.status !== 0) {
    failed++;
    console.error(`FAIL block ${i} (${isModule ? 'module' : 'classic'}):`);
    console.error((r.stderr || '').trim());
  }
  fs.unlinkSync(tmp);
}
console.log(`${file}: ${checked} inline block(s) checked, ${failed} failed`);
process.exit(failed ? 1 : 0);

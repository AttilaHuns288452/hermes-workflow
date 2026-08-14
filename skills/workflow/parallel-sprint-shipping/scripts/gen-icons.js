// Minimal PNG icon generator (zero deps) — PWA 192/512 icons without an image
// library. Solid rounded-square + simple white mark. Run from repo root:
//   node scripts/gen-icons.js [192 512 ...]
// Writes public/icons/icon-<size>.png. Reference from src/app/manifest.ts.
const zlib = require("zlib");
const fs = require("fs");
const path = require("path");

function crc32(buf) {
  let c, table = crc32.table;
  if (!table) {
    table = crc32.table = [];
    for (let n = 0; n < 256; n++) {
      c = n;
      for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
      table[n] = c >>> 0;
    }
  }
  c = 0xffffffff;
  for (let i = 0; i < buf.length; i++) c = table[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

function chunk(type, data) {
  const len = Buffer.alloc(4);
  len.writeUInt32BE(data.length);
  const t = Buffer.from(type, "ascii");
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(Buffer.concat([t, data])));
  return Buffer.concat([len, t, data, crc]);
}

function png(size, draw) {
  const raw = Buffer.alloc(size * (size * 4 + 1));
  for (let y = 0; y < size; y++) {
    raw[y * (size * 4 + 1)] = 0; // filter: none
    for (let x = 0; x < size; x++) {
      const [r, g, b, a] = draw(x, y, size);
      const o = y * (size * 4 + 1) + 1 + x * 4;
      raw[o] = r; raw[o + 1] = g; raw[o + 2] = b; raw[o + 3] = a;
    }
  }
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(size, 0);
  ihdr.writeUInt32BE(size, 4);
  ihdr[8] = 8; ihdr[9] = 6; // 8-bit RGBA
  return Buffer.concat([
    Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
    chunk("IHDR", ihdr),
    chunk("IDAT", zlib.deflateSync(raw)),
    chunk("IEND", Buffer.alloc(0)),
  ]);
}

// Customize: ACCENT = icon background (e.g. #2563eb), mark = white bars.
const ACCENT = [0x25, 0x63, 0xeb, 255];
const MARK = [255, 255, 255, 255];

function draw(x, y, size) {
  const m = Math.round(size * 0.06);
  const rad = Math.round(size * 0.22);
  const inset = size - m;
  const cx = Math.min(Math.max(x, m + rad), inset - rad);
  const cy = Math.min(Math.max(y, m + rad), inset - rad);
  const corners = [
    [m + rad, m + rad], [inset - rad, m + rad],
    [m + rad, inset - rad], [inset - rad, inset - rad],
  ];
  const inCorner = corners.some(([px, py]) => (cx - px) ** 2 + (cy - py) ** 2 <= rad * rad);
  const bg = x >= m && x < inset && y >= m && y < inset && inCorner ? ACCENT : [0, 0, 0, 0];

  const u = size / 100;
  const bar1 = x >= 40 * u && x < 48 * u && y >= 30 * u && y < 70 * u;
  const bar2 = x >= 52 * u && x < 60 * u && y >= 30 * u && y < 70 * u;
  const stroke = (y >= 30 * u && y < 36 * u) || (y >= 64 * u && y < 70 * u);
  const mark = x >= 34 * u && x < 66 * u && (bar1 || bar2 || stroke);
  return mark && bg[3] === 255 ? MARK : bg;
}

const sizes = process.argv.slice(2).map(Number).filter(Boolean);
if (!sizes.length) sizes.push(192, 512);
const outDir = path.join("public", "icons");
fs.mkdirSync(outDir, { recursive: true });
for (const size of sizes) {
  const file = path.join(outDir, `icon-${size}.png`);
  fs.writeFileSync(file, png(size, draw));
  console.log(`${file} written`);
}

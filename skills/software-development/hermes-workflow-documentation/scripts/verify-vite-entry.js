#!/usr/bin/env node
// Pre-build guard for the Hermes Workflow Vite site.
// Ensures root index.html is the Vite source entry, not a stale built file.

const fs = require('fs')
const path = require('path')

const file = path.resolve('index.html')

if (!fs.existsSync(file)) {
  console.error('✗ index.html not found')
  process.exit(1)
}

const html = fs.readFileSync(file, 'utf-8')

const staleAssetMatch = html.match(/src=["']\/[^"']*\/assets\/index-[A-Za-z0-9_-]+\.js["']/)
const stylesheetMatch = html.match(/href=["']\/[^"']*\/assets\/index-[A-Za-z0-9_-]+\.css["']/)

if (staleAssetMatch || stylesheetMatch) {
  console.error('✗ index.html contains stale hashed asset paths:')
  if (staleAssetMatch) console.error('  ' + staleAssetMatch[0])
  if (stylesheetMatch) console.error('  ' + stylesheetMatch[0])
  console.error('Root index.html must be the Vite source entry. Restore it from templates/index.html, then run npm run build.')
  process.exit(1)
}

if (!/src=["']\/src\/main\.(jsx|tsx)["']/.test(html)) {
  console.error('✗ index.html does not point to /src/main.jsx (or /src/main.tsx)')
  process.exit(1)
}

console.log('✓ index.html points to /src/main.jsx')
process.exit(0)

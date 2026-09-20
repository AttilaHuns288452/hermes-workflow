# Verifier trio: vm smoke tests + syntax + curl

Pattern for verifying vanilla-JS static sites (multi-page or SPA) without a browser. The browser harness on this machine frequently can't launch Chrome — this trio is the dependable default.

## The trio

1. **Syntax:** `for f in js/*.js; do node -c "$f" || echo "FAIL $f"; done`
2. **Serve:** `python3 -m http.server 8765` in the repo (background), then `curl -s -o /dev/null -w '%{http_code}' http://localhost:8765/<page>` per page. On GitHub Pages, cache-bust the check: `?cb=$(date +%s)` — the CDN serves stale builds for 2–3 minutes after push.
3. **vm smoke test:** run the site's JS modules in Node with stubbed browser globals and assert business invariants.

## vm smoke-test recipe

```js
const fs = require("fs");
const vm = require("vm");
const assert = require("assert");

const sandbox = {
  window: {}, GW: {},            // whatever globals the site's modules assume
  console, URLSearchParams, CustomEvent: class {},
  document: {
    getElementById: () => null,           // returns null → render fns no-op, but data/logic still runs
    querySelector: () => null,
    querySelectorAll: () => [],
    addEventListener() {}, dispatchEvent() {},
    createElement: () => ({ style: {} }),
  },
  localStorage: { getItem: () => null, setItem() {} },
  location: { search: "", href: "" },
};
vm.createContext(sandbox);
vm.runInContext(
  fs.readFileSync("js/data.js", "utf8") + "\n" +
  fs.readFileSync("js/app.js", "utf8") + "\n" +
  // modules assign to window.*; hoist them to sandbox scope for the test:
  "this.GWApp = window.GWApp; this.GWRec = window.GWRec;\n" +
  fs.readFileSync("js/recommendations.js", "utf8"),
  sandbox
);
const { GW, GWApp } = sandbox;
const GWRec = sandbox.window.GWRec;
```

Gotchas that cost time:

- Modules that do `window.GWApp = (function(){...})()` leave the result on `sandbox.window.GWApp`, NOT on `sandbox` directly — read them back via `sandbox.window.X` (or hoist with a `this.X = window.X` line between file concatenations).
- `URLSearchParams` and `CustomEvent` must be passed into the sandbox explicitly; `location` and `localStorage` need stubs with the exact methods called (`getItem`, `setItem`, `search`, `href`).
- Code that touches the DOM at load (a wizard builder reading a checked radio) throws on the null stub. Cut the script at its init boundary (`src.slice(0, src.indexOf("/* INIT SECTION */"))`) — data and pure functions still eval.
- For scripts inlined in HTML, extract with `[...html.matchAll(/<script>([\s\S]*?)<\\/script>/g)]` and `new vm.Script(block)` for a pure syntax check without running.

## Invariants worth asserting (per project type)

- **Catalog/data:** size matches the spec, every record has the fields every consumer reads (`scored`, `value`, `specs`), every image URL matches the expected host pattern.
- **Computed scores:** parity against a hand-computed value for one known record — catches silent formula drift after ports.
- **Frontier/rankings:** non-empty, subset of input, no member beaten on both axes (Pareto property), per-filter variants all non-empty.
- **Recommendations:** results for every category/use-case combination non-empty, all results within the scoped category, scores descending.
- **No orphan ids:** every id referenced by admin metrics, seeded history, moderation queues, and default-detail fallbacks resolves through the lookup function.
- **Feature filters:** each filter matches a non-empty subset of the catalog (catches a filter that's UI-only and matches nothing).

## Committing the tests

One `test-*.js` per subsystem at repo root (no framework, plain assert). They double as executable documentation of the invariants; run all three lines (syntax, vm tests, curl loop) before every push.

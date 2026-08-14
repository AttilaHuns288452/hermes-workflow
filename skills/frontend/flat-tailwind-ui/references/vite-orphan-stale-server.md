# Vite orphaned dev servers — stale code on old ports (Windows)

Hit on student-profile.app (2026-08): after several `process(kill)` cycles, three vite servers were
simultaneously listening (5173/5174/5175) — all orphans from killed background sessions, all serving
progressively older code. The newest `npm run dev` logged `Port 5173 is in use, trying another one...`
and bound 5175. Browser verification ran against the 5173 orphan → phantom logged-in state, "changes
not taking effect", ~3 rounds of wasted debugging.

## Why

`process(action="kill")` (and killing the bash session) terminates the bash WRAPPER, not the `node`
child running vite. The orphan keeps its port and keeps serving the code version it started with.

## Detection

```bash
# 1. All listeners on the dev ports:
netstat -ano | grep -E "517[3-5]" | grep LISTEN

# 2. Is the served source current? (the decisive check)
curl -s http://localhost:<port>/src/App.jsx | grep -c "<marker-from-new-code>"
# 0 matches = stale orphan. Also works on built apps: grep dist/assets/index-*.js
```

## Cleanup + restart

```bash
taskkill /PID <pid> /F            # single slashes work in git-bash; one per listener
netstat -ano | grep -E "517[3-5]" | grep LISTEN || echo "ports free"
npm run dev                       # confirm the 'Local:' line shows the port you expect
```

Always confirm the bound port in the `Local:` line before pointing browser tests at it.
If a port-5173 check is needed for the build: vite config can pin `server.port` + `strictPort`.

## Related

- `debugging-spawned-processes` §4/4b (Next.js variants of the same orphan/stale-server trap)
- `flat-tailwind-ui` verification section

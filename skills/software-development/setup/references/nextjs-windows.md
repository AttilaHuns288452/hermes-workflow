# Next.js 16 on Windows — Setup Reference

## Turbopack Workspace Root Detection

**Error:**
```
Warning: Next.js inferred your workspace root, but it may not be correct.
We detected multiple lockfiles and selected the directory of C:\Users\<user>\package-lock.json as the root directory.
 To silence this warning, set `turbopack.root` in your Next.js config, or consider removing one of the lockfiles if it's not needed.
```

Followed by build failure:
```
Error: ENOENT: no such file or directory, open 'C:\Users\<user>\...\.next\required-server-files.json'
```

**Root cause:** When `next build` or `next dev` runs inside a project subdirectory (e.g. `website/` of a monorepo), Turbopack scans up the directory tree for lockfiles. If it finds a lockfile closer to the filesystem root (e.g. a stray `package-lock.json` in `C:\Users\<user>\`), it selects that as the workspace root instead of the project directory. The build then fails because paths relative to the wrong root don't resolve to `.next/`.

**Root lockfiles are often created by accident:** running `npm install` from the wrong directory (e.g., `cd ~ && npm install @vercel/analytics` instead of first `cd ~/project`) drops a `package-lock.json` at the user home level. Turbopack finds this and gets confused. **Fix:** delete the root lockfile and pin the project root.

**Fix in `next.config.ts` (two options):**
```typescript
import type { NextConfig } from "next";

// Option A — use __dirname for the exact directory of the config file
const nextConfigA: NextConfig = {
  turbopack: {
    root: __dirname,
  },
};

// Option B — use process.cwd() for the build-time working directory
const nextConfigB: NextConfig = {
  turbopack: {
    root: process.cwd(),
  },
};

export default nextConfig;
```

Both work; `process.cwd()` is preferred for Vercel builds where the working directory is already the project root.

---

## metadataBase Required for Custom Domains

**Symptom:** Build passes but OG/Twitter preview cards show `http://localhost:3000` as the image URL:
```
⚠ metadataBase property in metadata export is not set for resolving social open graph
or twitter images, using "http://localhost:3000".
```

**Fix:** Add `metadataBase` at the top of the `metadata` export in `app/layout.tsx`:
```typescript
export const metadata: Metadata = {
  metadataBase: new URL("https://www.your-custom-domain.com"),
  // ... rest of metadata
};
```

---

## Missing @vercel/analytics Dependency

**Error:**
```
Module not found: Can't resolve '@vercel/analytics/next'
> 1 | import { Analytics } from "@vercel/analytics/next"
```

**Root cause:** `create-next-app` scaffolds `layout.tsx` with an import of `@vercel/analytics/next` but doesn't include the package as a dependency in `package.json`. This happens because the analytics instrumentation is added at project creation time but the package installation can be skipped or fail silently.

**Fix:** `npm install @vercel/analytics`

---

## Build Failure: Turbopack Auto-Generated TypeScript Error

**Error:**
```
Failed to type check.
.next/dev/types/validator.ts:139:1
Type error: Declaration or statement expected.
  137 |   // @ts-ignore
  138 |   type __Unused = __Check
> 139 | }
      | ^
```

**Root cause:** Turbopack generates a type validator file at `.next/dev/types/validator.ts` that can produce invalid TypeScript when it's regenerated mid-build. This is a Next.js 16 / Turbopack internal issue, not a project code error.

**Fixes (try in order):**
1. `rm -rf .next && npm run dev` — clean the cache and retry
2. Bypass type-checking during build with a separate command: `next build --no-lint`
3. Set `typescript.ignoreBuildErrors: true` in `next.config.ts` as last resort

---

## Port Conflict Resolution

**Symptom:** Dev server starts but exits immediately:
```
⨯ Another next dev server is already running.
- Local:        http://localhost:3001
- PID:          25956
- Dir:          C:\Users\<user>\...\website
```

**Check which process owns the port:**
```bash
netstat -ano | grep ':3000' | grep LISTEN
# Output: TCP    0.0.0.0:3000   0.0.0.0:0   LISTENING   16600
```

**Kill it** (Windows git-bash — note `//F` not `/F`):
```bash
taskkill //F //PID 16600
```

The `//F` syntax (double slash) is required because MSYS converts bare POSIX-style `/F` to `F:/` before passing it to `taskkill.exe`. Using `//F` escapes this conversion.

---

## Dev Server Wait Pattern

When starting `next dev` in background mode, the process produces no output for several seconds while it compiles. The "compiled successfully" or "Ready in X.Xs" markers appear in the log but may be delayed.

**Recommended verification:**
```python
# Wait up to 30s for the server to be ready
import time, subprocess
for i in range(30):
    result = subprocess.run(
        ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://localhost:3000"],
        capture_output=True, text=True
    )
    if result.stdout == "200":
        print("Server ready on port 3000")
        break
    time.sleep(1)
```

Or use bash:
```bash
for i in $(seq 1 15); do
  curl -s http://localhost:3000 > /dev/null && echo "READY" && break
  sleep 2
done
```

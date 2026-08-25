# Vercel cwd + next/headers Fix — Minimal Repros

## next/headers in client bundle
**Symptom**: `tsc --noEmit` clean, `next build` fails with `You're importing a module that depends on "next/headers"` + import trace `lib/supabase/server.ts → lib/entity.ts → lib/net-worth.ts → BalanceSheet.tsx`.
**Root**: `lib/entity.ts` imports `next/headers`. Any non-server helper importing it and re-exported to a `"use client"` component drags server code into browser.
**Fix**: Add `"use server";` as first line of the helper (`lib/net-worth.ts`) — makes it a Server Action boundary. Client calls it via RPC, not bundle.

## Vercel deploy cwd
**Symptom**: `npx --prefix C:/path/to/project vercel deploy` prompts `You are deploying your home directory. Do you want to continue?`
**Fix**: `cd <project> && npx vercel deploy --prod --cwd . --yes`

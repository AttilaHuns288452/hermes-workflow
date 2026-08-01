# Greenfield App Build Spec Template

Use this template when delegating a full-stack app build to DeepSeek V4 Flash via `delegate_task`. The orchestrator should fill in the project-specific details, then dispatch.

## Template

```
Build the complete <APP_NAME> v1 in <PROJECT_PATH>. This is a <STACK> app. 
The project is already scaffolded with <SCAFFOLDING>, dependencies installed 
(<LIST_DEPS>), and <CONFIG_FILES_EXIST>.

## CRITICAL: You must build EVERY file listed below. Do not skip anything. 
Do not write stubs. Every file must be complete and production-ready.

## Architecture Rules
- <ARCHITECTURE_RULES>
- <FOLDER_STRUCTURE>
- <PATTERNS>

## Database Schema
<Paste the full SQL migration>

## Files to Create

### <List every file with its path and a description of what it should contain>

### File patterns to specify:
- Types file (TypeScript types for all tables)
- Lib utilities (cn(), supabase clients)
- UI components (list each one: button, card, input, dialog, etc.)
- Feature modules (for each feature: components/ + actions.ts)
- Layout components (AppShell, Providers)
- App Router pages (one per route)
- Middleware (auth guard)
- Config files (.env.local.example)

## STYLING RULES
- Dark mode compatible
- Consistent spacing
- Loading states
- Empty states  
- Error states
- Mobile responsive
- Icon library

## IMPORTANT IMPLEMENTATION NOTES
1. <Any tool-specific quirks or workarounds>
2. <Pattern requirements>
3. <Server action patterns>
4. <Packages that may need installing>
5. After writing ALL files, run `npm run build` to verify everything compiles.
6. The app must run with `npm run dev` and show <FIRST_WORKING_PAGE>.

## WHEN DONE
After writing all files, run `npm run build` and report success or any errors.
```

## Key Principles

1. **Be exhaustive.** List every file. Missing one file means the subagent won't create it.
2. **Include the SQL.** Don't say "create a schema for..." — paste the actual SQL.
3. **Specify patterns.** Show the exact code pattern for things like `cn()`, server actions, component structure.
4. **Set a concrete finish line.** "Run `npm run build` and report" is better than "make it work."
5. **The orchestrator writes NO code from this point onward.** All `.tsx`, `.ts`, `.css` goes to DeepSeek.

## What the orchestrator does while waiting

While the subagent works:
- Write architecture docs (Architecture.md, Database.md, DecisionLog.md)
- Write README.md and V1_NOTES.md
- Write .env.local.example
- Prepare deployment configuration
- Write the migration file (as a duplicate safety net)
- Create the Supabase project if credentials are available

## What to do when the subagent times out (Ponytail Gap-Fill)

The subagent WILL time out on 40+ file builds (600s limit, 19 API calls). Do NOT re-dispatch — the second attempt will also time out. Instead:

1. **Check what was written:** `find src -type f | sort` — the subagent likely completed the complex UI primitives (shadcn components) and some feature code
2. **Orchestrator fills remaining gaps:** Write the missing route pages (thin one-liners), layout wrappers (AuthShell), middleware, any remaining feature components the subagent skipped
3. **Fix type errors:** The subagent's code may have minor TS issues (recharts types, null coalescing). Fix inline — `any` casts for recharts labels, `?? null` for undefined → null transitions
4. **Run `npm run build`** — iterate fixing errors until clean
5. **Deploy immediately** — `git push && npx vercel --yes --prod`

This pattern saved ~10 minutes vs re-dispatching in a real 63-file build. The subagent's output is partial but valuable — use it, don't discard it.

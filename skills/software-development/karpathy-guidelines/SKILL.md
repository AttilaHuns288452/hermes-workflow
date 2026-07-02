---
name: karpathy-guidelines
description: Behavioral guidelines to reduce common LLM coding mistakes. Use when writing, reviewing, or refactoring code to avoid overcomplication, make surgical changes, surface assumptions, and define verifiable success criteria.
license: MIT
tags: [guidelines, best-practices, coding, review, refactoring]
platforms: [linux, macos, windows]
---

# Karpathy Guidelines

Behavioral guidelines to reduce common LLM coding mistakes, derived from [Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876) on LLM coding pitfalls.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

> **Reference:** See `references/examples.md` for detailed real-world code examples (before/after diffs) for each principle.
>
> **Upstream repo:** https://github.com/multica-ai/andrej-karpathy-skills — the original CLAUDE.md these guidelines are derived from.
>
> **Plugin install:** From Claude Code, run `/plugin marketplace add forrestchang/andrej-karpathy-skills` then `/plugin install andrej-karpathy-skills@karpathy-skills`.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## 5. Framework-Specific Pitfalls

### Tailwind CSS: Dynamic Class Names

**`bg-${color}-600` DOES NOT WORK with Tailwind's JIT compiler.** Tailwind scans source files for complete class name strings at build time. Any class built via template literals, string concatenation, or dynamic interpolation at runtime won't exist in the compiled CSS.

**Wrong (looks like it should work):**
```tsx
<button className={`bg-${color}-600 text-white`}>Click</button>
```
Tailwind never sees `bg-purple-600` or `bg-pink-600` as strings — only the expression `bg-${color}-600`. No background color class is emitted.

**Fix: Store the full class name string in the data:**
```tsx
const BUTTONS = [
  { key: "all", label: "All", cls: "bg-purple-600" },
  { key: "waifu", label: "Waifus", cls: "bg-pink-600" },
];
// Then use cls directly:
<button className={`${active ? btn.cls : "bg-gray-100"} ...`}>{btn.label}</button>
```

**Detection:** The class is missing from rendered HTML even though the code looks correct. Open DevTools element inspector — if `bg-purple-600` isn't in the class list but the source code references it via interpolation, this is the bug.

### React: Hooks After Early Returns (Error #310)

**Every hook call must happen before any `if (...) return <JSX />` in the same component.** Hooks placed after a conditional return create an inconsistent hook count between renders, triggering React error #310 ("Rendered more hooks than during the previous render").

```tsx
// WRONG: useEffect after early return → hook count changes
function Quiz() {
  const [gender, setGender] = useState(null);
  const [mounted, setMounted] = useState(false);
  useEffect(() => { setMounted(true); }, []);

  if (!mounted) return null;
  if (!gender) return <GenderSelector />;   // ← returns here — skips next effect

  useEffect(() => { ... }, []);               // ← ONLY called when gender is set!
  return <QuizQuestions />;
}

// RIGHT: all hooks before any conditional return
function Quiz() {
  const [gender, setGender] = useState(null);
  const [mounted, setMounted] = useState(false);
  useEffect(() => { setMounted(true); }, []);
  useEffect(() => { ... }, []);               // ← always called, always counted

  if (!mounted) return null;
  if (!gender) return <GenderSelector />;
  return <QuizQuestions />;
}
```

See `software-development/nextjs-hydration` for the full write-up including detection via error boundary, browser console checks, and `next/dynamic` as an alternative fix.

### Next.js: `output: "export"` on Vercel

If the server-rendered HTML contains `BAILOUT_TO_CLIENT_SIDE_RENDERING` and the app uses nested `"use client"` mount-guard components (e.g. `useEffect(() => setMounted(true), [])` wrapping a child that also has `useState`), **restore `output: "export"` in `next.config.ts`**. Vercel's docs advise removing it for dynamic features, but for these patterns, removing it re-introduces SSR/hydration failure because React tries to reconcile server HTML with client-only state.

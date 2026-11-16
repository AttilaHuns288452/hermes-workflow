---
name: roblox-luau-types
description: "Use when adding or fixing Luau type annotations: generics, unions, narrowing, strict mode, sealed tables, module type exports, typed metatables"
---


# Luau Type System

## When to Load

Load for Luau annotations, inference, narrowing, strictness, exports, and solver features. Syntax: `roblox-luau-core`; lifecycle/scheduling: `roblox-luau-patterns`.

## Quick Reference

**Strictness:** `--!strict` for maintained code, `--!nonstrict` while transitioning, `--!nocheck` only for legacy or generated code. Directives and project settings select the mode; never assume one global default.

**New solver gate:** `keyof`, `rawkeyof`, `setmetatable<T, M>`, `type function`s, and `read` members need the new type solver. On by default for `nocheck`/`nonstrict` projects; strict projects need `Workspace.UseNewLuauTypeSolver = Enabled` (Scripting). Errors here usually mean wrong solver, not wrong syntax.

**Inference philosophy:** Infer first; annotate boundaries (params, returns, exports). Don't annotate every local.

**Sealed vs unsealed tables:** An unannotated local table stays open to new fields until annotated, returned from a function, or its scope exits; annotation seals it. Build tables fully before annotating; passing a table to a typed function does not seal it.

**Unions:** `local id: string | number` is a union; prefer tagged unions (`type State<T> = {kind:"loading"} | {kind:"ready", value:T}`) and discriminate on `kind` to narrow.

**Narrowing:** `typeof`, `IsA`, assertions, and tagged discriminants refine types; examples in full.md.

**Missing keys:** use `{ [K]: V? }` when lookups may miss; narrow before use.

**Closed vocabularies:** prefer literal unions; `never` checks can flag missing branches. Keep requires statically resolvable. Practitioner guidance: full.md.

**Generics:** Use when input→output type matters: `function first<T>(list: {T}): T?`, or `type Result<T> = {success: boolean, value: T?}`. Never replace with `any`.

**Type exports:** `export type Foo = {...}` at module boundaries; consumers use `Types.Foo`.

**Object typing:** `typeof(setmetatable({} :: CounterData, Counter))` types precise self; the new solver adds `setmetatable<T, M>` directly.

**Casts (::):** For narrowing overly generic inference, never for hiding errors.

**Heterogeneous array literals:** `{ Vector3.new(...), CFrame.new(...) }` infers its element type from the FIRST entry, so `luau-lsp` reports `Expected this to be 'Vector3', but got 'CFrame'` on every later row. The tuple annotation `{ { Vector3, CFrame } }` is NOT a fix — it is a syntax error in Luau. Use named fields (`{ size = ..., cf = ... }`) so each field carries its own type, or cast at the point of use.

**Optional helper results need a definite binding.** A helper that returns `T?` and falls back to another constructor leaves the variable optional: `local g = helper() or fallback()` still types as the union, and `if g then local h = g end` scopes `h` out of existence afterwards. Declare `local g: T` first and assign to it in both branches of the `if`, so every later field access is checked against a non-nil type. Without it the nil error surfaces far from the branch that caused it.

**Trust boundaries:** Annotations contract with the compiler, not runtime data. Remotes, DataStores, HttpService, and attributes still need checks; inside a trusted boundary, let types carry the load.

**Review:** no hidden `any`, premature sealing, unchecked casts, or solver-blind rewrites.

> Full reference: see `references/full.md`

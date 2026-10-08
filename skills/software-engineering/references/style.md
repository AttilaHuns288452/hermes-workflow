# Deliverable style: authorship + refactor verification

## Authorship voice (standing user requirement)

Deliverable code must read as if the user wrote it himself: a competent undergrad's idiomatic code, not machine output. Applies to every code artifact he will show (course projects, client sites), including edits and refactors of existing code.

- Adopt the ecosystem's standard structure over hand-rolled equivalents: the framework's own router (`react-router-dom` with `<Routes>/<Link>/<NavLink>`, `useParams`/`useSearchParams`), standard folders (`pages/`, `components/`), the framework's own state and hooks. A hand-rolled hash parser where a standard router exists is the strongest machine smell.
- Student-level complexity: plain functions and props are fine; no design-pattern cosplay (no abstract factories, DI containers, or wrapper layers without a second consumer).
- No machine residue: no dead exports, no unused imports, no helpers nothing calls, no TODO/scaffold comments, no numbering schemes on section comments that no human maintains.
- Comments explain WHY at the natural density of an experienced student: short, occasional, never narrating what the next line does.
- Naming reads like a person's (`GadgetCard`, `g`, `err`, not `ItemRenderer`, `entityData`); match the idiom already established in the codebase.

## Structural refactor verification (split / move / rename passes)

- Deleting a split source file's tail leaves its final `export {...}` line in the next region's file. Grep every generated file for old export lines before building: a re-export of a moved symbol fails the build with an "undefined" error far from the cause.
- Files moved into a subfolder keep their old relative imports (`./lib.js` must become `../lib.js`). Grep moved files for `from "./` after every move.
- A green build does not prove routes render: bundlers transpile missing imports into runtime `ReferenceError`s. After any restructure, load every route with console/pageerror capture, assert one known text per route, and click through the app's main navigation once.
- Hash-link to router conversion: `href="#/x"` becomes `to="/x"`. Keep the leading `#` and `<Link>` appends to the current hash route instead of replacing it.
- Git records splits/renames automatically (rename detection happens at diff time, not staging time). Stage only the specific paths and confirm `git status` shows `rename:` lines for split/moved files before committing.
- Never mask build exits in a shell pipeline: `npm run build | tail -N` reports `tail`'s exit code. Check `${PIPESTATUS[0]}` or run the build unpiped.

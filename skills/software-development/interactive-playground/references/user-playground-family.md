# User's Playground Family (Attila)

Established pattern: single-file HTML playground → desktop shortcut → GitHub repo + Pages. When the user says "you know my <X> playground", these are the files they mean.

## Tailwind CSS Playground (original)
- Local: `C:\Users\YOUR_USERNAME\Documents\Projects\tailwind-playground\index.html` (~3,700 lines, Tailwind Play CDN + vanilla JS, self-contained)
- Shortcut: `Desktop/Desktop/Tailwind Playground.lnk` (TargetPath = the index.html, no args)
- Repo: https://github.com/AttilaHuns288452/tailwind-playground (Pages from root, `main`)
- Live: https://attilahuns288452.github.io/tailwind-playground/
- Obsidian note: `~/Documents/Obsidian Vault/Tailwind CSS Playground.md` (frontmatter has repo/demo links)
- Features: 36 interactive utility sections, Tailwind Play REPL, 6 component templates, dark/light (localStorage), search, copy-code dock, mobile sidebar

## React JS Playground (built 2026-08-01, mirror of the above)
- Local: `C:\Users\YOUR_USERNAME\Documents\Projects\react-playground\index.html` (React 18 UMD + @babel/standalone via CDN)
- Shortcut: `Desktop/Desktop/React Playground.lnk`
- Repo: https://github.com/AttilaHuns288452/react-playground (Pages from root, `main`)
- Live: https://attilahuns288452.github.io/react-playground/
- Features: live JSX REPL (component named `App`), 9 presets (Counter, Todo, Tabs, Accordion, Stopwatch, Color Picker, Form, Profile Card, Clock), copy dock, search, dark/light, inline error panel, Ctrl+Enter re-run
- `preview-*.png` QA screenshots gitignored

## "Do that again" template
When asked for a new playground variant: single-file html in `~/Documents/Projects/<name>-playground/`, verify with headless Edge (see SKILL.md), create the .lnk next to the existing ones in `Desktop/Desktop/`, then `gh repo create <name>-playground --public --source . --push` + enable Pages on `main` root. MIT license (copy from tailwind-playground/LICENSE).

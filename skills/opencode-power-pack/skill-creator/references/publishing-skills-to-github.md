# Publishing Hermes Skills to GitHub as a Reference Repository

## When to Use

You've created a collection of Hermes Agent skills and want to publish them as a standalone GitHub repo — as a reference, a portfolio, or a replication guide for others. The repo should be a **working reference**, not just a showcase: every skill file is valid Hermes Agent frontmatter, usable by copying to `~/.hermes/skills/`.

## Repository Structure

```
your-repo-name/
├── index.html                     # (optional) Static companion website
├── skills/
│   ├── decide.md                  # Hermes skill: valid frontmatter + markdown body
│   ├── my-other-skill.md          # Each skill is a usable .md file
│   └── ...
├── LICENSE                        # MIT recommended
├── SETUP.md                       # Step-by-step replication guide
├── README.md                      # Narrative explaining the "why" behind each skill
└── .nojekyll                      # Required if deploying to GitHub Pages
```

## Steps

### 1. Create the Skill Files

Every skill file must be a valid Hermes Agent skill:

```yaml
---
name: my-skill
description: "Use when <trigger>. <one-line behavior>."
version: 1.0.0
author: Your Name
license: MIT
triggers:
  - trigger_phrases
---
# My Skill
```

Key requirements from `tools/skill_manager_tool.py`:
- Frontmatter starts at byte 0 with `---`, closes with `\n---\n`
- `name` ≤ 64 chars (lowercase + hyphens), `description` ≤ 1024 chars
- Non-empty body, total ≤ 100,000 chars (aim for 8-15k)

### 2. Write the Narrative README

The README must answer "why does each skill exist?" — not just "what is it?"

Good structure:
- **Why I Built This** — the origin story: what problems led to these skills
- **The Problems** — e.g. "token waste: 551K per file read", "model chaos: 5 uncoordinated sources"
- **Each Skill's Purpose** — table mapping skill name → problem it solves
- **Architecture Decisions** — why you chose this approach over alternatives
- **Tech Stack Table** — each tool, version, what it does, link to source repo
- **Repo Structure** — directory tree so visitors can orient
- **References** — table of every project referenced with GitHub links

### 3. Write SETUP.md (Replication Guide)

A step-by-step guide someone else can follow to replicate your stack:
- Install Hermes Agent (include commands for macOS/Windows/Linux)
- Clone the repo
- Copy skills to `~/.hermes/skills/`
- Install each tool (Graphify, CodeGraph, etc.) with exact commands
- Configure MCP servers in `~/.hermes/config.yaml`
- Verify each layer works
- Troubleshooting table (problem → solution)

### 4. Secrets Sanitization (Critical Before First Commit)

Scan every file for:

```bash
# API keys / tokens
grep -inE "(api[_-]?key|token|ghp_|gho_|sk-[a-zA-Z0-9]|xox[baprs]-)" <files>

# Local file paths with usernames
grep -inE "(C:\\\Users\\\[A-Za-z]+|/home/[A-Za-z]+)" <files>

# Environment variables with secrets
# Check for .env files, config.yaml with real API keys
```

Replace with placeholders (`YOUR_API_KEY_HERE`, relative paths, `~/`).

### 5. Add LICENSE

MIT is standard for open-source skill collections. Include a full MIT license file.

### 6. Optional: Deploy Companion Static Site

If you have an `index.html`:
- Add `.nojekyll` to root (prevents GitHub Pages from ignoring `_`-prefixed files)
- Enable Pages: repo Settings → Pages → Source: deploy from master branch, / (root)
- Site lives at `https://<user>.github.io/<repo>/`

### 7. Verify on GitHub

After pushing, confirm all files landed:
```bash
curl -s "https://api.github.com/repos/<user>/<repo>/contents" | python -c "import sys,json; [print(i['name']) for i in json.load(sys.stdin)]"
```

## Example

The canonical example: [AttilaHuns288452/hermes-workflow](https://github.com/AttilaHuns288452/hermes-workflow) — 5 skills (decide, core-identity-guardrail, token-saver, model-router, obsidian-docs) + narrative README + SETUP.md + LICENSE + GitHub Pages static site.

## Pitfalls

1. **Local paths leaked in HTML.** Before publishing any `index.html`, check for `file:///` links and `C:\Users\<username>`. These break for other users and leak your username.
2. **API keys in config examples.** Use placeholder values (`YOUR_API_KEY_HERE`) in every config file and example.
3. **Forgetting `.nojekyll`.** GitHub Pages ignores `_`-prefixed files. Without `.nojekyll`, the site will have broken links.
4. **Skill files without frontmatter.** A `.md` file without valid YAML frontmatter will not register as a Hermes skill. Every file in `skills/` must start with `---`.
5. **Generic descriptions in a public repo.** For a published collection, the description is someone else's first exposure. "Do X" is not enough — "Use when building Y. Handles Z edge cases with A approach" is better.
6. **No SETUP.md.** Without a replication guide, the repo documents a system no one else can build. SETUP.md is what makes it "working reference" vs "showcase."

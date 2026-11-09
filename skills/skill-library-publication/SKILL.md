---
name: skill-library-publication
description: Use when the public skill repo drifts from the live tree.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [skills, git, publishing, sync]
    related_skills: [external-skill-import, git-repo-hygiene, ecosystem-audit]
---

# Publishing a Skill Library

Syncing the public repo of skills (the workflow shared with classmates, friends, peers) against the live `~/.hermes/skills` tree. The repo is a **subset by design**: no credentials, no machine state, no private project facts. Direction matters: the live tree is the source, the repo is the publication.

## When to Use

- The user says their public repo is stale, missing skills, or differs from their setup.
- After importing packs locally and the repo should carry them.
- Before telling a user "your repo has X and your setup has Y" — measure it first.

## Procedure

1. **Inventory both sides by frontmatter `name:`**, falling back to the directory name when YAML fails to parse. Include every root from `skills.external_dirs` in the live set or externally-installed skills get mislabelled as missing.
2. **Classify every name**:
   - shared with different bytes: `git log -1 --format=%ct -- <repo path>` against the local file's mtime. Repo older than the local edit = stale publication.
   - local-only = work never published.
   - repo-only = library breadth the live profile does not install (keep it; it is what readers get).
3. **Hold what you cannot license.** A third-party pack with no LICENSE/NOTICE in its tree stays out until attribution is added. Name the held packs and the reason in the commit message; never publish them silently.
4. **Scan every staged file** before committing: key shapes (`sk-`, `osb_`, `sbp_`, `ghp_`, `AKIA`, PRIVATE KEY blocks), private paths (`~/.hermes/mcp-tokens`, `~/.ssh`), and absolute home paths (report those; rewrite only if asked).
5. **Publish on a branch**: `git checkout -b sync/<topic>-<date>`, commit with the counts and what was held, `git push -u origin <branch>`. Merging to the default branch is the owner's call.
6. **Run the repo's own gate** (e.g. `scripts/audit_skills.py`): frontmatter, duplicate names, secret hits. Fix hard failures before pushing.

## Pitfalls

- **A hand-curated site does not follow the skills.** Catalog JSON and `SKILLS_CATALOG.md` counts are often written by hand with no generator. Check `package.json` scripts and `scripts/` before promising the site reflects the sync, and say plainly when it does not.
- **"Every skill is installed" claims rot.** If the catalog says that while the repo holds skills the live profile never installs, fix the sentence, not the data.
- **Do not prune the repo to match the live catalog.** Repo-only skills are shareable breadth; deleting them to make the sets equal shrinks what peers get for no local gain. Explaining the two sets as disk-vs-injected is usually the answer the user needs.
- **Sync is one-directional by default.** Refreshing repo copies from the live tree is safe. Importing repo-only skills back costs prompt budget (each row is name + 60 description chars, every turn), so treat it as a separate measured decision with a named gap list, not a mirror operation.
- **A "different skills" report is usually drift, not divergence.** Quantify it (how many shared names, how many repo-older, how many local-only) before proposing any action.

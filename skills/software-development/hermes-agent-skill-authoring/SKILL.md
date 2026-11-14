---
name: hermes-agent-skill-authoring
description: "Author in-repo SKILL.md files: frontmatter and structure."
version: 2.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skills, authoring, hermes-agent, conventions, skill-md]
    related_skills: [requesting-code-review]
---

# Authoring Hermes-Agent Skills (in-repo)

## Overview

There are two places a SKILL.md can live:

1. **User-local:** `~/.hermes/skills/<maybe-category>/<name>/SKILL.md` — personal, not shared. Created via `skill_manage(action='create')`.
2. **In-repo (this skill is about this case):** `skills/<category>/<name>/SKILL.md` or `optional-skills/<category>/<name>/SKILL.md` inside the hermes-agent repo — committed, shipped with the package. Use `write_file` + `git add`. `skill_manage(action='create')` does NOT target this tree.

In-repo skills must meet the repo's **hardline authoring standards** (see AGENTS.md, "Skill authoring standards (HARDLINE)" — that section is the source of truth; this skill is the operational walkthrough). Reviewers reject PRs that violate them, so meeting them up front is cheaper than a salvage pass later.

## When to Use

- User asks you to add a skill "in this branch / repo / commit"
- You're committing a reusable workflow that should ship with hermes-agent
- You're editing an existing skill under `skills/` or `optional-skills/` (use `patch` for small edits, `write_file` for rewrites; `skill_manage` still works for patch on in-repo skills, but not for `create`)
- Don't use for: personal skills in `~/.hermes/skills/` (just use `skill_manage`)

### `skill_manage(action='create')` also enforces the 60-char description

The user-local path is not exempt from the frontmatter standard. `create`
**refuses** a description over 60 chars outright (`Description is 67 chars; a
skill description must fit the 60-char skill index`) — the whole operation
aborts and rolls back, so a multi-op batch that starts with a long description
loses every op in it.

After a successful `create`, the tool also lints and warns (advisory, not
blocking) when the file is missing `version` / `author` / `license` /
`metadata.hermes.{tags, related_skills}` or has no `## When to Use` near the top.

Cheapest path: write user-local skills to the same frontmatter shape as in-repo
ones from the start — `name`, ≤60-char description ending in a period,
`version`, `author`, `license`, `platforms`, `metadata.hermes.{tags,
related_skills}`, and a `## When to Use` section — and you get no refusal and no
follow-up patch.

## Decide the Tier First: Bundled vs Optional

- **Bundled (`skills/<category>/`)** — daily-driver behavior, broadly useful across many user types, low footprint. Hard bar: you can say "a user will load this in 5+ sessions per month" with a straight face.
- **Optional (`optional-skills/<category>/`)** — niche, vertical-specific (blockchain, gaming, finance, one app), recurring-job/task skills, or anything heavy. Installed via `hermes skills install official/<category>/<skill>`.

**When in doubt, optional.** Promoting later is easy; demoting is churn. "Would be useful to anyone who ever needs this" is an optional-tier argument, not a bundled one.

Pick the category by what the tool IS, not what it feels like (an AI-agent CLI goes in `autonomous-ai-agents/` even if it "feels productivity"). Confirm existing categories with `search_files(pattern='*', target='files', path='skills')` and don't invent new top-level categories casually.

**No router / index / hub skills.** A skill whose core content is a routing table pointing at sibling skills adds an indirection hop and duplicates the siblings' own `When to Use` triggers. If the skill would be empty without "load skill X instead" pointers, don't write it — the catalog and each sibling's triggers already do that job.

## Required Frontmatter

Validator source of truth: `tools/skill_manager_tool.py::_validate_frontmatter`. Validator hard requirements:

- Starts with `---` as the first bytes (no leading blank line).
- Closes with `\n---\n` before the body.
- Parses as a YAML mapping.
- `name` field present.
- `description` field present (validator ceiling 1024 chars — but see the repo hardline below, which is much stricter).
- Non-empty body after the closing `---`.

Repo-standard shape (all fields expected, even where the validator doesn't enforce them):

```yaml
---
name: my-skill-name               # lowercase, hyphens, ≤64 chars (MAX_NAME_LENGTH)
description: Concise capability statement, under sixty chars.
version: 0.1.0                    # semver; new skills start at 0.1.0
author: Real Name (github-handle), Hermes Agent
license: MIT
platforms: [linux, macos, windows]   # audit, don't guess — see Platform Gating
metadata:
  hermes:
    tags: [Short, Descriptive, Tags]
    related_skills: [other-in-repo-skill]
---
```

### `description` rules (HARDLINE — the validator's 1024 is NOT the standard)

- **≤ 60 characters.** One sentence. Ends with a period.
- State the capability, not the implementation, and don't repeat the skill name.
- No marketing words ("powerful", "comprehensive", "seamless", "advanced").
- The system prompt skill index clips to `SKILL_PROMPT_DESC_LIMIT` = 60 chars (`agent/skill_utils.py`), cut at a word boundary and suffixed with "..." — the trigger/capability must be self-contained in that window. Render the real line with `build_skills_system_prompt()` when unsure what survives the clip.
- If the description contains a `:`, wrap it in double quotes or YAML parses it as a mapping and the docs generator crashes. Quotes don't count toward the 60.

Good: `Track named companies for material news with cited digests.`
Bad: `Use when a user asks to monitor named competitors or companies for product launches, pricing changes, funding, ...` (240 chars — rejected in review)

### `author` rules

- Credit the **human first**, then "Hermes Agent" as secondary collaborator: `Ben Barclay (benbarclay), Hermes Agent`.
- Never `author: Hermes Agent` alone for contributed skills — credit the human, not the tool, even (especially) when an agent drafted the text.
- Maintainer-authored skills: `Teknium (teknium1), Hermes Agent`.

### `related_skills` rules

- Every entry must resolve to an existing **in-repo** skill in the same tree state as your PR. Do not reference skills that were only planned, live in another PR, or exist only in `~/.hermes/skills/`.
- Verify each entry: `search_files(pattern='<name>', target='files', path='skills')` (and `optional-skills/`).

## Platform Gating: audit, don't trust

`platforms:` gates loading by host OS. Set it from what the skill's prose and scripts actually invoke:

| Skill uses only… | `platforms:` |
|---|---|
| Hermes tools + stdlib Python + cross-platform CLIs | `[linux, macos, windows]` |
| bash pipelines, `grep`/`awk`/`sed` chains, heredocs | `[linux, macos]` |
| `osascript`, `defaults`, `pmset` | `[macos]` |
| `apt`/`systemctl`/`/proc` | `[linux]` |

<!-- no-tmp: ok — names the anti-pattern skill authors must avoid -->
POSIX-only signals to search for in `scripts/`: `fcntl`, `termios`, `pty`, `os.fork`, `os.killpg`, `signal.SIGKILL`, `os.kill(pid, 0)` liveness checks, hardcoded `/tmp` `/proc` `/etc`. Default posture: fix cross-platform first (`tempfile.gettempdir()`, `pathlib.Path`, `psutil.pid_exists`); gate narrower only when the dependency is genuinely platform-bound, and say why in `## Pitfalls`.

## Size Limits

- Full SKILL.md: ≤ 100,000 chars enforced (`MAX_SKILL_CONTENT_CHARS`), but target **~100 lines for a simple skill, ~200 for a complex one**. Peer skills sit at 8-14k chars.
- Bulky or branch-specific material goes in `references/*.md`, `templates/`, or `scripts/` — pointed to from SKILL.md, not inlined.
- Don't expect the model to inline-write parsers or non-trivial logic every call — ship a helper script in `scripts/` and reference it by path.

## Body Structure (modern section order)

```
# <Skill> Skill
2-3 sentence intro: what it does, what it doesn't do, dependency stance.

## When to Use          — bulleted triggers (+ "Don't use for:" counter-triggers)
## Prerequisites        — exact env vars, installs, API key sourcing
## How to Run           — canonical invocation through the `terminal` tool
## Quick Reference      — flat command list, no narration
## Procedure            — numbered steps, each with a checkable completion criterion
## Pitfalls             — known limits, things that look broken but aren't
## Verification         — how to prove the skill worked
```

Not every section applies to every skill (a pure-procedure task skill may have no Quick Reference), but When to Use + actionable body + Pitfalls + Verification are the minimum. Cut marketing intros, "Setup Check" no-ops, and re-explanations of env vars already in Prerequisites.

### Reference Hermes tools, not raw shell

When the skill needs a capability, name the proper Hermes tool in backticks: `terminal`, `read_file`, `write_file`, `patch`, `search_files`, `web_search`, `web_extract`, `browser_navigate`, `vision_analyze`, `delegate_task`, `cronjob`. Do NOT name shell utilities the agent already has wrapped (`grep` → `search_files`, `cat` → `read_file`, `sed`/`awk` → `patch`, `find`/`ls` → `search_files target='files'`). A CLI-wrapper skill should frame invocations as `terminal(command="{tool} ...", timeout=...)` — bare shell prose ("run `foo --version`") is a review-blocking non-conformance. If the skill depends on an MCP server, name it and document setup in Prerequisites.

### Never use machine-local paths

Write repo-relative paths (`skills/...`, `tools/skill_manager_tool.py`). A `/home/<you>/...` path baked into a committed skill breaks for every other user and is an instant review flag.

## Writing Quality Principles

A skill exists to make the agent's process more predictable — the agent reliably follows the same useful discipline.

1. **Optimize for process predictability.** If a line does not change behavior, cut it.
2. **Choose the right context load.** The description is paid for every turn; details go in the body or linked references.
3. **End steps with completion criteria.** Checkable and, when it matters, exhaustive: "every modified file accounted for" beats "summarize changes."
4. **Co-locate rules with the concept they govern.**
5. **Use strong leading words** ("tight loop," "root cause," "regression test") over long repeated explanations.
6. **Prune duplication and no-ops.** "Be careful" and "use best practices" don't change model behavior — replace with a checkable criterion or delete.
7. **Skills are folders, not files.** Put deep material in `references/`, `scripts/`, `examples/` subdirectories and load it on demand (progressive disclosure); keep the always-loaded body lean.
8. **Grow the Pitfalls section over time.** It is the highest-signal content in a skill: every observed failure point of the agent in that domain becomes one new pitfall line, not a rewrite.

### Activation wiring (user-local skills)

A skill that is only needed *after* another skill is already loaded cannot win the catalog scan on its description alone: the agent is working from the loaded skill and rarely rescans the index. Wire two triggers instead: put the trigger words inside the first 60 characters of the description, and add a one-line pointer at the end of every skill that precedes it in the workflow ("once the page is built, load the `X` skill and run it as a review layer"). The pointer is what fires in practice; the description is what makes the catalog row findable when no other skill is loaded.

Do not reach for `skills.auto_load` to fix underuse: it pins the full body into every session prompt, including sessions where the skill is irrelevant, and the fixed cost is paid on every API call and in every subagent. A one-line pointer plus a tight description beats a permanent token tax.

### Catalog health (user-local install)

Two failures make a skill present-but-invisible, and neither looks like a file-count problem:

- **Unparseable frontmatter.** A bulk import that joins YAML keys onto one line (`description: ..." when_to_use: "..." last_reviewed: ...`) raises a scanner error: the file exists, `find | wc -l` counts it, and the skill never enters the index. Repair by rebuilding `name`/`description` as valid YAML (drop or fold the extra keys into the body), then re-parse every touched file rather than trusting the count.
- **Plugin-registered skills.** `ctx.register_skill(name, path, description="")` accepts an optional description; a plugin that omits it leaves a bare `plugin:skill` row with no trigger even though its SKILL.md has one. In this install `hermes_cli/plugins_content.py` hydrates description + frontmatter from the SKILL.md when a plugin supplies none (kept as a local patch in `ensure_agent_patches.py`). Verify with `python3 ~/.hermes/scripts/check_plugin_skill_descriptions.py` (exit 0 = every plugin skill has a description).

- **Directory name ≠ frontmatter `name:`.** Hermes resolves a skill by three aliases — declared name, **directory basename**, and path relative to the root — so a skill whose name equals another skill's *directory* name resolves `ambiguous`, and whichever one's own name matches the shared alias is then refused by `skill_view`. Nothing looks broken: the file exists, `hermes skills list` shows it enabled, and the catalog prints a "a copy of X is not listed … so skill_view cannot load it" note that is easy to read as cosmetic. Rename the DIRECTORY to the skill's own frontmatter identity; renaming the skill just moves the collision. Symlinked skill dirs (`~/.hermes/skills/<name>` → another tool's tree) are the usual source, since the symlink's name becomes a second alias for the same string.

Run `python3 ~/.hermes/scripts/skills_health.py` after any import or bulk edit: it fails on unparseable frontmatter, empty descriptions, duplicate names inside one root, plugin skills without a description, and any skill Hermes' own resolver marks unloadable (no `load_name`, excluding intentional cross-tier `shadowed` copies). It walks with `os.walk(followlinks=True)`, so a symlinked skill dir is scanned exactly as Hermes scans it — a plain `rglob` misses those and reports a clean bill of health while a capability is unreachable. Advisories list descriptions that clip on a stopword. The cron watchdog runs the same check on a schedule, so a broken import surfaces within hours even if you forget.

(Principles 7-8 adapted from shanraisshan/claude-code-best-practice, MIT.)

## Coherent skill improvement

Before patching a skill, compare its trigger, procedure, dependencies, output, and failure handling with its likely siblings. Record a per-sibling verdict: propagate, already covered, distinct, or not inspected. Shared wording alone does not prove duplication. Start from the live file and preserve unique behavior.

A repeated violation is evidence about enforcement: after the same rule fails twice without an intervening fix, prefer a test, lint, hook, safer default, or narrower interface over a third prose rewrite. A zero-result scan is evidence about the instrument until an independent probe verifies the population is empty. Substantial restructures remain staged and recoverable; use Hermes `skill_manage` as the live write path, not a second observer or installer.

Adapted from Eoghan Henn's [Task Observer](https://github.com/rebelytics/one-skill-to-rule-them-all), commit `da860265ae968bdc6bb13b96c2c75fcb61176b72`, `references/observation-log.md` and `references/signals.md`, under CC-BY-4.0. The Claude-specific activation, hooks, observation store, and staging installer are deliberately not adopted.

## Tests and Docs (required for repo skills)

1. **Tests** live at `tests/skills/test_<skill>_skill.py` — stdlib + pytest + `unittest.mock` only, no live network. Run via `scripts/run_tests.sh tests/skills/test_<skill>_skill.py -q`. (The generic `tests/tools/test_skill_manager_tool.py` passing proves nothing about YOUR skill.)
2. **Docs regen:** run `python website/scripts/generate-skill-docs.py`, then apply scope discipline — the generator rewrites EVERY auto-gen page. `git checkout --` everything that isn't yours; the final diff must show only your SKILL.md, your one per-skill docs page, a one-line catalog row, and a one-line `website/sidebars.ts` insertion (verify with `search_files(pattern='<your-slug>', path='website/sidebars.ts')` — exactly one hit, or the page is an orphan).
3. **`.env.example`** (only if the skill needs new env vars): one clearly delimited commented block; touch nothing else in the file.

## Workflow

1. **Survey peers** in the target category with `search_files(target='files')` and read 2-3 peer SKILL.md files to match tone and structure. Prefer extending an existing skill over creating a narrow sibling.
2. **Decide tier and category** (see above). When in doubt, optional — and ask before pushing rather than defaulting.
3. **Draft** with `write_file` to `skills/<category>/<name>/SKILL.md` (or `optional-skills/...`).
4. **Validate locally**:
   ```python
   import re, pathlib
   from ruamel.yaml import YAML
   content = pathlib.Path("skills/<category>/<name>/SKILL.md").read_text()
   assert content.startswith("---")
   m = re.search(r'\n---\s*\n', content[3:])
   fm = YAML(typ="safe").load(content[3:m.start()+3])
   assert "name" in fm and "description" in fm
   assert len(fm["description"]) <= 60, f"description {len(fm['description'])} chars — hardline is 60"
   assert fm["description"].endswith(".")
   assert "platforms" in fm
   assert len(content) <= 100_000
   ```
   Also verify every `related_skills` entry exists in-repo.
5. **Add tests + regen docs** (previous section).
6. **Git add + commit** on the active branch; open a PR.
7. **Note:** the CURRENT session's skill loader is cached — `skill_view` / `skills_list` will not see the new skill until a new session. This is expected, not a bug.

## Editing Existing In-Repo Skills

- **Small fix:** `skill_manage(action='patch', ...)` works on in-repo skills, as does `patch`.
- **Major rewrite:** `write_file` the whole SKILL.md.
- **Supporting files:** `write_file` to `references/`, `templates/`, or `scripts/` under the skill dir.
- **Always commit** — in-repo skills are source, not runtime state. Re-run the docs generator when frontmatter changed.

## Common Pitfalls

1. **Using `skill_manage(action='create')` for an in-repo skill.** It writes to `~/.hermes/skills/`, not the repo tree. Use `write_file`.
2. **Trusting the validator's limits as the standard.** The validator allows 1024-char descriptions; review rejects anything over 60. The validator doesn't check `platforms:`, author format, tests, or docs — review does.
3. **`author: Hermes Agent` on a contributed skill.** Credit the human first.
4. **Leading whitespace before `---`.** Validation fails on any leading blank line or BOM.
5. **Description too generic or trigger buried past char 57.**
6. **`related_skills` pointing at skills that don't exist in-repo** (user-local, planned, or in a sibling PR).
7. **Duplicating a peer.** Survey the category first; extend rather than sibling.
8. **Skipping the docs generator or pushing its unrelated drift.** Both directions are wrong: no regen = orphan skill with no docs page; blind regen = a ballooned diff full of other skills' drift.
9. **Expecting the current session to see the new skill.** The loader is initialized at session start.
10. **Letting skills accumulate sediment.** When adding a rule, remove the old wording it replaces.

## Verification Checklist

- [ ] Tier decided deliberately (bundled bar: 5+ sessions/month; else `optional-skills/`)
- [ ] File at `skills/<category>/<name>/SKILL.md` or `optional-skills/<category>/<name>/SKILL.md`
- [ ] Frontmatter starts at byte 0 with `---`, closes with `\n---\n`
- [ ] `name`, `description`, `version`, `author`, `license`, `platforms`, `metadata.hermes.{tags, related_skills}` all present
- [ ] Description ≤ 60 chars, one sentence, ends with a period, no marketing words
- [ ] `author` credits the human contributor first
- [ ] `platforms:` audited against actual prose/scripts, not copied from a sibling
- [ ] Every `related_skills` entry resolves in-repo
- [ ] Body follows the modern section order; commands framed through Hermes tools
- [ ] No machine-local paths anywhere in the file
- [ ] Each ordered step has a checkable completion criterion
- [ ] Tests at `tests/skills/test_<skill>_skill.py` pass under `scripts/run_tests.sh`
- [ ] Docs regenerated with scope discipline; sidebar has exactly one entry for the slug
- [ ] `git add` + commit on the intended branch; PR opened

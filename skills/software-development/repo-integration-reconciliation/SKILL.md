---
name: repo-integration-reconciliation
description: "Audit existing skills when setting up new repos, resolve overlaps by keeping the better method, fill gaps, document complementarity. Covers the full workflow: clone → audit → reconcile → fill gaps → verify → document."
version: 1.0.0
---

# Repo Integration & Skill Reconciliation

## Role
When setting up a new repository into this agent environment, this skill audits existing skills for overlap/capability conflicts, resolves them decisively (keep the better method, never duplicate), fills gaps the repo introduces, preserves complementary approaches, and verifies integrity after integration.

## Workflow

### Phase 1 — Install & Scaffold
Clone the repo, install dependencies, and verify it runs correctly before touching anything else.

```bash
git clone <url> ~/Documents/Projects/<repo-name>
cd ~/Documents/Projects/<repo-name>
# Install deps per build system
ls package.json && npm install
ls requirements.txt && pip install -r requirements.txt
ls pyproject.toml && uv sync --frozen
ls Cargo.toml && cargo build
# Verify: try --help, --version, or a quick run
```

### Phase 2 — Audit Existing Skills
Read every skill file present in the skills directory. For each capability the new repo provides, identify whether an existing skill already covers it (fully or partially).

```bash
# List all existing skills
ls ~/AppData/Local/hermes/skills/*/*/SKILL.md
```

For each skill, ask:
- Does this skill provide the same or overlapping capability as the new repo?
- Is the overlap full (can do exactly what the repo does) or partial (one aspect)?
- Does the new repo do something the existing skill doesn't and vice versa?

### Phase 3 — Resolve Overlaps Decisively
When the new repo and an existing skill cover the same capability, evaluate both on:
- **Accuracy**: Which produces more correct results?
- **Robustness**: Which handles edge cases and errors better?
- **Maintainability**: Which is easier to update and integrate?
- **Fit**: Which fits better with the existing stack (Hermes Agent, OpenCode, Obsidian)?

**Keep whichever is objectively better. Do not maintain duplicates.** Document what was replaced and why.

Decision matrix:

| Overlap Type | Resolution |
|---|---|
| Full overlap, new repo is better | Replace existing skill's method with new repo's approach. Update SKILL.md to reference new repo. |
| Full overlap, existing skill is better | Keep existing skill. Flag new repo as secondary/additional resource. |
| Partial overlap, complementary strengths | Keep both. Document when to use each (see Phase 5). |
| No overlap | New repo fills a gap (see Phase 4). |

### Phase 4 — Fill Gaps
If the new repo introduces capabilities not covered by any existing skill, register them as new skills following the existing skill format and naming conventions:

- Use lowercase-hyphenated names
- Add proper frontmatter (name, description, triggers, version)
- Place in appropriate category directory under `skills/`
- Link to the repo's README/docs in the skill body

### Phase 5 — Preserve Complementary Methods
If both the repo and an existing skill handle the same domain but through genuinely different approaches (e.g. one is faster, one is more thorough), keep both and document when to use each.

Documentation template:
```markdown
## Compared with <Existing Skill>

| Aspect | <New Repo> | <Existing Skill> |
|---|---|---|
| Approach | <how it works> | <how it works> |
| Best for | <use case> | <use case> |
| Performance | <benchmarks> | <benchmarks> |
| Integration | <how to use> | <how to use> |
```

### Phase 6 — Verify Integrity
After integration, confirm no existing skill was silently broken or shadowed by the new repo's methods:

1. Run a test case that previously worked with the existing skill
2. Verify the new repo's method works correctly
3. Check for port conflicts, path overlaps, or config interference
4. Run the full Obsidian bundle (scan + render) if Obsidian integration exists

## Triggers
- "setup <url> with reconciliation"
- "integrate <repo> and audit skills"
- "add <repo> with skill conflict resolution"
- "setup this repo and reconcile overlapping skills"

## Related
- `software-development/setup` — Standard setup without reconciliation
- `software-development/update` — Full ecosystem onboarding
- `software-development/graphify-integrate` — Graphify code-graph integration
- `note-taking/obsidian` — Mandatory documentation phase

---
name: ecc-bridge
description: Wires ECC agents from Projects/ECC/agents/ into the Hermes runtime pipeline by extracting agent prompts, stripping Sonnet/Opus model requirements, and running them through the free model chain (OpenCode → Freebuff → FreeLLMAPI → OpenRouter). Also catalogs all 64 agents and reports free-model compatibility.
triggers:
  - ecc-agent
  - comment-analyzer
  - silent-failure-hunter
  - pr-test-analyzer
  - type-design-analyzer
  - code-simplifier
  - doc-updater
  - database-reviewer
  - refactor-cleaner
  - performance-optimizer
  - code-review-from-ECC
---

# ECC Bridge — Runtime Agent Wiring

## Purpose

ECC agents are `.md` skill files designed for Claude Code with `model: sonnet`/`model: opus` requirements.  
This bridge **extracts their prompt body**, strips the paid-model requirement, and routes them through  
the **free model chain** (opencode-go/meta/muse-spark-1.2-contributor for code agents, opencode-go/mimo-v2.5 for vision agents → OpenCode bundled free → Freebuff → FreeLLMAPI → OpenRouter :free).

**All 64 agents run on free models** via `config.yaml` `delegation.model` (currently `opencode-go/meta/muse-spark-1.2-contributor`) for text agents, and `config.yaml` `auxiliary.vision` (`opencode-go/mimo-v2.5`) for vision agents.  The7 opus agents (architect, chief-of-staff, gan-evaluator, gan-generator, gan-planner, healthcare-reviewer, planner) also route through the same delegation config — complex architecture reasoning may be weaker than native opus, but they execute.

### Live routing is pinned to `config.yaml` (`delegation.model = opencode-go/meta/muse-spark-1.2-contributor`, `auxiliary.vision = mimo-v2.5`). The table below is the historical mapping — trust config, not this table, for new work.

### Model Mapping

| Agent Type | Free Model | Fallback |
|-----------|-----------|----------|
| Code/analysis agents (comment-analyzer, code-simplifier, refactor-cleaner, etc.) | `opencode-go/meta/muse-spark-1.2-contributor` (config truth) | `opencode-go/meta/muse-spark-1.2-contributor` |
| Vision/multimodal agents (image-prompt-engineer, visual-storyteller, ui-designer) | `opencode-go/mimo-v2.5` | `opencode-go/mimo-v2.5` |

## Triggers (when this skill is activated)

| Trigger phrase | Routes to ECC Agent |
|---------------|-------------------|
| "review this code for silent failures" | `silent-failure-hunter` |
| "analyze these comments" / "comment rot" | `comment-analyzer` |
| "review PR test coverage" / "test quality" | `pr-test-analyzer` |
| "analyze type design" / "type safety review" | `type-design-analyzer` |
| "simplify this code" / "clean up code" | `code-simplifier` |
| "update docs" / "generate codemaps" | `doc-updater` |
| "review this database schema" / "SQL review" | `database-reviewer` |
| "remove dead code" / "refactor" / "cleanup" | `refactor-cleaner` |
| "optimize performance" / "bottleneck" | `performance-optimizer` |
| "list ECC agents" / "which agents are safe for free" | Agent index (list-safe) |
| "run ECC agent <name>" | Agent lookup + execution |

## Parallel Multi-Agent Quality Gate (⭐ recommended)

**When:** After building a feature/project, before shipping. Dispatch
3-5 ECC review agents via `delegate_task(tasks=...)`. All return in ~3 min.
Proven: caught 38 issues in CashFlow OS that primary builder missed.
**Gate size (2026-08-05):** baseline 3, full 5 — see mapping below; scale by
surface (schema → +database-reviewer, UI → +a11y-architect).

```ts
delegate_task(tasks=[
  { goal: "Review database schema — RLS, indexes, constraints, cascades",
    context: "Project: <path>. Check supabase/migrations/*.sql." },
  { goal: "Scan codebase for silent failures — empty catches, unhandled promises, missing error states",
    context: "Project: <path>. Check all .ts/.tsx files." },
  { goal: "Full code quality review — DRYness, TypeScript safety, React patterns, imports",
    context: "Project: <path>. Check all source files." },
])
```

**Agent mapping (use these goals, not ECC agent names):**

| Dimension | Goal | ECC Equivalent |
|-----------|------|---------------|
| Database | Schema review | `database-reviewer` |
| Error handling | Silent failure hunt | `silent-failure-hunter` |
| Code quality | DRYness, types, patterns | `code-reviewer` |
| Security | AuthZ, injection, secrets, XSS | `security-reviewer` |
| Build/TS | Build errors, warnings | `build-error-resolver` |
| A11y (UI batches) | WCAG, labels, contrast, focus | `a11y-architect` |

**Apply results:** fix root causes first (one fix often cascades to 10+ issues).

See `references/fullstack-quality-gate.md` for the CashFlow OS session evidence.

## Invocation Patterns

### Pattern 1 — Load agent prompt into this conversation (analysis/review agents)

For read-only analysis agents (comment-analyzer, silent-failure-hunter, pr-test-analyzer,  
type-design-analyzer, database-reviewer), load the agent's prompt directly into this session  
so the current free model executes the review:

```bash
python C:\Users\YOUR_USERNAME\AppData\Local\hermes\skills\ecc-bridge\scripts\ecc-runner.py <agent-name>
```

Take the output and use it as the **system prompt** for this conversation. The agent body  
contains the analysis framework, criteria, and output format — apply the user's code or  
filesystem context against those criteria.

### Pattern 2 — Delegate to OpenCode (code-modification and analysis agents)

For agents that write/change files (code-simplifier, refactor-cleaner, doc-updater,  
performance-optimizer), OR for analysis agents run through OpenCode (comment-analyzer,  
silent-failure-hunter), extract the prompt and pipe it to OpenCode with a free model:

```bash
# Extract prompt to a Windows-safe path (NOT /tmp — MSYS issue)
python ecc-runner.py code-simplifier > ecc-prompt.md
opencode run --model opencode-go/meta/muse-spark-1.2-contributor \
  --file ecc-prompt.md \
  "Simplify the code in the current working directory"
```

**Windows tip:** Never use `/tmp/ecc-prompt.md` — MSYS doesn't resolve it. Use a relative path or a full `C:/Users/...` path. See `references/2026-07-11-comment-analyzer-opencode-pipeline.md` for a proven example.

### Pattern 3 — Delegate to Freebuff (alternative coding agent)

For agents that need cloud model access (likely won't degrade on freebuFF's models):

```bash
python ecc-runner.py performance-optimizer > /tmp/ecc-prompt.md
freebuff run --model "DeepSeek V4 Flash" \
  "Optimize performance: $(cat /tmp/ecc-prompt.md)"
```

## Agent → Free Model Mapping

| ECC Agent | Original Model | Recommended Free Model | Tier |
|-----------|---------------|----------------------|------|
| doc-updater | haiku | `opencode-go/deepseek-v4-flash` | strong ✅ |
| comment-analyzer | sonnet | `opencode-go/deepseek-v4-flash` | good ✅ |
| silent-failure-hunter | sonnet | `opencode-go/deepseek-v4-flash` | good ✅ |
| pr-test-analyzer | sonnet | `opencode-go/deepseek-v4-flash` | good ✅ |
| type-design-analyzer | sonnet | `opencode-go/deepseek-v4-flash` | good ✅ |
| code-simplifier | sonnet | `opencode-go/deepseek-v4-flash` | good ✅ |
| database-reviewer | sonnet | `opencode-go/deepseek-v4-flash` | good ✅ |
| refactor-cleaner | sonnet | `opencode-go/deepseek-v4-flash` | good ✅ |
| performance-optimizer | sonnet | `opencode-go/deepseek-v4-flash` | good ✅ |
| image-prompt-engineer | sonnet | `opencode-go/mimo-v2.5` | good ✅ |
| visual-storyteller | sonnet | `opencode-go/mimo-v2.5` | good ✅ |
| ui-designer | sonnet | `opencode-go/mimo-v2.5` | good ✅ |

All 47 other sonnet agents and doc-updater (haiku) follow the same pattern.  
The 7 opus agents (architect, chief-of-staff, gan-evaluator, gan-generator, gan-planner,  
healthcare-reviewer, planner) also route to `opencode-go/meta/muse-spark-1.2-contributor` (2026-08-05) —  
expected: good, with weaker complex-architecture reasoning than native opus.

## Free Model Fallback Chain

When OpenCode's bundled free models fail:

1. **OpenCode free** → `opencode-go/meta/muse-spark-1.2-contributor` (primary, most reliable)
2. **Freebuff** → `freebuff run --model "DeepSeek V4 Flash"` (second, cloud-based)
3. **FreeLLMAPI** → custom Hermes provider at `localhost:3001/v1` (110+ models, local)
4. **OpenRouter :free** → only `openai/gpt-oss-120b:free` or `nex-agi/nex-n2-pro:free` (last free resort)

## What Gets Stripped From Each ECC Agent

When the bridge extracts an agent prompt:

| Removed | Kept |
|---------|------|
| YAML frontmatter (`name`, `model`, `tools`) | Agent role description |
| `model: sonnet` / `model: opus` / `model: haiku` | Analysis framework |
| Prompt Defense Baseline (8 bullet points) | Review criteria checklist |
| Claude Code-specific tool declarations | Output format instructions |
| | Shell commands (diagnostic) |
| | Workflow steps |

### Pattern 4 — Parallel Multi-Agent Quality Gate (⭐ recommended for any non-trivial build)

**When:** After building a feature or project, before shipping. Dispatches 3-4 ECC
review agents in parallel via `delegate_task(tasks=...)`. Each covers a different
quality dimension. All return within ~3 minutes. Proven: caught 38 issues in CashFlow OS
that the primary builder missed.

```ts
delegate_task(tasks=[
  {
    goal: "Review the database schema for RLS correctness, missing indexes, constraints",
    context: "Project: <path>. Check supabase/migrations/*.sql. Focus on RLS, cascades, constraints."
  },
  {
    goal: "Scan the codebase for silent failures, unhandled errors, swallowed exceptions",
    context: "Project: <path>. Check all .ts/.tsx files. Focus on empty catch blocks, unhandled promises, missing error states."
  },
  {
    goal: "Full code quality review — DRYness, TypeScript safety, React patterns, import hygiene",
    context: "Project: <path>. Check all source files. Focus on duplicated code, any casts, unused imports, naming."
  },
])
```

**Recommended agent mapping (use these goals, not ECC agent names directly):**

| Dimension | Goal | ECC Agent Equivalent |
|-----------|------|---------------------|
| Database | Schema review | `database-reviewer` |
| Error handling | Silent failure hunt | `silent-failure-hunter` |
| Code quality | DRYness, types, patterns | `code-reviewer` |
| Build/TS | Build errors, warnings | `build-error-resolver` |

**Apply results in priority order:** fix root causes first (e.g. extract duplicated
`getEntity()`), then cascading fixes (structured errors), then low-severity (unused imports).
One root-cause fix often cascades to resolve 10+ reported issues.

See `references/fullstack-quality-gate.md` for the CashFlow OS session example.

1. User invokes with a trigger phrase referencing an ECC agent
2. Run `python ecc-runner.py <agent> <context>` to extract the stripped prompt
3. **For analysis**: load the agent's prompt into this conversation's system context → apply against user's code
4. **For modification**: delegate to OpenCode with `--model opencode/<free-model>` and the agent prompt + task
5. Return results and suggest Obsidian documentation if findings were produced

## Verification

After running an ECC agent through the bridge:

- [ ] Agent prompt was extracted (no frontmatter or defense baseline in output)
- [ ] Original `model:` field was replaced with free model name
- [ ] The agent completed its analysis or modification
- [ ] If code was changed, verify no regressions (build + tests)

## Self-Audit: Running ECC Agents Against the Bridge Itself

After modifying `ecc-runner.py`, run one of the ECC analysis agents against it to catch
bugs. This is a **real technique demonstrated this session** — running `silent-failure-hunter`
against the bridge script found 5 bugs, and 2 high-severity ones were fixed immediately.

```bash
# Extract the agent prompt
python scripts/ecc-runner.py silent-failure-hunter \
  "Analyze scripts/ecc-runner.py for silent failures, bad fallbacks, and error propagation"
```

Use the output as the analysis framework for this conversation. The ECC agent's criteria
become the review checklist. Common findings from the inaugural self-audit:

1. **Missing try/except around file I/O** — `read_text()` calls can throw `FileNotFoundError`,
   `PermissionError`, or `UnicodeDecodeError`
2. **Undefined variable on unrecognized model field** — `tier` is never assigned if the agent's
   `model:` doesn't match `haiku`/`sonnet`/`opus`, causing `NameError`. Always add an `else`
   fallback.
3. **Duplicate keys from copy-paste** — When extending `SAFE_AGENTS` (or similar registry
   dicts), check for duplicate keys that silently overwrite previous entries.
4. **None-check before regex group access** — `m.group(1)` on a non-matching regex
   raises `AttributeError`. Always guard with `if m is not None:`.
5. **Shell argument joining drops structure** — Joining `sys.argv[2:]` with spaces loses
   newlines and indentation in context. Accept stdin pipe as an alternative for structured input.

### Self-Audit Procedure

1. Pick an ECC analysis agent (silent-failure-hunter for error handling, comment-analyzer
   for comment rot, database-reviewer for logic consistency)
2. Extract its prompt against the bridge's own `scripts/ecc-runner.py`
3. Apply the agent's analysis framework to identify issues
4. Fix high-severity findings immediately
5. Add any new pitfall discovered to this SKILL.md's Pitfalls section

## Pitfalls

- **Opus agents on free models**: Complex architectural thinking (architect, planner) WILL degrade on free models. These should be run through paid fallback when quality matters.
- **Code-modification agents can break things**: code-simplifier, refactor-cleaner, performance-optimizer make file changes. Always verify with build + tests after running.
- **OpenCode write mode**: code-modification agents need write mode. Ensure `opencode run` is in write mode (default). If no write mode, the agent will only produce a diff description.
- **Agent doesn't know about the current project**: When loading the agent prompt into this conversation, the current context (files, project structure) provides the codebase awareness the agent needs. When delegating to OpenCode, workdir must be set to the project root.
- **OpenCode stale DB**: If `opencode run` fails with "Unexpected server error" / SQLite "no such column: replacement_seq", the local DB schema is stale from a version upgrade. Fix: kill any opencode processes, delete `~/.local/share/opencode/opencode.db`, retry.
- **Windows /tmp doesn't exist**: When writing temp prompt files, use a project-relative path or full `C:/Users/...` path. MSYS `/tmp` fails silently — `opencode run` with `--file /tmp/foo` reports "File not found".
- **MSYS path doubling when running ecc-runner.py**: `python ~/AppData/Local/.../ecc-runner.py list` fails with `C:\c\Users\Attila\...` because MSYS resolves `~` to `/c/Users/YOUR_USERNAME` then Python prepends a drive letter. Use native Windows path: `python "C:/Users/YOUR_USERNAME/AppData/Local/hermes/skills/ecc-bridge/scripts/ecc-runner.py"`.
- **Multiple ECC agents in one OpenCode call**: Pass multiple `--file` flags to combine agent frameworks in a single pass. Tested: `opencode run 'read and improve X' --file architect-prompt.md --file reviewer-prompt.md`. OpenCode reads all attached files alongside the task.
- **Undefined variable on unexpected model field**: If the `index_all_agents()` function (or equivalent) encounters a `model:` value that isn't `haiku`/`sonnet`/`opus`, the `tier` variable is never assigned — `NameError` at the next line. Always add an `else: tier = "unknown"` fallback.
- **Duplicate keys in mapping dicts**: When maintaining `SAFE_AGENTS` (or agent-name-to-free-model mappings), a copy-pasted duplicate key silently overwrites the first entry. After every edit, grep for duplicates: `grep -c '"agent-name"' scripts/ecc-runner.py`.
- **None-check before regex .group()**: When extracting frontmatter, a regex that doesn't match returns `None` — calling `.group(1)` raises `AttributeError`. Always guard frontmatter extraction with `if m is not None:` before accessing captured groups.
- **Supabase trigger migration splitting**: PL/pgSQL function bodies with `$$` blocks contain internal semicolons. Splitting a migration SQL file by semicolons for REST API execution WILL corrupt function bodies. Move complex trigger logic to app code (`signUp` server action or middleware) instead.
- **Next.js `redirect()` in server actions ≠ form action**: `redirect()` throws `NEXT_REDIRECT` internally. When called imperatively from a `form onSubmit` handler (not the `action` prop), Next.js doesn't catch it — the promise rejects silently with no navigation and no error UI. Fix: return `{success: true}` from server actions, let the client call `router.push()`.

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
the **free model chain** (OpenCode bundled free → Freebuff → FreeLLMAPI → OpenRouter :free).

**57 of 64 agents** are compatible with free models (all haiku/sonnet agents).  
**6 opus agents** (architect, chief-of-staff, gan-*, healthcare-reviewer, planner) may show quality degradation.

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

## Invocation Patterns

### Pattern 1 — Load agent prompt into this conversation (analysis/review agents)

For read-only analysis agents (comment-analyzer, silent-failure-hunter, pr-test-analyzer,  
type-design-analyzer, database-reviewer), load the agent's prompt directly into this session  
so the current free model executes the review:

```bash
python $HERMES_HOME/skills/ecc-bridge/scripts/ecc-runner.py <agent-name>
```

Take the output and use it as the **system prompt** for this conversation. The agent body  
contains the analysis framework, criteria, and output format — apply the user's code or  
filesystem context against those criteria.

### Pattern 2 — Delegate to OpenCode (code-modification agents)

For agents that write/change files (code-simplifier, refactor-cleaner, doc-updater,  
performance-optimizer), extract the prompt and pipe it to OpenCode with a free model:

```bash
# Extract prompt, pipe to opencode
python ecc-runner.py code-simplifier > /tmp/ecc-prompt.md
opencode run --model opencode/deepseek-v4-flash-free \
  --file /tmp/ecc-prompt.md \
  "Simplify the code in the current working directory"
```

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
| doc-updater | haiku | `opencode/north-mini-code-free` | strong ✅ |
| comment-analyzer | sonnet | `opencode/deepseek-v4-flash-free` | good ✅ |
| silent-failure-hunter | sonnet | `opencode/deepseek-v4-flash-free` | good ✅ |
| pr-test-analyzer | sonnet | `opencode/deepseek-v4-flash-free` | good ✅ |
| type-design-analyzer | sonnet | `opencode/deepseek-v4-flash-free` | good ✅ |
| code-simplifier | sonnet | `opencode/deepseek-v4-flash-free` | good ✅ |
| database-reviewer | sonnet | `opencode/mimo-v2.5-free` | good ✅ |
| refactor-cleaner | sonnet | `opencode/deepseek-v4-flash-free` | good ✅ |
| performance-optimizer | sonnet | `opencode/mimo-v2.5-free` | good ✅ |

All 47 other sonnet agents and doc-updater (haiku) follow the same pattern.  
Opus agents (6): architect, chief-of-staff, gan-evaluator, gan-generator, gan-planner,  
healthcare-reviewer, planner — use `opencode/nemotron-3-ultra-free` as fallback but  
quality may drop on complex architectural reasoning.

## Free Model Fallback Chain

When OpenCode's bundled free models fail:

1. **OpenCode free** → `opencode/deepseek-v4-flash-free` (primary, most reliable)
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

## Execution Order Within This Skill

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
- **Undefined variable on unexpected model field**: If the `index_all_agents()` function (or equivalent) encounters a `model:` value that isn't `haiku`/`sonnet`/`opus`, the `tier` variable is never assigned — `NameError` at the next line. Always add an `else: tier = "unknown"` fallback.
- **Duplicate keys in mapping dicts**: When maintaining `SAFE_AGENTS` (or agent-name-to-free-model mappings), a copy-pasted duplicate key silently overwrites the first entry. After every edit, grep for duplicates: `grep -c '"agent-name"' scripts/ecc-runner.py`.
- **None-check before regex .group()**: When extracting frontmatter, a regex that doesn't match returns `None` — calling `.group(1)` raises `AttributeError`. Always guard frontmatter extraction with `if m is not None:` before accessing captured groups.

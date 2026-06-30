# Skill Enforcement Pattern — Making Rules Actually Actionable

## Problem

Skills often document rules as "ACTIVE — enforced" or "MANDATORY" but the agent never follows them. This happens because:

1. **Rules are buried** below routing tables, philosophy, and background context.
2. **No self-check** exists — the agent reads the rules, then moves on to execution without verifying.
3. **Aspirational text looks like enforcement** — "before ANY read_file() call, you MUST run the probe chain" looks like enforcement but has no consequence when skipped.
4. **No visibility into failure** — if the agent skips the probe, nothing bad happens, no one notices, so it becomes the default behavior.

This pattern fixes all four problems.

## The Enforcement Architecture

### 1. Rules FIRST — Before Everything Else

Place enforcement rules as the FIRST content after the frontmatter, before routing tables, selection rules, philosophy, or any background material.

```markdown
---
name: example-skill
---
# ENFORCED RULES (Execute in this order for EVERY request)

## 🔴 Rule 1: [concrete action]
Step-by-step commands. Include the actual tool calls.

## 🔴 Rule 2: [another concrete action]
...
```

**Why this works:** When the skill is loaded via `skill_view()`, the first thing the agent reads IS the enforcement rules. Routing tables come after — once the rules are already internalized.

**Caveat:** The decide skill itself is special because it runs at session start and contains routing. But even there, the enforcement rules are the first paragraph after the frontmatter, before routing tables.

### 2. 🔴 MUST / 🟡 SHOULD Separation

Use distinct visual markers:

| Marker | Meaning | Consequence of Skipping |
|--------|---------|------------------------|
| 🔴 **Rule N** | Must follow. No exceptions (except documented ones). | Token waste, bad output, user notices. |
| 🟡 **Guideline N** | Should follow when applicable. Use judgment. | No immediate consequence, but best practice. |

**Don't mix them.** If a rule says "enforced" but 50% of the time the agent skips it, it's not enforced — demote it to 🟡 or fix the rule to be actually followable.

### 3. Self-Audit Checklist (Run Before Finishing)

Add a checklist at the end of the skill — the agent MUST run it before the final response:

```markdown
## 🔍 Self-Audit (Run Before Finishing)

- [ ] Did I probe CodeGraph before read_file() on any code project?
- [ ] Did I route video to OpenMontage (if applicable)?
- [ ] Is the tier classification honored (Obsidian/KG skipped if Tier 1-2)?
- [ ] Did I use the right tool for the task (not ad-hoc scripts)?
```

**Why this works:** The agent can't claim it "forgot" — the checklist is a conscious verification step. An unchecked box forces a fix before delivery.

**Placement:** Put the self-audit near the end of the skill's execution order section, so it's the last thing the agent reads before acting.

### 4. Honesty Note (Optional but Recommended)

If the skill previously claimed "enforcement" that wasn't followed, add a note at the very top:

```markdown
> **⚠️ HONESTY NOTE:** Previous versions documented "ACTIVE enforcement"
> that was never actually followed. This version is restructured so the
> critical rules are literally the first thing you read.
```

**Why this works:** It builds trust and prevents the agent from repeating the old behavior pattern. The admission that past enforcement was aspirational creates cognitive friction when the agent would otherwise skip the rules.

### 5. Concrete Commands, Not Descriptions

Each rule must contain the EXACT commands the agent should run, not a description of them:

```markdown
### ❌ Bad — description only:
Probe CodeGraph before reading files. It saves tokens.

### ✅ Good — concrete command:
### Step A — Probe CodeGraph
\`\`\`bash
cd ~/Documents/Projects && codegraph query "<symbol>"
\`\`\`
```

The agent will copy-paste the commands. If the command isn't in the skill, the agent won't run it.

### 6. Document Exceptions Explicitly

If a rule has exceptions, document them in the rule itself:

```markdown
**Exception:** System files, temp files, config files under ~/AppData/ or
~/.hermes/ — these are not code projects, skip the probe.
```

Without explicit exceptions, the agent will either:
- Skip the rule entirely (because it's "too rigid")
- Follow it blindly (probing system files unnecessarily)

## Application to the decide Skill (June 23, 2026)

The decide skill was rewritten using this pattern:

| Pattern Element | Before | After |
|----------------|--------|-------|
| Rule placement | Line 154 (after routing tables) | First content after frontmatter |
| 🔴/🟡 separation | Mixed "enforced" and aspirational text | Clear RULES vs GUIDELINES sections |
| Self-audit | None | G2: Self-Audit checklist |
| Honesty note | None | ⚠️ HONESTY NOTE at top |
| Concrete commands | Described in text | `\`\`\`bash` blocks with exact commands |
| Exceptions | Implicit | Explicit: system files skip probe |

## Checklist for Auditing Any Skill

When you suspect a skill has aspirational enforcement, check:

- [ ] Are the enforcement rules the FIRST content after the frontmatter?
- [ ] Is there a clear 🔴 MUST / 🟡 SHOULD separation?
- [ ] Does each rule have concrete, copy-pasteable commands?
- [ ] Are exceptions explicitly documented?
- [ ] Is there a self-audit checklist that runs before finishing?
- [ ] Is there an honesty note if this was previously aspirational?

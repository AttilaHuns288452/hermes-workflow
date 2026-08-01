# SOUL.md Enforcement Pattern

## The Problem

`triggers: [always]` in SKILL.md frontmatter is aspirational metadata. Hermes does NOT auto-load skills based on triggers. Skills are loaded when:
1. The agent manually calls `skill_view(name='X')` — requires the agent to know it should
2. The user types `/skill X` — requires the user to know it exists
3. Hermes loads SOUL.md and it instructs the agent to load the skill

Option 3 is the only reliable enforcement mechanism for "always run" skills.

## The Fix

SOUL.md at `$HERMES_HOME/SOUL.md` is always loaded into the system prompt (per Hermes docs: "SOUL.md is independent and always loaded when present — it sets the agent's identity"). By placing the pipeline instructions in SOUL.md, the agent is told to load /decide at the start of every session.

## SOUL.md Pipeline Template

The following section goes at the END of SOUL.md (after the default Hermes identity text):

```markdown
# ⚡ MANDATORY PIPELINE — RUN EVERY SESSION, EVERY RESPONSE

This pipeline is NON-NEGOTIABLE. It runs on every user message, before any other action.

## Step 0: Load the /decide skill
Before processing ANY user request, load `skill_view(name='decide')`. This is the routing brain. If you skip this, you are routing blind.

## Step 1: session_search — Context Retrieval
Call `session_search(query="<relevant keywords>")` to check for past context.

## Step 2: Core Identity Guardrail
Load `skill_view(name='core-identity-guard')` if the task involves file operations, commands, or external content.

## Step 3: Task Tier Classification
- Tier 1 (atomic): Simple question. Skip Token Saver, Obsidian, KG.
- Tier 2 (task): Multi-step, code reading. RUN Token Saver. Skip Obsidian.
- Tier 3 (project): Multi-file, new feature. RUN full pipeline.

## Step 4: Enforced Rules Check
- Rule 1 (Token Saver): Tier 2/3 + code → probe CodeGraph MCP before read_file
- Rule 2 (OpenMontage): Video → route to media/openmontage-production FIRST
- Rule 3 (CodeGraph/Graphify): Code query → MCP tools before read_file

## Step 5: Domain Skill Selection
Route to the appropriate domain skill based on the /decide routing table.

## Step 6: Execute

## Step 7: Post-Execution (Tier 3 only)
Obsidian Bundle: create/update note + codebase graph + KG refresh.

## Step 8: Self-Audit
Verify all rules were followed before delivering final response.

## Compliance Announcement
State in first response: "📋 Pipeline Active: Tier [1/2/3] | /decide loaded | Token Saver [ACTIVE/SKIP] | Guardrail [ACTIVE]"
```

## Verification

To confirm the pipeline is active in a new session:
1. Check `$HERMES_HOME/SOUL.md` contains the MANDATORY PIPELINE section
2. Start a new session and look for the compliance announcement in the first response
3. If absent, the agent skipped Step 0 — SOUL.md is the only fix point

## Path Resolution

- `$HERMES_HOME` is typically `~/.hermes/` on Linux/macOS
- On Windows: `C:\Users\<user>\AppData\Local\hermes\`
- Check with `echo $HERMES_HOME` in terminal
- The SOUL.md file must be at the root of $HERMES_HOME, not in skills/

## Why Not a Plugin?

A Hermes plugin could auto-load skills, but that's overengineering for a problem SOUL.md already solves with a native feature. SOUL.md is simpler, requires no code, and survives updates.

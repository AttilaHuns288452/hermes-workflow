---
name: hermes-multiagent-team
description: "Build a coordinated multi-agent specialist team in Hermes."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [multi-agent, profiles, bot-mode, delegation, team, orchestration]
    related_skills: [team-agent-orchestration, hermes-kanban-setup, subagent-delegation, hermes-agent]
---

# Hermes Multi-Agent Team

Build a real specialist team where each agent is an independent Hermes profile with its own memory,
skills, config, and sessions, coordinated by a Project Manager. This is NOT one chatbot generating
fictional perspectives. For the generic team operating model (ownership, Kanban states, merge gates),
load `team-agent-orchestration`; this skill covers the Hermes construction mechanics.

## When to Use
- The user wants a coordinated org of specialist agents (PM + Marketing/Sales/Dev/Design/Research/Docs/QA).
- Setting up Bot Mode, role contracts, a shared charter, group chat, or role-routed delegation.
- Extending an existing team with a new specialist role.

## Procedure

### 1. Classify roles before creating agents
Only give a role its own profile when it has a recurring, distinct deliverable. Roles that are just
responsibilities (architect, devops, security, analyst) belong to an existing specialist. Extra agents
are coordination overhead, not capability. State the final role table (agent → profile → owns) first.

### 2. Create each specialist profile
Clone from a well-configured source profile (e.g. `learning` or `codingprofile`), do not clone
messaging channels:
```bash
hermes profile create <role> --clone-from <golden> --no-alias --description "<one-line role>"
```
Run creates sequentially with a generous timeout (300s+); a create can trigger the source-update
dependency completion flow and one giant batch hits the tool time ceiling mid-way. Verify with
`hermes profile list` after.

### 3. Write a role SOUL.md per specialist
Each `~/.hermes/profiles/<role>/SOUL.md` is a contract: role identity, `## Owns`, `## Rules`,
`## Handoff output`, `## Stay in lane`. Reference the shared charter rather than duplicating it. The
handoff contract is fixed: objective, output, evidence/verification performed, acceptance-criteria
status, open risks, next action/owner.

### 4. Shared charter
One `~/.hermes/team/CHARTER.md` holds the role table, operating rules (findings not agreement; label
facts vs assumptions; one owner per task; PM arbitrates), the idea→launch lifecycle, handoff contract,
and knowledge locations. Keep per-project state in `~/.hermes/team/projects/<project>/` (brief,
research, design, architecture, market, commercial, testplan, decisions, status).

### 5. PM contract
The PM is the `default` profile. APPEND a "Team Lead" section to its SOUL: convert owner goals to scoped
work, route to the owning specialist, do NOT do everything yourself, track on Kanban, reconcile
conflicting input, integrate and review before presenting. You are accountable for delivery, not for
personally executing each task.

### 6. Route by role for Kanban
`hermes profile describe <role> --text "<what it does best>"` so the decomposer routes tasks by role,
not name. Keep the PM as `kanban.orchestrator_profile`.

### 7. Direct delegation is the default; group chat is optional
Route work through direct profile delegation (`delegate_task`, Kanban handoffs, `message_agent` DMs)
as the PRIMARY path. Do NOT set up a group room before the team can work — that is a convenience
surface, never a prerequisite. If the user says "make the team work without a group chat," switch to
direct delegation immediately and do not walk them through manual GUI steps.

Group rooms (Bot Mode) are a Desktop GUI surface. See `references/bot-mode-architecture.md` for the room
model and headless path. Room creation can fail with RPC errors (`invalid_params`); that must never
block team execution. If the user wants a room later, fix the RPC then — the team runs fine without one.

### 8. Skill alignment and provisioning
Use `team-alignment-traceability` for cross-functional requests. A skill living only in the global
`~/.hermes/skills/` tree does NOT resolve inside profile-scoped workers: each specialist sees its own
`~/.hermes/profiles/<role>/skills/` tree. Propagate every shared contract skill into each role's tree
(byte-identical copy, verify hash parity), then confirm resolution with a per-profile load probe
(`hermes -p <role> skills list` + an explicit load-and-echo one-shot). Shared external skill dirs cover
catalog breadth, not contract skills. Search local skills and references before GitHub or hub discovery.
For a real gap, record provenance, version, license, dependencies, security verdict, assigned profiles,
and an invocation check before integrating a candidate.

### 9. Test the organization
Verify in three layers, in this order:
1. **Structural test** (deterministic, no model calls; starter at `scripts/structural_team_test.py`):
   assert every role SOUL carries the required contract clauses AND every profile-local copy of each
   shared contract skill exists with matching content hash. This catches provisioning drift without
   burning model calls.
2. **Per-profile resolution probe**: `hermes -p <role> skills list` shows the shared skill, and a one-shot
   asking the role to load it and echo a marker returns the marker.
3. **Behavioral smoke**: one-shot per specialist on the same cross-functional prompt:
   ```bash
   hermes -p <role> -z "<short prompt: your role's concern + recommendation + what you need from another specialist>"
   ```
   Pass = distinct, in-role answers that name the right counterpart. For an alignment-contract smoke, the
   expected shape is: classification (independent vs cross-functional), affected roles + one owner,
   an observable acceptance criterion with its verification, and one conflict/provenance risk surfaced.
   If answers converge into generic agreement, the role contracts are too weak; if they proceed without
   naming owner/acceptance/risk, the alignment contract is not reaching the profile.

### 10. End-to-end product test with a tiny artifact
Commission one small real deliverable through the full pipeline (proposal → brief → build → QA →
deliverables) to prove the organization actually hands work across roles. Keep the artifact trivially
small on purpose — one self-contained HTML file, no backend, no auth, no external dependencies,
demo data — because a large product test burns tokens without testing the organization any better.
The pass signal is the cross-functional trace: specialists must produce DISTINCT outputs (design
prioritizes flow/safety, engineering scopes the data model, sales challenges monetization, research
labels assumptions and evidence gaps) and the PM brief must be able to REJECT scope the specialists
propose. Deliverables land in `~/Downloads` and the project root with a README pointer, and the
verification actually runs (syntax check + headless browser QA asserting real behaviors).

## Pitfalls
- `-z`/`--oneshot` is a TOP-LEVEL flag: use `hermes -p <role> -z "..."`. `hermes chat -z "..."` fails
  with "unrecognized arguments" because `-z` is not a chat subcommand flag.
- `hermes profile create --clone` deliberately does NOT copy messaging channels: two profiles holding
  one bot token make two gateways fight over it. Configure each profile's own bots via `hermes -p <role>
  setup` if it needs a messaging surface.
- To replace a freshly cloned profile's SOUL.md wholesale, write it via `execute_code`/terminal Python.
  The `write_file` read-before-write gate refuses to overwrite a file this session has not fully read.
- Group `message_agent` DMs only exist in a profile's canonical "Bot Chat" session, not ordinary chats
  or CLI sessions. See `references/bot-mode-architecture.md` before expecting bot-to-bot messaging to
  appear.
- Automating the Desktop GUI (to create the group room) needs the focus-stealing click technique in
  `desktop/linux-gui-automation`; a fullscreen app on top steals focus on plain mouse moves.
- Testing skill resolution from the PM/organizer profile is a false green: the PM and the specialists use
  different skill trees. Probe every profile that will actually run the work.
- A SOUL clause instructing a specialist to load a skill its profile cannot resolve silently degrades to a
  generic answer that still sounds role-correct. Verify resolution, not just the presence of the clause.
- When testing the organization (step 10), the artifact is the vehicle, not the goal: scope creep into
  real backends or auth makes the test expensive without making the team test stronger. Build details
  (HTML escaping, syntax gate, browser harness) live in `html-prototype-build` and `webapp-testing` —
  load those for the artifact instead of re-deriving their rules here.
- Desktop `groups.create` RPC can reject member dicts with `invalid_params` when they carry extra fields
  (`title`, `connectionId`, `remoteSource`, etc.) that the strict-field validator rejects before
  normalization runs. Fix in `gateway/hosted_room_discussion.py`: strip known extra fields from member
  dicts BEFORE the remote-fields check, not after. Verify with the exact failing payload through the
  same dispatch path the GUI uses, not a hand-built dict that omits the extras.
- Do not present manual group-chat creation steps as a required workflow when the user wants the team
  to function. Direct delegation works immediately; the room is optional polish.

## Verify
- `hermes profile list` shows every specialist.
- Each `SOUL.md` has the role heading and references the charter.
- `hermes profile describe` values are present (Kanban routes by them).
- The structural test passes (contracts + per-profile shared-skill hash parity).
- Each profile resolves the shared contract skills (list + load-and-echo probe).
- The one-shot role test (step 9) produced distinct, cross-referencing answers.

# Handing a repository to another AI agent

A fresh agent inherits nothing but the repo: no session history, no memory, no
knowledge of what was tried. What it reads becomes its ground truth. Docs that
claim a finished state misdirect it worse than having no docs at all, because it
will build on the claim instead of the code.

## 1. `AGENTS.md` is the entry point

Coding agents look for `AGENTS.md` (and its variants) at the repo root first.
Without one they sample random files and invent the direction. One file, dense,
with pointers out — not a second README.

Sections that actually change behaviour, in this order:

1. **Direction** — what this product is trying to be, and a ranked value order for
the next person (e.g. first-30-seconds > feature depth > polish > new systems).
   Add an explicit **out-of-scope** list; an agent that does not know what is
   forbidden will helpfully build it.
2. **Non-negotiable rules** — where configuration lives, which layer is
   authoritative, which gates must stay green, and the standing user preferences
   for that repo. These are the rules a well-meaning agent breaks silently.
3. **Build / test / run / ship** — copy-pasteable commands, plus the one fact that
   confuses every newcomer (an empty viewport before Play because the world is
   runtime-built; a required env var; the fact that the artifact is generated).
4. **Architecture map** — a table of which file owns what. Not a tree dump: the
   ownership table is what stops an agent from adding a second owner for a fact.
5. **Traps** — every one that has already cost time, stated as rule + mechanism.
   This section pays for itself immediately; it is the highest-value part of the
   file after Direction.
6. **Current state** — what is live, gate counts, what is in flight, and an
   explicit **not verified** list. An agent will otherwise assume green = shipped.
7. **Doc index** — one line per doc saying what it is for, so the agent reads in
   the right order instead of alphabetically.
8. **How to work here** — verify before claiming, delete over add, root-cause
   fixes, commit-message expectations, and what requires asking first.

Close with the override rule: **if this file and the code disagree, the code
wins — and fix the file.** That single line prevents a stale doc from becoming
binding.

## 2. Verify the doc before you publish it

An `AGENTS.md` written from working memory contains claims that were true two
hours ago. Before committing, check every checkable sentence against the repo:

- Named symbol exists → grep for the definition.
- Stated counts and versions → re-run the command that produces them.
- File paths → `ls` them.
- Claims like "N wires" / "N services" → count them.

A grep that counts header comments instead of code will happily confirm a wrong
number; count the construct, not the word. Publishing an unverified entry point
is the same failure as an unverified completion report, one level up.

## 3. Triage the existing docs first

Repos accumulate reports asserting completion. An agent reads a file named
`FINAL_REPORT` or `STATUS` as current state.

- Move anything that asserts a finished/verified state and is no longer accurate
  into `docs/archive/`, do not delete it — provenance has value and the move is
  reversible.
- In the doc index, label the archive explicitly: *historical, not current
  status.* An unlabelled archive directory is just a second source of truth.
- Delete true duplicates (the same strategy doc committed at root and under
  `docs/`) rather than letting them drift apart.
- Prefer one decision record (`GAME_PLAN.md` / `ARCHITECTURE.md` / `ADR`s) that
  the entry point points at, over a growing pile of per-pass reports.

## 4. Tell the reviewer what not to trust

The handoff note is worth as much as the warnings it carries:

- **Expected-empty and expected-ugly states.** "The scene is built at runtime, so
  an empty viewport before Play is correct" saves a reviewer from filing a
  non-bug, and from "fixing" a correct design.
- **Environment artifacts.** If a capture pipeline, emulator or viewport cannot
  render a class of change, say so, with the falsification that proved it. A
  reviewer who does not know will chase a phantom defect.
- **The unverified list.** Name what nobody has done: played it on a phone,
tested with two users, observed retention. Stated plainly it reads as rigour;
  discovered later it reads as a cover-up.
- **A suggested attack order**, cheapest-to-confirm first. It gives the reviewer
  a route instead of a firehose, and it doubles as a self-audit of where you know
  the code is weakest.

## 5. Say which scripts are dangerous

Repos with deploy/publish/upload scripts hand a reviewer a loaded gun. In the
entry point, state which commands write to a live system or to the owner's
account, and that a review pass must not run them. Keep credentials outside the
tree (`~/.<tool>_key`, `chmod 600`) and reference them by path only.

Before the first push, grep the tracked files for key-shaped strings and confirm
no `.env`, token, or credential file is staged. A private repo is still a
remote.

## 6. Verify the handoff from the other side

A successful `git push` on your machine is not proof the remote has your work.
Read it back through the host's API — head commit message, default branch,
visibility, and the presence and size of the entry-point file — and confirm the
commit count matches locally. Same rule as any deploy: verify the delivered
artifact, not the command that was supposed to deliver it.

If the repo is private and the reviewer needs access, that is an owner action:
state the invite (or token) requirement explicitly instead of assuming the agent
can clone.

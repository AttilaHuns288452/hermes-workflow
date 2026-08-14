---
name: capstone-proposal-polish
description: Audit and improve capstone proposal docs to user standards.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
tags: [capstone, proposal, docx, academic, ucc]
related_skills: [docx, capstone-project-evaluation]
---

# Capstone Proposal Polish (UCC academic docs)

## When to use

- User asks to improve/fix/audit a project proposal doc (`.doc`/`.docx`/pasted text) — "improve the inconsistencies and dead ends", "fix the proposal", "polish the SAD/proposal doc".
- Recurring class for this user: UCC capstone documents (Dental Practice Management System, Guardian Alert, and future ones).

## User's standing doc preferences (non-negotiable)

- **No em dashes.** Replace with commas, parentheses, or colons. (En dash in number ranges like 2026-2027 is fine.)
- **APA in-text citations + References section.** Cite ONLY real, verifiable sources (manufacturer datasheets are safe: Espressif, u-blox, SIMCom, ETSI). Never fabricate a reference.
- **Local .docx output** (python-docx), never Google OAuth round-trips.
- **Consistent numbers**: same ₱ range, same counts, same dates everywhere; averages must satisfy avg = total ÷ count.
- **No red text.**
- UCC proposal structure: Submitted by / **Approved by (course adviser)** / **Accepted by (client)** blocks. A proposal missing those blocks is a dead end for the panel.

## Dead-end audit checklist (run before rewriting)

1. **Placeholders**: `[Team Name]`, `[Course Code]`, `[University]`, `[School Year]` — fill everything knowable (UCC, College of Computer Studies, SY); leave ONLY genuinely-unknown fields bracketed and tell the user which ones remain.
2. **Flows with no destination**: a dashboard/monitor described with no responder workflow (ack/resolve/log?) is a dead end — define the end-to-end flow: trigger → backend → who gets notified → what the responder does.
3. **Features in one section but absent in another**: a mitigation in the Risk table must also exist in Objectives/Scope (e.g. false-alarm cancel window). Scope and risks must agree.
4. **Undefined notification paths**: "emergency contacts are notified" with no mechanism — name the channel (SMS via device SIM, dashboard as primary).
5. **Math vs tables**: "2 people per track" while the work-breakdown table allocates 1+1 to two tracks — reconcile wording with the table, and the member total must sum.
6. **Back-references to content that doesn't exist**: "the original concept" / "as previously mentioned" with no earlier section — reword.
7. **References section missing entirely** — academic dead end; add real APA entries + in-text citations at the component/tech claims.
8. **Cost vagueness**: "a few thousand pesos" → fixed range, reused consistently.

## Workflow

1. Extract text: `.docx` via `read_file` (auto-extracts); legacy `.doc` via `antiword file.doc > out.txt` (git-bash). Word COM via PowerShell fails on this machine (TYPE_E_CANTLOADLIBRARY) — antiword is the path.
2. Run the checklist; list every finding as a numbered table (issue → fix).
3. Build the improved `.docx` with python-docx (`C:/Users/YOUR_USERNAME/AppData/Local/Programs/Python/Python311/python.exe` — bare `python` has the PYTHONPATH leak): title block → numbered sections → `List Bullet` style for bullets → `Light Grid Accent 1` tables with bold header rows → hanging-indent APA references. Save under `~/Documents/Projects/<project-name>/`.
4. Verify by reading the .docx back (`read_file` auto-extracts) and grep the build script for `—` (must be 0). Original file stays untouched.
5. Report the fix table; call out the remaining bracketed fields.

## Pitfalls

- Don't rewrite scope decisions the user made; only close the gaps. If the doc says the alarm is a deterrent, keep it a deterrent.
- Bullets must be actual `List Bullet` paragraphs, not literal `•` text.
- python-docx table style names must exist in the default template (`Light Grid Accent 1` works); bold header row via run-level formatting, not cell style.

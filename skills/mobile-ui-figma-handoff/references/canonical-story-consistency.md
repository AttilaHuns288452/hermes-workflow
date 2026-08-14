# Canonical Story Consistency (multi-frame decks)

When a deck passes geometry/deep QA but still "feels whack", the cause is story drift — frames
built across many turns contradict each other. A 4-agent audit council found 28 story, 21 flow,
and 25 copy inconsistencies in a 67-frame deck that had passed every geometry check.

## 1. One canonical story in DESIGN.md

Define once, audit everything against it:

- **Today's date** (all "today/tomorrow/week ahead" copy derives from it)
- **Personas — one per flow, never shared:** active staff dentist ≠ pending registrant ≠ invited
  dentist. Split them: e.g. Ramos = active staff (permissions/settings/staff-view frames),
  Castro = self-registered pending (register→pending→login-blocked→queue→reject→activated),
  Lim = invited (invite→invite-sent→queue's "awaiting registration" row).
- **The anchor patient's complete history** with dates + amounts (every visit list, receipt,
  notification, and ledger row must be a subset of it).
- **Today's schedule** — identical rows across dashboard, calendar week, calendar day, and
  staff-view frames. Same counts on every KPI strip (appointments/pending/income today).
- **All money arithmetic:** avg = total ÷ transactions (₱86,400 ÷ 62 = ₱1,394, not ₱1,450).
  Same value in the KPI card, the report row, and any text mentioning it.
- **Care attribution:** clinical notes, chat, and receipts signed by the STAFF dentist who
  treats, not always the owner.
- **Temporal logic:** a "mark completed + amount paid" dialog must complete TODAY's visit;
  the receipt it generates is for that same visit. No completing future appointments.

## 2. Sweep, don't spot-fix

When one value changes, `grep` the generator for the old name/amount/date and patch every
occurrence in the same pass. Verify with story checks in `scripts/audit.py`:
`(label, needle, [file-prefixes])` asserting each canonical fact appears in its frames.

## 3. Negative checks — the regression guard

Add to `scripts/audit.py` a `negatives` dict of words that must appear in NO frame:

```python
negatives = {"GCash": [], "Maya": [], "Outstanding": [], "preferred": [], "slot online": []}
for fn in frames_dir_html_files:
    txt = open(fn, encoding="utf-8").read()
    for word in negatives:
        if word in txt: negatives[word].append(basename(fn))
# exit 1 with the offender list if any key has files
```

Rules learned the hard way:

- When a feature is removed (payment methods, outstanding balances, patient-picked time slots),
  an old POSITIVE check will fail. The correct response is to INVERT it (assert absence
  everywhere), not delete it. Deleting the check is how the next edit quietly reintroduces
  the old concept.
- Beware legitimate uses of the banned word: "time slots" is correct on the DENTIST calendar
  (clinic blocks), banned on PATIENT booking screens. Scope negative checks to the frames
  where the concept was removed, or pick wording that can't legitimately appear ("slot online",
  "GCash", "Outstanding").

## 4. Deck order = user journey, not build order

Frames accumulate in feature-build order (happy path, then edges, then new modules at the
tail) — registration ends up at frame 39, after the patient has had two visits. Reorder the
FRAMES list into sections before delivery:

A) auth + registration lifecycle (welcome → both logins → login errors → role select →
   patient register → dentist register → pending → blocked states → activated)
B) patient happy path → C) patient edges
D) dentist/owner by module (Home → Calendar → Requests → Patients → Income → Staff)
E) dentist edges → F) notifications + settings

A defense panel reads top-to-bottom; the order must tell the product story.

## 5. Collapsed-render probe (stray-closer detector)

Symptom: qa_deep reports a huge void (>300px) on a frame whose source looks complete, or a
Playwright probe shows `.nav` offsetTop ≈ 844 (nav below the fold) and bodyH ~300.

Cause: a patch/revert left one extra `</div>` (or dropped one). The browser auto-closes,
reparenting the rest of the content OUTSIDE `.body`.

Diagnose by depth-walking the generated frame's body (not the source — the generator output
is truth):

```python
import re
html = open(frames_path, encoding="utf-8").read()
body = html.split('<div class="body">')[1].split('<div class="nav">')[0]
depth = 0
for m in re.finditer(r'<div\b|</div>', body):
    depth += 1 if m.group() == '<div' else -1
    if depth < 0:
        print("stray closer near:", body[max(0, m.start()-120):m.start()+20])
        break
```

Also valid: `opens = len(re.findall(r'<div\b', body)); closes = len(re.findall(r'</div>', body))`
— a simple 2-count imbalance first, the depth walk to locate it.

Fix the source (usually one line), regen, re-run the full QA ladder. Do NOT keep patching on
top of an unverified generation after multi-hunk patches — each patch batch ends with
generate + lint + qa_deep before the next batch.

## 6. Council audit dispatch (deck-level consistency)

For "there are many inconsistencies — start a council": fan out 4 leaf auditors in ONE batch
(≤500 words each, terse `FRAME NN: issue → fix` lines, no code, read the frames dir):

1. STORY: cross-frame names/IDs/dates/amounts/statuses/counts vs the canonical story
2. FLOW: dead ends, wrong active tabs, role-tab errors, leftover outdated UI
3. COPY: module naming, banners, jargon, duplicated explainers, header title style
4. ORDERING: the A–F ordered filename list

The consolidated delivery may arrive truncated or get dropped — read the full summaries from
`~/AppData/Local/hermes/cache/delegation/subagent-summary-N-<ts>.txt` and the live transcripts
`.../live/<deleg_id>/task-N.log`. Apply every finding + the reorder + negative checks, then
run the QA ladder to zero.

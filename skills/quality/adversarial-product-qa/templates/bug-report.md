# [BUG-NNN] Short title

**Role:** Patient / Doctor / Owner (or actor name)
**Screen:**
**Severity:** P0 / P1 / P2 / P3
**Precondition:**
**Steps to reproduce:**
1. ...
2. ...

**Expected:**
...

**Actual:**
...

**Design/reference expectation:**
...

**Database/backend behavior:**
...

**Cross-role impact:**
...

**Likely root cause:**
...

**Recommended fix:**
...

---

# Final System Matrix

| Area | Role A | Role B | Owner | Backend | Design | QA Result | Severity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Authentication | | | | | | | |
| Profile | | | | | | | |
| Core entity CRUD | | | | | | | |
| Primary workflow | | | | | | | |
| Money/payments | | | | | | | |
| Analytics | | | | | | | |
| Navigation | | | | | | | |
| Authorization | | | | | | | |

# Final Acceptance Gate

Per role:
- [ ] Authentication works
- [ ] Authorization works
- [ ] Core workflows work end to end
- [ ] Data persists across refresh and re-login
- [ ] Invalid/unauthorized actions are prevented

Cross-role:
- [ ] Every actor→observer sync direction verified live

Backend:
- [ ] Relationships correct
- [ ] RLS correct (UI hiding is not security)
- [ ] Authorization enforced server-side
- [ ] No fake persistence / no orphan rows / no duplicate mutations

UI:
- [ ] Design faithfully replicated
- [ ] Navigation, forms, states match
- [ ] Responsive behavior works

# Severities

- **P0** — security, data corruption, impossible workflow, major role bypass,
  broken core workflow
- **P1** — major feature broken, major cross-role inconsistency, important
  design functionality missing
- **P2** — meaningful UX/data issue that doesn't completely block the workflow
- **P3** — minor visual, copy, spacing, or polish issue

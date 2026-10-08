# Adversarial Test Checklist + Bug Report Format

Attack at the API with throwaway accounts (created via admin API, deleted after), one account per victim role. UI hiding is never the boundary — every UI affordance gets a direct PostgREST probe.

## Trust-boundary checklist

1. **Insert pinning (money/state forgery):** create a row with self-granted confirmed state, `payment_status='verified'`, `price = 0`, negative price, inflated price, price below a per-customer exception, and completed+paid (free history). All must be rejected; an honest insert must still succeed.
2. **Update abuse on owned rows:** price, identity fields, internal/clinical notes, status escalation to clinic-only states, resource timestamps. Only free-text + cancel-of-own-pending should pass.
3. **Cross-user reads:** Patient A → Patient B rows, attachments, internal notes (incl. column-level probes on one's OWN row — internal fields must not be readable by their subject when the product says confidential).
4. **Spoofed ownership/identity fields:** `sender='clinic'`, `user_id`, `patient_id`, `role`, `patient_code` on insert/update.
5. **Destructive powers:** self-delete of parent rows (orphans children), staff deletes/renames of core records — append-mostly unless the product explicitly requires it.
6. **Privilege escalation:** self-update of own `role`; owner-only writes attempted as patient/doctor.
7. **RPC abuse:** oversize/empty payloads, double-submit, cross-user invocation, replay after state change. Each must fail with a clear error and leave zero partial rows (check the child table).
8. **Races:** two parallel creates for the same natural key — exactly one may win; same resource (slot/seat) claimed by two payers — second payment must fail cleanly.
9. **State machine:** enumerate valid transitions from the product's model, then attempt every invalid one (reverse, repeat, skip-ahead, unauthorized actor per transition).
10. **Ledger math:** recompute displayed totals from raw rows independently (income = system-derived + manual − expenses) and compare; check date-bucket edge cases (null dates must not inflate the current period).
11. **Injection of content:** long strings (300+ chars), HTML/script payloads, special characters — stored safely, rendered escaped, no crash.

## Silent-failure probes (verify the RIGHT thing)

- Denied writes: assert rows-affected == 0, not `error == null`.
- Double-click submits: count resulting rows == 1.
- Mock/shortcut buttons must call the real endpoint so analytics/ledger probes stay meaningful.

## Bug report format

```
### [BUG-NNN] Short title
**Role:** Patient/Doctor/Owner  **Screen:**  **Severity:** P0/P1/P2/P3
**Precondition:**
**Steps to reproduce:** 1. …
**Expected:**   **Actual:**
**Reference expectation:** (design/flow source)
**Database behavior:** (policy/trigger/constraint involved)
**Cross-role impact:**
**Likely root cause:**   **Recommended fix:**
```

Classify: P0 security / data corruption / impossible workflow · P1 major feature or cross-role breakage · P2 meaningful UX/data issue · P3 polish. Keep testing around a found bug (never stop at first failure) and retest its downstream flows after fixing.

# Figma → Shipped App

Procedure for the phase where the user says "build it shippable based on our Figma/design PDF" — going from placeholder-only foundation to full working screens backed by real data.

## 1. Audit the design before coding

- Render the design PDF pages to images (`pdftoppm -png -r 110`) and vision-audit the key frames (dashboard, each role's home, list screens, detail screens, chat).
- Extract the concrete inventory: colors (accent hex), per-role tab lists, section order per screen, card anatomy (which fields in which order), pill/tag styling, button placement, empty states.
- Re-vision-audit the SCREENSHOTS of your build against the frames before shipping; the delta list is your fix list.

## 2. Implementation order

1. Auth (real Supabase): signup with role in `options.data`, a `profiles` table + `handle_new_user` trigger creating role-appropriate rows (patient record for patients, dentist rows for staff). Demo staff accounts for teammates. Turn OFF "Confirm email" in Auth settings for capstone testing.
2. Patient screens: booking (service picker with effective price, date, notes) → my appointments (status pills, cancel pending).
3. Staff screens: requests (approve with datetime assignment / decline / complete), calendar (Day/Week/Month seg control + hour grid with open slots), patient list → chat.
4. Chat: bubbles per role (patient left/clinic right), realtime subscription AND refetch-after-send (see SKILL.md pitfalls).
5. Owner Manage: clinic profile + hours editable (day chips + time inputs, persisted to a settings row), services CRUD, per-patient price exceptions (group-chat member picker: tap circle to toggle, inline price input).
6. Income: from completed appointments using the per-appointment price column (exceptions included), minus expenses.
7. Staff roster from the dentists table.

## 3. Data model notes

- `appointments.price` column locks the price AT BOOKING TIME so later catalog changes and per-patient exceptions don't rewrite history. Booking resolves effective price = service_prices exception ?? services.price.
- `clinic_settings` single-row table (id=1 CHECK) for name/hours/days.
- `service_prices (service_id, patient_id)` composite PK for exceptions.
- RLS: services public read; appointments insert-own (patient via patients.user_id) + staff update; chat insert-own-or-clinic; settings owner-only write. The `chat insert` policy needs the staff branch (profile role in doctor/owner) or clinic-side replies fail with a silent RLS error.

## 4. Seed data (`seed.mjs`, committed, idempotent)

- 5+ named patients with PH phone numbers; check existence before insert.
- Appointments in ALL statuses (approved today with times inside clinic hours, pending ×3, completed in the past for Income, one cancelled).
- 2 price exceptions on named patients.
- Chat threads both directions.
- Test-account cleanup: QA runs create junk patient rows — delete them via the staff-authed client (appointments/chat/prices first, then the patient), or the Patients list looks like a test dump.

## 5. QA suite (`qa_all.mjs`, committed)

- Playwright 390×844, collecting `pageerror` + console errors; exit non-zero on either.
- Sections per role: login → assert app bar, tab list (exact, incl. absence checks like "no Requests"), KPI cards, banner counts, approve flow (fill datetime → Confirm), calendar controls, chat open + send + visible bubble, Manage save, exception tag + input value, Income renders ₱, staff roster; patient register → book → appointments → chat → profile → logout.
- Check `input.value` via `evaluate`, not `textContent` (see SKILL.md pitfalls).
- Make navigation robust: navigate directly to routes in the suite rather than clicking tabs, so a stale click never fails the run for timing reasons.
- Run: build → (re)start preview → suite → fix → rebuild + restart + rerun until 0 failed / 0 page errors → commit → push → verify the production URL with a final Playwright pass.

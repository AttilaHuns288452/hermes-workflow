# Third-party payment provider: moving the account to the client

A working payment flow that runs on the DEVELOPER's provider account is not a deliverable. When a client takes the system, the merchant account, its KYC identity, and its settlement bank must be theirs. This is the handover recipe: what the client supplies, where each value lands, and what to verify before you call it wired.

## 0. Prove what the running integration actually uses, from its own data

Before telling the client which credentials to send, establish from EVIDENCE which provider features the deployed system touches. Otherwise you ask for a feature it never calls, or omit the one that keeps payments settling.

- **Which webhook events are live:** group the event-ledger table (`provider_events` or equivalent) by `event_type` with `count(*)` and `min/max(processed_at)`. The handler is the only writer of that table and it only writes after a signature check, so hundreds of `payment.paid` rows prove a webhook is registered on the CURRENT account and firing. That is the answer to "do we even need a webhook?", not an opinion or a reading of the docs.
- **Webhook vs client polling:** read the payment screen's poll interval and its guard. A 5-second poll that runs only while the QR page is open settles nothing once the patient closes the tab — the payment stays `pending` until someone reopens it. State this mechanism when asked why the webhook matters; "polling seems to work in demos" is exactly the case where the missing webhook shows up later as an unconfirmed payment.
- **Dynamic QR and in-store static QR are different products.** If the create function rejects the static style (e.g. returns 503 for `qr_style=instore`), the app mints a per-payment dynamic QR through the API; a dashboard standee QR then only serves walk-in counter payments. Do not ask the client to create a standee "to connect the app", and never ship the provider's template standee image — placeholder merchant text ("Aa") in a clinic's public assets is a visible tell.
- **Which of the returned values the code reads:** grep for the public key before requesting it. A stored-but-unread `*_public_key` row changes nothing; asking for it sends the client hunting for a value that has no effect.

## 1. Decide who owns the account before anything else

**The client registers the provider account themselves, in their own name, email, mobile, and government ID.** Say this explicitly and early. If the developer signs up:

- settlements land in the developer's bank account (clinic revenue in a personal account),
- the BIR/tax trail names the wrong person,
- the client can never retrieve the account (the KYC identity is what support asks for).

The deliverable is a short handover document the client can act on unaided: documents to prepare, the signup fields that will be asked, the keys to copy back, and the exact webhook URL + event list. Write it as a standalone file, put it in the repo's `docs/` AND in `~/Downloads` so it can be sent without hunting.

## 2. What to request from the client

Three groups. Ask for all three at once; the account cannot be activated without the first two.

**Identity (KYC)** — 1 primary ID OR 2 secondary IDs:
- Primary: Driver's License, UMID, SSS ID, PRC ID, Philippine Passport, PhilSys/ePhilID
- Secondary: NBI Clearance, Police Clearance, PhilHealth ID, TIN ID, Pag-IBIG ID, Postal ID, Voter's ID, Barangay Clearance

**Business profile** — collected during signup, cannot be skipped, blocks activation:
- Legal/trade name (must match the registration certificate), business description, industry, business size, operating history
- Business address + customer-facing contact channel
- TIN and tax classification
- Estimated monthly volume
- Price range: lowest and highest price for a single service (read it off the product's own catalog rather than inventing a number)
- **A working public website** — required for activation. The deployed app URL qualifies.

**Business documents** — needed to upgrade from Individual to a registered entity. Entity type changes the list:

| Entity | Documents |
|---|---|
| Individual | none (KYC only) |
| Sole proprietor | DTI Certificate of Business Name, BIR Form 2303, owner's government ID |
| Partnership | SEC Certificate of Partnership, Articles of Partnership, partner's resolution, a partner's ID, BIR 2303 |
| Corporation | SEC Certificate of Incorporation, Articles + By-Laws, latest GIS, beneficial-ownership declaration, authorized rep's ID, BIR 2303, notarized Secretary's Certificate |
| One Person Corporation | SEC Certificate, Articles + By-Laws, Form of Appointment of Officers, beneficial-ownership declaration, BIR 2303, owner's ID, notarized Secretary's Certificate |

Plus the payout bank account: bank name, account name, account number.

**Every account starts as Individual and must upgrade within 30 days of activation or the provider disables it.** State the deadline in the handover doc — it is the single most common way a small-merchant integration silently dies a month after launch.

## 3. What comes back, and where it goes

Offer the client two ways to hand over access, in this order:

1. **Preferred — invite you as a team member** (`Settings → Team Members → Add team member`, role Admin). You set everything up yourself and the client can revoke it whenever. No secret keys pasted into chat, no copy-paste errors, no keys in a message thread.
2. **Fallback — they copy the two required values out of the dashboard** (`Developers → API Keys`, `Developers → Webhooks`).

| From the provider dashboard | Format | Destination |
|---|---|---|
| Secret key | `sk_live_...` | provider-config table, `*_secret_key` row |
| Public key | `pk_live_...` | provider-config table, `*_public_key` row (often only stored for reference — grep the codebase before claiming it is used) |
| Webhook signing secret | `whsk_...` | provider-config table, `*_webhook_secret` row |
| Mode flag | `live` / `test` / `mock` | provider-config table, `provider_mode` row |

A DB-first resolver (read the config table with the service key, fall back to `Deno.env`) means rotating to the client's keys needs **no code change and no redeploy** — confirm that is how the deployed functions actually read them before promising it.

Webhook setup to hand over:
- URL is the deployed edge-function endpoint. Public HTTPS with a real domain; IP literals are rejected.
- Subscribe the exact events the handler branches on — grep the webhook function for the string comparisons (`payment.paid`, `payment.failed`, `payment.expired`/`qrph.expired`) instead of guessing the list.
- Acknowledgement contract: return HTTP 200-209 with a JSON body. Deliveries retry up to 12 times, and **3 consecutive events that exhaust their retries auto-disable the webhook** — after handover, a silently disabled webhook looks exactly like an app that stopped confirming payments.

QR Ph (and most default methods) activate automatically with the account; other methods need self-service activation in the dashboard.

## 4. Sequence that avoids blocking

1. Client signs up → **test keys are usable immediately**, before activation and before the documents clear review.
2. Wire the app with the test keys and prove the full flow end to end (create → provider settle → webhook → paid) in `test` mode while KYB is under review.
3. Documents approved → client copies the live keys and the webhook secret back.
4. Set the three secrets + `provider_mode = test`, run one real end-to-end pass, then flip to `live` and run a minimum-value real charge (a ₱1 payment is the cheapest possible proof that keys, webhook, and mode all agree).
5. Refund/reverse the smoke charge and confirm the ledger shows it.

## 5. Before you hand over the system

- **The developer's own live keys must not remain in the production database.** Set `provider_mode = mock` (safe fail-closed default) or overwrite all three rows with the client's values, then rotate the developer's live secret in their own dashboard. Leaving them there means the client's bookings charge the developer's account.
- Grep the payment description/metadata string for the developer's placeholder project name (`<DEV-PROJECT> <reference>`) and change it to the client's registered business name so the cardholder statement matches the DTI name.
- Confirm the mode is explicit, not inferred: a provider integration that treats "keys present" as "live" will move real money the first time someone pastes a key into a demo environment.

## Pitfalls

- **Never sign the client's provider account up yourself "to save time".** Name change after KYC is a support ticket and a re-verification, not an edit.
- **Test-mode completion is not live-mode proof.** Test keys bypass activation, so a green test run says nothing about whether KYB passed or the webhook is registered on the live account. Verify the live account's webhook exists after handover, not just the URL in your notes.
- **The activation-blocking fields are the boring ones.** A missing price range or business website stalls activation with no error a developer would notice, and the client never learns why the account is "Under review".
- **Pin the events from the handler, not from the provider's full event catalog.** Subscribing everything floods the endpoint with event types it silently ignores; subscribing too few leaves payments that never settle.
- **A webhook secret from the test account does not verify live deliveries.** Signature schemes that carry both hashes (test vs live) must receive the live secret for live events, or every live delivery is rejected 401 while test deliveries still pass.

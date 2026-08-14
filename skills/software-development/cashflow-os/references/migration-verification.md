# Live-DB migration verification probes (Supabase + user's SQL-Editor paste flow)

The user applies migrations by pasting into the Supabase SQL Editor; the paste
flow skips migrations SILENTLY (proven 2026-08-06: 009 loans + 020 import index
were never applied while the code referenced them). "User said done" is not
evidence — probe. All probes use the anon key + a password-grant user token
(no JWT minting needed):

```bash
set -a && source .env.local && set +a
TOKEN=$(curl -s -X POST "$NEXT_PUBLIC_SUPABASE_URL/auth/v1/token?grant_type=password" \
  -H "apikey: $NEXT_PUBLIC_SUPABASE_ANON_KEY" -H "Content-Type: application/json" \
  -d '{"email":"attila@cashflow.test","password":"demodemo123"}' \
  | python -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))")
```

## 1. Table sweep — every table the app queries (run after every paste round)

```bash
grep -oh "\.from([\"'][a-z_]*" src/ --include="*.ts" | sed "s/.*from([\"']//" | sort -u
# then loop each name:
curl -s -o /dev/null -w "%{http_code}" "$URL/rest/v1/<t>?select=id&limit=1" \
  -H "apikey: $ANON" -H "Authorization: Bearer $TOKEN"   # 404 = migration never applied
```

Do NOT trust a speculative table list — `employees`/`sales`/`automation_rules`
sound like tables but aren't; only `.from()` names in src matter.

## 2. Unique-index probe (e.g. 020 import-key backstop)

PostgREST can't introspect indexes. Attempt a duplicate insert:

```bash
# grab one existing row as the insert payload, POST it again
curl -s -w "\nHTTP %{http_code}\n" -X POST "$URL/rest/v1/transactions" \
  -H "apikey: $ANON" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "$ROW"
# 409/23505 = index LIVE (good); 201 = NOT applied (BAD) — then clean up:
#   list ids ordered by created_at.desc for that row's natural key, DELETE the newest
```

Password-grant token avoids JWT minting entirely.

## 3. SECURITY DEFINER guard probe (e.g. 021 notify_user)

```bash
curl -s -X POST "$URL/rest/v1/rpc/notify_user" -H "apikey: $ANON" \
  -H "Content-Type: application/json" \
  -d '{"p_user_id":"00000000-0000-0000-0000-000000000001","p_entity_id":null,"p_kind":"system","p_title":"spam","p_body":"x","p_link":null}'
# expect: {"code":"P0001","message":"not authorized"}  (anything else = bypass still open)
```

## Pitfalls

- **Windows curl vs git-bash /tmp:** `curl -o /tmp/x.json` writes to `C:\tmp`
  (Windows path), which the later bash read of `/tmp/x.json` can't see — write
  probe bodies to a REPO-RELATIVE path (e.g. `./.probe.json`) or use `-w` inline.
- Password-grant needs the TEST user creds (attila@cashflow.test/demodemo123);
  the real account (YOUR_EMAIL@gmail.com) has no known password — never
  attempt it.
- RLS policy behavior (staff insert 'approved' → expect rejection) can't be
  probed without staff creds — verify policy-vs-app alignment by reading the
  policy SQL against the action's status derivation instead (see SKILL.md
  migration-021 lessons).

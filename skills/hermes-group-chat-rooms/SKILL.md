---
name: hermes-group-chat-rooms
description: Create Hermes group chat rooms from the CLI.
---

# Hermes Group Chat Rooms (CLI)

## When to Use

Load this when asked to create, list, or inspect a Hermes group chat / "room" from the CLI — especially when the desktop app's UI is unavailable or you need it scripted. Also load it before concluding group chats "aren't supported", because they are; only the creation RPC is auth-gated.

Group chats ("hosted rooms") are stored in `~/.hermes/shared-state.db`, table `hosted_rooms`. The desktop app creates them through the `groups.create` TUI-gateway RPC; that RPC is auth-gated (HTTP 403 on the loopback port), so drive the storage + validation layer directly instead.

## Create a room

```python
import sys, os, uuid
sys.path.insert(0, os.path.expanduser("~/.hermes/hermes-agent"))
from pathlib import Path
from gateway import hosted_rooms
from gateway.hosted_room_discussion import validate_roster

db = Path.home()/".hermes"/"shared-state.db"
local_profiles = ["default","channel","codingprofile","designer","documents","engineering",
                  "finance","learning","local","marketing","qa","research","sales","trading"]

members_raw = [
    {"member_id":"trading-lead",     "profile":"trading",  "handle":"trading"},
    {"member_id":"finance-quant",    "profile":"finance",  "handle":"finance"},
    {"member_id":"qa-verifier",      "profile":"qa",       "handle":"qa"},
    {"member_id":"research-evidence","profile":"research", "handle":"research"},
]
normalized = validate_roster(members_raw, local_profiles=local_profiles)

room = hosted_rooms.create_room(
    db, room_id=str(uuid.uuid4()), name="Trading Paper Lab",
    members=[{"member_id":m.member_id,"profile":m.profile,"handle":m.handle,
              "target":dict(m.target or {})} for m in normalized],
    authority_gateway_id=hosted_rooms.local_authority_gateway_id())
```

## List rooms (same function the desktop calls)

```python
from gateway.hosted_rooms import list_rooms
for r in list_rooms(db, include_disbanded=False, limit=50):
    print(r["name"], r["room_id"], [m["profile"] for m in r["members"]])
```

## Roster rules (enforced by `validate_roster`)

- 2 to 6 members. Fewer or more raises.
- Each member needs `member_id`, `profile`, `handle` — all unique. `handle` cannot be `all` or `everyone`.
- `profile` must be a local profile served by this gateway, else "not local to this gateway".
- Omit `target` for a local member; the validator fills `{"kind":"local","profile":<profile>}`. A `target` with `kind` other than `local`/`peer`, or cross-gateway fields, is rejected.
- Optional `display_name`.

## Pitfalls

- **Loopback RPC is auth-gated.** `ws://127.0.0.1:<port>` returns HTTP 403 without the desktop session; do not try to speak `groups.*` over it from a script.
- **The gateway control socket is a different surface.** `~/.hermes/gateway.sock` accepts only control verbs (`status`, `identify`, `serve-profile`, pausing, ...) and answers `unknown verb` to `groups.list`.
- **Do not hand-write SQL** into `hosted_rooms`. `create_room` also seeds authority rows and retired-id bookkeeping; a bare INSERT leaves the room unopenable.
- **Profiles must be served by the running gateway.** Check `served_profiles` in `~/.hermes/gateway_state.json`; a newly created profile the gateway has not picked up is rejected as "not local".
- **Rooms appear in the desktop on its next refresh**, not instantly — it re-reads via `groups.list`.

## Verify

After creating, re-read with `list_rooms` and confirm the name + member profiles. That is the same read path the desktop uses, so a match means it will render.

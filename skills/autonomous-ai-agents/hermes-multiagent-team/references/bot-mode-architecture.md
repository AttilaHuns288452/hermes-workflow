# Bot Mode and Group Chat Architecture (Hermes)

Depth for `hermes-multiagent-team` step 7. Source: current Hermes docs.

## A Bot IS a profile
A Bot Mode bot is a Hermes profile (`~/.hermes/profiles/<name>/`) presented in the desktop's Bots
roster with an avatar and a persistent canonical "Bot Chat". Same state is visible from the CLI:
`hermes -p <bot> chat` opens the same agent. Routines are ordinary cron jobs namespaced
`[bot:<name>]`.

## Group Chat rooms (desktop GUI)
- Created in the Desktop Bots pane (`+` → New Group Chat). 2–6 members. Drawer
  flow: focus the member search field → type a name → click the result row to
  toggle its checkbox (selected members accumulate as removable chips; the
  submit button label becomes `Create Group (N)`) → confirm the auto-generated
  group name (member names joined by commas) → click Create Group. Verify a new
  room row appears in the Bots roster before reporting success; a dismissed
  drawer leaves no partial state. Internally the dialog calls `groups.create`
  with a UUID, the group name, and the 2–6 local member handles.
- Turn model: your message triggers up to three serial rounds. @-mentioned bots respond (everyone if
  none mentioned); each replies briefly or passes; the room settles when a round stays silent.
  Hard caps: 10 messages per send, 3 rounds.
- Each member keeps its OWN persistent room session (titled `Group: <room> · <thread>`). Not every bot
  replies to every message — a bot speaks only when it has something to add. @mention specific members
  to scope the round; `@all`/`@everyone` addresses the room; `@user` escalates to the human.
- When all members share one gateway, the gateway owns turn scheduling through a durable driver —
  closing the Desktop does not stop a room mid-discussion.
- Room state lives in the install's root `shared-state.db` (older rooms were in `state.db`).

## Bot-to-bot DMs (`message_agent`)
- A Bot messages a teammate via `message_agent(target="<profile-or-handle>", message="...")` from its
  canonical Bot Chat. Delivery is fire-and-forget (a queued ack ≠ delivered). Target is the teammate's
  profile name, friendly name, or @-handle.
- The tool and the team roster are injected ONLY into canonical "Bot Chat" sessions on Bot-Mode-managed
  installs. Regular chats, group-room member sessions, and CLI sessions never see it.

## Headless enablement (no Desktop)
Two conditions must hold or `message_agent` is unreachable even with `agent.bot_mode_protocol` on:
1. The session is titled exactly `Bot Chat`:
   `hermes -p <bot> chat -c "Bot Chat" --create-if-missing`
2. At least one profile carries the Bot-Mode marker in its `profile.yaml` (an empty block is enough):
   ```yaml
   ui_meta:
     hermes-bots: {}
   ```
From the next turn in that Bot Chat the teammate roster, protocol, and `message_agent` are all picked up.

## Coordination surfaces (which to use)
- Kanban: durable task/ownership record, role-routed workers.
- Group room: cross-functional discussion only.
- Bot Chat DM (`message_agent`): direct 1:1 assignment.
- `delegate_task`: short parallel subtasks whose result returns to the caller.

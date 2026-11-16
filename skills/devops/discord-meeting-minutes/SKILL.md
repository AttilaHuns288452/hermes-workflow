---
name: discord-meeting-minutes
description: "Configure a Hermes Discord bot as a silent meeting recorder."
triggers:
  - meeting bot
  - discord minutes
  - auto-join voice
  - silent meeting
  - re-apply meeting patches
  - voice_minutes_map
---

# Discord Meeting Minutes Bot

Configure the Hermes Discord gateway bot as a silent meeting recorder: auto-join watched voice channels when a human enters, transcribe all speakers, post a summary to a minutes text channel, and auto-leave when the room empties.

## When to Use

- Setting up a meeting recorder for a Discord voice channel
- Re-applying patches after `hermes update` wipes local changes
- Adding/removing watched meeting channels
- Switching between silent (record-only) and interactive voice mode

## Prerequisites

Before auto-join works, verify:

1. **Privileged intents enabled**: https://discord.com/developers/applications → Bot → Privileged Gateway Intents → **Voice States** ON (Server Members too if using username allowlists)
2. **Channel permissions**: bot role has View Channel + Connect on each watched voice channel
3. **Code patches**: the 5 insertions below are present in `adapter.py` and `run_voice.py`

Auto-join is purely event-driven. It fires on `voice_state_update` when a non-bot joins a watched channel. If the bot is already connected, or only bots are in the channel, or the handler was wiped by an update, nothing happens.

## Config Keys (config.yaml under `discord:`)

```yaml
discord:
  auto_join_voice_channels: "1111111111,2222222222"
  voice_minutes_map: "1111111111:3333333333,2222222222:3333333333"
  voice_minutes_channel: 3333333333
  auto_leave_grace_seconds: 10
  silent_meeting: true
```

## Patching Process

The shipped Hermes Discord adapter does NOT read these keys. Local patches to `~/.hermes/hermes-agent/plugins/platforms/discord/adapter.py` and `~/.hermes/hermes-agent/gateway/run_voice.py` are required.

### 1. State vars in `__init__` (adapter.py)

Add after `self._voice_fx_cfg`:
```python
self._auto_voice_guilds: set = set()
self._auto_leave_tasks: Dict[int, asyncio.Task] = {}
self._auto_voice_cfg: Dict[str, Any] = self._load_auto_voice_config()
self._meeting_transcripts: Dict[int, List] = {}
```

### 2. Config loader `_load_auto_voice_config` (adapter.py)

Add method before `_load_voice_fx_config`. See `references/patches.md` for full implementation.

### 3. Extended `on_voice_state_update` (adapter.py)

Replace the existing handler. See `references/patches.md`. Key behaviors:
- Ignore bots and self
- Auto-join when a human joins a watched channel and bot isn't already connected
- Auto-leave with grace period when channel empties of humans

### 4. Meeting methods (adapter.py)

Add `_auto_join_meeting`, `_accumulate_transcript`, `_post_meeting_summary`, `_auto_leave_and_minutes` after `leave_voice_channel`. See `references/patches.md`.

### 5. Silent mode guard (gateway/run_voice.py)

Before `await adapter.handle_message(event)` in `_handle_voice_channel_input`:
```python
if guild_id in getattr(adapter, "_auto_voice_guilds", set()):
    cfg = getattr(adapter, "_auto_voice_cfg", {})
    if cfg.get("silent", False):
        await adapter._accumulate_transcript(guild_id, user_id, transcript)
        return
```

### 6. Rejoin live meetings on boot (adapter.py) — patch 6

Auto-join is purely event-driven (fires on a member JOIN), so a gateway restart during a meeting leaves the bot outside the room for the rest of the meeting and the minutes are lost. `_rejoin_live_meetings()` is called from `on_ready` and rescans every watched channel (bounded 6 x 10s) for humans already in it, then joins through the normal `_auto_join_meeting` path. It skips empty rooms, unwatched channels, and guilds already connected. Self-check: `python3 ~/.hermes/scripts/test_meeting_rejoin.py` (4 checks).

### 7. Capture-health instrumentation (adapter.py) — patch 7

"The bot is in the room but the minutes channel is empty" is unanswerable from a log that only reports joins: DAVE decrypt failures were logged for the **first 10 packets only**, and a failed STT returned **silently**. Patch 7 adds `_dave_failed` / `_stt_failed` / `_utterances` / `_transcripts` counters, logs DAVE failures 1-in-250 forever and STT failures 1-in-25, and emits a `[VoiceCapture]` heartbeat on the 15s keepalive tick:

```
[VoiceCapture] decoded=812 decode_failed=0 dave_failed=9 buffered={5513: 2.3, 5473: 0.7} utterances=4 transcripts=4 stt_failed=0
```

`buffered` seconds per SSRC is the only positive proof audio is arriving. Read the verdict with `python3 ~/.hermes/scripts/probe_capture_now.py --watch 90` → ACQUIRING / DEAF / SILENT / NO-HEARTBEAT. Self-check: `python3 ~/.hermes/scripts/test_capture_health.py` (2 checks; fails if a deaf receiver is reported healthy). Installer: `~/.hermes/scripts/instrument_capture.py`, called by `ensure_meeting_patches.py` on every run.

Before blaming patches, prove audio reaches the process at all: `ss -unp | grep <gateway pid>` for the voice UDP socket, then watch its receive queue (`ss -un` column 1) grow and drain while people talk. A growing queue with no `[VoiceCapture]` decode progress means the receiver thread is stuck, not the network.

### 8. Empty-room presence poll (adapter.py) — patch 8

Auto-leave fires only on a `voice_state_update` LEAVE. A post-restart rejoin (or a cache that never saw the leave) can therefore strand the bot in a room whose humans already went home: no leave event ever arrives, `_auto_leave_and_minutes` never runs, and `_post_meeting_summary` is never called, so the minutes silently vanish. Patch 8 polls presence on the same 15s heartbeat: for an auto-joined guild with no humans left and no leave already pending, it schedules the usual leave+minutes task at `max(grace_seconds, 60)`. It never touches a manual `/voice join` (guild absent from `_auto_voice_guilds`). Self-check: `python3 ~/.hermes/scripts/test_empty_room_poll.py` (4 checks).

### 9. Record the whole room, not just the allowlist (adapter.py + run_voice.py) — patch 9

`DISCORD_ALLOWED_USERS` is the **assistant** auth boundary: who may talk to the agent. It is not the boundary for who a silent recorder hears. Two gates applied it to audio anyway, so with a one-person allowlist only that one person ever appeared in the minutes:

1. `_voice_listen_loop` skipped the speaker before STT.
2. `run_voice._handle_voice_channel_input` refused the transcript at route canonicalization / auth.

Patch 9 makes a silent auto-joined meeting record every speaker, and accumulates the line at the top of `_handle_voice_channel_input` (before canonicalization). `handle_message` stays allowlist-gated, so a stranger in the room **can be recorded but can never instruct the bot**. Interactive voice mode (`silent: false`) and manual `/voice join` keep the old allowlist behavior. Self-check: `python3 ~/.hermes/scripts/test_record_all_speakers.py` (4 checks — asserts all speakers recorded in a silent meeting, and that the stranger gets 0 agent turns).

If teammates still do not appear, confirm the identity exists at all: `grep -oE 'Voice state: .*' gateway.log` will list joiners, while `[VoiceCapture] utterances` increments only when someone actually speaks.

### 10. Voice key-rotation fix — OBSOLETE (do not apply)

Upstream `VoiceReceiver` now re-resolves credentials at runtime (`_resolve_credentials`, invoked on every session description, DAVE epoch prepare, membership change, or decrypt-failure streak). The old patch is unnecessary; `~/.hermes/patches-discord-voice-key-rotation.patch` no longer applies to current upstream and would break the read-only `_secret_key` property. Verified 2026-10-08.

### 11. STT Model Setup

**The local backend must exist in the environment the gateway actually boots from.** Since Hermes moved to PM-managed 
```yaml
stt:
  provider: local
  local:
    model: large-v3-turbo
```

Install it into the LIVE environment (not the legacy `hermes-agent/venv`, which is ignored):
```bash
cd ~/.hermes/hermes-agent && ./.hermes/bin/hermes pm install --extra stt-whisper
```
Then verify from that same environment: `.hermes/bin/hermes` boot preamble + `import faster_whisper`. Models cache under `~/.cache/huggingface/hub` and survive environment rebuilds.

Pre-download: `python3 -c "from faster_whisper import WhisperModel; WhisperModel('large-v3-turbo', device='cpu', compute_type='int8')"`

### Silence failure mode: "no minutes anymore" with a healthy-looking gateway

Symptom: auto-join logs still fire, `VoiceReceiver started` appears, members join/leave normally, but the minutes channel gets nothing. `grep -c 'Voice input from user' ~/.hermes/logs/gateway.log` is 0. Cause: STT resolution fails for every utterance, so `_process_voice_input` returns before the transcript callback and no line is ever accumulated. Confirm in one shot:
```bash
cd ~/.hermes/hermes-agent && PYTHONPATH=<selected venv>/lib/python3.14/site-packages \
  <store python> -c "import tools.transcription_tools as t; print(t._detect_local_backend())"
```
`None` + a `STT provider 'local' configured but unavailable` warning means faster-whisper is missing from the boot environment. `security.allow_lazy_installs: false` blocks the runtime self-heal, so it never installs itself. Fix with the `pm install --extra stt-whisper` line above, then restart. Note the gateway restart refuses while live sessions exist; pass `-y` or run it detached.

## Troubleshooting

### Bot doesn't auto-join

1. **Check the bot is still in the guild FIRST** — membership is upstream of every other check, and removal is silent: the gateway keeps running green, the bot's own connection logs look normal, and no `voice_state_update` ever arrives. Diagnosing intents or patches against a server the bot is no longer in wastes a session. Verify with the REST API using the token from `~/.hermes/.env`:
   ```bash
   TOK=$(grep -m1 "^DISCORD_BOT_TOKEN" ~/.hermes/.env | cut -d= -f2)
   curl -s -H "Authorization: Bot $TOK" https://discord.com/api/v10/users/@me/guilds
   ```
   If the expected guild is missing, the fix is a re-invite, not debugging. The invite URL needs the APPLICATION ID (not the bot user id — get it from `GET /oauth2/applications/@me`):
   `https://discord.com/oauth2/authorize?client_id=<APP_ID>&scope=bot+applications.commands&permissions=1051648`
   (1051648 = View Channel + Send Messages + Connect). Also compare WHICH guild the meeting happens in against the config — with two servers, one can be dropped while the other keeps auto-joining and masks the loss.

2. Check the handler fires — add a temp debug line at the top of `on_voice_state_update`:
   ```python
   with open("/tmp/autovoice_debug.log", "a") as f:
       f.write(f"{member.display_name}: {before.channel} -> {after.channel}\n")
   ```
   Then `hermes gateway restart` and join a voice channel. If the file isn't created, Discord is dropping events → check step 1 again, then enable **Voice States** intent in the Developer Portal.

3. If the handler fires but join still fails:
   - Check `[AutoVoice]` logs in `~/.hermes/logs/gateway.log`
   - Verify channel ID is in `auto_join_voice_channels`
   - Verify bot isn't already connected to that guild (`guild_id not in self._voice_clients`)

4. **Permissions bitmask ≠ intent**. Channel perms (View Channel/Connect) are necessary but insufficient — the Voice States privileged intent is a separate portal toggle.

### Bot joins but meeting ends with "No transcripts to summarize"

The bot can sit in the VC the whole meeting logging joins/leaves and still capture nothing. Diagnosis order:

1. `grep -a "NaCl decrypt failed" ~/.hermes/logs/agent.log` — if present, packets arrive but decryption fails. On current upstream the receiver re-resolves credentials on rotation, so a persistent decrypt failure means that refresh path is broken (see the step 6 note), not stale cache. Correlate: `Disconnected from voice by force... potentially reconnecting.` shortly after `VoiceReceiver started`, then decrypt warnings from the first speech packets.
2. If the log has NO `NaCl decrypt failed` AND no `Voice input from user` lines, no RTP is arriving at all → check `VoiceReceiver started` appears after the last `Voice connection complete` (a second guild join can restart the receiver).
3. If `Voice input from user` lines exist but no MoM post → the summary step failed (model fallback ladder in the adapter logs).

Note: the4014 rotation itself is normal and handled by discord.py silently (no "connection attempt 2" line on the reconnect path). Current upstream refreshes receiver credentials on rotation, so treat decrypt failures as a refresh-path bug, not a cached-key bug.

### Meeting ends but no minutes posted

Transcripts were collected but nothing posted; log shows `[AutoVoice] No minutes channel configured for guild`. `voice_minutes_map` / `voice_minutes_channel` are missing from the `discord:` block (config migrations drop keys silently). Fix with `hermes config set discord.voice_minutes_map "<voice_channel_id>:<minutes_channel_id>,..."` and verify through the adapter's own loader (`read_raw_config` → split `id:id` pairs) — a value that parses wrong drops every meeting's output.

### hermes update Wipes Patches

`hermes update` overwrites the local checkout. After every update, run:

1. `python3 ~/.hermes/scripts/ensure_meeting_patches.py` — repairs patches 1-5 automatically (adapter.py + run_voice.py), verifies the end state, and restarts the gateway. It runs on cron too, but its exit-1 incidents are easy to miss.
2. Verify with `grep AutoVoice ~/.hermes/logs/gateway.log`

If the script reports "end state incomplete", the upstream anchors drifted — update the anchors in `ensure_meeting_patches.py` from the patch text below, then re-run.

Current managed set: patches 1-5 (adapter + run_voice), patch 6 (post-restart rejoin), patch 7 (capture instrumentation), patch 8 (empty-room poll), plus an STT availability check that reinstalls `stt-whisper` when the boot environment lost it. Each has a self-check script next to it (`test_meeting_rejoin.py`, `test_capture_health.py`, `test_empty_room_poll.py`) and the live proof lives in `~/.hermes/scripts/verify_meeting_bot.py` / `probe_capture_now.py`.

**This skill's patch list is the spec; the repair script must install and check every patch documented here.** When adding a patch section to this skill, extend `ensure_meeting_patches.py`'s `check_patches()` and `reapply_patches()` in the same change — a documented-but-unmanaged patch dies silently on the next update.

## Full Patch Source

See `references/patches.md` for the complete, copy-pasteable patch implementations.

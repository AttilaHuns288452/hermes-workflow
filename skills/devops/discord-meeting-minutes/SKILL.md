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

### 6. Voice key-rotation fix — OBSOLETE (do not apply)

Upstream `VoiceReceiver` now re-resolves credentials at runtime (`_resolve_credentials`, invoked on every session description, DAVE epoch prepare, membership change, or decrypt-failure streak). The old patch is unnecessary; `~/.hermes/patches-discord-voice-key-rotation.patch` no longer applies to current upstream and would break the read-only `_secret_key` property. Verified 2026-10-08.

### 7. STT Model Setup

```yaml
stt:
  provider: local
  local:
    model: large-v3-turbo
```

Pre-download: `python3 -c "from faster_whisper import WhisperModel; WhisperModel('large-v3-turbo', device='cpu', compute_type='int8')"`

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

**This skill's patch list is the spec; the repair script must install and check every patch documented here.** When adding a patch section to this skill, extend `ensure_meeting_patches.py`'s `check_patches()` and `reapply_patches()` in the same change — a documented-but-unmanaged patch dies silently on the next update.

## Full Patch Source

See `references/patches.md` for the complete, copy-pasteable patch implementations.

# Discord meeting-minutes auto-join patch (local)

Feature: bot auto-joins watched voice channels when a member enters, transcribes
everyone present, then posts meeting minutes to a bound text channel and leaves
after the room has been empty for a grace period.

Ships nowhere upstream — re-apply after `hermes update`. `git diff` in
`hermes-agent/` is the source of truth for the exact hunks; this file is the
map of WHY and WHERE.

## Files touched (2)

1. `plugins/platforms/discord/adapter.py`
   - `__init__`: add `_auto_voice_cfg`, `_auto_voice_guilds` (set), `_auto_leave_tasks`.
   - `_load_auto_voice_config()` — mirrors `_load_voice_fx_config` pattern:
     reads `discord.auto_join_voice_channels` (list or comma-string),
     `discord.voice_minutes_channel`, `discord.auto_leave_grace_seconds` via
     `hermes_cli.config.read_raw_config()`. Feature OFF unless channels set.
   - `_handle_auto_voice_state(member, before, after)` — called from
     `on_voice_state_update` **before** the `bot_guild_ids` early-return (the
     bot is not connected yet — that's the point). Join branch: member enters
     a watched channel → `join_voice_channel(after.channel, text_channel_id=minutes)`.
     Empty branch: non-bot member left and the bot's VC has 0 humans →
     schedule `_auto_leave_and_minutes` (grace sleep → re-check → fire minutes
     → `leave_voice_channel`).
   - `user_in_voice_channel(guild_id, user_id)` — presence check helper.
   - `_voice_listen_loop`: when `guild_id in _auto_voice_guilds`, replace the
     `_is_allowed_user` gate with presence-in-VC (anyone in the room talks).
2. `gateway/run.py` — `_handle_voice_channel_input`: **second auth gate**.
   Voice input is authorized twice: adapter listen loop AND run.py
   `_is_user_authorized(source)`. Both must be relaxed for meeting mode
   (presence = auth), or non-allowlisted speakers get silently dropped.

## The minutes trigger trick

Don't try to dispatch a synthetic user message or summarize from cron (cron
sessions don't share the meeting transcript). Instead reuse the voice pipeline:

```python
await self._voice_input_callback(guild_id, int(owner_id),
    "The meeting has ended and everyone has left. Write the meeting minutes "
    "with key decisions and action items, then post them here.")
```

It runs through `_handle_voice_channel_input` in the SAME session as the
meeting transcript (bound via `_voice_text_channels`), so the agent has full
context. Owner id = `next(iter(self._allowed_user_ids))`.

**The self-block bug (minutes never posted):** the presence-auth gate in
run.py rejects the trigger — it impersonates the owner, and the owner JUST
LEFT the voice channel (which is the trigger). Fix: `self._auto_voice_guilds.discard(guild_id)`
**BEFORE** calling `_voice_input_callback` so it falls through to the normal
allowlist. Discarding after the callback keeps the block. Symptom in logs:
auto-join works (`[AutoVoice] joined`), empty-room leave works (`left ...
after meeting ended`), but no minutes post and no error.

## Silent-meeting mode (no live transcript, minutes only)

User requirement: bot must NOT post `[Voice]` transcript lines during the
meeting; record silently, transcribe once at the end, deliver only the minutes.
Enabled by `discord.silent_meeting: true`. Added to the same patch:

- `_load_auto_voice_config` gains `"silent": False` default, read from
  `discord.silent_meeting`.
- New state in `__init__`: `_silent_meeting_guilds` (set) + `_meeting_audio`
  (dict guild_id → user_id → bytearray). Join branch adds the guild to the
  silent set when `cfg.get("silent")`.
- `_voice_listen_loop`: FIRST branch after `check_silence()` — if guild in
  `_silent_meeting_guilds`, append each completed utterance's PCM to
  `_meeting_audio[guild_id][user_id]` and `continue` (no transcription, no
  agent turns, no channel posts).
- `_auto_leave_and_minutes`: silent path calls `_transcribe_meeting_audio(guild_id)`
  (one `transcribe_audio` pass per speaker, `asyncio.to_thread`, speaker-labelled
  `**Name:** text` blocks), then fires the callback with the full transcript
  embedded ("Here is the full transcript of the meeting that just ended: …").
- `_transcribe_meeting_audio`: pops `_meeting_audio`, per user: temp wav →
  `VoiceReceiver.pcm_to_wav` → `transcribe_audio` (large-v3, slow on CPU —
  a 30-min meeting ≈ 2–5 min of transcription after the meeting; set team
  expectations). Resolves display names via `guild.get_member`.
- `gateway/run.py` `_handle_voice_channel_input`: the `[Voice] <@user>: …`
  channel post is skipped when `guild_id in getattr(adapter, "_silent_meeting_guilds", set())`.

**Callback ordering pitfall (silent mode):** `_auto_voice_guilds` is discarded
BEFORE the callback (auth fallback to allowlist), but `_silent_meeting_guilds`
must stay set THROUGH the callback (it gates the [Voice] post suppression —
the transcript would leak to the channel otherwise) and only be discarded after.
Two sets, two different discard points.

## Verify harness gotcha (to_thread fakes)

`transcribe_audio` is called via `asyncio.to_thread` — the fake in the verify
script must be a **sync** function (`def fake_transcribe(path): return {...}`),
not `async def`. An async fake returns a coroutine, `result.get("success")`
fails, transcription silently returns "" and the callback never fires.
Also: `FakeVC` needs `.channel` set to a fake with the matching `id` and a
`.members` list, or `_auto_leave_and_minutes` early-returns before the trigger.

## Config (set via `hermes config set` — config.yaml is write-protected from patch tool)

```yaml
discord:
  auto_join_voice_channels: "1531670932467220550,1531672533445906622"  # watched VCs
  voice_minutes_channel: 1534591025429876897                            # minutes text channel
  auto_leave_grace_seconds: 10    # 60 default; user asked for 10 (short grace = fast minutes)
  voice_channel_inactivity_timeout_seconds: 0   # default 300 would bail mid-meeting
  silent_meeting: true            # record-only; minutes delivered after, no live transcript
```

`voice_channel_inactivity_timeout_seconds: 0` is REQUIRED — the default 300s
idle timer disconnects the bot during quiet meeting stretches.

## Verify harness pattern

Subclass the real `DiscordAdapter` with fakes for `_voice_clients` /
`_client.user` / channel+member stubs, override `join_voice_channel` /
`leave_voice_channel` to record calls. Real import:
`PYTHONPATH="$(pwd)" venv/Scripts/python verify.py`. Cases: config parse from
real config.yaml, join-on-entry, empty-room leave, minutes callback fires for
owner then leaves, presence gate, control (empty config → no-op).

## Pitfalls

- `on_voice_state_update` early-returns when bot has no voice clients — the
  auto-join call must go BEFORE that gate or it never fires.
- VC emptiness: `[m for m in vc.channel.members if m != self._client.user]`
  (member cache requires Server Members Intent — already enabled).
- `join_voice_channel(..., text_channel_id=...)` is the official programmatic
  join API (used by `/voice join` flow) — do not hand-roll channel.connect().
- Grace re-check is mandatory: people hop out and back mid-meeting; cancel the
  pending task on re-join (`_cancel_auto_leave`).

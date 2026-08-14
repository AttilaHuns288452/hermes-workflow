# Patch inventory — Discord meeting-minutes bot

All patches are local to `C:\Users\YOUR_USERNAME\AppData\Local\hermes\hermes-agent` (git checkout).
`hermes update` reverts them; re-apply with `git diff` / this inventory. Diff: ~250 insertions across 2 files.

## plugins/platforms/discord/adapter.py

| Site | What it does |
|---|---|
| `__init__` (~line 1036) | State: `_auto_voice_cfg`, `_auto_voice_guilds`, `_auto_leave_tasks`, `_silent_meeting_guilds`, `_meeting_audio` (guild→user→pcm), `_meeting_started` (monotonic), `_meeting_started_wall` (epoch) |
| `__init__` (next to `_auto_leave_tasks`) | **`_vc_humans` (guild→set of human ids) — event-tracked occupancy. Discord's cached `channel.members` can hold a ghost (bot joined pre-ready during initial state sync), which wedged the minutes flow: leave events arrived but the cache check saw a phantom member, no task was ever scheduled, bot sat in an empty channel forever. The event stream is the wire truth; the cache is not.** |
| `_load_auto_voice_config()` | Reads `discord.auto_join_voice_channels`, `voice_minutes_channel`, `voice_minutes_map` ("v:t,v:t"), `auto_leave_grace_seconds`, `silent_meeting`. Map keys merged into watched `channels`. Defaults: grace 60, silent False |
| `on_voice_state_update` (inside connect) | Calls `await adapter_self._handle_auto_voice_state(...)` BEFORE the bot-connected early return (auto-join must run while disconnected) |
| `_handle_auto_voice_state()` | Join when member enters watched channel (bind `text_channel_id` = mapped minutes channel, record start times, flag silent guild); seed `_vc_humans` from `after_ch.members` on join; `else` branch adds entrant when bot already in the channel; on departure: `_vc_humans.discard(member.id)`, schedule `_auto_leave_and_minutes` when the EVENT set empties (no cache check) |
| `_cancel_auto_leave()` | Cancel pending leave task (someone re-entered) |
| `_auto_leave_and_minutes()` | Grace sleep → re-check: proceed when cache OR `_vc_humans` says empty (either can be stale; never block on both) → **discard from `_auto_voice_guilds` BEFORE callback** (presence-auth self-block fix) → silent: ETA notice + transcribe + prompt w/ transcript; live: prompt only → `_silent_meeting_guilds.discard` → leave; finally pops `_auto_leave_tasks` + `_vc_humans` |
| `_transcribe_meeting_audio()` | Per speaker: `VoiceReceiver.pcm_to_wav` (48k stereo→16k mono via ffmpeg) → `transcribe_audio` (to_thread) → `**Name:** text`; pops `_meeting_audio` |
| `_build_minutes_prompt()` / `_load_minutes_template()` | Loads `~/AppData/Local/hermes/minutes_template.md` (fallback builtin); fills `{date} {time_started} {time_ended}` from wall clock; REASON-don't-copy rules; `{duration}` replaced last |
| `_post_minutes_eta()` | ETA = `speech_min*0.40 + 1` (0.40 = benchmarked large-v3-turbo int8 CPU rate on this machine); logs send success / cache miss |
| `_post_no_speech_notice()` | Posts "no speech captured" instead of silent failure |
| `_format_duration()` | static: `45s` / `2m 05s` / `1h 02m` |
| `_voice_listen_loop` | Silent-mode branch BEFORE the `_is_allowed_user` gate: accumulate `check_silence()` output into `_meeting_audio`, `continue`. Plus **5s stale-cache sweep**: if no leave task pending and cache OR event set says empty → schedule `_auto_leave_and_minutes` (self-heals a missed/ghosted voice-state event without restart) |
| `user_in_voice_channel()` | Presence check: user physically in bot's VC |
| `_load_auto_voice_config` minutes_map | per-channel routing |

Receiver (unchanged core, referenced): `VoiceReceiver.check_silence()` — SILENCE_THRESHOLD=1.5s, MIN_SPEECH_DURATION=0.5s, 48kHz stereo 16-bit = 192000 B/s; SPEAKING hook maps ALL speakers (no allowlist filter); `_infer_user_for_ssrc` only maps when exactly one ALLOWED user in channel (edge case: bot joins mid-speech, unmapped non-allowed speaker's first sentence can drop).

## gateway/run.py

| Site | What it does |
|---|---|
| `_handle_voice_channel_input` (auth gate) | Meeting mode (`guild_id in adapter._auto_voice_guilds`): presence = auth via `adapter.user_in_voice_channel`; else normal `_is_user_authorized` |
| `_handle_voice_channel_input` ([Voice] post) | Suppress `**[Voice]**` channel post when `guild_id in adapter._silent_meeting_guilds` |

## Config reference (current values)

```
discord:
  auto_join_voice_channels: 1531670932467220550,1531672533445906622   # SE1 scrum/lounge
  voice_minutes_channel: 1534591025429876897                          # SE1 minutes
  voice_minutes_map: "1531670932467220550:1534591025429876897,1531672533445906622:1534591025429876897,1534531253804470446:1534912758334619800"
  auto_leave_grace_seconds: 10
  silent_meeting: true
  voice_channel_inactivity_timeout_seconds: 0
stt:
  enabled: true
  provider: local
  local: { model: large-v3-turbo }
```

.env: `DISCORD_BOT_TOKEN`, `DISCORD_ALLOWED_USERS=489037199917056000`.

## Verification recipe (run after re-applying)

`PYTHONPATH="$(pwd)" venv/Scripts/python` with a temp verify script (delete after):
1. `_load_auto_voice_config` on `object.__new__(DiscordAdapter)` → channels {3 voice IDs}, minutes_map resolves both servers, silent True, grace 10.
2. `_format_duration(45)=="45s"`, `(3725)=="1h 02m"`.
3. `_build_minutes_prompt("**X:** hi", "1h", epoch)` contains template + transcript + rules, no `{duration}` left.
4. Silent join marks `_silent_meeting_guilds`; `_auto_leave_and_minutes` with fake receiver + patched `tools.transcription_tools.transcribe_audio` fires callback with transcript, then leaves.
5. Control: silent=False → live prompt, no transcript.
6. grep run.py for `_silent_meeting_guilds` guard.

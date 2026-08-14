---
name: discord-meeting-minutes-bot
description: Use when working on Attila's Discord meeting minutes bot.
---

# Discord Meeting Minutes Bot

Hermes gateway bot `Hermes minutes of meeting#8667` (owner user 489037199917056000). Auto-joins watched voice channels when anyone enters, silently records, and posts reasoned meeting minutes (leader's template) to a text channel after the room empties. Lives in 2 servers: SE1 (1531670931393744936) and SF-3B System Builders (1534531250793222226).

## The flow

```
someone joins watched voice channel → bot joins, records per-speaker audio (silent, no messages)
room empty for auto_leave_grace_seconds (10) → ETA notice → transcribe once per speaker (large-v3-turbo)
→ build minutes from template + reasoning rules → post to that voice channel's minutes channel → leave
no speech captured → "no speech" notice (never fail silently)
```

## Live voice-reply mode (`/voice`) — codebase is ahead of this doc

The adapter + runner ship a live voice→text reply system alongside the minutes flow:

- `/voice` slash command (owner-only): `join|channel` (join your VC, mode=all), `leave`, `on` (voice_only: TTS replies to voice input), `tts` (all: TTS to everything), `off` (**text only — text replies still fire**; TTS gating only), `status`.
- Flow: utterance (≥0.5s speech + trailing silence) → `VoiceReceiver.check_silence()` → `_process_voice_input` (adapter.py ~4882, faster-whisper STT) → `_voice_input_callback` → `_handle_voice_channel_input` (run.py:18837) → synthetic `MessageEvent(MessageType.VOICE)` sourced at the linked text channel (`_voice_text_channels[guild_id]`) → full agent pipeline → **TEXT reply lands in that text channel**. Transcript echoed as `**[Voice]** @user: ...` unless silent meeting.
- Per-chat modes persist in `<hermes_home>/gateway_voice_mode.json` as `discord:<chat_id>: mode` (legacy unprefixed keys are skipped with a warning — re-enable to rebuild).
- `voice_mode` gates TTS audio only (`_should_send_voice_reply`, run.py ~18925); text replies always flow for authorized voice input (presence-auth in `_auto_voice_guilds`, else `DISCORD_ALLOWED_USERS`).

## Config (config.yaml — write-protected, use `hermes config set`)

| Key (under `discord:`) | Meaning |
|---|---|
| `auto_join_voice_channels` | comma-separated voice IDs to watch |
| `voice_minutes_channel` | fallback minutes channel (when no map entry) |
| `voice_minutes_map` | `"voiceID:textID,voiceID:textID"` — per-channel routing; map keys auto-added to watched set |
| `auto_leave_grace_seconds` | wait after room empties before minutes+leave (10) |
| `silent_meeting` | true = no live transcripts, record-then-minutes |
| `voice_channel_inactivity_timeout_seconds` | 0 = never idle-leave mid-meeting |

Minutes template: `~/AppData/Local/hermes/minutes_template.md` (leader's format; edit file, no code change). Placeholders `{date}` `{time_started}` `{time_ended}` filled from wall clock; `[bracketed hints]` filled by the model.

## Local patches (hermes-agent git checkout)

`hermes update` WIPES these — re-apply from `git diff` (see references/patch-inventory.md for sites). Files: `plugins/platforms/discord/adapter.py`, `gateway/run.py`. Verify with real imports: `PYTHONPATH="$(pwd)" venv/Scripts/python verify_*.py` then delete the script.

## Pitfalls (all hit in production)

1. **Bot not in server** → nothing works (no slash, no voice). Check `curl -H "Authorization: Bot $TOKEN" https://discord.com/api/v10/users/@me/guilds`. Empty `[]` = invite never completed. Use manual OAuth2 URL: `https://discord.com/oauth2/authorize?client_id=<appid>&scope=bot+applications.commands&permissions=277062192192` (any server, needs Manage Server on the inviter).
2. **Privileged intents** (Message Content + Server Members) must be ON in Developer Portal or connect fails with `PrivilegedIntentsRequired`.
3. **Permissions integer must include Speak (bit 21)** for VC talking; missing send perms → `403 Missing Access` (error 50001). Current known-good integer: 277062192192.
4. **Presence-auth self-block**: meeting mode authorizes by physical presence in VC; the minutes trigger impersonates the owner who just LEFT → must `discard` guild from `_auto_voice_guilds` BEFORE firing `_voice_input_callback`, else minutes silently never fire.
5. **Short test hops** (<10s, little speech) capture nothing — utterance needs ≥0.5s audio + 1.5s trailing silence (receiver thresholds). Bot now posts a "no speech captured" notice instead of silence.
6. **STT is local faster-whisper** `large-v3-turbo` ≈ 0.40× realtime on Attila's PC (benchmarked — use for ETA math: `eta = speech_min*0.40 + 1`). Tagalog/Taglish supported. Groq free tier: 2,000 req/day, **25MB/file ≈ 13 min audio** (long meetings need chunking), ~2h audio/clock-hour.
7. **Slash commands & text chat** gated by `DISCORD_ALLOWED_USERS` (owner only). Meeting VC capture is presence-auth — everyone in the room is recorded regardless of allowlist.
8. **Gateway is a background process** (Windows Startup VBS) — desktop app can be closed; PC must be on + user logged in. **Watchdog added 2026-08-10**: Task Scheduler "Hermes Gateway Watchdog" runs `gateway-service/watchdog.cmd` every 5 min (StartWhenAvailable) — checks for any `gateway run` python process, then probes `http://127.0.0.1:8642/` (any HTTP code ≠ 000 = alive); spawns via `Hermes_Gateway.vbs` only when both checks fail. `schtasks /run /tn "Hermes Gateway Watchdog"` to test manually. NOTE: launchers set `HERMES_GATEWAY_DETACHED=1` → the CLI spawns a wrapper (venv python, exits ~100s) + detached worker (Python311, owns state pid + port 8642). **Two python processes = NORMAL, do not kill the Python311 one.** A real duplicate (both workers) shows as API port conflicts / the second instance dying — only then kill by PID.
9. **`gateway_state.json` lies after a crash** — it can say `discord: connected` while the PID is dead (unclean exits after machine sleep/shutdown leave stale state). When "bot is offline", verify PID liveness (`tasklist //FI "PID eq <pid>"`) and tail `gateway.log` — don't trust the state file. Both known deaths (Aug 6, Aug 9) were SIGKILL-style unclean exits right after posting minutes.
10. **Bot parked in an empty VC, no minutes** (hit Aug 10): the leave handler used to trust `vc.channel.members`, which can hold a **ghost member** when the bot joined mid-session pre-ready — the initial state sync replays each occupant as a "joined" event while the VoiceClient is still connecting, spraying `Auto voice state handler failed: Already connected to a voice channel` warnings, and the desynced cache then never shows the room empty. Fixed with `_vc_humans` (event-tracked occupancy) + a 5s sweep in the listen loop — but the fix needs a gateway restart to load. Old behavior = permanent wedge until restart, with the meeting's audio (in memory) lost.
9. **`silent_meeting` wins over `/voice` in watched channels.** The silent gate (adapter.py ~4849, `_silent_meeting_guilds`) accumulates raw audio and `continue`s — no live STT, no text replies, no transcript echo, regardless of voice_mode. With `silent_meeting: true` (current config.yaml), `/voice on` produces NO live replies in auto-joined channels — don't claim otherwise. Live replies require: (a) `/voice join` in a non-watched VC, or (b) `silent_meeting: false` (end-of-meeting minutes then generated from the agent session, NOT the full per-speaker transcript — weaker minutes).

## Activation (bot down → running)

1. `gateway_state.json` can be STALE after an unclean exit — still says `running`/`connected` while the PID is dead. Cross-check the PID: `tasklist //FI "PID eq <pid>"` (empty = dead). Unclean deaths log `exited UNCLEANLY (no exit path ran — SIGKILL / OOM / VM death)` and do NOT auto-recover.
2. Relaunch by running `"$HOME/AppData/Local/hermes/gateway-service/Hermes_Gateway.cmd"` as a background process. It IS the gateway — never kill it; close the tab with close_terminal instead (tab close ≠ process kill).
3. Launcher stdout is buffered WARNING noise — verify in the log, not the process tab: `tail ~/AppData/Local/hermes/logs/gateway.log` for `[Discord] Connected as Hermes minutes of meeting#8667` + `✓ discord connected`, then confirm fresh `updated_at` in gateway_state.json.

## Verification

- Logs: `~/AppData/Local/hermes/logs/gateway.log` — grep `AutoVoice|Voice state|SPEAKING|inbound message|response ready|Failed to send`.
- `hermes gateway restart` then confirm `Connected as` in log.
- Config parse check: `object.__new__(DiscordAdapter); DiscordAdapter._load_auto_voice_config(a)` via venv python.

See `references/patch-inventory.md` for exact patch sites and function names.

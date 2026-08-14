# Discord Bot Setup + Meeting-Minutes Recipe (Aug 2026 session)

Session reality-check: walked a first-time user through bot creation → invite → token config → gateway connect. The bot failed to connect once with PrivilegedIntentsRequired; user fixed intents in dev portal; reconnect is automatic.

## Step 0 — answer the "can I do this on other servers?" question

- Bot works in ANY server, not just ones you create. Inviting requires **Manage Server** permission on the target server (owner has it; admins can open the invite link themselves, or grant a role).
- Access control is by **user/role**, not by server — `DISCORD_ALLOWED_USERS`/`DISCORD_ALLOWED_ROLES` apply wherever the bot lives.
- 100+ servers → Discord forces verification for privileged intents. Irrelevant for personal/meeting use.

## Step 1 — Developer Portal (user does this, ~5 min)

1. discord.com/developers/applications → New Application → Bot tab → Reset Token → **copy (shown once)**.
2. **Privileged Gateway Intents → ON for Server Members + Message Content.** #1 cause of "bot online but never responds" and of the connect failure below.
3. Installation tab: use **Discord Provided Link** (auto-generates the OAuth2 URL from Default Install Settings; Custom Install Link is only for hand-built URLs — unnecessary). Default Install Settings → Guild Install:
   - Scopes: `bot` + `applications.commands` (the latter enables `/voice join`, `/voice tts` etc.)
   - Permissions: View Channels, Send Messages, Read Message History, Connect, Speak, Attach Files (+ Add Reactions for 👀/✅ feedback).
4. User ID: Discord → Settings → Advanced → Developer Mode → right-click own name → Copy User ID.

## Step 2 — Hermes side (agent does this)

```bash
# .env (append; .env IS writable by tools, config.yaml is NOT)
echo "DISCORD_BOT_TOKEN=<token>" >> ~/AppData/Local/hermes/.env
echo "DISCORD_ALLOWED_USERS=<userid>" >> ~/AppData/Local/hermes/.env

# config.yaml is write-protected from patch/write_file → use CLI
hermes config set stt.enabled true     # local faster-whisper = free, no key
hermes config set stt.provider local

hermes gateway start
tail ~/AppData/Local/hermes/logs/gateway.log | grep -E "Connecting to discord|✓ .* connected|✗ discord failed"
```

## Failure mode — PrivilegedIntentsRequired

Log sequence with a **valid** token but intents off:

```
INFO hermes_plugins.discord_platform.adapter: [Discord] Registered /skill command with 765 skill(s) via autocomplete
ERROR hermes_plugins.discord_platform.adapter: [Discord] Failed to connect to Discord: Shard ID None is requesting privileged intents...
discord.errors.PrivilegedIntentsRequired: ... explicitly enable the privileged intents within your application's page.
WARNING gateway.run: ✗ discord failed to connect
INFO gateway.run: Starting reconnection watcher for 1 failed platform(s): discord
```

- The `/skill command` registration line proves the token works — don't chase token issues.
- Fix = user flips the two intents in dev portal. Reconnection watcher retries; no restart needed.
- Also check: bot has `applications.commands` scope (missing slash commands → can't `/voice join`).

## Meeting-minutes recipe (the actual use case)

| Goal | Setting |
|------|---------|
| Bot reads a channel without @mentions | `DISCORD_FREE_RESPONSE_CHANNELS=<channel_id>` (or `discord.free_response_channels` in config.yaml) |
| Whole meeting = one shared session | `group_sessions_per_user: false` (default true isolates per-user sessions) |
| Voice transcription | `stt.enabled: true`, provider `local` (faster-whisper, free) |
| Bot joins voice meeting | `/voice join` in the meeting channel; `/voice leave` to stop. **With the auto-join patch** (hermes-local-patching) the bot joins watched VCs itself and `/voice join` is optional |
| Minutes | After the meeting, in the same session: "write the meeting minutes with action items" — full transcript is in session context. **With the patch:** delivered automatically after the room empties (grace period), no ask needed |
| Meeting-scoped persona | `discord.channel_prompts: {<channel_id>: "<minute-taker system prompt>"}` |

Notes:
- Free-response channels skip auto-threading → inline replies, lightweight chat.
- Text-meeting alternative: free-response channel + shared session absorbs the whole conversation, same "write minutes" ask at the end.
- Bot shows **offline** in Discord until the gateway runs (login item exists: Hermes_Gateway.vbs in Startup).
- Default `voice_channel_inactivity_timeout_seconds: 300` — bot auto-leaves VC after 5 min idle; set 0 to stay until `/voice leave`.

## Permissions integer decoding (user pastes a big number — what is it?)

The **Permissions integer** in the Installation tab is just the encoded sum of the permission checkboxes, baked into the invite URL. Users never type it anywhere; when they paste it, decode it to find what's missing:

```python
bits = [i for i in range(52) if 2252074692709376 >> i & 1]  # e.g. [10, 11, 16, 20, 38, 51]
```

Relevant bit table (bit = 2^bit): 6 Add Reactions · 10 View Channels · 11 Send Messages · 15 Attach Files · 16 Read Message History · 20 Connect · 21 **Speak** · 31 Use Application Commands · 38 Send Messages in Threads.

- **Missing Speak (21)** = bot joins voice + transcribes but can't talk back. Missing 6/15/31 = no reactions, no file sends, slash commands gated.
- **Fix = re-invite, don't re-create:** ticking the missing boxes and re-running the invite link **updates the bot's permissions in servers where it's already installed** — no removal needed. (Discord-generated defaults often omit Speak — e.g. the observed default `2252074692709376` was bits 10,11,16,20,38,51.)
- Decoy numbers users paste that are NOT the user ID: **Application ID** (bot's own ID, embedded in invite link) and **Public Key** (webhook signature verification, unused by Hermes). Neither needs configuring.

## Failure mode — connected but in ZERO servers (invite never completed)

**Symptom:** gateway log shows `[Discord] Connected as <bot>#xxxx` + `✓ discord connected`, but in Discord the bot has **no profile in the member list**, slash commands do nothing, voice never joins. User says "it doesn't even have a profile like a bot."

**Root cause:** the bot user is online but was never authorized into the server. The invite link was either never clicked by someone with Manage Server, or was generated with the wrong scopes (missing `bot` scope → Discord silently does nothing when authorized).

**Diagnosis — REST, not logs (gateway connection ≠ server membership):**
```bash
TOKEN=$(grep DISCORD_BOT_TOKEN ~/AppData/Local/hermes/.env | cut -d= -f2)
curl -s -H "Authorization: Bot $TOKEN" "https://discord.com/api/v10/users/@me/guilds"
# []  = in zero servers → invite never completed
# [{"id":...,"name":...}] = in the server → look elsewhere
```

**Fix — hand-built invite URL with explicit scopes (bypasses whatever the Installation tab generated):**
```
https://discord.com/oauth2/authorize?client_id=<APP_ID>&scope=bot+applications.commands&permissions=<INT>
```
`permissions` = the decoded integer (see below). Both scopes are REQUIRED: `bot` puts the user in the server, `applications.commands` enables slash commands. After authorization, re-verify with the same `guilds` curl.

**403 Forbidden (50001 Missing Access) on sends** = the bot is in the server but its role can't see/send in that channel — usually added with an old invite missing permissions. Verify with `curl /guilds/<id>/channels` (does the channel exist? any overrides?) + `curl /guilds/<id>/roles` (bot role integer), then re-run the invite link to update permissions in place.

## Slash command access control

By default only `DISCORD_ALLOWED_USERS` can invoke slash commands (others see them but get silently denied). Split admin/user tiers via the discord platform `extra` block: `allow_admin_from` (full commands) + `user_allowed_commands` (regular users, e.g. `status`, `voice join`); `/help` + `/whoami` always allowed. `/whoami` shows the caller's tier. Meeting voice input is NOT gated by this — the presence-auth patch (see hermes-local-patching) lets anyone physically in the VC be transcribed.

## STT accuracy tuning (Tagalog/Taglish meetings)

faster-whisper multilingual models auto-detect language (`language: ''`). Local ladder, all free:

| Model | Speed | Accuracy | Notes |
|-------|-------|----------|-------|
| `base` | instant | baseline | default; weak on accents/taglish |
| `large-v3` | ~1× realtime | max | ~3GB first-use download, heavy CPU |
| `large-v3-turbo` | **~8× faster** | ≈99% of large-v3 | **best default** — current config |

`hermes config set stt.local.model large-v3-turbo`. Verify the model name is accepted before switching (faster-whisper 1.x supports `large-v3-turbo`): load it once with the venv python (`WhisperModel('large-v3-turbo', device='cpu', compute_type='int8')`). First voice message after a model switch lags while the new model downloads+loads (~1.6GB for turbo); cached after. Next step up = cloud STT (Groq `whisper-large-v3-turbo` = near-instant, free tier, needs API key).

## Auto-join voice + auto-minutes — LOCAL PATCH (not upstream)

Hermes has **no native** auto-join-voice / auto-minutes feature. Implemented as a local patch to the git checkout (see `hermes-local-patching` skill — **`hermes update` wipes it, re-apply from `git diff`**). Files touched: `plugins/platforms/discord/adapter.py` (~230 lines) + `gateway/run.py` (~10 lines).

**Key hook points found in the code:**
- `DiscordAdapter.join_voice_channel(channel, text_channel_id=...)` — **built for programmatic joins** ("supports automatic/programmatic voice joins"); binds `_voice_text_channels[guild_id]` so transcriptions route to a text channel without `/voice join`.
- `adapter._voice_input_callback(guild_id, user_id, transcript)` — set by run.py; dispatches a synthetic VOICE MessageEvent through the FULL gateway pipeline (auth → session → agent → reply). This is how the bot "asks itself" to write minutes in the same session as the meeting.
- `on_voice_state_update` handler in the adapter fires for every VC join/leave; the auto-join hook must be called BEFORE the `bot_guild_ids` early-return (which returns when the bot isn't connected — the whole point of auto-join).

**Config keys (all `hermes config set`, read via `read_raw_config`):**
```yaml
discord:
  auto_join_voice_channels: "1531670932467220550,1531672533445906622"  # watched VCs
  voice_minutes_channel: 1534591025429876897      # where minutes get posted
  auto_leave_grace_seconds: 10                    # empty-room wait before minutes+leave
  voice_channel_inactivity_timeout_seconds: 0     # 0 = stay in VC until room empties
  silent_meeting: true                            # record-only; minutes at end, no live transcript
```

**Behavior:** someone enters a watched VC → bot joins + records. Room empty for grace → post ETA notice ("Meeting ended (duration X). Transcribing — estimated Y min"), transcribe once per speaker (large-v3-turbo), fire minutes prompt through `_voice_input_callback`, leave.

**Pitfall — presence-auth self-block (real bug hit):** the run.py auth gate for voice input was patched to "physical presence in the VC = authorized" (so meetings can record everyone, not just allowlisted users). But the minutes trigger impersonates the OWNER (`next(iter(self._allowed_user_ids))`) — who has just LEFT the channel. The presence check then rejects the trigger silently (`logger.debug` — looks like "nothing happened" after the meeting). **Fix: `self._auto_voice_guilds.discard(guild_id)` BEFORE firing the callback** so it falls through to the normal allowlist (owner is on it).

**Pitfall — live transcript spam:** in live mode each utterance posts `**[Voice]** <@user>: ...` to the channel AND runs the agent per utterance. For record-then-minutes use `silent_meeting: true`: the listen loop accumulates PCM per user (`_meeting_audio[guild_id][user_id] += pcm`, 48kHz stereo 16-bit = 192000 bytes/sec) instead of transcribing; at the end `_transcribe_meeting_audio()` converts each speaker's buffer via `VoiceReceiver.pcm_to_wav` + `transcribe_audio` (in a thread — large models are slow on CPU) and suppresses the `[Voice]` post in run.py via `_silent_meeting_guilds`.

**Verify-script pattern (FakeAdapter):** subclass `DiscordAdapter` overriding only the pieces the handler touches (`join_voice_channel`, `leave_voice_channel`, `user_in_voice_channel`), fake `_client`/`_voice_clients`/`_allowed_user_ids`; monkeypatch `tools.transcription_tools.transcribe_audio` and `VoiceReceiver.pcm_to_wav` (as `staticmethod(lambda ...)`). Gotchas: fake VC needs `.channel` + `.is_connected()`; fakes passed to `asyncio.to_thread` must be SYNC (async def fake breaks); `Path(__file__).parents[0]` not `[1]` when the script lives in the repo root.

**Meeting duration + ETA:** `_meeting_started[guild_id] = time.monotonic()` on join; duration formatted `_format_duration()` (h/m/s) and embedded in the minutes prompt + ETA post. **ETA must be MEASURED, not guessed** (user asked "is the estimation time actually estimate?" — the first 0.7× multiplier was a guess and was ~2× too conservative). Benchmark the exact model on the actual machine once, then hard-code the measured rate:

```bash
# 120s of 16kHz mono noise → time WhisperModel.transcribe → rate = elapsed/audio_secs
# Measured 2026-08-06 on this PC: large-v3-turbo int8 CPU ≈ 0.40× realtime
```

Current formula: `max(2, int(speech_secs/60 * 0.40 + 1))` (speech_secs from accumulated PCM at 192000 B/s; +1 min for summary generation). Re-measure after any model/hardware change.

## Minutes template (leader-provided format)

The bot must follow the TEAM'S template, not freeform. Template file: `~/AppData/Local/hermes/minutes_template.md` — user-editable, single source of truth; the bot reads it per meeting and the user can update it with no code change. Placeholders `{date}`, `{time_started}`, `{time_ended}` are filled programmatically from wall-clock (`_meeting_started_wall[guild_id] = time.time()` on join; ended = now); bracketed hints like `[numbered list of every member who spoke]` are filled by the model.

The minutes prompt (`_build_minutes_prompt()`) must include explicit REASONING rules, or the model echoes raw transcript:
1. "REASON, don't copy" — no verbatim transcript sentences, no filler/stutters/transcription artifacts
2. Members Present = distinct speakers, resolved to Discord display names (label format = names you get — tell user to keep display names in "Surname, Given" format if the template wants that)
3. Members Absent = only if explicitly mentioned; else the leader's stock phrase (e.g. "NO MEMBERS IS ABSENT")
4. Never invent details — uncovered sections get "Not discussed"/"TBA"
5. Include vote results/decisions per agenda item

## Groq STT free tier (if local is too slow)

`whisper-large-v3-turbo` free: **2,000 requests/day, 20/min**, throughput ~2h audio per clock-hour, **25MB max file per request** (dev tier 100MB). 16kHz mono WAV = 1.9MB/min → **25MB ≈ 13 min of audio per request** — a 2h meeting with one talkative speaker EXCEEDS the per-file cap; needs auto-chunking into ~10-min segments (a few extra requests, still trivial vs 2,000/day). Quota is never the issue for meetings; file size is. Local turbo has no file cap (2h meeting ≈ 15-20 min on this PC) — recommend local unless minutes must land in ~2 min.

## Multi-server routing (known limitation, NOT yet built)

Current config is a SINGLE `voice_minutes_channel` — all watched VCs route to one text channel. Adding a second server needs a per-voice→text mapping (`voice_minutes_mapping: "vc_id:text_id,vc_id:text_id"` or a dict) resolved at join time in `_handle_auto_voice_state`. Verify bot membership in the new server FIRST via `curl /users/@me/guilds` before configuring (the invite often silently never completes).

## "Are you sure it captures everyone?" — proof trail

Capture is unfiltered by the allowlist: packet buffering (`_buffers[ssrc].extend(pcm)`) has no auth check, SPEAKING events map ssrc→user for ALL speakers (`map_ssrc`), `check_silence()` returns completed utterances for every user, and the silent-mode accumulation runs BEFORE the `_is_allowed_user` gate. Allowlist only gates text/DMs/slash. One edge case: if the bot joins while someone is mid-sentence, Discord may not resend that person's SPEAKING event until their next utterance — that one sentence can be dropped (pre-existing, affects everyone equally).

## Bot runs without the desktop app

The gateway is a separate background process (Windows login item `Hermes_Gateway.vbs` in Startup) — closing the Hermes desktop app does NOT take the bot offline. It's tied to the PC being on + Windows session logged in; always-on hosting = VPS, not required for a normal workday.

## Windows restart quirk

`hermes gateway restart` drains the old process (~19 s teardown) before the new one logs. `gateway.log` looks dead/stale for ~30-60 s after the restart line; the new instance's `Starting Hermes Gateway...` and `Connected as` lines land later. Verify with `hermes gateway status` (PID alive) + `grep -E "Connected as" gateway.log`, not with an immediate tail.

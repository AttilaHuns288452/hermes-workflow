# Discord Meeting Minutes — Full Patch Source

Complete, copy-pasteable implementations for the meeting bot patches to `~/.hermes/hermes-agent/plugins/platforms/discord/adapter.py` and `~/.hermes/hermes-agent/gateway/run.py`.

## 1. State vars in `__init__` (adapter.py)

Add after `self._voice_fx_cfg` (around line 1154):

```python
# Meeting auto-join state: guilds the bot auto-joined (not /voice-joined)
self._auto_voice_guilds: set = set()
self._auto_leave_tasks: Dict[int, asyncio.Task] = {}
self._auto_voice_cfg: Dict[str, Any] = self._load_auto_voice_config()
```

## 2. Config loader `_load_auto_voice_config` (adapter.py)

Add this method before `_load_voice_fx_config`:

```python
def _load_auto_voice_config(self) -> Dict[str, Any]:
    """Read meeting auto-join settings from config.yaml.

    Keys (all under ``discord`` in config.yaml, NOT .env):
      auto_join_voice_channels: list or comma-string of voice channel IDs
      voice_minutes_channel:    text channel ID where minutes get posted
      auto_leave_grace_seconds: wait after room empties before minutes
      silent_meeting:           bool — if True, bot never speaks in VC, only records+minutes
      voice_minutes_map:        voice_channel_id:text_channel_id bindings
    """
    defaults: Dict[str, Any] = {
        "channels": set(),
        "minutes_channel": None,
        "grace_seconds": 60,
        "silent": False,
        "minutes_map": {},
    }
    try:
        from hermes_cli.config import read_raw_config
        cfg = read_raw_config() or {}
        d = cfg.get("discord") or {}

        raw_channels = d.get("auto_join_voice_channels", "")
        if isinstance(raw_channels, str):
            raw_channels = raw_channels.strip()
            if raw_channels:
                defaults["channels"] = {
                    int(c.strip()) for c in raw_channels.split(",") if c.strip()
                }
            else:
                defaults["channels"] = set()
        elif isinstance(raw_channels, list):
            defaults["channels"] = {int(c) for c in raw_channels}

        mc = d.get("voice_minutes_channel")
        if mc is not None:
            defaults["minutes_channel"] = int(mc)

        gs = d.get("auto_leave_grace_seconds")
        if gs is not None:
            defaults["grace_seconds"] = int(gs)

        defaults["silent"] = bool(d.get("silent_meeting", False))

        raw_map = d.get("voice_minutes_map", "")
        if isinstance(raw_map, str) and raw_map.strip():
            m = {}
            for pair in raw_map.split(","):
                pair = pair.strip()
                if ":" in pair:
                    k, v = pair.split(":", 1)
                    m[int(k.strip())] = int(v.strip())
            defaults["minutes_map"] = m
        elif isinstance(raw_map, dict):
            defaults["minutes_map"] = {int(k): int(v) for k, v in raw_map.items()}

    except Exception as e:
        logger.debug("Could not load discord auto-join config: %s", e)
    return defaults
```

## 3. Extended `on_voice_state_update` (adapter.py)

Replace the existing handler (around line 1472) with:

```python
async def on_voice_state_update(member, before, after):
    """Track voice channel join/leave events; auto-join meeting channels."""
    guild_id = member.guild.id
    # Ignore the bot itself
    if member == adapter_self._client.user:
        return
    # Ignore other bots
    if member.bot:
        return

    cfg = adapter_self._auto_voice_cfg
    auto_channels = cfg.get("channels", set())
    joined_ch = after.channel
    left_ch = before.channel

    # Auto-join: member (non-bot) joins a watched voice channel
    if (
        joined_ch is not None
        and joined_ch.id in auto_channels
        and guild_id not in adapter_self._voice_clients
    ):
        minutes_map = cfg.get("minutes_map", {})
        text_ch_id = minutes_map.get(joined_ch.id) or cfg.get("minutes_channel")
        silent = cfg.get("silent", False)
        logger.info(
            "[AutoVoice] %s joined watched channel %s — auto-joining (silent=%s)",
            member.display_name,
            joined_ch.name,
            silent,
        )
        # Schedule the join (don't await — we're in an event handler)
        asyncio.create_task(
            adapter_self._auto_join_meeting(guild_id, joined_ch, text_ch_id, silent)
        )
        return

    # Only track channels where the bot is connected
    bot_guild_ids = set(adapter_self._voice_clients.keys())
    if not bot_guild_ids:
        return
    if guild_id not in bot_guild_ids:
        return

    joined = before.channel is None and after.channel is not None
    left = before.channel is not None and after.channel is None
    switched = (
        before.channel is not None
        and after.channel is not None
        and before.channel != after.channel
    )

    if joined or left or switched:
        logger.info(
            "Voice state: %s (%d) %s (guild %d)",
            member.display_name,
            member.id,
            "joined " + after.channel.name if joined
            else "left " + before.channel.name if left
            else f"moved {before.channel.name} -> {after.channel.name}",
            guild_id,
        )

    # Auto-leave: if bot auto-joined this guild and channel is now empty of humans
    if guild_id in adapter_self._auto_voice_guilds:
        vc = adapter_self._voice_clients.get(guild_id)
        if vc and vc.is_connected():
            voice_ch = vc.channel
            if voice_ch:
                human_members = [m for m in voice_ch.members if not m.bot]
                if not human_members:
                    # Cancel any pending leave task
                    task = adapter_self._auto_leave_tasks.get(guild_id)
                    if task:
                        task.cancel()
                    grace = cfg.get("grace_seconds", 60)
                    logger.info(
                        "[AutoVoice] Channel empty — leaving in %ds (guild %d)",
                        grace,
                        guild_id,
                    )
                    adapter_self._auto_leave_tasks[guild_id] = asyncio.create_task(
                        adapter_self._auto_leave_and_minutes(guild_id, grace)
                    )
```

## 4. `_auto_join_meeting` and `_auto_leave_and_minutes` methods (adapter.py)

Add after `leave_voice_channel` (around line 4822):

```python
async def _auto_join_meeting(self, guild_id: int, voice_channel: Any, text_channel_id: int | None, silent: bool) -> None:
    """Auto-join a watched meeting voice channel and bind transcription routing."""
    try:
        ok = await self.join_voice_channel(voice_channel, text_channel_id=text_channel_id)
        if ok:
            self._auto_voice_guilds.add(guild_id)
            self._meeting_transcripts[guild_id] = []
            if silent:
                logger.info("[AutoVoice] Silent mode — bot will not speak in VC (guild %d)", guild_id)
            logger.info("[AutoVoice] Auto-joined %s (guild %d)", voice_channel.name, guild_id)
    except Exception as e:
        logger.error("[AutoVoice] Failed to auto-join guild %d: %s", guild_id, e)

async def _accumulate_transcript(self, guild_id: int, user_id: int, transcript: str) -> None:
    """Store a transcript line for the meeting summary."""
    if guild_id not in self._meeting_transcripts:
        self._meeting_transcripts[guild_id] = []
    self._meeting_transcripts[guild_id].append((user_id, transcript))
    logger.info("[AutoVoice] Accumulated transcript for guild %d: %d lines", guild_id, len(self._meeting_transcripts[guild_id]))

async def _post_meeting_summary(self, guild_id: int) -> None:
    """Post the accumulated meeting transcript to the minutes channel."""
    transcripts = self._meeting_transcripts.pop(guild_id, [])
    if not transcripts:
        logger.info("[AutoVoice] No transcripts to summarize (guild %d)", guild_id)
        return

    cfg = self._auto_voice_cfg
    minutes_map = cfg.get("minutes_map", {})
    text_ch_id = cfg.get("minutes_channel")
    vc = self._voice_clients.get(guild_id)
    if vc and vc.channel:
        voice_ch_id = vc.channel.id
        text_ch_id = minutes_map.get(voice_ch_id, text_ch_id)

    if not text_ch_id:
        logger.warning("[AutoVoice] No minutes channel configured for guild %d", guild_id)
        return

    lines = []
    for user_id, transcript in transcripts:
        lines.append(f"<@{user_id}>: {transcript}")
    full_transcript = "\n".join(lines)

    try:
        channel = self._client.get_channel(text_ch_id)
        if channel:
            header = "## 📝 Meeting Transcript\n\n"
            chunks = [full_transcript[i:i+1900-len(header)] for i in range(0, len(full_transcript), 1900-len(header))]
            await channel.send(f"{header}{chunks[0]}")
            for chunk in chunks[1:]:
                await channel.send(chunk)
            logger.info("[AutoVoice] Posted transcript to channel %d (%d chars)", text_ch_id, len(full_transcript))
    except Exception as e:
        logger.error("[AutoVoice] Failed to post transcript: %s", e)

async def _auto_leave_and_minutes(self, guild_id: int, grace_seconds: int) -> None:
    """Wait grace period; if still empty, leave the voice channel."""
    try:
        await asyncio.sleep(grace_seconds)
        vc = self._voice_clients.get(guild_id)
        if not vc or not vc.is_connected():
            return
        voice_ch = vc.channel
        if voice_ch:
            human_members = [m for m in voice_ch.members if not m.bot]
            if human_members:
                logger.info("[AutoVoice] Channel re-occupied — staying (guild %d)", guild_id)
                return
        logger.info("[AutoVoice] Grace elapsed, leaving voice (guild %d)", guild_id)
        # Post summary before leaving
        await self._post_meeting_summary(guild_id)
        await self.leave_voice_channel(guild_id)
    except asyncio.CancelledError:
        return
    except Exception as e:
        logger.error("[AutoVoice] Error in auto-leave for guild %d: %s", guild_id, e)
    finally:
        self._auto_leave_tasks.pop(guild_id, None)
        self._auto_voice_guilds.discard(guild_id)
```

## 5. Silent mode guard + transcript accumulation in `_handle_voice_channel_input` (gateway/run.py)

Before `await adapter.handle_message(event)` (around line 24857), add:

```python
# Silent meeting mode: bot records/transcribes only — no agent pipeline
if guild_id in getattr(adapter, "_auto_voice_guilds", set()):
    cfg = getattr(adapter, "_auto_voice_cfg", {})
    if cfg.get("silent", False):
        logger.info("[AutoVoice] Silent mode — skipping agent pipeline (guild %d)", guild_id)
        # Accumulate transcript for meeting summary
        await adapter._accumulate_transcript(guild_id, user_id, transcript)
        return
```

## 6. STT Model Setup

```yaml
stt:
  provider: local
  local:
    model: large-v3-turbo
```

Pre-download the model (avoids first-meeting delay):
```bash
python3 -c "from faster_whisper import WhisperModel; WhisperModel('large-v3-turbo', device='cpu', compute_type='int8')"
```

## Testing the Patch

```bash
# Verify syntax
python3 -c "import ast; ast.parse(open('plugins/platforms/discord/adapter.py').read()); print('adapter.py: OK')"
python3 -c "import ast; ast.parse(open('gateway/run.py').read()); print('run.py: OK')"

# Restart gateway
hermes gateway restart

# Watch logs
tail -f ~/.hermes/logs/gateway.log | grep AutoVoice
```

## Re-applying After `hermes update`

`hermes update` overwrites the local checkout. After every update:

1. Re-apply the three insertions to `adapter.py` and one to `gateway/run.py`
2. `hermes gateway restart`
3. Verify with `grep AutoVoice ~/.hermes/logs/gateway.log`

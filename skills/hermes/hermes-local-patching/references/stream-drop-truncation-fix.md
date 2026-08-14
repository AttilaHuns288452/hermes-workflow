# Stream-drop truncation fix — "Response remained truncated after 4 continuation attempts"

## Symptom
User sees `Response remained truncated after 4 continuation attempts` (from
`agent/conversation_loop.py`) even though the response was not actually
length-truncated. The desktop log (`logs/desktop.log`) shows the signature:
`⚠️ Stream interrupted by network error (finish_reason='length' on
partial-stream-stub)` repeated, and the session transcript shows the loop
injecting `[System: The previous response was cut off by a network error
mid-stream...]` prompts to which the model replies "nothing more to add" —
the turn dead-ends.

## Root cause
- Provider stream drops mid-generation → `chat_completion_helpers.py`
  `build_partial_stream_stub()` tags the response `PARTIAL_STREAM_STUB_ID`
  with `finish_reason='length'` (`FINISH_REASON_LENGTH`).
- The text-continuation path treated that as an output-cap truncation:
  appended the partial + a "continue" prompt (`_get_continuation_prompt`
  stub variant), burning all 4 `length_continue_retries` on a flaky primary.
- Contributing factors found on this install: `fallback_providers: []`
  (no recovery route) and no `model.context_length` (compression threshold
  0.5 never fired until ~500K input; the failing session was at 451,992
  input tokens).

## Fix shipped 2026-08-11 (`agent/conversation_loop.py`)
1. **Plain network stubs re-run the call from scratch** — no partial append,
   no continuation prompt (a dropped stream's partial is unreliable and the
   "continue" prompt invites a re-answer). Mirrors the tool-call stub path.
   Stub-with-`_dropped_tool_names` (oversized tool-call timeout) keeps the
   chunked-retry guidance — that prompt is pure instruction, no partial needed.
2. **2 consecutive stubs escalate to the fallback chain** — new block after
   the content-filter stall block (~line 2984): `stub_stream_streak >= 2`
   and `agent._fallback_index < len(agent._fallback_chain)` →
   `agent._try_activate_fallback()`, roll back partials, reset counters,
   `_retry.restart_with_rebuilt_messages = True`, break. The retry loop
   re-issues the call against the fallback runtime.
3. **Honest dead-end**: when ALL retries were stubs, error becomes
   "Stream kept dropping (network/provider issue) after 4 retries...".
   Genuine output-cap truncation keeps the original message.
4. `stub_stream_streak` counter initialized at the turn top, reset on
   fallback activation and on turn success.

## Config companion
```yaml
model:
  context_length: 524288        # compression at ~256K instead of ~500K
fallback_providers:
  - provider: opencode-zen
    model: deepseek-v4-flash-free
```
Pitfall: `hermes config set fallback_providers '[...]'` stores a STRING —
surgical line-level python edit needed, then verify `hermes fallback list`.

## Verification
- `tests/run_agent/test_partial_stream_finish_reason.py` (15 tests) — the
  stub-continuation test asserts re-run semantics (2 API calls, no continue
  prompt, no partial in messages, final response = regenerated full answer).
- Live: `hermes -z "<long-generation prompt>"` on the flaky provider;
  grep `logs/agent.log` tail for `Requesting continuation` /
  `re-running call` / `remained truncated` — expect 0.
- Restart the desktop backend (`hermes_cli.main serve`) to load patched code.

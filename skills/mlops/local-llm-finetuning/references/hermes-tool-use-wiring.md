# Hermes + local Ollama model: tool-use wiring

The context/registration plumbing needed before a locally-registered model can
call tools from `hermes chat`.

## Three-place context agreement

Hermes refuses tool use under a 64k runtime window (`num_ctx` >= 65536
required). THREE places must agree, or you get
`Context length exceeded (N tokens). Cannot compress further.` with a tiny N:

1. Ollama Modelfile `PARAMETER num_ctx` (or per-request `options.num_ctx`)
2. `model.ollama_num_ctx` in `~/.hermes/config.yaml`
3. the model's entry under `custom_providers[].models.<tag>.context_length`
   (a YAML list entry — the model must also appear in the provider's `models`)

`discover_models: true` finds the tag but does NOT create the catalog entry —
add it yourself. `config.yaml` is refused by the patch tool by design; use
`hermes config set` or a terminal script.

## Prompt budget is the real limit

- Hermes system prompt + tool schemas + one preloaded 27KB skill (`-s`) =
  ~67k tokens — over a 65k window. Preload a condensed quickref (`-s`,
  ≤3KB) and keep the full skill for on-demand `skill_view`.
- On a 4GB card 65k works and 131k OOMs (measured).
- An OOM at high `num_ctx` LOOKS like a hang: the model is evicted
  mid-request and the client waits on a dead stream. Diagnose with
  `nvidia-smi` (0% + no model resident) and `/api/ps` (empty) instead of
  waiting.
- Prefill cost: every turn re-sends the full prompt; ~67k on a 3050 is
  minutes per turn. Large windows are capacity, not speed — keep
  local-model sessions lean.
- Run-time budget: this class of card generates ~5 tok/s; one 4-6-tool
  verification run takes 15-45 min. A foreground call that looks dead usually
  is not — run long harness/chat runs as tracked background commands or with a
  1500s+ timeout, and judge completion by the session's tool rows, not by the
  clock.

## Multi-turn tool sessions vs. context compaction

- The compressor threshold is printed in the session-start log
  (`Context compressor initialized: … threshold=N`; e.g. 55,705 on a
  65,536 window). When a multi-turn tool session's prompt sits near that
  line, compaction fires mid-run and strips the tool schemas: the model
  then calls tools through the wrong invoker (`'<tool>' is not a
  deferrable tool`) or as shell commands (`command not found`) while its
  prose still reports success.
- Keep the WHOLE multi-turn session under the threshold: trim the toolset
  (`hermes chat -t <toolset>`, e.g. `-t packet-tracer` instead of the
  default ~42 toolsets — the deferred-tool catalog in the system prompt
  is thousands of tokens) and preload a condensed skill. Free prompt
  budget by trimming tools/skills, not by raising `num_ctx` (OOM note
  above).

## Verify tool calls EXECUTED — the model's prose is not proof

After any tool-session test, read the session's tool rows directly:

```bash
sqlite3 ~/.hermes/state.db "SELECT role, substr(content,1,200) FROM messages
  WHERE session_id='<id>' AND role='tool';"
```

Every call must have a real result, not an error string. A model that
narrates "done" in prose can have every call errored or skipped — check
the rows before reporting the capability as working.

## Registration lifecycle

- `ollama create` does not affect the currently loaded instance — unload
  first (`{"keep_alive": 0}` posted to `/api/chat`), confirm via `/api/ps`,
  then re-create and confirm `context_length` on the reloaded model.
- Invocation: `hermes chat -m <tag> --provider ollama`; `--no-context`
  prevents the old transcript from re-filling the window on every prompt.

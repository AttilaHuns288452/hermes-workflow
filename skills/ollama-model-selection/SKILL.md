---
name: ollama-model-selection
description: Best local Ollama model per device. Verify tags first.
triggers:
  - local model
  - ollama
  - which model
  - best local model
  - pull model
  - vram
---

# Ollama Model Selection

Use when the user asks which local (Ollama) model fits their machine or stack, or when `ollama pull` fails.

## Rule 1: Probe the device first

Never guess specs. Read them in one call:

```bash
wmic memorychip get capacity; wmic cpu get name; wmic path win32_VideoController get name
```

The binding constraint is VRAM: 4GB → 7–8B Q4 is the ceiling; 14B/30B MoE becomes CPU-bound (3–5 tok/s) and is not worth it.

## Rule 2: Verify the tag BEFORE recommending or pulling

`ollama pull` error `pull model manifest: file does not exist` = the tag doesn't exist. Do NOT retry; verify:

- Reliable: `web_extract` on `https://ollama.com/library/<model>/tags` (lists real tags + sizes).
- Unreliable: the registry API `https://registry.ollama.ai/v2/library/<model>/tags/list` (returned empty in-session).

Example of a real mistake: recommended `qwen3-coder:8b` — it does NOT exist. The qwen3-coder library only ships 30b/480b; qwen3-coder-next is 52GB. On small GPUs, `qwen2.5-coder:7b` remains the best coder-tuned local model.

## Size ladder (4GB VRAM rig, Q4_K_M)

| Model | Size | tok/s | Use for |
|---|---|---|---|
| qwen2.5-coder:1.5b | ~1GB | 60–80 | autocomplete only (Continue) |
| qwen2.5-coder:3b | ~2GB | 35–50 | skip — not smart enough for real work, same setup cost as 8b |
| qwen2.5-coder:7b | 4.7GB | 12–18 | real component work, 2–4 file edits |
| qwen3:8b | ~5GB | 10–15 | best generalist at this size |
| 14b / 30b MoE | 9–19GB | 3–5 | too slow on 4GB VRAM |

Quality jumps are non-linear: 1.5→3b small, 3→7b big, 7→8b meaningful (newer training).

## Honest framing

A 7–8B local model ≈ decent junior coder — fine for offline/private quick edits and autocomplete, but cloud (e.g. DeepSeek V4 Flash) remains the right tool for real feature work. Say this instead of overselling the local model.

## Pitfalls

- Recommending a tag you haven't verified = failed pull + wasted user time. Verify first, always.
- 1.5B handles single-function snippets; it hallucinates multi-file consistency (invents props parents never pass). Never recommend it for component work.
- Cap context at 8–16k on 4GB VRAM — KV cache overflow makes re-prompts painfully slow.

## References

- `references/model-fit-details.md` — session-verified sizing notes and qwen3-coder library facts.

# Model fit details (session-verified, Aug 2026)

Verified on user's device: RTX 3050 Laptop 4GB VRAM, i5-11400H, 24GB RAM (probed via wmic).

## qwen3-coder library facts (verified via ollama.com/library)

- `qwen3-coder` ships ONLY 30b, 480b, 480b-cloud tags. **No 8b/14b exists** — recommending
  `qwen3-coder:8b` fails with `pull model manifest: file does not exist`.
- `qwen3-coder-next` = 52GB (q4_K_M) / 85GB (q8_0) — too big for small GPUs.
- Therefore on 4GB-VRAM rigs the best coder-TUNED local model remains `qwen2.5-coder:7b`.
  The generalist upgrade at the same size is `qwen3:8b` (~5GB, newer training).

## Verification paths

- ollama.com/library/<model>/tags — reliable (web_extract shows tag table with sizes).
- registry.ollama.ai/v2/library/<model>/tags/list — returned empty for qwen3 models in
  session; treat as unreliable.
- The `file does not exist` pull error is a TAG problem, not a network problem. Verify
  before retrying; retrying the same bad tag always fails.

## Size ladder rationale

- 1.5b → 3b: small quality step (both snippet-level models).
- 3b → 7b: large step (7b handles multi-file component work).
- 7b → 8b: meaningful step (newer training, better instruction following).
- >8b on 4GB VRAM: CPU offload dominates → 3–5 tok/s, unusable interactively.

## 1.5b capability ceiling (for honest framing)

Fine: single-function snippets, autocomplete, regex, code explanation.
Not fine: multi-file work — hallucinates props/imports that don't exist, reaches for
React 16-era patterns, invents Tailwind classes. 8B is the floor for real component work.

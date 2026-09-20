---
name: local-llm-runtimes
description: "Ollama local LLMs - custom-arch fork builds, CUDA backends."
---

# Local LLM Runtimes (Ollama)

Covers stock Ollama plus vendor-forked Ollama builds for custom model
architectures, and CUDA backend builds so the NVIDIA GPU is actually used.

## Workflow

1. **GPU check first.** Before accepting any CPU-only path, run
   `nvidia-smi --query-gpu=driver_version,name --format=csv`. Never default
   to CPU when a working NVIDIA GPU exists.
2. **`unknown model architecture: '<arch>'`** means stock Ollama cannot parse
   the weights. Check the model's ollama.com page "Run with Ollama" section
   for a vendor fork-build recipe and follow it — see
   `references/ollama-custom-arch.md`.
3. **CUDA builds:** install `nvidia-cuda-toolkit` (foreground — background
   runs have no TTY for the sudo password), enable the matching
   `OLLAMA_LLAMA_BACKENDS`, and pin `CMAKE_CUDA_ARCHITECTURES` to the local
   GPU if the toolkit predates the requested archs (details in reference).
4. **Go toolchain:** Ollama main needs bleeding-edge Go; distro apt Go is
   too old. Install the official tarball and let GOTOOLCHAIN auto-fetch.
5. **Quote VRAM honestly:** a model larger than VRAM only partial-offloads.
   Never promise full-GPU speed in that case.
6. **CUDA auto-start (benefit):** When Ollama is installed as a systemd service (`systemctl enable ollama`), CUDA works automatically on boot — no manual GPU selection needed. Models that fit in VRAM get GPU-accelerated automatically; oversized models fall back to CPU. Verify with `nvidia-smi` after loading a model.
7. **CLI model discovery:** CommandCode and OpenCode won't auto-detect local Ollama models. Setup:
   - **CommandCode**: `commandcode /connect` → add provider `http://localhost:11434/v1` (no key)
   - **OpenCode**: `opencode providers login http://localhost:11434/v1`
   - **Hermes**: Already discovers via `discover_models: true`

## References

- **[ollama-custom-arch.md](references/ollama-custom-arch.md)** — fork-build recipe, CUDA backend flags, old-nvcc arch pitfall, Go/sudo notes
- **[ollama-serve-benchmark.md](references/ollama-serve-benchmark.md)** — dual-server ports/stores, SIGPIPE, clean benchmark protocol, VRAM squatters, thinking-model budgets, quantize-to-fit

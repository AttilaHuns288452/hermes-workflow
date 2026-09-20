# Ollama: models with unsupported architectures (custom fork builds)

When `ollama pull <model>` succeeds but `ollama run` fails with
`error loading model: unknown model architecture: '<arch>'`, stock Ollama
cannot parse that arch. Check the model's ollama.com page "Run with Ollama"
section — vendors shipping new archs (e.g. iFlyTek Spark-X2.5 `spark2_5`)
document a forked-runtime build there. Follow the vendor recipe, not stock.

## Vendor fork-build recipe (Spark-X2.5 pattern, from ollama.com model page)

```bash
git clone https://github.com/XHToken/llama.cpp.git llama.cpp-spark
git clone https://github.com/ollama/ollama.git ollama-spark
cd ollama-spark
export OLLAMA_LLAMA_CPP_SOURCE="$(cd ../llama.cpp-spark && pwd)"
cmake -S . -B build
cmake --build build --parallel 8
./ollama serve   # then in another shell: ./ollama run <model>
```

## GPU-first: check for NVIDIA before accepting a CPU-only build

Defaulting to a CPU build when the box has a working NVIDIA GPU wastes the
GPU (user correction, 2026-09). Step 0 is always:

```bash
nvidia-smi --query-gpu=driver_version,name --format=csv
```

If a GPU is present, enable the matching backend at configure time. This
repo's superbuild takes `OLLAMA_LLAMA_BACKENDS` (see `cmake/local.cmake`):

```bash
cmake -S . -B build -DOLLAMA_LLAMA_BACKENDS="cuda_v12"   # matches CUDA 12.x toolkit
```

Needs `nvidia-cuda-toolkit` (`nvcc`) installed: `sudo apt install -y
nvidia-cuda-toolkit`. Run sudo installs in the FOREGROUND — background runs
have no TTY and fail with "a terminal is required to read the password".

## Old nvcc vs new CUDA arch flags

Verified root cause (2026-09): the fork's ggml requests archs up to
`compute_100`/`compute_120` (Blackwell), but nvcc from CUDA 12.0 aborts
compiler detection with `nvcc fatal: Unsupported gpu architecture
'compute_100'`. Fix: pin archs to the local GPU, forwarded to the nested
build by the superbuild (`CMAKE_CUDA_ARCHITECTURES`, see `cmake/local.cmake`
`ollama_cache_arg_is_set` + `ollama_append_cache_arg_if_set`):

```bash
# RTX 3050 Mobile (Ampere) = sm_86
cmake -S . -B build -DOLLAMA_LLAMA_BACKENDS="cuda_v12" -DCMAKE_CUDA_ARCHITECTURES=86
```

Validated end-to-end 2026-09-04 (RTX 3050 Mobile, sm_86, CUDA 12.0 toolkit):
`libggml-cuda.so` builds, FP16 Spark-X2.5-4B loads with 10/37 layers offloaded
(4.1 tok/s); Q6_K quant (3.2GB) loads 26/37 layers (14.1 tok/s). Serve +
benchmark hygiene lives in `ollama-serve-benchmark.md`.

## Go toolchain

Ollama main tracks bleeding-edge Go (`go 1.26.0` in go.mod). Distro apt
Go (1.22 on Ubuntu 24.04) is too old — install the official tarball
(go.dev/dl) and let GOTOOLCHAIN auto-fetch the exact toolchain (observed:
go1.25.1 auto-downloaded go1.26.0 during configure).

## VRAM honesty

An 8.2GB Q4 model does NOT fit a 4GB RTX 3050 fully — llama.cpp partial-
offloads (~half the layers to GPU, rest to system RAM). Still far faster
than CPU-only, but quote it as partial offload, never full-GPU speed.

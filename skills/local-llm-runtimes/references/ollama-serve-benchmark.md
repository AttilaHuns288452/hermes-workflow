# Ollama: serving a fork build + honest benchmarking

Companion to `ollama-custom-arch.md` (build side). This covers running the
fork serve alongside stock Ollama and measuring tok/s without fooling
yourself. All verified 2026-09-04 (RTX 3050 4GB, i5-11400H).

## Two servers, two stores

- Stock Ollama runs as user `ollama` (systemd), models in
  `/usr/share/ollama/.ollama/models` (root-only). Fork serve as the user
  sees `~/.ollama/models` — empty by default (`/api/tags` → `[]`).
- Cheapest fix when the blob already exists in the stock store: copy, don't
  re-download — `sudo cp -rn <stock>/models/. ~/.ollama/models/ && sudo
  chown -R $(whoami) ~/.ollama/models` (foreground: sudo needs a TTY).
- Fork serve needs its own port: `OLLAMA_HOST=127.0.0.1:11435 ./ollama
  serve`. Point the fork CLI at it too: `OLLAMA_HOST=127.0.0.1:11435
  ./ollama create/run/...`.
- NEVER pipe serve stdout into `head` (e.g. `| head -30`): SIGPIPE kills
  the server once the pipe fills. Redirect to a log file instead:
  `./ollama serve >> /tmp/ollama-spark.log 2>&1` (background, silent is
  fine — it never exits).

## Benchmark protocol (clean numbers)

```bash
# one model at a time; unload between runs or VRAM contention contaminates results
curl -s http://127.0.0.1:PORT/api/generate -d '{"model":"M","keep_alive":0}'
curl -s http://127.0.0.1:PORT/api/generate -d '{"model":"M","prompt":"...","stream":false,"options":{"num_predict":128}}' \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['eval_count']/(d['eval_duration']/1e9), 'tok/s')"
```

- Metric: `eval_count` / `eval_duration` = decode tok/s; `prompt_eval_*` =
  prefill. Same prompt + same `num_predict` across models or don't compare.
- Before trusting a slow number, check for VRAM squatters: `nvidia-smi
  --query-compute-apps=pid,process_name,used_memory --format=csv`.
  Orphaned `llama-server` processes from dead serve sessions hold GBs and
  silently cut the next load's offload ratio (observed: 934MiB free →
  0/37 layers; after kill: 3.5GiB free → 10/37). Kill orphans, unload,
  reload, re-measure.
- Offload truth is the LATEST `offloaded N/M layers to GPU` line in the
  serve log — `grep ... | tail`, never `-m1` (stale first match lies).
- Confirm with `nvidia-smi` memory.used, not vibes.

## Thinking models need headroom

Hybrid thinking models (qwen3.5) put reasoning in the `thinking` field and
`response` may be empty with `done_reason: length` if `num_predict` is too
small. Give 3-4x the token budget; when extracting code fences, prefer
`response` over `thinking` (drafts there may be indented fragments).

## Quantize-to-fit workflow (speed closest to full quality)

FP16 4B weights (7.8GB) only partial-offload on 4GB VRAM. Q6_K (~3.2GB,
~6.5 BPW, near-lossless) is the sweet spot over Q8_0 (still partial) and
Q5 (dumber). The fork build already contains `llama-quantize`:

```bash
BLOB=$(grep -a -m1 -o -E 'blobs/sha256-[0-9a-f]+' /tmp/ollama-spark.log)  # or from load line
~/ollama-spark/build/lib/ollama/llama-quantize ~/.ollama/models/$BLOB ~/spark-q6k.gguf Q6_K
printf 'FROM /home/attila/spark-q6k.gguf\n' > /tmp/Modelfile.spark
OLLAMA_HOST=127.0.0.1:11435 ~/ollama-spark/ollama create spark-q6k -f /tmp/Modelfile.spark
```

Measured: FP16 4.1 tok/s (10/37 layers) → Q6_K 14.1 tok/s (26/37).
Keep the FP16 blob until the quant proves itself, then delete to reclaim GBs.

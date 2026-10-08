---
name: local-llm-finetuning
description: "Use when fine-tuning local LLMs for tool use."
---

# Local LLM Fine-Tuning (small models, tool use)

Adapt a local model (~1-4B) to drive one tool domain (usually a tool/MCP server):
the correct APIs, argument shapes, and decision habits. Everything is
evaluate-first: claims come from bench logs, never from training loss.
When the model must "know" a tool domain in an agent runtime, prefer injecting
docs as a skill and training only behavior — knowledge in weights is
unfixable without retraining.

## Procedure

1. **Build the eval harness BEFORE anything else.** Loop the candidate model
   against the real tool server (Ollama `/api/chat` `tools=` format over a
   stdio JSON-RPC MCP broker). Curate the tool schemas to 10-20 relevant
   ones — the full list (60+) is noise for a small model. Per-call logging
   to a run log, deterministic seeds where available. Template:
   `templates/mcp_bench_harness.py`.
2. **Run the baseline in escalating conditions, 3+ runs each:**
   - bare — what the weights already know
   - +docs (verified API reference in the system prompt) — whether knowledge alone fixes it
   - +docs+strict (state echo rule: "after ANY command call, request its output
     before deciding") — whether reasoning scaffolding fixes it
   Fine-tune only for what +docs does NOT fix (format/habit problems).
3. **Dataset = decision windows, not trajectories.** One sample = conversation
   prefix ending at exactly one correct assistant tool call, capped to the
   training sequence length (~480 est tokens for seq 512). Sources:
   - correct recipe/task walkthroughs with randomized device names, IPs, facts
   - error-recovery pairs MINED from baseline logs: the model's own failures
     relabeled with the correct next call
   100-300 samples shape behavior; they do not teach knowledge. Validate by
   rendering `apply_chat_template` over one sample before training.
   Pitfalls: Qwen chat templates iterate `tool_call.arguments|items` — pass a
   **dict**, never a JSON string (template crash). `system` must be a
   `{role, content}` message, not a bare string (schema inference crash).
4. **Train: unsloth 4-bit QLoRA on 4GB VRAM.** seq 512, r=8, lora_alpha 16,
   grad-accum 8, adamw_8bit, batch 1,
   `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`.
   - Triton autotuner reserves 256MB scratch and OOMs at `loss.backward()` on
     a 4GB card: monkeypatch
     `triton.backends.nvidia.driver.CudaDriver.get_empty_cache_for_benchmark`
     to a 32MB buffer before `trainer.train()`.
   - Qwen3.5-family is linear-attention (fla kernels) — the autotuner triggers
     for these. Expect roughly 20s/step at seq 512 on a 3050.
   - Loss on format data falls 2.3 to 0.008 within ~40 steps. Match max_steps
     to dataset size (13 steps/epoch at accum 8 on 104 samples).
5. **Export GGUF.** `save_pretrained_gguf`, merged on CPU if the agent process
   holds VRAM (GPU merge OOMs; CPU merge just takes minutes).
   - unsloth appends `_gguf` to the output dir name.
   - Prebuilt `llama-cpp-python` wheels lag — unsloth bundles conversion;
     do not pip-install it as a prerequisite.
   - Disk: HF save ~9GB + GGUF ~2.5GB; delete merged safetensors before
     `ollama create` (which copies another full GGUF).
6. **Register + wire.** `ollama create -f Modelfile` (set `PARAMETER num_ctx`).
   For Hermes tool use the context must agree in three places — see
   `references/hermes-tool-use-wiring.md`.
7. **Re-run the SAME harness** (same prompts, conditions, 3+ runs each) and
   report a per-condition table of observed behaviors. Claim only what the
   logs show.

## Standing rules

- **Training loss proves nothing.** The bench log is the only evidence. A run
  that wedges in a tool loop is a FAIL with a named failure mode.
- **Known ceiling at this scale:** knowledge and argument shapes transfer
  well; repetition compulsion and long-horizon convergence do not fix with
  ~100 samples on 4B params. State this ceiling in any report instead of
  implying the model is agent-grade.
- **Weights vs docs:** habits belong in weights (which API, which shape,
  state tracking); knowledge belongs in docs/skills the runtime can inject.
- **Kill the harness on a wedge** (turn cap + identical-call counter); a hung
  run eats the GPU for nothing.

## References

- `references/hermes-tool-use-wiring.md` — context/registration plumbing for
  Hermes tool use. Harness template: `templates/mcp_bench_harness.py`.

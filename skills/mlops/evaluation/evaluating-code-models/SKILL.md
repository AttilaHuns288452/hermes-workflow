---
name: evaluating-code-models
description: Benchmark code-generation models with reproducible pass@k tasks.
version: 0.1.0
author: Orchestra Research, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [upstream-adaptation, evaluating-code-models]
    upstream_repository: "https://github.com/foryourhealth111-pixel/Vibe-Skills"
    upstream_commit: "ddcaa2affca93c1efe026d008b6b93709e5fb7e2"
---

# BigCode Evaluation Harness - Code Model Benchmarking

## Quick Start

BigCode Evaluation Harness evaluates code generation models across 15+ benchmarks including HumanEval, MBPP, and MultiPL-E (18 languages).

**Safety gate**: Never execute model-generated code on the host. Use `--generation_only` first, then run evaluation inside an isolated sandbox such as a locked-down container with no network, read-only filesystem, resource limits, and a disposable temporary directory. Treat `--trust_remote_code` as an additional supply-chain risk.

**Installation**:
```bash
git clone https://github.com/bigcode-project/bigcode-evaluation-harness.git
cd bigcode-evaluation-harness
pip install -e .
accelerate config
```

**Evaluate on HumanEval** (two stages — generate on host, execute only in a sandbox):
```bash
# Stage 1 (host, safe): generate solutions only — no code is executed
accelerate launch main.py \
  --model bigcode/starcoder2-7b \
  --tasks humaneval \
  --max_length_generation 512 \
  --temperature 0.2 \
  --n_samples 20 \
  --batch_size 10 \
  --generation_only \
  --save_generations \
  --save_generations_path generations_humaneval.json

# Stage 2 (sandbox only): execute and score inside a locked-down container
# (no network, read-only fs, resource limits, disposable tmp). Never run
# --allow_code_execution on the host.
docker pull ghcr.io/bigcode-project/evaluation-harness
docker tag ghcr.io/bigcode-project/evaluation-harness evaluation-harness
docker run --network=none --read-only --tmpfs /tmp \
  -v $(pwd)/generations_humaneval.json:/app/generations.json:ro \
  -it evaluation-harness python3 main.py \
  --model bigcode/starcoder2-7b \
  --tasks humaneval \
  --load_generations_path /app/generations.json \
  --allow_code_execution \
  --metric_output_path /tmp/humaneval_results.json
```

**View available tasks**:
```bash
python -c "from bigcode_eval.tasks import ALL_TASKS; print(ALL_TASKS)"
```

## Common Workflows

### Workflow 1: Standard Code Benchmark Evaluation

Evaluate model on core code benchmarks (HumanEval, MBPP, HumanEval+).

**Checklist**:
```
Code Benchmark Evaluation:
- [ ] Step 1: Choose benchmark suite
- [ ] Step 2: Configure model and generation
- [ ] Step 3: Generate on host, then score in a sandbox
- [ ] Step 4: Analyze pass@k results
```

**Step 1: Choose benchmark suite**

**Python code generation** (most common):
- **HumanEval**: 164 handwritten problems, function completion
- **HumanEval+**: Same 164 problems with 80× more tests (stricter)
- **MBPP**: 974 crowd-sourced problems, entry-level difficulty (500-problem test split, indices 11-511)
- **MBPP+**: 399 curated problems with 35× more tests

**Multi-language** (18 languages):
- **MultiPL-E**: HumanEval/MBPP translated to C++, Java, JavaScript, Go, Rust, etc.

**Advanced**:
- **APPS**: 10,000 problems (introductory/interview/competition)
- **DS-1000**: 1,000 data science problems across 7 libraries

**Step 2: Configure model and generation**

All host-side commands use `--generation_only` (no execution). Scoring with
`--allow_code_execution` happens only inside a sandbox — see Step 3.

```bash
# Standard HuggingFace model
accelerate launch main.py \
  --model bigcode/starcoder2-7b \
  --tasks humaneval \
  --max_length_generation 512 \
  --temperature 0.2 \
  --do_sample True \
  --n_samples 200 \
  --batch_size 50 \
  --generation_only \
  --save_generations \
  --save_generations_path generations_humaneval.json

# Quantized model (4-bit)
accelerate launch main.py \
  --model codellama/CodeLlama-34b-hf \
  --tasks humaneval \
  --load_in_4bit \
  --max_length_generation 512 \
  --generation_only \
  --save_generations \
  --save_generations_path generations_humaneval.json

# Custom/private model
# --trust_remote_code runs arbitrary code from the model repo — a supply-chain
# risk on top of generated-code execution; audit the model repo first and only
# ever combine it with sandboxed execution.
# Keep credentials out of source: read the token from the environment.
accelerate launch main.py \
  --model /path/to/my-code-model \
  --tasks humaneval \
  --trust_remote_code \
  --token "$HF_TOKEN" \
  --generation_only \
  --save_generations \
  --save_generations_path generations_humaneval.json
```

**Step 3: Score in a sandbox (never on the host)**

```bash
# Pull and tag the harness image once
docker pull ghcr.io/bigcode-project/evaluation-harness
docker tag ghcr.io/bigcode-project/evaluation-harness evaluation-harness

# Execute and score generated code inside a restricted container only
# (mount a results dir to collect metrics out of the read-only container)
mkdir -p results
docker run --network=none --read-only --tmpfs /tmp \
  -v $(pwd)/generations_humaneval.json:/app/generations.json:ro \
  -v $(pwd)/results:/app/results \
  -it evaluation-harness python3 main.py \
  --model bigcode/starcoder2-7b \
  --tasks humaneval \
  --temperature 0.8 \
  --n_samples 200 \
  --load_generations_path /app/generations.json \
  --allow_code_execution \
  --metric_output_path results/starcoder2-humaneval.json
```

**Step 4: Analyze results**

Results in `results/starcoder2-humaneval.json`:
```json
{
  "humaneval": {
    "pass@1": 0.354,
    "pass@10": 0.521,
    "pass@100": 0.689
  },
  "config": {
    "model": "bigcode/starcoder2-7b",
    "temperature": 0.8,
    "n_samples": 200
  }
}
```

### Workflow 2: Multi-Language Evaluation (MultiPL-E)

Evaluate code generation across 18 programming languages.

**Checklist**:
```
Multi-Language Evaluation:
- [ ] Step 1: Generate solutions (host machine)
- [ ] Step 2: Run evaluation in Docker (safe execution)
- [ ] Step 3: Compare across languages
```

**Step 1: Generate solutions on host**

```bash
# Generate without execution (safe)
accelerate launch main.py \
  --model bigcode/starcoder2-7b \
  --tasks multiple-py,multiple-js,multiple-java,multiple-cpp \
  --max_length_generation 650 \
  --temperature 0.8 \
  --n_samples 50 \
  --batch_size 50 \
  --generation_only \
  --save_generations \
  --save_generations_path generations_multi.json
```

**Step 2: Evaluate in Docker container**

```bash
# Pull and tag the MultiPL-E Docker image
docker pull ghcr.io/bigcode-project/evaluation-harness-multiple
docker tag ghcr.io/bigcode-project/evaluation-harness-multiple evaluation-harness-multiple

# Run evaluation inside a restricted container
# (--allow_code_execution here is safe: it executes inside the container,
# never on the host)
docker run --network=none --read-only --tmpfs /tmp -v $(pwd)/generations_multi.json:/app/generations.json:ro \
  -it evaluation-harness-multiple python3 main.py \
  --model bigcode/starcoder2-7b \
  --tasks multiple-py,multiple-js,multiple-java,multiple-cpp \
  --load_generations_path /app/generations.json \
  --allow_code_execution \
  --n_samples 50
```

**Supported languages**: Python, JavaScript, Java, C++, Go, Rust, TypeScript, C#, PHP, Ruby, Swift, Kotlin, Scala, Perl, Julia, Lua, R, Racket

### Workflow 3: Instruction-Tuned Model Evaluation

Evaluate chat/instruction models with proper formatting.

**Checklist**:
```
Instruction Model Evaluation:
- [ ] Step 1: Use instruction-tuned tasks
- [ ] Step 2: Configure instruction tokens
- [ ] Step 3: Run evaluation
```

**Step 1: Choose instruction tasks**

- **instruct-humaneval**: HumanEval with instruction prompts
- **humanevalsynthesize-{lang}**: HumanEvalPack synthesis tasks

**Step 2: Configure instruction tokens** (generate on host — score in the sandbox as in Workflow 1 Step 3)

```bash
# For models with chat templates (e.g., CodeLlama-Instruct)
accelerate launch main.py \
  --model codellama/CodeLlama-7b-Instruct-hf \
  --tasks instruct-humaneval \
  --instruction_tokens "<s>[INST],</s>,[/INST]" \
  --max_length_generation 512 \
  --generation_only \
  --save_generations \
  --save_generations_path generations_instruct-humaneval.json
```

**Step 3: HumanEvalPack for instruction models** (generate on host)

```bash
# Test code synthesis across 6 languages
accelerate launch main.py \
  --model codellama/CodeLlama-7b-Instruct-hf \
  --tasks humanevalsynthesize-python,humanevalsynthesize-js \
  --prompt instruct \
  --max_length_generation 512 \
  --generation_only \
  --save_generations \
  --save_generations_path generations_humanevalpack.json
```

### Workflow 4: Compare Multiple Models

Benchmark suite for model comparison.

**Step 1: Create evaluation script**

```bash
#!/bin/bash
# eval_models.sh
# Stage A: generate on the host (no execution). Stage B: score each model's
# generations inside a restricted container.

MODELS=(
  "bigcode/starcoder2-7b"
  "codellama/CodeLlama-7b-hf"
  "deepseek-ai/deepseek-coder-6.7b-base"
)
TASKS="humaneval,mbpp"

# Stage A: generation only, on the host
for model in "${MODELS[@]}"; do
  model_name=$(echo $model | tr '/' '-')
  echo "Generating for $model"

  accelerate launch main.py \
    --model $model \
    --tasks $TASKS \
    --temperature 0.2 \
    --n_samples 20 \
    --batch_size 20 \
    --generation_only \
    --save_generations \
    --save_generations_path generations_${model_name}.json
done

# Stage B: execute + score inside a sandbox (never on the host)
docker pull ghcr.io/bigcode-project/evaluation-harness
docker tag ghcr.io/bigcode-project/evaluation-harness evaluation-harness
mkdir -p results
for model in "${MODELS[@]}"; do
  model_name=$(echo $model | tr '/' '-')

  docker run --network=none --read-only --tmpfs /tmp \
    -v $(pwd)/generations_${model_name}.json:/app/generations.json:ro \
    -v $(pwd)/results:/app/results \
    -it evaluation-harness python3 main.py \
    --model $model \
    --tasks $TASKS \
    --load_generations_path /app/generations.json \
    --allow_code_execution \
    --metric_output_path results/${model_name}.json
done
```

**Step 2: Generate comparison table**

```python
import json
import pandas as pd

models = ["bigcode-starcoder2-7b", "codellama-CodeLlama-7b-hf", "deepseek-ai-deepseek-coder-6.7b-base"]
results = []

for model in models:
    with open(f"results/{model}.json") as f:
        data = json.load(f)
        results.append({
            "Model": model,
            "HumanEval pass@1": f"{data['humaneval']['pass@1']:.3f}",
            "MBPP pass@1": f"{data['mbpp']['pass@1']:.3f}"
        })

df = pd.DataFrame(results)
print(df.to_markdown(index=False))
```

## When to Use vs Alternatives

**Use BigCode Evaluation Harness when:**
- Evaluating **code generation** models specifically
- Need **multi-language** evaluation (18 languages via MultiPL-E)
- Testing **functional correctness** with unit tests (pass@k)
- Benchmarking for **BigCode/HuggingFace leaderboards**
- Evaluating **fill-in-the-middle** (FIM) capabilities

**Use alternatives instead:**
- **lm-evaluation-harness**: General LLM benchmarks (MMLU, GSM8K, HellaSwag)
- **EvalPlus**: Stricter HumanEval+/MBPP+ with more test cases
- **SWE-bench**: Real-world GitHub issue resolution
- **LiveCodeBench**: Contamination-free, continuously updated problems
- **CodeXGLUE**: Code understanding tasks (clone detection, defect prediction)

## Supported Benchmarks

| Benchmark | Problems | Languages | Metric | Use Case |
|-----------|----------|-----------|--------|----------|
| HumanEval | 164 | Python | pass@k | Standard code completion |
| HumanEval+ | 164 | Python | pass@k | Stricter evaluation (80× tests) |
| MBPP | 974 (500 test) | Python | pass@k | Entry-level problems |
| MBPP+ | 399 | Python | pass@k | Stricter evaluation (35× tests) |
| MultiPL-E | 164×18 | 18 languages | pass@k | Multi-language evaluation |
| APPS | 10,000 | Python | pass@k | Competition-level |
| DS-1000 | 1,000 | Python | pass@k | Data science (pandas, numpy, etc.) |
| HumanEvalPack | 164×3×6 | 6 languages | pass@k | Synthesis/fix/explain |
| Mercury | 1,889 | Python | Efficiency | Computational efficiency |

## Common Issues

**Issue: Different results than reported in papers**

Check these factors:
```bash
# 1. Verify n_samples (need 200 for accurate pass@k)
--n_samples 200

# 2. Check temperature (0.2 for greedy-ish, 0.8 for sampling)
--temperature 0.8

# 3. Verify task name matches exactly
--tasks humaneval  # Not "human_eval" or "HumanEval"

# 4. Check max_length_generation
--max_length_generation 512  # Increase for longer problems
```

**Issue: CUDA out of memory**

```bash
# Use quantization
--load_in_8bit
# OR
--load_in_4bit

# Reduce batch size
--batch_size 1

# Note: --max_memory_per_gpu is NOT a documented bigcode-evaluation-harness
# argument (verify against your installed harness version before relying on
# it); use accelerate's memory config or the quantization/batch options above.
```

**Issue: Code execution hangs or times out**

Use Docker for safe execution:
```bash
# Generate on host (no execution)
--generation_only --save_generations

# Evaluate in Docker
docker run ... --allow_code_execution --load_generations_path ...
```

**Issue: Low scores on instruction models**

Ensure proper instruction formatting:
```bash
# Use instruction-specific tasks
--tasks instruct-humaneval

# Set instruction tokens for your model
--instruction_tokens "<s>[INST],</s>,[/INST]"
```

**Issue: MultiPL-E language failures**

Use the dedicated Docker image:
```bash
docker pull ghcr.io/bigcode-project/evaluation-harness-multiple
```

## Command Reference

| Argument | Default | Description |
|----------|---------|-------------|
| `--model` | - | HuggingFace model ID or local path |
| `--tasks` | - | Comma-separated task names |
| `--n_samples` | 1 | Samples per problem (200 for pass@k) |
| `--temperature` | 0.2 | Sampling temperature |
| `--max_length_generation` | 512 | Max tokens (prompt + generation) |
| `--batch_size` | 1 | Batch size per GPU |
| `--allow_code_execution` | False | Execute generated code — ONLY inside an isolated sandbox/container |
| `--generation_only` | False | Generate without evaluation |
| `--load_generations_path` | - | Load pre-generated solutions |
| `--save_generations` | False | Save generated code |
| `--metric_output_path` | results.json | Output file for metrics |
| `--load_in_8bit` | False | 8-bit quantization |
| `--load_in_4bit` | False | 4-bit quantization |
| `--trust_remote_code` | False | Run custom model-repo code (supply-chain risk; audit first) |
| `--token` | - | HuggingFace token (replaces deprecated `--use_auth_token`; keep out of source) |
| `--precision` | fp32 | Model precision (fp32/fp16/bf16) |

## Hardware Requirements

| Model Size | VRAM (fp16) | VRAM (4-bit) | Time (HumanEval, n=200) |
|------------|-------------|--------------|-------------------------|
| 7B | 14GB | 6GB | ~30 min (A100) |
| 13B | 26GB | 10GB | ~1 hour (A100) |
| 34B | 68GB | 20GB | ~2 hours (A100) |

## Resources

- **GitHub**: https://github.com/bigcode-project/bigcode-evaluation-harness
- **Documentation**: https://github.com/bigcode-project/bigcode-evaluation-harness/tree/main/docs
- **BigCode Leaderboard**: https://huggingface.co/spaces/bigcode/bigcode-models-leaderboard
- **HumanEval Dataset**: https://huggingface.co/datasets/openai/openai_humaneval
- **MultiPL-E**: https://github.com/nuprl/MultiPL-E

## Hermes adaptation

This is an adapted, on-demand Hermes skill. Use the existing project environment and installed dependencies; do not install packages or contact external services automatically. Supporting files are relative to `${HERMES_SKILL_DIR}`.

## Provenance

Adapted from [https://github.com/foryourhealth111-pixel/Vibe-Skills](https://github.com/foryourhealth111-pixel/Vibe-Skills) at commit `ddcaa2affca93c1efe026d008b6b93709e5fb7e2`. Upstream repository license: MIT. The repository and third-party notice remain the provenance boundary; benchmark execution is opt-in.

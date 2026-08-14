# ECC Comment Analyzer + OpenCode Pipeline

Proven 2026-07-11: piping an ECC analysis agent prompt into OpenCode as a `--file` attachment.

## Command

```bash
# 1. Extract the ECC agent prompt to a file (use full Windows paths, not /tmp)
python "C:/Users/YOUR_USERNAME/AppData/Local/hermes/skills/ecc-bridge/scripts/ecc-runner.py" \
  comment-analyzer "Analyze <file> for comment quality" \
  > "C:/Users/YOUR_USERNAME/Documents/Projects/<project>/ecc-prompt.md"

# 2. Delegate to OpenCode with the prompt as context
cd /c/Users/YOUR_USERNAME/Documents/Projects/<project> && \
opencode run 'Read <file> and analyze it for comment quality, accuracy, and 
completeness using the attached analysis framework. Report findings.' \
  --model opencode/deepseek-v4-flash-free \
  --file ecc-prompt.md
```

## Key Lessons

- **Windows paths only** — `/tmp/ecc-prompt.md` fails in MSYS. Use `C:/...` or `~/...` instead.
- **`--file` works for analysis agents** — OpenCode reads the attached file as context even though it's a framework, not code. No need to inline the prompt.
- **DeepSeek V4 Flash Free handles it** — the comment-analyzer (originally `model: sonnet`) ran successfully on `opencode/deepseek-v4-flash-free`.
- **Result was thorough** — found 4 incomplete areas + 1 misleading field + fragile `indexOf`-by-reference pattern in 84-line JS file.

## Prerequisites

- OpenCode v1.16+ with `opencode/deepseek-v4-flash-free` model working
- If `opencode run` gives "Unexpected server error" / SQLite "no such column: replacement_seq", delete `~/.local/share/opencode/opencode.db` and retry.

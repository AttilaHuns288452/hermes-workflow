# Live Token Savings Benchmarks

## Summary
The token-saver was **documented but never used** across all prior sessions until June 12, 2026. The decide skill now enforces it via **Rule 1 (Token Saver Probe Chain)**.

## Live-Tested Token Savings

| Method | Tokens | vs Raw Read | Savings | Notes |
|--------|--------|-------------|---------|-------|
| `codegraph query "symbol"` | ~300 | 15K (10 files) | **50×** | Always works — 1,607 files indexed |
| `graphify query "question"` | ~300 | 370K (full tree) | **1,233×** | BFS traversal, 21/24 projects |
| `codegraph callers "fn"` | ~200 | 10K (grep+3 files) | **50×** | FTS5 symbol search |
| `graphify explain "symbol"` | ~145 | 5K (1 file) | **35×** | Plain-language summary |
| Full probe chain (3+2 queries) | ~1,500 | 350K (feature understanding) | **233×** | CodeGraph → Graphify → read_file |

**Savings range:** 35×–1,233× depending on probe type and scope.

## 4-Step Probe Chain Commands (Copy-Paste Ready)

```bash
# Step A — Detect Project (from any file path)
PROJECT=$(echo "$FILE_PATH" | sed 's|.*Documents/Projects/\([^/]*\).*|\1|')

# Step B — Probe CodeGraph MCP (ALWAYS AVAILABLE)
cd ~/Documents/Projects
codegraph query "function_name"
codegraph callers "function_name"
codegraph callees "function_name"
codegraph impact "function_name"

# Step C — Probe Graphify (IF INDEX EXISTS)
if [ -f "~/Documents/Projects/$PROJECT/graphify-out/graph.json" ]; then
  cd ~/Documents/Projects/$PROJECT
  ~/.local/bin/graphify.exe query "what does X do?" --budget 2000 --graph graphify-out/graph.json
  ~/.local/bin/graphify.exe explain "symbol_name" --graph graphify-out/graph.json
fi

# Step D — Targeted read_file (LAST RESORT)
read_file("path/to/file.py", offset=<line>, limit=50)
```

## Graphify Index Coverage (21/24 Projects)

| Project | Notes |
|---------|-------|
| ai-marketing-skills | ✅ 2,270 nodes, 2,885 edges |
| AI-Youtube-Shorts-Generator | ✅ |
| anime-waifu-quiz | ✅ |
| API-mega-list | ✅ 59KB |
| atm-crypto-bank | ✅ 116KB |
| atm-machine | ✅ 461KB |
| buildable-plugin-skills | ✅ 3,152 nodes, 3,352 edges |
| countdown-timer | ✅ 1.4KB |
| ECC | ✅ 34MB (5,821 files) |
| ecosystem-test | ✅ 9.8KB |
| free-ai-tools | ✅ 236KB |
| freebuff-test | ✅ |
| freelance-rate-calculator | ✅ |
| freellmapi | ✅ |
| free-llm-api | ✅ 1MB |
| graphify (self) | ✅ 7.8MB (8,267 nodes) |
| hermes-workflow | ✅ 7.8MB (11,501 nodes, 13,727 edges, built Jun 30) |
| hw-new | ✅ 1.9MB |
| hermes-token-test | ✅ 33KB (45 nodes, 74 edges, benchmark: 4.0× savings, built Jun 30) |
| MoneyPrinterTurbo | ✅ 830KB |
| MoneyPrinterV2 | ✅ |
| task-manager-cli | ✅ 49KB |
| Hermes Skills | ❌ (exported skill tree, not code) |
| hermes-dashboard | ❌ (single HTML) |
| unit-converter | ❌ (no code files) |

## Key Insight

> **The token-saver was passive prose — now it's an active enforcement rule in `/decide` (Rule 1).**
>
> Before June 12: `read_file()` called directly every time.
> After June 12: Mandatory 4-step probe chain must run first.
> After June 23 (this session): decide skill rewritten so Rule 1 is the FIRST thing you read.

**Build command** (run from project root to create missing indices):
```bash
~/.local/bin/graphify.exe update .
```
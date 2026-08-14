# Agent Reach setup recipe (Windows, 2026-08-13)

Verified install + integration for https://github.com/Panniantong/agent-reach (v1.5.0, MIT, 71k stars). CLI = capability layer: selects/installs/doctors/routes upstream tools; agents call upstream tools directly.

## Install (pipx absent → uv tool)

```bash
git clone --depth 1 https://github.com/Panniantong/agent-reach C:/Users/YOUR_USERNAME/.agent-reach/src
uv tool install C:/Users/YOUR_USERNAME/.agent-reach/src      # binary → ~/.local/bin/agent-reach (on PATH)
uv tool install yt-dlp                                # SEPARATE — tool venv deps are not commands
npm install -g mcporter                               # Exa MCP client (Node, → AppData/Roaming/npm)
mcporter config add exa https://mcp.exa.ai/mcp --scope home   # free, no key
```

- Do NOT `pip install` the PyPI `agent-reach` package — the README warns it is a different, unrelated package.
- Repo skill files: `agent_reach/skill/SKILL_en.md` (English) + `references/*.md` (7 files, Chinese but commands universal). Install into Hermes as `C:/Users/YOUR_USERNAME/AppData/Local/hermes/skills/agent-reach/` (copy SKILL_en.md → SKILL.md).

## Windows fixes the doctor demands

- **yt-dlp `[!]` "not configured JS runtime"** → create `~/.config/yt-dlp/config` containing `--js-runtimes node` (Node is installed). Without this, YouTube extraction fails on JS-challenge videos.
- **Exa `[!]`** — doctor deliberately never live-probes remote MCP; verify manually instead:
  `mcporter call exa.web_search_exa query="..." numResults=2`
- **Bilibili channel** works zero-config via curl search API (needs `User-Agent: agent-reach/1.0` + `Referer: https://www.bilibili.com` headers); full channel = `uv tool install bilibili-cli` (optional).
- Doctor counts channels conservatively (5/15 after core setup) — it does not live-probe gh auth or Exa by design.

## Zero-config channels after setup (verified live)

Jina Reader (curl r.jina.ai/URL), YouTube (yt-dlp), RSS (feedparser), V2EX (public API), Bilibili search, GitHub (gh CLI), Exa semantic search. Login-backed (need user cookies/browser session, never auto-install): Twitter, Reddit, Facebook, Instagram, XiaoHongShu, LinkedIn, Xueqiu, Xiaoyuzhou (Groq key).

## Integration pattern (reuse for any new repo-tool)

1. Install CLI + verify every channel with a live smoke test (doctor ≠ proof).
2. Copy upstream SKILL.md into Hermes skills dir (English version if bilingual repo).
3. Patch `/decide` BOTH copies (hermes + `~/.agents`): one Domain Skills row (research/URL/platform triggers) + one Complementary Setup Routing row.
4. Save compact memory entry (CLI locations, live channels, login-gated channels).
5. Report before/after benefit table to the user; offer optional channels + daily `agent-reach watch` cron.

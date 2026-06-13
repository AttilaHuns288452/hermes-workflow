# Hermes + ECC Integration Notes

## Directory mapping

| Scope | Path | Purpose |
|-------|------|---------|
| Hermes skills | `~/.hermes/skills/ecc/` | ECC skills visible to Hermes |
| OpenCode install | `~/.opencode/` | ECC OpenCode adapter files |
| ECC source/repo | `~/Documents/Projects/ECC` | Canonical repo clone and installer |
| Claude Code install | `~/.claude/` | ECC Claude Code adapter files |

## Rule

Do not assume `~/.claude/` files are visible to Hermes. For Hermes to use ECC content, copy or link it into `~/.hermes/skills/ecc/`.

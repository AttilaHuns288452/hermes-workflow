# uv tool / uvx env leakage + Windows path mangling (2026-08, LinkedIn MCP case)

Real case that proved the Hermes-venv PYTHONPATH leak reaches **uv-isolated
environments**, plus two Windows quirks discovered alongside.

## Symptom

Installing `mcp-server-linkedin` (Python MCP server) and running `--login`:

```
uv tool install mcp-server-linkedin          # OK, isolated env created
mcp-server-linkedin --help
→ ImportError: cannot import name 'TextSizing' from 'wcwidth'
  (C:\Users\YOUR_USERNAME\AppData\Local\hermes\hermes-agent\venv\Lib\site-packages\wcwidth\__init__.py)
```

Same error from `uvx mcp-server-linkedin@latest --login`, and even from a
fresh `uv venv` + `uv pip install` — the traceback always resolved `wcwidth`
to the **Hermes venv**, not the env being run.

## Root cause

This machine's shell exports a global:

```
PYTHONPATH=C:\Users\YOUR_USERNAME\AppData\Local\hermes\hermes-agent;C:\Users\YOUR_USERNAME\AppData\Local\hermes\hermes-agent\venv\Lib\site-packages
```

`PYTHONPATH` prepends to `sys.path` in EVERY Python process — uv's ephemeral
`uvx` envs, `uv tool` envs, and fresh `uv venv`s included. The Hermes venv's
`wcwidth` (old, no `TextSizing`) shadowed the correct one. Note:
`uv pip install --python <env> "wcwidth>=0.2.13"` reported "Checked 1 package"
(satisfied) because the env *already had* wcwidth — the leak made the import
resolve elsewhere anyway. Version checks on the env are misleading when the
leak is present.

## Fix (verified)

```bash
env -u PYTHONPATH "C:/path/to/venv/Scripts/mcp-server-linkedin.exe" --login
```

`env -u PYTHONPATH` strips the var for just that process. In cmd.exe:
`set PYTHONPATH=` first. When wiring such CLIs into a manager (e.g. mcporter
config with `--command uvx ...`), the child inherits the leak — use a wrapper
script that unsets PYTHONPATH before exec, or point the manager at a binary
installed with the var stripped.

## Related quirk: uv venv MSYS path mangling (git-bash)

```bash
uv venv "$HOME/.linkedin-mcp-venv"
# prints: Activate with: C:\c\Users\Attila\.linkedin-mcp-venv\Scripts\activate
# (double-mangled: /c/Users → C:\c\Users)
```

`uv` (a native Windows exe) receives the MSYS path literally. The venv is
created and fully usable at the mangled path — don't fight it, just reference
it as `C:/c/Users/<user>/...`. If you need a clean path, pass the Windows path
explicitly (`uv venv "C:/Users/<user>/.x-venv"`).

## Companion note: pipx replacement

`pipx` is NOT installed on this machine; `uv tool install <pkg>` is the
equivalent (installs to `~/.local/bin`, which is on PATH). Used successfully
for: agent-reach, yt-dlp, opencli (npm actually), twitter-cli,
mcp-server-linkedin. `uv tool install` from a local repo dir also works:
`uv tool install C:/path/to/repo`.

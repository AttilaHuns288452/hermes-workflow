# Fastfetch Logo + Module Theming

## Config location

`~/.config/fastfetch/config.jsonc` — auto-loaded by `fastfetch`.

## Logo color overrides

Built-in ASCII logos use `$1`, `$2`, `$3` as color placeholders. Override them
in the `logo.color` object:

```json
{
  "logo": {
    "source": "linuxmint",
    "color": {
      "1": "#0e846c",
      "2": "#0a5c4c"
    }
  }
}
```

- `$1` = main body (mint leaf interior)
- `$2` = border / outline
- `$3` = accent (if used by the logo)

## Module text colors (keys, output, separator)

**CRITICAL:** The correct JSONC schema path is `display.color.*`, NOT root-level
`colorKeys`/`colorTitle`/`colorOutput`/`colorSeparator`. Root-level keys are
silently ignored.

```json
{
  "display": {
    "color": {
      "keys": "#d4af37",
      "output": "#e0d0b0",
      "separator": "#333333"
    }
  }
}
```

- `keys` — color of module key names ("OS:", "Kernel:", etc.)
- `output` — color of module values ("Linux Mint 22.3", etc.)
- `separator` — color of the key-value separator (": ")
- `title` — (optional) color of the title line; falls back to `keys` if unset

## Full working example (gold + black for CAPITAL-Gold / Mint-Y-Dark-Teal)

```jsonc
{
    "$schema": "https://github.com/fastfetch-cli/fastfetch/raw/dev/doc/json_schema.json",
    "logo": {
        "source": "linuxmint",
        "color": {
            "1": "#d4af37",
            "2": "#1a1a1a"
        }
    },
    "display": {
        "color": {
            "keys": "#d4af37",
            "output": "#e0d0b0",
            "separator": "#333333"
        }
    },
    "modules": [
        "title", "separator", "os", "host", "kernel", "uptime",
        "packages", "shell", "display", "de", "wm", "wmtheme", "theme",
        "icons", "font", "cursor", "terminal", "terminalfont", "cpu",
        "gpu", "memory", "swap", "disk", "localip", "battery",
        "poweradapter", "locale", "break", "colors"
    ]
}
```

## Matching a Mint-Y theme

For **Mint-Y-Dark-Teal** (teal):
- Logo `$1`: `#0e846c`, `$2`: `#0a5c4c`
- Keys: `#0e846c` (teal), Output: `#e0e0e0`, Separator: `#333333`

For **Mint-Y-Dark-Blue** (blue):
- Logo `$1`: `#1a5fb4`, `$2`: `#0c3d7a`
- Keys: `#1a5fb4` (blue), Output: `#e0e0e0`, Separator: `#333333`

For **CAPITAL-Gold on Mint-Y-Dark-Teal** (gold + black):
- Logo `$1`: `#d4af37` (metallic gold), `$2`: `#1a1a1a` (near-black)
- Keys: `#d4af37` (gold), Output: `#e0d0b0` (warm off-white), Separator: `#333333`

## Common pitfalls

- `logo.type` is NOT a valid key for built-in logos — use `"source"`.
- Root-level `colorKeys`, `colorTitle`, `colorOutput`, `colorSeparator` are
  **silently ignored** — must use `display.color.keys/output/separator`.
- Colors accept hex (`#rrggbb`), ANSI names (`"red"`, `"bright_cyan"`), or `null`.
- Terminal must support color (not `dumb`) to see the effect.
- Hermes desktop chat uses `TERM=dumb` — colors won't render in chat preview.
  Test in a real terminal (kitty, alacritty, gnome-terminal).
- Use `fastfetch -c <path>` to test a config without replacing the default.

## Verification

```bash
# Direct test in terminal
fastfetch -c ~/.config/fastfetch/config.jsonc

# TTY capture test (when terminal output is piped/stripped)
script -q -c "fastfetch -c ~/.config/fastfetch/config.jsonc" /dev/null | head -5 | od -c
```

Check the logo renders with the intended colors in a color-capable terminal.
Look for `38;2;<r>;<g>;<b>` ANSI escape sequences in TTY capture output.

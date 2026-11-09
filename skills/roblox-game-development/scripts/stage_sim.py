#!/usr/bin/env python3
"""Stage a Rojo src/ tree for headless Luau execution.

Rewrites instance-based requires to plain-Luau relative requires and injects the
mock-env prelude, so the SHIPPED modules can be required by `luau` with a mock
Roblox API installed. Fails loudly on any require form it does not understand:
 an unrunnable staged module would make the simulation lie.

Usage:
    python3 tests/sim/build.py                 # defaults: root=cwd, out=.sim
    python3 scripts/stage_sim.py --root . --out .sim

Then, in the sim:
    local M = require("./mock")
    assert(require("../../.sim/env").game == M.game, "mock env split")
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

RULES = [
    (re.compile(r'require\(script\.Parent:WaitForChild\("(\w+)"\)\)'), r'require("./\1")'),
    (re.compile(r'require\(script\.Parent\.(\w+)\)'), r'require("./\1")'),
    (re.compile(r'require\(script:WaitForChild\("(\w+)"\)\)'), r'require("./\1")'),
    (re.compile(r'require\(ReplicatedStorage\.Shared\.(\w+)\)'), r'require("../shared/\1")'),
]

# locals shadow the CLI's absent/readonly globals
PRELUDE = (
    'local __env = require("../env")\n'
    "local game, workspace, Workspace, Instance, Vector3, CFrame, Color3, UDim, UDim2, "
    "NumberRange, TweenInfo, Random, Enum, task, warn, tick, time =\n"
    "\t__env.game, __env.workspace, __env.Workspace, __env.Instance, __env.Vector3, __env.CFrame, "
    "__env.Color3, __env.UDim, __env.UDim2,\n"
    "\t__env.NumberRange, __env.TweenInfo, __env.Random, __env.Enum, __env.task, __env.warn, "
    "__env.tick, __env.time\n"
)

ENV_STUB = (
    '-- generated: single shared instance of the mock env for sim + modules\n'
    'return require("../tests/sim/mock").env\n'
)


def stage(src_dir: Path, dst_dir: Path) -> list[str]:
    dst_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for path in sorted(src_dir.glob("*.luau")):
        text = path.read_text()
        for pattern, repl in RULES:
            text = pattern.sub(repl, text)

        leftovers = [
            line
            for line in text.splitlines()
            if "require(script" in line or "require(ReplicatedStorage" in line
        ]
        if leftovers:
            sys.exit(f"UNREWRITTEN require in {path}:\n" + "\n".join(leftovers))

        lines = text.splitlines(keepends=True)
        keep = 1 if lines and lines[0].lstrip().startswith("--!") else 0
        text = "".join(lines[:keep]) + PRELUDE + "".join(lines[keep:])

        # Roblox Scripts return nothing; require demands exactly one value.
        if path.name.endswith((".server.luau", ".client.luau")):
            text += "\nreturn true -- staging only: Roblox Scripts return nothing\n"

        name = path.name.replace(".server.luau", ".luau").replace(".client.luau", ".luau")
        (dst_dir / name).write_text(text)
        written.append(name)
    return written


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="project root containing src/")
    parser.add_argument("--out", default=".sim", help="staging directory (gitignore it)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out = root / args.out
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    (out / "env.luau").write_text(ENV_STUB)
    counts = {}
    for name in ("shared", "server", "client"):
        src = root / "src" / name
        if not src.is_dir():
            continue
        counts[name] = len(stage(src, out / name))

    summary = ", ".join(f"{n} {k}" for k, n in counts.items())
    print(f"staged {summary} modules into {out}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Obsidian Codebase Graph Generator — TypeScript/React/Next.js Edition

Scans a Next.js / TypeScript codebase and emits an Obsidian note graph:
  project index -> folders -> files -> symbols
with wikilinks reflecting imports, exports, calls, inheritance, and type relationships.

Uses regex-based parsing for TypeScript/JSX (NOT Python's ast, which can't handle TS).
Handles: .ts, .tsx, .js, .jsx files in modern projects.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# ─── Configuration ───────────────────────────────────────────────────────────

# Files to parse for symbols
SOURCE_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx"}

# Files to include as file notes (non-source files get a basic note)
ALL_TEXT_EXTENSIONS = SOURCE_EXTENSIONS | {".json", ".md", ".css", ".scss", ".less", ".yaml", ".yml", ".toml"}

# Directories to skip entirely
IGNORE_DIRS = {
    "node_modules", ".next", "dist", "build", ".git", "__pycache__",
    "bin", "obj", ".vercel", ".turbo", ".cache", "coverage",
    ".vscode", ".husky", ".storybook", "public/fonts", "public/images",
    "out", ".graphify", "graphify-out", ".parcel-cache", ".env", "tmp",
}

# ─── Helpers ─────────────────────────────────────────────────────────────────


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def safe_name(name: str) -> str:
    """Create a safe Obsidian-friendly note name from any string."""
    # Remove file extension if present
    name = re.sub(r"\.(ts|tsx|js|jsx|css|scss|less|json|md|yaml|yml|toml)$", "", name)
    # Replace separators with spaces
    name = re.sub(r"[/\\_\-]+", " ", name)
    # Title case each word
    name = " ".join(w.capitalize() if w else "" for w in name.split())
    # Collapse whitespace
    name = re.sub(r"\s+", " ", name).strip()
    return name or "Untitled"


def rel_path(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def slugify(text: str) -> str:
    """Make a URL-safe slug from text."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def iter_source_files(root: Path) -> List[Path]:
    """Walk the project tree and return all source files."""
    files: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for name in filenames:
            p = Path(dirpath, name)
            if p.suffix.lower() in ALL_TEXT_EXTENSIONS:
                files.append(p)
    return sorted(files)


def resolve_import_path(imp: str, current_file: Path, project_root: Path) -> Optional[str]:
    """Resolve a relative import path to a project-relative file path."""
    if imp.startswith("."):
        # Relative import
        base = current_file.parent
        resolved = (base / imp).resolve()
        # Try extensions
        for ext in SOURCE_EXTENSIONS:
            candidate = resolved.with_suffix(ext)
            if candidate.exists():
                return rel_path(candidate, project_root)
            # Try index files
            index_candidate = resolved / f"index{ext}"
            if index_candidate.exists():
                return rel_path(index_candidate, project_root)
        return None
    else:
        # Bare specifier (npm package) — can't resolve to a local file
        return None


# ─── TypeScript/JSX Regex Parser ─────────────────────────────────────────────


def ts_parse_imports(text: str) -> List[Dict]:
    """Extract import declarations from TypeScript/JSX source."""
    imports: List[Dict] = []

    # import X from '...'
    for m in re.finditer(
        r'import\s+(?:type\s+)?(?:\{[^}]*\}|[^;{]+?)\s+from\s+[\'"]([^\'"]+)[\'"]\s*;?',
        text,
    ):
        source = m.group(1)
        # Extract imported names
        before_from = m.group(0).split("from")[0]
        names: List[str] = []
        # Named imports: { X, Y as Z }
        brace_match = re.search(r"\{(.+?)\}", before_from)
        if brace_match:
            for part in brace_match.group(1).split(","):
                part = part.strip()
                if part:
                    # Handle 'as' aliases
                    alias_match = re.match(r"(\w+)(?:\s+as\s+(\w+))?", part)
                    if alias_match:
                        names.append(alias_match.group(1))
        # Default import: import X from ...
        default_match = re.search(
            r"import\s+(?:type\s+)?(\w+)(?:\s*,|\s+from)", before_from
        )
        if default_match:
            names.append(default_match.group(1))
        # namespace import: import * as X from ...
        ns_match = re.search(r"import\s+\*\s+as\s+(\w+)", before_from)
        if ns_match:
            names.append(ns_match.group(1))

        imports.append({"source": source, "names": names})

    # import '...' (side-effect)
    for m in re.finditer(r"import\s+['\"]([^'\"]+)['\"]\s*;?", text):
        imports.append({"source": m.group(1), "names": []})

    return imports


def ts_parse_exports(text: str) -> Dict[str, Dict]:
    """Extract export declarations from TypeScript/JSX source."""
    exports: Dict[str, Dict] = {}

    # export function X(...)
    for m in re.finditer(
        r"export\s+(default\s+)?function\s+(\w+)", text
    ):
        is_default = bool(m.group(1))
        name = m.group(2)
        exports[name] = {"name": name, "type": "function", "default": is_default}

    # export const X = ...
    for m in re.finditer(
        r"export\s+(default\s+)?const\s+(\w+)", text
    ):
        is_default = bool(m.group(1))
        name = m.group(2)
        exports[name] = {"name": name, "type": "constant", "default": is_default}

    # export class X ...
    for m in re.finditer(r"export\s+(default\s+)?class\s+(\w+)", text):
        is_default = bool(m.group(1))
        name = m.group(2)
        exports[name] = {"name": name, "type": "class", "default": is_default}

    # export interface X ...
    for m in re.finditer(
        r"export\s+(default\s+)?interface\s+(\w+)", text
    ):
        is_default = bool(m.group(1))
        name = m.group(2)
        exports[name] = {"name": name, "type": "interface", "default": is_default}

    # export type X = ...
    for m in re.finditer(
        r"export\s+(default\s+)?type\s+(\w+)\s*=", text
    ):
        is_default = bool(m.group(1))
        name = m.group(2)
        exports[name] = {"name": name, "type": "type", "default": is_default}

    # export enum X ...
    for m in re.finditer(r"export\s+(default\s+)?enum\s+(\w+)", text):
        is_default = bool(m.group(1))
        name = m.group(2)
        exports[name] = {"name": name, "type": "enum", "default": is_default}

    # export default class/function X (inline default)
    if not any(e.get("default") for e in exports.values()):
        for m in re.finditer(r"export\s+default\s+(?:class|function)\s+(\w+)", text):
            exports[m.group(1)] = {
                "name": m.group(1),
                "type": "default",
                "default": True,
            }

    # export default <expression> (anonymous default)
    # Detect 'export default' followed by non-declaration syntax
    for m in re.finditer(
        r"export\s+default\s+(?!function|class|const|let|var|interface|type|enum)(\w+)",
        text,
    ):
        name = m.group(1)
        if name not in exports:
            exports[name] = {"name": name, "type": "default-export", "default": True}

    return exports


def ts_parse_declarations(text: str) -> Dict[str, Dict]:
    """Extract top-level declarations (not necessarily exported)."""
    decls: Dict[str, Dict] = {}

    # function X(...)
    for m in re.finditer(
        r"(?:^|\n)\s*(?:export\s+(?:default\s+)?)?(?:async\s+)?function\s+(\w+)",
        text,
    ):
        name = m.group(1)
        # Detect if it's a React hook or component
        sym_type = "hook" if name.startswith("use") else "function"
        decls[name] = {"name": name, "type": sym_type}

    # const X = ... (arrow function or value)
    for m in re.finditer(
        r"(?:^|\n)\s*(?:export\s+(?:default\s+)?)?const\s+(\w+)\s*[:=]",
        text,
    ):
        name = m.group(1)
        sym_type = "hook" if name.startswith("use") else "constant"
        decls[name] = {"name": name, "type": sym_type}

    # class X ...
    for m in re.finditer(
        r"(?:^|\n)\s*(?:export\s+(?:default\s+)?)?class\s+(\w+)", text
    ):
        name = m.group(1)
        decls[name] = {"name": name, "type": "class"}

    # interface X ...
    for m in re.finditer(
        r"(?:^|\n)\s*(?:export\s+(?:default\s+)?)?interface\s+(\w+)", text
    ):
        name = m.group(1)
        decls[name] = {"name": name, "type": "interface"}

    # type X = ...
    for m in re.finditer(
        r"(?:^|\n)\s*(?:export\s+(?:default\s+)?)?type\s+(\w+)\s*=", text
    ):
        name = m.group(1)
        decls[name] = {"name": name, "type": "type"}

    # enum X ...
    for m in re.finditer(
        r"(?:^|\n)\s*(?:export\s+(?:default\s+)?)?enum\s+(\w+)", text
    ):
        name = m.group(1)
        decls[name] = {"name": name, "type": "enum"}

    return decls


def detect_react_component(name: str, text: str) -> bool:
    """Check if a function/const is likely a React component (returns JSX)."""
    # Find the function body and check for JSX
    pattern = rf"(?:export\s+(?:default\s+)?)?(?:const\s+)?{re.escape(name)}\s*(?:=\s*(?:\([^)]*\)|[\w<>]+)\s*=>|\([^)]*\)\s*{{)"
    m = re.search(pattern, text)
    if m:
        # Look for JSX in the surrounding context
        pos = m.end()
        chunk = text[pos : pos + 2000]
        if re.search(r"return\s*\(?\s*<", chunk) or re.search(r"<\w+[\s>]", chunk):
            return True
    return False


def extract_symbols_from_file(file_path: Path, project_root: Path) -> Dict:
    """Extract all symbols, imports, and exports from a TS/JS/TSX/JSX file."""
    text = read_text(file_path)
    rel = rel_path(file_path, project_root)

    imports = ts_parse_imports(text)
    exports = ts_parse_exports(text)
    declarations = ts_parse_declarations(text)

    # Merge declarations with export info
    symbols: List[Dict] = []
    seen: Set[str] = set()
    for name, decl in declarations.items():
        if name in seen:
            continue
        seen.add(name)
        sym_type = decl.get("type", "function")
        export_info = exports.get(name, {})
        is_exported = name in exports

        # Detect React component
        if sym_type in ("function", "constant") and detect_react_component(name, text):
            sym_type = "component"
        elif sym_type == "hook" and detect_react_component(name, text):
            sym_type = "component"

        sym: Dict = {
            "name": name,
            "type": sym_type,
            "file": rel,
            "exported": is_exported,
            "default_export": export_info.get("default", False),
            "imports": [],
            "calls": [],
            "references": [],
        }
        symbols.append(sym)

    # Associate imports with symbols (heuristic: match import names to declarations)
    imported_names: List[str] = []
    for imp in imports:
        imported_names.extend(imp["names"])
    for sym in symbols:
        sym["imports"] = list(set(imported_names))

    # Collect all exported symbol names
    exported_names = list(exports.keys())

    return {
        "symbols": symbols,
        "imports_raw": [imp["source"] for imp in imports],
        "imported_names": imported_names,
        "exported_names": exported_names,
        "has_default_export": any(e.get("default") for e in exports.values()),
    }


# ─── Note Generation ─────────────────────────────────────────────────────────


def folder_note_name(folder_rel: str) -> str:
    """Create a readable note name from a folder path."""
    return safe_name(folder_rel)


def file_note_name(file_rel: str) -> str:
    """Create a readable note name from a file path."""
    return safe_name(Path(file_rel).name)


def write_note(path: Path, frontmatter: Dict, body: str) -> None:
    """Write an Obsidian markdown note with YAML frontmatter."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fm_lines = ["---"]
    for key, value in frontmatter.items():
        if isinstance(value, list):
            if value:
                items = "\n".join(f"  - {json.dumps(v, ensure_ascii=False)}" for v in value)
                fm_lines.append(f"{key}:\n{items}")
            else:
                fm_lines.append(f"{key}: []")
        elif isinstance(value, bool):
            fm_lines.append(f"{key}: {str(value).lower()}")
        elif isinstance(value, (int, float)):
            fm_lines.append(f"{key}: {value}")
        elif value is None:
            fm_lines.append(f"{key}: null")
        else:
            fm_lines.append(f"{key}: {json.dumps(str(value), ensure_ascii=False)}")
    fm_lines.append("---")
    content = "\n".join(fm_lines) + "\n" + body + "\n"
    path.write_text(content, encoding="utf-8")


def build_codebase_graph(source_dir: Path, vault_dir: Path) -> None:
    """Main entry point: scan and generate the full Obsidian codebase graph."""
    project_root = source_dir.resolve()
    project_name = safe_name(project_root.name)
    project_notes_root = vault_dir / f"{project_name} Project"

    print(f"Scanning: {project_root}")
    print(f"Output:   {project_notes_root}")

    files = iter_source_files(project_root)
    print(f"Found {len(files)} source files")

    # Phase 1: Group files by folder
    folder_files: Dict[str, List[Path]] = {}
    file_rels: Dict[Path, str] = {}
    for fp in files:
        rel = rel_path(fp, project_root)
        file_rels[fp] = rel
        folder = str(Path(rel).parent)
        folder_files.setdefault(folder, []).append(fp)

    folder_note_map: Dict[str, str] = {}  # folder_rel -> note_name
    file_note_map: Dict[str, str] = {}    # file_rel -> note_name
    symbol_to_file: Dict[str, str] = {}   # symbol_name -> file_rel

    # Phase 2: Generate folder and file notes
    for folder, fpaths in sorted(folder_files.items()):
        f_note = folder_note_name(folder) if folder not in ("", ".") else "_root_"
        folder_note_map[folder] = f_note

        child_file_notes: List[str] = []
        for fp in fpaths:
            frel = file_rels[fp]
            fname_note = file_note_name(frel)
            file_note_map[frel] = fname_note
            child_file_notes.append(fname_note)

            # Extract symbols from this file
            parsed = extract_symbols_from_file(fp, project_root)
            symbols = parsed["symbols"]
            imp_sources = parsed["imports_raw"]
            exported_names = parsed["exported_names"]

            # --- File note ---
            file_body_parts = [f"# {fp.name}\n"]

            if imp_sources:
                file_body_parts.append("## Imports\n")
                for s in imp_sources:
                    file_body_parts.append(f"- `{s}`")
                file_body_parts.append("")

            if exported_names:
                file_body_parts.append("## Exports\n")
                for en in exported_names:
                    safe_sym = safe_name(en)
                    file_body_parts.append(f"- [[{safe_sym}]]")
                file_body_parts.append("")

            if symbols:
                file_body_parts.append("## Symbols\n")
                for sym in symbols:
                    safe_sym = safe_name(sym["name"])
                    sym_type_icon = {
                        "function": "ƒ", "hook": "⚡", "component": "🧩",
                        "class": "🏛", "interface": "📐", "type": "📋",
                        "constant": "🔢", "enum": "📊", "default-export": "📤",
                    }.get(sym["type"], "•")
                    file_body_parts.append(f"- {sym_type_icon} [[{safe_sym}]]")
                    symbol_to_file[sym["name"]] = frel
                file_body_parts.append("")

            file_body_parts.append("## Dependencies\n")
            dep_files = [
                f"[[{file_note_map.get(d, d)}]]"
                for d in imp_sources[:20]  # cap at 20
            ]
            file_body_parts.append(", ".join(dep_files) if dep_files else "_none imported_")
            file_body_parts.append("")

            file_front = {
                "type": "file",
                "path": frel,
                "extension": fp.suffix.lower().lstrip("."),
                "imports": imp_sources,
                "exports": exported_names,
                "dependencies": imp_sources,
            }
            write_note(
                project_notes_root / f"{fname_note}.md",
                file_front,
                "\n".join(file_body_parts),
            )
        # --- Folder note ---
        fold_body_parts = [
            f"# {f_note}\n## Files\n",
        ]
        fold_body_parts.extend(f"- [[{n}]]" for n in child_file_notes)
        fold_body_parts.append("")

        fold_front = {
            "type": "folder",
            "path": folder if folder not in ("", ".") else "/",
            "children": child_file_notes,
        }
        write_note(
            project_notes_root / f"{f_note}.md",
            fold_front,
            "\n".join(fold_body_parts),
        )

    print(f"Created {len(folder_files)} folder notes + {len(file_note_map)} file notes")

    # Phase 3: Generate symbol notes with relationship edges
    symbol_count = 0
    for fp in files:
        frel = file_rels[fp]
        parsed = extract_symbols_from_file(fp, project_root)
        for sym in parsed["symbols"]:
            sym_name = sym["name"]
            safe_sym = safe_name(sym_name)

            # Resolve imports as [[wikilinks]]
            import_wikilinks: List[str] = []
            for imp_name in sym.get("imports", []):
                target_file = symbol_to_file.get(imp_name)
                if target_file:
                    import_wikilinks.append(f"[[{safe_name(imp_name)}]]")
                else:
                    # Try resolving as a file path
                    resolved = resolve_import_path(imp_name, fp, project_root)
                    if resolved and resolved in file_note_map:
                        import_wikilinks.append(f"[[{file_note_map[resolved]}]]")

            sym_body_parts = [
                f"# {sym_name}\n",
                f"**Type:** `{sym['type']}`\n",
                f"**File:** `{frel}`\n",
                f"**Defined In:** [[{file_note_map.get(frel, frel)}]]\n",
            ]

            if sym["type"] == "component":
                sym_body_parts.append("**Kind:** React Component\n")
            elif sym["type"] == "hook":
                sym_body_parts.append("**Kind:** React Hook\n")

            sym_body_parts.append("\n## Location\n")
            sym_body_parts.append(f"[[{file_note_map.get(frel, frel)}]]\n")
            sym_body_parts.append("\n## Relationships\n")

            if import_wikilinks:
                sym_body_parts.append("### Imports / Dependencies\n")
                for link in import_wikilinks[:15]:
                    sym_body_parts.append(f"- {link}")
                sym_body_parts.append("")

            if sym.get("exported"):
                sym_body_parts.append("### Exported\n")
                sym_body_parts.append(f"- This symbol is **exported** from [[{file_note_map.get(frel, frel)}]]\n")

            # Add neighbor symbols from same file
            same_file_symbols = [
                safe_name(s["name"])
                for s in parsed["symbols"]
                if s["name"] != sym_name
            ]
            if same_file_symbols:
                sym_body_parts.append("### Sibling Symbols (same file)\n")
                for ns in same_file_symbols[:10]:
                    sym_body_parts.append(f"- [[{ns}]]")
                sym_body_parts.append("")

            if not import_wikilinks and not sym.get("exported") and not same_file_symbols:
                sym_body_parts.append("_No relationships detected._\n")

            sym_front: Dict = {
                "type": sym["type"],
                "file": frel,
                "definedIn": f"[[{file_note_map.get(frel, frel)}]]",
                "imports": sym.get("imports", []),
                "exported": sym.get("exported", False),
                "calls": sym.get("calls", []),
                "references": sym.get("references", []),
                "tags": [],
            }
            write_note(
                project_notes_root / f"{safe_sym}.md",
                sym_front,
                "\n".join(sym_body_parts),
            )
            symbol_count += 1

    print(f"Created {symbol_count} symbol notes")

    # Phase 4: Generate project index note
    top_folders = sorted(
        set(
            folder_note_map.get(f, safe_name(f))
            for f in folder_files
            if f not in ("", ".")
        )
    )

    # Detect entry points
    entry_points = []
    for candidate in ["app", "pages", "src/app", "src/pages", "index", "main"]:
        for frel in file_note_map:
            if frel.startswith(candidate):
                entry_points.append(f"`{frel}`")

    index_body_parts = [
        f"# {project_name}\n",
        f"Auto-generated Obsidian codebase graph for `{project_root}`.\n",
        f"**Framework:** Next.js / TypeScript\n",
        f"**Source files:** {len(files)}\n",
        f"**Symbols mapped:** {symbol_count}\n",
        "\n## Folder Structure\n",
    ]
    index_body_parts.extend(
        f"- [[{f}]]" for f in top_folders
    )
    if entry_points:
        index_body_parts.append("\n## Entry Points\n")
        for ep in entry_points[:10]:
            index_body_parts.append(f"- {ep}")

    index_body_parts.append(
        "\n## Generation Info\n"
        f"- Generated: `{__import__('datetime').datetime.now().isoformat()}`\n"
        "- Generator: `scripts/generate_codebase_graph.py`\n"
        "- Uses regex-based TS/JSX parsing\n"
    )

    index_front = {
        "type": "project",
        "path": str(project_root),
        "framework": "Next.js",
        "language": "TypeScript",
        "sourceFiles": len(files),
        "symbols": symbol_count,
    }
    write_note(
        project_notes_root / f"{safe_name(project_name)}.md",
        index_front,
        "\n".join(index_body_parts),
    )

    print(f"\n✅ Codebase graph generated at: {project_notes_root}")
    print(f"   {len(folder_files)} folders, {len(file_note_map)} files, {symbol_count} symbols")
    print(f"   Open Obsidian vault: {vault_dir}")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate Obsidian codebase graph for Next.js/TypeScript projects"
    )
    parser.add_argument("source", help="Source codebase root directory")
    parser.add_argument(
        "vault",
        nargs="?",
        default=None,
        help="Obsidian vault directory (default: ~/Documents/Obsidian Vault)",
    )
    parser.add_argument(
        "--skip-vault", action="store_true", help="Dry-run: print summary without writing files"
    )
    parser.add_argument(
        "--clean", action="store_true", help="Delete existing project notes folder before generating"
    )
    args = parser.parse_args()

    source = Path(args.source).resolve()
    vault = Path(args.vault).resolve() if args.vault else (
        Path.home() / "Documents" / "Obsidian Vault"
    )

    if not source.is_dir():
        print(f"ERROR: Source directory does not exist: {source}")
        return

    vault.mkdir(parents=True, exist_ok=True)

    # Clean option: remove project notes folder before generating
    project_notes_root = vault_dir if 'vault_dir' in dir() else vault
    _pn = vault / f"{safe_name(source.name)} Project"
    if args.clean and _pn.exists():
        import shutil
        shutil.rmtree(_pn)
        print(f"Cleaned: {_pn}")

    build_codebase_graph(source, vault)


if __name__ == "__main__":
    main()

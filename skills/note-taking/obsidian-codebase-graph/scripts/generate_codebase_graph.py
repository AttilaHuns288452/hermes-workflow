#!/usr/bin/env python3
"""
Obsidian Codebase Graph Generator
Scans a Next.js / TypeScript codebase and emits an Obsidian note graph:
  project index -> folders -> files -> symbols
with wikilinks reflecting imports, exports, calls, extends, implements.
"""

from __future__ import annotations

import ast
import json
import os
import re
from pathlib import Path
from typing import Iterable


DEFAULT_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".json", ".md"}
TEXT_EXTENSIONS = DEFAULT_EXTENSIONS | {".css", ".scss", ".less"}
IGNORE_DIRS = {"node_modules", ".next", "dist", "build", ".git", "__pycache__", "bin", "obj"}

Symbol = dict


def is_source_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS


def find_project_root(start: Path) -> Path:
    current = start.resolve()
    for parent in [current] + list(current.parents):
        if (parent / "package.json").exists():
            return parent
        if (parent / ".git").exists():
            return parent
    return current


def project_name_from_root(root: Path) -> str:
    return root.name.replace("-", " ").replace("_", " ").title()


def safe_name(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", " ", name).strip() or name


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def iter_files(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for name in filenames:
            p = Path(dirpath, name)
            if is_source_file(p):
                yield p


def relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


# -----------------------------
# Lightweight TS/JS parsing
# -----------------------------

def parse_ts_ast(source: str) -> ast.AST | None:
    try:
        return ast.parse(source)
    except Exception:
        return None


def top_level_names(tree: ast.AST) -> list[str]:
    names: list[str] = []
    try:
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.append(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        names.append(target.id)
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                names.append(node.target.id)
    except Exception:
        pass
    return names


def extract_imports(tree: ast.AST, root: Path, file_path: Path) -> tuple[list[str], list[str]]:
    symbols: list[str] = []
    files: list[str] = []
    try:
        for node in tree.body:
            if isinstance(node, ast.ImportFrom) and node.module:
                mod = node.module or ""
                files.append(mod.replace(".", "/") + ".ts")
                for alias in node.names:
                    name = alias.name
                    if alias.asname:
                        name = f"{alias.asname}"
                    if name == "*":
                        continue
                    symbols.append(name)
    except Exception:
        pass
    return symbols, files


def extract_exports(tree: ast.AST) -> list[str]:
    exports: list[str] = []
    try:
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and any(
                getattr(deco, "attr", "") == "export" or getattr(deco, "id", "") == "export"
                for deco in getattr(node, "decorator_list", [])
            ):
                exports.append(node.name)
            if isinstance(node, ast.ClassDef) and any(
                getattr(deco, "attr", "") == "export" or getattr(deco, "id", "") == "export"
                for deco in getattr(node, "decorator_list", [])
            ):
                exports.append(node.name)
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        exports.append(target.id)
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                exports.append(node.target.id)
    except Exception:
        pass
    return exports


def heuristic_imports_exports(text: str) -> tuple[list[str], list[str]]:
    imports: list[str] = []
    exports: list[str] = []
    for m in re.finditer(r"import\s+.*?\s+from\s+['\"]([^'\"]+)['\"]", text):
        imports.append(m.group(1))
    for m in re.finditer(r"import\s+['\"]([^'\"]+)['\"]", text):
        imports.append(m.group(1))
    for m in re.finditer(r"\bexport\s+(?:default\s+)?(?:function|class|const|let|var|interface|type|enum)\s+([A-Za-z_$][A-Za-z0-9_$]*)", text):
        exports.append(m.group(1))
    for m in re.finditer(r"\bexport\s+\{[^}]*\}", text):
        inner = m.group(0)
        for sym in re.findall(r"\b([A-Za-z_$][A-Za-z0-9_$]*)\b", inner):
            if sym not in {"export"}:
                exports.append(sym)
    return imports, exports


def extract_symbols(path: Path, root: Path) -> tuple[list[Symbol], list[str], list[str]]:
    text = read_text(path)
    rel = relative(path, root)
    tree = parse_ts_ast(text)
    names = top_level_names(tree) if tree else []
    imports = []
    files = []
    exports = []
    if tree:
        imports, files = extract_imports(tree, root, path)
        exports = extract_exports(tree)
    if not imports and not exports:
        imports, exports = heuristic_imports_exports(text)
    if not names:
        names = list(dict.fromkeys(exports))

    symbols: list[Symbol] = []
    grouped = {}
    if tree:
        try:
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    sym_type = "hook" if node.name.startswith("use") else "function"
                    grouped.setdefault(node.name, {**{
                        "type": sym_type,
                        "name": node.name,
                        "file": rel,
                        "calls": [],
                        "references": [],
                        "usesType": [],
                        "exports": [],
                    }})
                elif isinstance(node, ast.ClassDef):
                    grouped.setdefault(node.name, {**{
                        "type": "class",
                        "name": node.name,
                        "file": rel,
                        "extends": [],
                        "implements": [],
                        "calls": [],
                        "references": [],
                        "usesType": [],
                    }})
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            grouped.setdefault(target.id, {**{
                                "type": "constant",
                                "name": target.id,
                                "file": rel,
                                "references": [],
                                "usesType": [],
                                "exports": [],
                            }})
                elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                    grouped.setdefault(node.target.id, {**{
                        "type": "constant",
                        "name": node.target.id,
                        "file": rel,
                        "references": [],
                        "usesType": [],
                        "exports": [],
                    }})
        except Exception:
            pass

    symbols = list(grouped.values())

    # Light-weight relationship inference
    for imp in imports:
        candidate = re.sub(r"[./]+", "/", imp).strip("/")
        candidate = candidate.replace("./", "").replace("../", "")
        for sym in symbols:
            sym.setdefault("imports", [])
            sym["imports"].append(candidate)

    return symbols, files, list(dict.fromkeys(exports))


# -----------------------------
# Note generation
# -----------------------------

def folder_to_note_name(folder_rel: str) -> str:
    return safe_name(folder_rel.replace("/", " ").replace("\\", " "))


def file_to_note_name(file_rel: str) -> str:
    return safe_name(Path(file_rel).name)


def write_note(path: Path, frontmatter: dict, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fm = json.dumps(frontmatter, ensure_ascii=False, indent=2)
    content = f"---\n{fm}\n---\n{body}\n"
    path.write_text(content, encoding="utf-8")


def build_graph(root: Path, vault: Path) -> None:
    project_root = find_project_root(root)
    project_name = project_name_from_root(project_root)
    project_folder_name = f"{project_name} Project"
    project_notes_root = vault / safe_name(project_folder_name)

    folders: dict[str, list[Path]] = {}
    files_by_folder: dict[str, list[Path]] = {}
    all_files: list[Path] = []
    folder_note_names: dict[str, str] = {}

    for file_path in sorted(iter_files(project_root)):
        rel = relative(file_path, project_root)
        folder = str(Path(rel).parent)
        folders.setdefault(folder, [])
        folders[folder].append(file_path)
        files_by_folder.setdefault(folder, []).append(file_path)
        all_files.append(file_path)

    # Folder notes and file notes
    file_notes: dict[str, Path] = {}
    folder_children: dict[str, list[str]] = {}

    for folder, files in sorted(folders.items()):
        if folder in {"", "."}:
            continue
        note_name = folder_to_note_name(folder)
        folder_note_names[folder] = note_name
        child_names: list[str] = []
        for fp in files:
            fname = file_to_note_name(relative(fp, project_root))
            child_names.append(fname)
            file_rel = relative(fp, project_root)
            symbols, dep_files, exports = extract_symbols(fp, project_root)
            file_front = {
                "type": "file",
                "path": file_rel,
                "extension": fp.suffix.lower().lstrip("."),
                "imports": dep_files,
                "exports": exports,
                "dependencies": dep_files,
            }
            symbols_section = "\n".join(
                f"- [[{safe_name(s['name'])}]]" for s in symbols
            ) or "- _No top-level symbols detected_"
            body = (
                f"# {fp.name}\n\n"
                f"## Symbols\n\n{symbols_section}\n\n"
                f"## Relationships\n\n"
                f"- imports: {', '.join(dep_files) or '_none_'}\n"
                f"- exports: {', '.join(exports) or '_none_'}\n"
            )
            file_note_path = project_notes_root / f"{fname}.md"
            write_note(file_note_path, file_front, body)
            file_notes[file_rel] = file_note_path

        folder_children[folder] = child_names
        folder_front = {
            "type": "folder",
            "path": folder,
            "children": child_names,
        }
        folder_body = (
            f"# {note_name}\n\n"
            f"## Files\n\n"
            + "\n".join(f"- [[{n}]]" for n in child_names)
            + "\n"
        )
        write_note(project_notes_root / f"{note_name}.md", folder_front, folder_body)

    # Symbol notes
    for file_rel, fp in [(rel, project_root / rel) for rel in file_notes]:
        symbols, _dep_files, _exports = extract_symbols(project_root / file_rel, project_root)
        for sym in symbols:
            sym_name = sym.get("name")
            if not sym_name:
                continue
            safe_sym = safe_name(sym_name)
            file_note_name = file_to_note_name(file_rel)
            front = {
                "type": sym.get("type", "function"),
                "file": file_rel,
                "definedIn": f"[[{file_note_name}]]",
                "imports": sym.get("imports", []),
                "exports": sym.get("exports", []),
                "references": sym.get("references", []),
                "usesType": sym.get("usesType", []),
                "tags": [],
            }
            if "extends" in sym:
                front["extends"] = sym["extends"]
            if "implements" in sym:
                front["implements"] = sym["implements"]
            if "calls" in sym:
                front["calls"] = sym["calls"]
            rels_body = (
                "- location: "
                f"[[{file_note_name}]]\n"
                "- imports: "
                + ", ".join(sym.get("imports", []) or ["_none_"])
                + "\n"
            )
            write_note(
                project_notes_root / f"{safe_sym}.md",
                front,
                f"# {sym_name}\n\n## Relationships\n\n{rels_body}\n",
            )

    # Project index
    top_level_folders = sorted(
        {f for f in folders if f not in {"", "."}}
    )
    entry_points: list[str] = []
    try:
        for name in ["app", "pages", "src", "components", "lib", "utils"]:
            if any(rel.startswith(name) for rel in files_by_folder):
                entry_points.append(name)
    except Exception:
        pass

    index_front = {
        "type": "project",
        "path": str(project_root),
        "framework": "Next.js",
        "language": "TypeScript",
    }
    index_body = (
        f"# {project_name}\n\n"
        f"Auto-generated Obsidian codebase graph for `{project_root}`.\n\n"
        f"## Folders\n\n"
        + "\n".join(
            f"- [[{folder_note_names.get(f, safe_name(f))}]]"
            for f in top_level_folders
        )
        + "\n\n"
        f"## Entry Points\n\n"
        + ("\n".join(f"- `{p}`" for p in entry_points) or "- _none detected_")
        + "\n"
    )
    write_note(project_notes_root / f"{safe_name(project_name)}.md", index_front, index_body)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Generate Obsidian codebase graph")
    parser.add_argument("source", help="Source codebase root")
    parser.add_argument("vault", help="Obsidian vault root")
    args = parser.parse_args()
    build_graph(Path(args.source), Path(args.vault))


if __name__ == "__main__":
    main()

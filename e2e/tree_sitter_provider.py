from __future__ import annotations

from pathlib import Path
from typing import Any


LANGUAGE_MODULES = {
    ".py": "tree_sitter_python",
    ".js": "tree_sitter_javascript",
    ".jsx": "tree_sitter_javascript",
    ".mjs": "tree_sitter_javascript",
    ".cjs": "tree_sitter_javascript",
    ".ts": "tree_sitter_typescript",
    ".tsx": "tree_sitter_typescript",
}

SYMBOL_NODES = {
    "function_definition",
    "function_declaration",
    "method_definition",
    "method_declaration",
    "function_item",
    "function_signature_item",
    "class_definition",
    "class_declaration",
    "class_specifier",
    "interface_declaration",
    "type_alias_declaration",
}
CALL_NODES = {"call", "call_expression", "new_expression", "method_invocation"}
IMPORT_NODES = {
    "import_statement",
    "import_declaration",
    "import_clause",
    "import_from_statement",
    "import_specifier",
    "require",
}


def available_for(path: Path) -> bool:
    return path.suffix.lower() in LANGUAGE_MODULES


def _language(module: Any, extension: str) -> Any:
    from tree_sitter import Language

    raw = module.language()
    if extension in {".ts", ".tsx"} and hasattr(module, "language_typescript"):
        raw = module.language_tsx() if extension == ".tsx" and hasattr(module, "language_tsx") else module.language_typescript()
    return Language(raw)


def _text(node: Any, source: bytes) -> str:
    return source[node.start_byte : node.end_byte].decode("utf-8", errors="replace")


def _identifier(node: Any, source: bytes) -> str:
    preferred = {
        "name",
        "identifier",
        "property_identifier",
        "type_identifier",
        "field_identifier",
        "member_name",
    }
    for child in node.children:
        if child.type in preferred:
            return _text(child, source).strip()
    return ""


def _load_module(extension: str) -> Any:
    import importlib

    return importlib.import_module(LANGUAGE_MODULES[extension])


def parse(path: Path, root: Path) -> tuple[list[dict], list[dict], list[dict]]:
    """Parse one file with Tree-sitter and return symbols, edges, diagnostics.

    The provider is intentionally optional. Missing bindings are reported to the
    caller so the deterministic regex parser can remain the portable fallback.
    """
    extension = path.suffix.lower()
    if not available_for(path):
        raise LookupError(f"no tree-sitter grammar configured for {extension}")

    from tree_sitter import Parser

    module = _load_module(extension)
    language = _language(module, extension)
    parser = Parser(language)
    source = path.read_bytes()
    tree = parser.parse(source)
    rel = path.relative_to(root).as_posix()
    symbols: list[dict] = []
    edges: list[dict] = []
    diagnostics: list[dict] = []

    def walk(node: Any, owner: str | None = None) -> None:
        nonlocal symbols, edges
        if node.type in SYMBOL_NODES:
            name = _identifier(node, source)
            if name:
                kind = "class" if "class" in node.type or "interface" in node.type else "function"
                line = node.start_point[0] + 1
                symbol_id = f"{rel}:{name}:{line}"
                symbols.append({"name": name, "kind": kind, "file": rel, "line": line, "id": symbol_id, "parser": "tree-sitter"})
                owner = symbol_id
        if node.type in IMPORT_NODES:
            value = _text(node, source).strip()
            if value:
                edges.append({"type": "imports", "from": rel, "to": value, "parser": "tree-sitter", "line": node.start_point[0] + 1})
        if node.type in CALL_NODES and owner:
            callee = ""
            if node.children:
                callee = _text(node.children[0], source).strip()
            if callee:
                edges.append({"type": "calls", "from": owner, "to": callee, "file": rel, "line": node.start_point[0] + 1, "parser": "tree-sitter"})
        for child in node.children:
            walk(child, owner)

    walk(tree.root_node)
    if tree.root_node.has_error:
        diagnostics.append({"file": rel, "error": "tree-sitter parse tree contains syntax errors", "parser": "tree-sitter"})
    return symbols, edges, diagnostics

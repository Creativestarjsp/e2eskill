from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections import deque
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "2"
SUPPORTED = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".java", ".go", ".rs", ".php", ".rb", ".cs", ".kt", ".swift"}
IGNORED = {".git", "node_modules", "vendor", "dist", "build", ".next", ".nuxt", "coverage", ".e2e"}


def _revision(root: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unknown"


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CodeBrain:
    """Repository graph with an optional Tree-sitter provider and portable fallback."""

    def __init__(self, root: str | Path = ".", provider: str = "auto") -> None:
        self.root = Path(root).resolve()
        self.store = self.root / ".e2e" / "brain.json"
        self.provider_preference = provider
        self.data: dict[str, Any] = {"schema_version": SCHEMA_VERSION, "files": [], "symbols": [], "edges": [], "errors": []}
        if self.store.exists():
            self.data = json.loads(self.store.read_text(encoding="utf-8"))

    def _files(self) -> list[Path]:
        result = []
        for p in self.root.rglob("*"):
            if not p.is_file() or p.suffix.lower() not in SUPPORTED:
                continue
            if any(part in IGNORED for part in p.parts):
                continue
            result.append(p)
        return sorted(result)

    def _extract_regex(self, path: Path, text: str) -> tuple[list[dict], list[dict]]:
        rel = path.relative_to(self.root).as_posix()
        symbols: list[dict] = []
        edges: list[dict] = []
        patterns = [
            (r"\b(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(", "function"),
            (r"\b(?:export\s+)?(?:async\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\(", "function"),
            (r"\b(?:export\s+)?class\s+([A-Za-z_$][\w$]*)", "class"),
            (r"\b(?:def|async\s+def)\s+([A-Za-z_]\w*)\s*\(", "function"),
            (r"\bfunc\s+(?:\([^)]*\)\s*)?([A-Za-z_]\w*)\s*\(", "function"),
            (r"\b(?:pub\s+)?fn\s+([A-Za-z_]\w*)\s*\(", "function"),
            (r"\b(?:public|private|protected|static|final|abstract|async|synchronized|native|inline|virtual|override|\s)+\s*(?:[\w<>\[\],.?]+\s+)+([A-Za-z_]\w*)\s*\(", "function"),
        ]
        seen = set()
        for pattern, kind in patterns:
            for m in re.finditer(pattern, text):
                name = m.group(1)
                key = (name, m.start())
                if key in seen:
                    continue
                seen.add(key)
                line = text.count("\n", 0, m.start()) + 1
                symbols.append({"name": name, "kind": kind, "file": rel, "line": line, "id": f"{rel}:{name}:{line}", "parser": "regex"})
        for m in re.finditer(r"(?:from\s+['\"]([^'\"]+)['\"]|import\s+['\"]([^'\"]+)['\"]|import\s+([\w.]+))", text):
            target = next(x for x in m.groups() if x)
            edges.append({"type": "imports", "from": rel, "to": target, "parser": "regex"})
        local_names = {s["name"] for s in symbols}
        for name in local_names:
            for m in re.finditer(r"\b" + re.escape(name) + r"\s*\(", text):
                line = text.count("\n", 0, m.start()) + 1
                owner = max((s for s in symbols if s["line"] <= line), key=lambda s: s["line"], default=None)
                if owner and owner["name"] != name:
                    edges.append({"type": "calls", "from": owner["id"], "to": name, "file": rel, "line": line, "parser": "regex"})
        return symbols, edges

    def _extract(self, path: Path, text: str) -> tuple[list[dict], list[dict], list[dict], str]:
        if self.provider_preference != "regex":
            try:
                from .tree_sitter_provider import available_for, parse
                if available_for(path):
                    symbols, edges, diagnostics = parse(path, self.root)
                    return symbols, edges, diagnostics, "tree-sitter"
            except (ImportError, ModuleNotFoundError):
                pass
            except Exception as exc:
                return *self._extract_regex(path, text), [{"file": path.relative_to(self.root).as_posix(), "error": str(exc), "parser": "tree-sitter"}], "regex-fallback"
        symbols, edges = self._extract_regex(path, text)
        return symbols, edges, [], "regex"

    def build(self) -> dict[str, Any]:
        files, symbols, edges, errors = [], [], [], []
        providers: dict[str, int] = {}
        for path in self._files():
            rel = path.relative_to(self.root).as_posix()
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
                files.append({"path": rel, "hash": _hash(path), "bytes": path.stat().st_size, "lines": text.count("\n") + 1})
                s, e, diagnostics, provider = self._extract(path, text)
                symbols.extend(s)
                edges.extend(e)
                errors.extend(diagnostics)
                providers[provider] = providers.get(provider, 0) + 1
            except Exception as exc:
                errors.append({"file": rel, "error": str(exc), "parser": "filesystem"})
        self.data = {
            "schema_version": SCHEMA_VERSION,
            "provider": "tree-sitter" if providers.get("tree-sitter") else ("regex-fallback" if providers.get("regex-fallback") else "regex"),
            "providers": providers,
            "revision": _revision(self.root),
            "files": files,
            "symbols": symbols,
            "edges": edges,
            "errors": errors,
        }
        self.store.parent.mkdir(parents=True, exist_ok=True)
        self.store.write_text(json.dumps(self.data, indent=2, sort_keys=True), encoding="utf-8")
        return self.data

    def check(self) -> dict[str, Any]:
        if not self.store.exists():
            return {"fresh": False, "reason": "not-built"}
        current = {p.relative_to(self.root).as_posix(): _hash(p) for p in self._files()}
        indexed = {x["path"]: x["hash"] for x in self.data.get("files", [])}
        changed = sorted(set(current) ^ set(indexed) | {p for p in current if p in indexed and current[p] != indexed[p]})
        return {"fresh": not changed and self.data.get("revision") == _revision(self.root), "changed": changed, "indexed_files": len(indexed), "provider": self.data.get("provider")}

    def search(self, query: str) -> list[dict]:
        q = query.lower()
        return [s for s in self.data.get("symbols", []) if q in s["name"].lower() or q in s["file"].lower()][:100]

    def find_symbol(self, name: str) -> list[dict]:
        return [s for s in self.data.get("symbols", []) if s["name"] == name]

    def _symbol_ids(self, target: str) -> set[str]:
        return {s["id"] for s in self.find_symbol(target)} | {target}

    def callers(self, target: str) -> list[dict]:
        ids = self._symbol_ids(target)
        return [e for e in self.data.get("edges", []) if e.get("type") == "calls" and e.get("to") in ids]

    def callees(self, target: str) -> list[dict]:
        ids = self._symbol_ids(target)
        return [e for e in self.data.get("edges", []) if e.get("type") == "calls" and e.get("from") in ids]

    def dependencies(self, target: str) -> list[dict]:
        path = target
        if self.find_symbol(target):
            path = self.find_symbol(target)[0]["file"]
        return [e for e in self.data.get("edges", []) if e.get("type") == "imports" and (e.get("from") == path or e.get("to") == path)]

    def impact(self, target: str) -> dict[str, Any]:
        seeds = self._symbol_ids(target)
        direct = self.callers(target)
        transitive, seen = [], set(seeds)
        queue = deque(e.get("from") for e in direct)
        while queue:
            node = queue.popleft()
            if not node or node in seen:
                continue
            seen.add(node)
            transitive.append(node)
            for e in self.data.get("edges", []):
                if e.get("type") == "calls" and e.get("to") == node:
                    queue.append(e.get("from"))
        files = sorted({s["file"] for s in self.data.get("symbols", []) if s["id"] in seen} | {e.get("file") for e in direct if e.get("file")})
        return {"target": target, "direct": direct, "transitive_symbols": transitive, "affected_files": files, "coverage": "partial" if self.data.get("errors") else "structural"}

    def map(self, prefix: str = "") -> dict[str, list]:
        files = [f["path"] for f in self.data.get("files", []) if f["path"].startswith(prefix)]
        return {p: [s["name"] for s in self.data.get("symbols", []) if s["file"] == p] for p in files}

    def context(self, task: str) -> dict[str, Any]:
        hits = self.search(task)
        files = sorted({h["file"] for h in hits})
        if not files:
            words = {w.lower() for w in re.findall(r"[A-Za-z_][\w-]{2,}", task)}
            files = [f["path"] for f in self.data.get("files", []) if any(w in f["path"].lower() for w in words)][:20]
        return {"objective": task, "relevant_files": files[:20], "relevant_symbols": hits[:50], "tests": [p for p in files if "test" in p.lower() or "spec" in p.lower()], "provenance": {"provider": self.data.get("provider"), "providers": self.data.get("providers", {}), "revision": self.data.get("revision"), "coverage": "partial" if self.data.get("errors") else "structural"}}

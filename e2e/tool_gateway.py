from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

from .tools import audit, decide, load_tools

JSON = dict[str, Any]


class ToolGatewayError(RuntimeError):
    pass


def _safe_path(root: Path, value: str) -> Path:
    candidate = (root / value).resolve()
    if candidate != root and root not in candidate.parents:
        raise ToolGatewayError("path escapes repository root")
    return candidate


def _repo_read(root: Path, arguments: JSON) -> JSON:
    path = _safe_path(root, str(arguments.get("path", "")))
    if not path.is_file():
        raise ToolGatewayError("file-not-found")
    max_bytes = min(max(int(arguments.get("max_bytes", 200_000)), 1), 200_000)
    return {"path": str(path.relative_to(root)), "content": path.read_text(encoding="utf-8")[:max_bytes]}


def _git_read(root: Path, arguments: JSON) -> JSON:
    operation = str(arguments.get("operation", "status"))
    commands = {
        "status": ["status", "--short", "--branch"],
        "diff": ["diff", "--stat"],
        "log": ["log", "-10", "--oneline"],
        "branch": ["branch", "--show-current"],
    }
    if operation not in commands:
        raise ToolGatewayError("unsupported-git-operation")
    proc = subprocess.run(["git", *commands[operation]], cwd=root, text=True, capture_output=True, timeout=30)
    if proc.returncode:
        raise ToolGatewayError(proc.stderr.strip() or "git-command-failed")
    return {"operation": operation, "stdout": proc.stdout}


def _shell_read(root: Path, arguments: JSON) -> JSON:
    command = str(arguments.get("command", ""))
    allowed = {"pwd", "git status --short --branch", "git diff --stat", "git branch --show-current", "python -m pytest -q"}
    if command not in allowed:
        raise ToolGatewayError("command-not-allowlisted")
    proc = subprocess.run(shlex.split(command), cwd=root, text=True, capture_output=True, timeout=120)
    return {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


HANDLERS: dict[str, Callable[[Path, JSON], JSON]] = {
    "repo.read": _repo_read,
    "git.read": _git_read,
    "shell.read": _shell_read,
}


def _tool_schema(name: str, description: str) -> JSON:
    schemas = {
        "repo.read": {"type": "object", "properties": {"path": {"type": "string"}, "max_bytes": {"type": "integer"}}, "required": ["path"], "additionalProperties": False},
        "git.read": {"type": "object", "properties": {"operation": {"type": "string", "enum": ["status", "diff", "log", "branch"]}}, "additionalProperties": False},
        "shell.read": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"], "additionalProperties": False},
    }
    return {"name": name, "description": description, "inputSchema": schemas[name]}


def visible_tools(root: Path, role: str) -> list[JSON]:
    return sorted(
        [_tool_schema(tool.name, tool.description) for tool in load_tools(root) if role in tool.roles and tool.approval == "none" and tool.name in HANDLERS],
        key=lambda item: item["name"],
    )


def write_mcp_configs(root: str | Path, role: str = "sd1") -> dict[str, str]:
    root_path = Path(root).resolve()
    config_dir = root_path / ".e2e" / "mcp"
    config_dir.mkdir(parents=True, exist_ok=True)
    command = sys.executable
    args = ["-m", "e2e.tool_gateway", "--root", str(root_path), "--role", role]
    claude_path = config_dir / "claude.json"
    claude_path.write_text(json.dumps({"mcpServers": {"e2e-gateway": {"command": command, "args": args, "env": {"E2E_TOOL_ROLE": role}}}}, indent=2, sort_keys=True), encoding="utf-8")
    codex_path = config_dir / "codex.toml"
    codex_path.write_text("[mcp_servers.e2e-gateway]\n" f"command = {json.dumps(command)}\n" f"args = {json.dumps(args)}\n" "enabled = true\nrequired = true\n", encoding="utf-8")
    return {"claude": str(claude_path), "codex": str(codex_path)}


def _response(request_id: Any, result: JSON | None = None, error: JSON | None = None) -> JSON:
    response: JSON = {"jsonrpc": "2.0", "id": request_id}
    if error is not None:
        response["error"] = error
    else:
        response["result"] = result or {}
    return response


def handle(root: Path, role: str, request: JSON) -> JSON | None:
    method = request.get("method")
    request_id = request.get("id")
    if method == "notifications/initialized":
        return None
    if method == "initialize":
        return _response(request_id, {"protocolVersion": "2026-07-28", "capabilities": {"tools": {"listChanged": False}}, "serverInfo": {"name": "e2e-gateway", "version": "0.1.0"}})
    if method == "tools/list":
        return _response(request_id, {"tools": visible_tools(root, role)})
    if method != "tools/call":
        return _response(request_id, error={"code": -32601, "message": "method not found"})
    params = request.get("params") or {}
    name = str(params.get("name", ""))
    arguments = params.get("arguments") or {}
    tool = next((item for item in load_tools(root) if item.name == name), None)
    if tool is None:
        return _response(request_id, error={"code": -32602, "message": "unknown tool"})
    decision = decide(root, name, role, set(tool.scopes))
    if not decision.allowed:
        audit(root, agent=f"mcp:{role}", runtime="mcp", tool=name, operation="call", decision=decision, arguments=arguments, result=decision.reason)
        return _response(request_id, error={"code": -32003, "message": decision.reason})
    handler = HANDLERS.get(name)
    if handler is None:
        return _response(request_id, error={"code": -32004, "message": "tool transport unavailable"})
    try:
        value = handler(root, arguments)
        audit(root, agent=f"mcp:{role}", runtime="mcp", tool=name, operation="call", decision=decision, arguments=arguments, result="success")
        return _response(request_id, {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False)}], "structuredContent": value})
    except (ToolGatewayError, OSError, ValueError, UnicodeError) as exc:
        audit(root, agent=f"mcp:{role}", runtime="mcp", tool=name, operation="call", decision=decision, arguments=arguments, result=str(exc))
        return _response(request_id, error={"code": -32005, "message": str(exc)})


def serve(root: str | Path = ".", role: str | None = None) -> int:
    root_path = Path(root).resolve()
    selected_role = role or os.environ.get("E2E_TOOL_ROLE", "sd1")
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            response = handle(root_path, selected_role, json.loads(line))
        except json.JSONDecodeError:
            response = _response(None, error={"code": -32700, "message": "parse error"})
        except Exception as exc:
            response = _response(None, error={"code": -32603, "message": str(exc)})
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="e2e-mcp-gateway")
    parser.add_argument("--root", default=".")
    parser.add_argument("--role", default=os.environ.get("E2E_TOOL_ROLE", "sd1"))
    args = parser.parse_args()
    return serve(args.root, args.role)


if __name__ == "__main__":
    raise SystemExit(main())

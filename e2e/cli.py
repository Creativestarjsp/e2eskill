from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .adapters import capabilities, detect
from .benchmark import run_case
from .brain import CodeBrain
from .context import build_context
from .release import release_check
from .skills import discover, match
from .verify import verify


def _root() -> Path:
    return Path.cwd()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="e2e", description="E2E engineering runtime")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("init", "doctor", "status", "release"):
        sub.add_parser(name)
    c = sub.add_parser("context"); c.add_argument("task")
    s = sub.add_parser("skill"); ss = s.add_subparsers(dest="skill_cmd", required=True); ss.add_parser("list"); si = ss.add_parser("inspect"); si.add_argument("name")
    b = sub.add_parser("brain"); bs = b.add_subparsers(dest="brain_cmd", required=True); bs.add_parser("build"); bs.add_parser("check"); bm = bs.add_parser("map"); bm.add_argument("path", nargs="?", default=""); bx = bs.add_parser("search"); bx.add_argument("query"); bi = bs.add_parser("impact"); bi.add_argument("target")
    r = sub.add_parser("run"); r.add_argument("task")
    v = sub.add_parser("verify"); v.add_argument("--test", dest="test_command")
    be = sub.add_parser("benchmark"); be.add_argument("command"); be.add_argument("--repetitions", type=int, default=1)
    args = p.parse_args(argv)
    root = _root()
    if args.cmd == "init":
        (root / ".e2e").mkdir(exist_ok=True); print(json.dumps({"status":"initialized","root":str(root)}, indent=2)); return 0
    if args.cmd == "doctor":
        print(json.dumps({"runtime": detect(root), "capabilities": capabilities(root), "python": os.sys.version}, indent=2)); return 0
    if args.cmd == "status":
        brain = CodeBrain(root); print(json.dumps({"runtime": detect(root), "brain": brain.check(), "skills": len(discover(root)), "capabilities": capabilities(root)}, indent=2)); return 0
    if args.cmd == "context":
        brain = CodeBrain(root)
        if not brain.store.exists(): brain.build()
        print(json.dumps({"context": build_context(root, args.task, brain), "skills": match(root, args.task)}, indent=2)); return 0
    if args.cmd == "skill":
        skills = discover(root)
        if args.skill_cmd == "list": print(json.dumps(skills, indent=2)); return 0
        found = next((s for s in skills if s["name"] == args.name), None); print(json.dumps(found or {"error":"skill-not-found"}, indent=2)); return 0 if found else 1
    if args.cmd == "brain":
        brain = CodeBrain(root)
        if args.brain_cmd == "build": print(json.dumps({"indexed_files": len(brain.build()["files"])}, indent=2)); return 0
        if not brain.store.exists(): brain.build()
        if args.brain_cmd == "check": print(json.dumps(brain.check(), indent=2)); return 0
        if args.brain_cmd == "map": print(json.dumps(brain.map(args.path), indent=2)); return 0
        if args.brain_cmd == "search": print(json.dumps(brain.search(args.query), indent=2)); return 0
        if args.brain_cmd == "impact": print(json.dumps(brain.impact(args.target), indent=2)); return 0
    if args.cmd == "run":
        brain = CodeBrain(root); brain.build(); print(json.dumps({"task":args.task,"context":build_context(root,args.task,brain),"skills":match(root,args.task),"next":"SD2 should decompose and assign SD1 workers."}, indent=2)); return 0
    if args.cmd == "verify":
        result = verify(root, args.test_command); print(json.dumps(result, indent=2)); return 0 if result["status"] == "pass" else 1
    if args.cmd == "benchmark":
        result = run_case(root, args.command, args.repetitions); print(json.dumps(result, indent=2)); return 0 if result["success_rate"] == 1 else 1
    if args.cmd == "release":
        result = release_check(root); print(json.dumps(result, indent=2)); return 0 if result["status"] == "pass" else 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

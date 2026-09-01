from pathlib import Path

from e2e.context import build_context
from e2e.hooks import protected_path, secret_scan
from e2e.skills import discover, match


def test_context_is_bounded_and_has_rules(tmp_path: Path):
    (tmp_path / "CLAUDE.md").write_text("# Rules\nUse evidence.\n")
    ctx = build_context(tmp_path, "build authentication flow")
    assert ctx["objective"] == "build authentication flow"
    assert ctx["rules"]["precedence"][0] == "safety"


def test_protected_paths_block():
    assert protected_path(".env") ["status"] == "block"
    assert protected_path("src/app.py")["status"] == "pass"


def test_secret_scan(tmp_path: Path):
    (tmp_path / "bad.py").write_text("api_key = '123456789abcdef'")
    assert secret_scan(tmp_path)["status"] == "block"


def test_skill_registry_discovers_and_matches(tmp_path: Path):
    skill = tmp_path / "skills" / "backend-developer"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("# Backend\n\n## Purpose\nBuild backend APIs.\n\n## Use When\nUse for backend API work.\n")
    assert discover(tmp_path)
    assert match(tmp_path, "backend API")

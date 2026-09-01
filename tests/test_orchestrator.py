from pathlib import Path

from e2e.orchestrator import MAX_ACTIVE_WORKERS, plan


def test_plan_respects_worker_limit_and_sd3_gate(tmp_path: Path):
    skills = tmp_path / "skills"
    for name in ("frontend-developer", "qa-engineer", "security-engineer", "software-architect", "devops-engineer"):
        folder = skills / name
        folder.mkdir(parents=True)
        (folder / "SKILL.md").write_text(f"# {name}\n\n## Purpose\nBuild {name} solutions.\n\n## Use When\nUse this for {name} work.\n")
    result = plan(tmp_path, "build frontend API and security deployment")
    assert result["role"] == "SD2"
    assert len(result["workers"]) <= MAX_ACTIVE_WORKERS
    assert result["supervisor_gate"]["role"] == "SD3"
    assert result["supervisor_gate"]["required"] is True
    assert all("depends_on" in worker for worker in result["workers"])

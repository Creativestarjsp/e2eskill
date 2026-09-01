from pathlib import Path

import pytest

from e2e.context import build_context
from e2e.memory import Memory


def test_memory_rejects_secret_like_content(tmp_path: Path):
    memory = Memory(tmp_path)
    with pytest.raises(ValueError):
        memory.add("decision", "project", "Use api_key from environment")


def test_memory_search_returns_relevant_current_record(tmp_path: Path):
    memory = Memory(tmp_path)
    record = memory.add("decision", "architecture", "Use PostgreSQL for durable project state", evidence=["approved in architecture review"])
    memory.add("decision", "architecture", "Old database choice", supersedes=record["id"])
    results = memory.search("PostgreSQL durable state")
    assert results == []


def test_memory_can_expire_and_list_history(tmp_path: Path):
    memory = Memory(tmp_path)
    record = memory.add("note", "project", "Temporary migration constraint", expires_days=0)
    assert memory.list() == []
    assert memory.list(include_expired=True)[0]["id"] == record["id"]


def test_context_includes_relevant_memory(tmp_path: Path):
    memory = Memory(tmp_path)
    memory.add("decision", "project", "Keep authentication behind the existing API boundary")
    context = build_context(tmp_path, "authentication API boundary")
    assert context["memory"]
    assert "existing API boundary" in context["memory"][0]["summary"]

#!/usr/bin/env python3
"""Dependency-free structural checks for factory templates."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "README.md",
    "docs/WORKFLOW.md",
    "docs/SECURITY.md",
    "docs/REPOSITORY_SETUP.md",
    "docs/ISSUE_CLOSURE.md",
    "templates/verify.yml",
    "templates/promote.yml",
)
for filename in REQUIRED:
    file = ROOT / filename
    assert file.is_file(), f"Missing {filename}"
    assert file.stat().st_size > 50, f"Empty {filename}"

workflow = (ROOT / "docs/WORKFLOW.md").read_text()
for command in ("/feature", "/execute", "/execute test", "/execute prod"):
    assert command in workflow, f"Missing command: {command}"
promotion = (ROOT / "templates/promote.yml").read_text()
assert "workflow_dispatch" in promotion
assert "commit_sha" in promotion
assert "deploy:" not in promotion, "Example must not deploy automatically"
print("Factory templates validated")

closure = (ROOT / "docs/ISSUE_CLOSURE.md").read_text()
for marker in ("Dev-Completes:", "dev-acceptance-verified", "Test and Production", "read-only"):
    assert marker in closure, f"Missing closure policy: {marker}"

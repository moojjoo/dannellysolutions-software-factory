#!/usr/bin/env python3
"""Run bounded local checks and capture exact-PR-head GitHub evidence."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import shlex
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence


PASSING_CHECK_STATES = {"SUCCESS"}


class EvidenceError(RuntimeError):
    """A fail-closed verification error."""


def _run_text(args: Sequence[str], cwd: Path) -> str:
    result = subprocess.run(
        args, cwd=cwd, check=False, text=True, capture_output=True
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise EvidenceError(f"{' '.join(args)} failed: {detail}")
    return result.stdout.strip()


def validate_linked_worktree(cwd: Path) -> dict[str, str]:
    root = Path(_run_text(("git", "rev-parse", "--show-toplevel"), cwd)).resolve()
    git_dir_raw = _run_text(("git", "rev-parse", "--git-dir"), root)
    common_raw = _run_text(("git", "rev-parse", "--git-common-dir"), root)
    git_dir = (root / git_dir_raw).resolve() if not Path(git_dir_raw).is_absolute() else Path(git_dir_raw).resolve()
    common_dir = (root / common_raw).resolve() if not Path(common_raw).is_absolute() else Path(common_raw).resolve()
    if git_dir == common_dir:
        raise EvidenceError("refusing primary checkout; use a registered linked worktree")
    registered = _run_text(("git", "worktree", "list", "--porcelain"), root)
    registered_roots = {
        Path(line.removeprefix("worktree ")).resolve()
        for line in registered.splitlines()
        if line.startswith("worktree ")
    }
    if root not in registered_roots:
        raise EvidenceError(f"worktree is not registered: {root}")
    dirty = _run_text(("git", "status", "--porcelain", "--untracked-files=all"), root)
    if dirty:
        raise EvidenceError("refusing dirty worktree; commit or stash changes before verification")
    return {"root": str(root), "git_dir": str(git_dir), "common_dir": str(common_dir)}


@dataclass(frozen=True)
class CommandSpec:
    name: str
    command: str


@dataclass(frozen=True)
class CommandResult:
    name: str
    command: str
    status: str
    exit_code: int | None
    duration_seconds: float
    stdout: str
    stderr: str


def parse_command(value: str) -> CommandSpec:
    name, separator, command = value.partition("=")
    if not separator or not name.strip() or not command.strip():
        raise argparse.ArgumentTypeError("commands must use NAME=COMMAND")
    return CommandSpec(name.strip(), command.strip())


def run_command(spec: CommandSpec, cwd: Path, timeout: float) -> CommandResult:
    started = time.monotonic()
    try:
        parts = shlex.split(spec.command)
    except ValueError as error:
        return CommandResult(spec.name, spec.command, "invalid", None, 0.0, "", str(error))
    if not parts or shutil.which(parts[0]) is None:
        return CommandResult(
            spec.name, spec.command, "missing-tool", None,
            round(time.monotonic() - started, 3), "", f"tool not found: {parts[0] if parts else '<empty>'}",
        )
    process = subprocess.Popen(
        spec.command,
        cwd=cwd,
        shell=True,
        executable="/bin/bash",
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
        status = "passed" if process.returncode == 0 else "failed"
        exit_code = process.returncode
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            stdout, stderr = process.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
        status = "timed-out"
        exit_code = None
    return CommandResult(
        spec.name,
        spec.command,
        status,
        exit_code,
        round(time.monotonic() - started, 3),
        stdout[-12000:],
        stderr[-12000:],
    )


def run_commands(
    specs: Sequence[CommandSpec], cwd: Path, timeout: float, jobs: int
) -> list[CommandResult]:
    if not specs:
        raise EvidenceError("at least one explicit verification command is required")
    if jobs < 1:
        raise EvidenceError("jobs must be at least 1")
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(jobs, len(specs))) as pool:
        futures = {pool.submit(run_command, spec, cwd, timeout): index for index, spec in enumerate(specs)}
        indexed = [(futures[future], future.result()) for future in concurrent.futures.as_completed(futures)]
    return [result for _, result in sorted(indexed)]


class GitHubClient:
    @staticmethod
    def _run(args: Sequence[str], allowed_exit_codes: set[int] | None = None) -> str:
        if shutil.which("gh") is None:
            raise EvidenceError("gh is not installed; cannot collect live GitHub evidence")
        result = subprocess.run(args, check=False, text=True, capture_output=True)
        allowed = allowed_exit_codes or {0}
        if result.returncode not in allowed:
            detail = result.stderr.strip() or result.stdout.strip()
            raise EvidenceError(f"{' '.join(args)} failed: {detail}")
        return result.stdout

    def pr(self, repo: str, number: int) -> dict[str, Any]:
        raw = self._run((
            "gh", "pr", "view", str(number), "-R", repo,
            "--json", "headRefOid,baseRefName,mergeStateStatus,statusCheckRollup,url",
        ))
        try:
            return json.loads(raw)
        except json.JSONDecodeError as error:
            raise EvidenceError(f"gh returned invalid PR evidence JSON: {error}") from error


def collect_github_evidence(repo: str, pr_number: int, client: GitHubClient) -> dict[str, Any]:
    before = client.pr(repo, pr_number)
    sha = before["headRefOid"]
    after = client.pr(repo, pr_number)
    after_sha = after["headRefOid"]
    if sha != after_sha:
        raise EvidenceError(f"PR head changed while collecting evidence: {sha} -> {after_sha}")
    # Use the second snapshot so conclusions and mergeability are the freshest
    # state observed after confirming that the PR head did not move.
    checks = after.get("statusCheckRollup") or []
    normalized = sorted(
        ({
            "name": check.get("name") or check.get("context"),
            "state": check.get("conclusion") or check.get("state") or check.get("status"),
            "workflow": check.get("workflowName"),
            "url": check.get("detailsUrl") or check.get("targetUrl"),
        } for check in checks),
        key=lambda item: (item["name"] or "", item["url"] or ""),
    )
    states = {str(check["state"]).upper() for check in normalized}
    merge_state = str(after.get("mergeStateStatus") or "UNKNOWN").upper()
    checks_passed = bool(normalized) and states <= PASSING_CHECK_STATES
    passed = checks_passed and merge_state == "CLEAN"
    return {
        "repository": repo,
        "pull_request": pr_number,
        "pull_request_url": after["url"],
        "head_sha": sha,
        "head_stable": True,
        "base_ref": after.get("baseRefName"),
        "merge_state": merge_state,
        "required_checks": normalized,
        "status": "passed" if passed else "blocked",
        "diagnostic": (
            "all reported checks passed and GitHub reports the stable PR head mergeable"
            if passed
            else "checks are missing, pending, unsuccessful, or GitHub reports a merge blocker"
        ),
    }


def render_markdown(evidence: dict[str, Any]) -> str:
    lines = [
        "# Verification evidence",
        "",
        f"Overall: **{evidence['status']}**",
        "",
        "## Local verification (not live acceptance)",
        "",
        "| Check | Status | Seconds |",
        "| --- | --- | ---: |",
    ]
    for command in evidence["local"]["commands"]:
        lines.append(f"| {command['name']} | {command['status']} | {command['duration_seconds']:.3f} |")
    github = evidence.get("github")
    if github:
        lines.extend([
            "", "## Live GitHub checks and merge state", "",
            f"PR: [{github['repository']}#{github['pull_request']}]({github['pull_request_url']})  ",
            f"Exact head: `{github['head_sha']}`  ",
            f"Status: **{github['status']}** — {github['diagnostic']}", "",
            "| Reported check | State | Link |",
            "| --- | --- | --- |",
        ])
        for check in github["required_checks"]:
            link = f"[details]({check['url']})" if check["url"] else ""
            lines.append(f"| {check['name']} | {check['state']} | {link} |")
    else:
        lines.extend(["", "## Live GitHub checks and merge state", "", "Not collected; local checks are not live acceptance."])
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--command", action="append", type=parse_command, required=True, dest="commands")
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument("--repo", help="OWNER/REPO for live PR evidence")
    parser.add_argument("--pr", type=int, help="pull request number for live evidence")
    parser.add_argument("--json-out", type=Path, default=Path("verification-evidence.json"))
    parser.add_argument("--markdown-out", type=Path, default=Path("verification-evidence.md"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if bool(args.repo) != bool(args.pr):
        raise EvidenceError("--repo and --pr must be supplied together")
    worktree = validate_linked_worktree(Path.cwd())
    started = time.monotonic()
    results = run_commands(args.commands, Path(worktree["root"]), args.timeout, args.jobs)
    github = collect_github_evidence(args.repo, args.pr, GitHubClient()) if args.repo else None
    local_status = "passed" if all(result.status == "passed" for result in results) else "failed"
    overall = "passed" if local_status == "passed" and (not github or github["status"] == "passed") else "blocked"
    evidence = {
        "schema_version": 1,
        "status": overall,
        "worktree": worktree,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "local": {"status": local_status, "authority": "local-only", "commands": [asdict(result) for result in results]},
        "github": github,
    }
    args.json_out.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    args.markdown_out.write_text(render_markdown(evidence))
    print(render_markdown(evidence), end="")
    return 0 if overall == "passed" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except EvidenceError as error:
        print(f"verification-evidence: {error}", file=sys.stderr)
        sys.exit(2)

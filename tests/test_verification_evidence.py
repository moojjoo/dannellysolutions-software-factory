import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).parents[1]))

from scripts.verification_evidence import (
    CommandSpec,
    EvidenceError,
    collect_github_evidence,
    render_markdown,
    run_commands,
    validate_linked_worktree,
)


class VerificationEvidenceTests(unittest.TestCase):
    def test_parallel_commands_preserve_order_and_reduce_wall_time(self):
        commands = [
            CommandSpec("first", "python3 -c 'import time; time.sleep(.25)'"),
            CommandSpec("second", "python3 -c 'import time; time.sleep(.25)'"),
        ]
        started = time.monotonic()
        results = run_commands(commands, Path.cwd(), timeout=2, jobs=2)
        self.assertLess(time.monotonic() - started, 0.45)
        self.assertEqual([result.name for result in results], ["first", "second"])
        self.assertTrue(all(result.status == "passed" for result in results))

    def test_failure_timeout_and_missing_tool_are_diagnostic(self):
        commands = [
            CommandSpec("failure", "python3 -c 'raise SystemExit(7)'"),
            CommandSpec("timeout", "python3 -c 'import time; time.sleep(2)'"),
            CommandSpec("missing", "factory-tool-that-does-not-exist --version"),
        ]
        results = run_commands(commands, Path.cwd(), timeout=0.1, jobs=3)
        self.assertEqual([result.status for result in results], ["failed", "timed-out", "missing-tool"])
        self.assertEqual(results[0].exit_code, 7)
        self.assertIn("tool not found", results[2].stderr)

    def test_primary_and_dirty_worktrees_fail_closed(self):
        responses = {
            ("git", "rev-parse", "--show-toplevel"): "/repo",
            ("git", "rev-parse", "--git-dir"): ".git",
            ("git", "rev-parse", "--git-common-dir"): ".git",
        }
        with mock.patch("scripts.verification_evidence._run_text", side_effect=lambda args, cwd: responses[tuple(args)]):
            with self.assertRaisesRegex(EvidenceError, "primary checkout"):
                validate_linked_worktree(Path("/repo"))

        def dirty_response(args, cwd):
            values = {
                ("git", "rev-parse", "--show-toplevel"): "/repo-linked",
                ("git", "rev-parse", "--git-dir"): "/repo/.git/worktrees/linked",
                ("git", "rev-parse", "--git-common-dir"): "/repo/.git",
                ("git", "worktree", "list", "--porcelain"): "worktree /repo-linked\nHEAD abc\n",
                ("git", "status", "--porcelain", "--untracked-files=all"): " M file.py",
            }
            return values[tuple(args)]

        with mock.patch("scripts.verification_evidence._run_text", side_effect=dirty_response):
            with self.assertRaisesRegex(EvidenceError, "dirty worktree"):
                validate_linked_worktree(Path("/repo-linked"))

    def test_github_evidence_requires_stable_head_and_passing_required_checks(self):
        class Client:
            calls = 0
            def pr(self, repo, number):
                self.calls += 1
                return {"head": {"sha": "a" * 40}, "html_url": "https://example/pr/20"}
            def required_checks(self, repo, number):
                return [{"name": "test", "state": "SUCCESS", "link": "https://example/run", "bucket": "pass", "workflow": "CI"}]

        evidence = collect_github_evidence("owner/repo", 20, Client())
        self.assertEqual(evidence["status"], "passed")
        self.assertEqual(evidence["head_sha"], "a" * 40)

        class PendingClient(Client):
            def required_checks(self, repo, number):
                return [{"name": "test", "state": "PENDING", "link": None, "bucket": "pending", "workflow": "CI"}]

        self.assertEqual(collect_github_evidence("owner/repo", 20, PendingClient())["status"], "blocked")

        class EmptyClient(Client):
            def required_checks(self, repo, number):
                return []

        self.assertEqual(collect_github_evidence("owner/repo", 20, EmptyClient())["status"], "blocked")

        class MovingClient(Client):
            def pr(self, repo, number):
                self.calls += 1
                sha = ("a" if self.calls == 1 else "b") * 40
                return {"head": {"sha": sha}, "html_url": "https://example/pr/20"}

        with self.assertRaisesRegex(EvidenceError, "head changed"):
            collect_github_evidence("owner/repo", 20, MovingClient())

    def test_markdown_separates_local_from_live_evidence(self):
        evidence = {
            "status": "blocked",
            "local": {"commands": [{"name": "unit", "status": "passed", "duration_seconds": 0.25}]},
            "github": None,
        }
        rendered = render_markdown(evidence)
        self.assertIn("Local verification (not live acceptance)", rendered)
        self.assertIn("Not collected; local checks are not live acceptance", rendered)


if __name__ == "__main__":
    unittest.main()

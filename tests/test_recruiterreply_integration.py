"""Cross-repository contract checks for the RecruiterReply closure integration."""

import os
from pathlib import Path
import unittest
from urllib.request import Request, urlopen


RECRUITERREPLY_REF = os.environ.get("RECRUITERREPLY_REF", "main")
BASE = (
    "https://raw.githubusercontent.com/moojjoo/recruiterreply/"
    f"{RECRUITERREPLY_REF}/"
)


def fetch(path: str) -> str:
    request = Request(BASE + path, headers={"User-Agent": "factory-contract-test"})
    with urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8")


class RecruiterReplyIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template = fetch(".github/PULL_REQUEST_TEMPLATE.md")
        cls.reconciler = fetch(".github/scripts/reconcile-dev-issues.cjs")
        cls.audit_workflow = fetch(".github/workflows/issue-reconciliation-audit.yml")
        cls.test_promotion = fetch(".github/workflows/promote-test.yml")
        cls.prod_promotion = fetch(".github/workflows/promote-prod.yml")

    def test_shared_acceptance_contract_is_consumed(self):
        for marker in ("Refs #123", "Dev-Completes: #123", "dev-acceptance-verified"):
            self.assertIn(marker, self.template)
        for marker in ("PROJECTS_WRITE_TOKEN", "DEV_DEPLOYMENT_VERIFIED", "merge_commit_sha === sha",
                       "dev-acceptance-verified", "checksPass"):
            self.assertIn(marker, self.reconciler)

    def test_read_only_audit_and_manual_release_gates_are_present(self):
        self.assertIn("workflow_dispatch:", self.audit_workflow)
        self.assertIn("schedule:", self.audit_workflow)
        self.assertIn("workflow_dispatch:", self.test_promotion)
        self.assertIn("workflow_dispatch:", self.prod_promotion)
        self.assertIn("environment: test", self.test_promotion)
        self.assertIn("environment: prod", self.prod_promotion)

    def test_recruiterreply_factory_contract_is_present(self):
        contract = Path(__file__).parents[1] / "contracts/applications/recruiterreply.yml"
        content = contract.read_text()
        for marker in (
            "application_repo: moojjoo/recruiterreply",
            "default_branch: main",
            "project_name: RecruiterReply MVP",
            "approval_label: dev-acceptance-verified",
            "dev_workflow: .github/workflows/build.yml",
            "test_workflow: .github/workflows/promote-test.yml",
            "prod_workflow: .github/workflows/promote-prod.yml",
        ):
            self.assertIn(marker, content)


if __name__ == "__main__":
    unittest.main()

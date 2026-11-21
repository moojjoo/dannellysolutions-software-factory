# Acceptance evidence and issue closure contract

This policy is reusable across Dannelly Solutions projects. Applications own deployment and issue reconciliation; the factory provides guardrails and templates.

1. Partial PRs link issues with `Refs #123`; do not use `Closes`, `Fixes`, `Resolves`, or `Dev-Completes` until final completion.
2. Final implementation PRs use `Dev-Completes: #123` only after all acceptance criteria are verified. Record build, test, CodeQL, security and smoke-test evidence tied to immutable commit SHAs.
3. Verified Dev deployment and smoke evidence may close eligible issues automatically; a manual acceptance label is not required for routine Dev completion.
4. `dev-acceptance-verified` remains an optional controlled owner-approval label for product acceptance and must trigger a retry for an already verified deployment when added later.
5. The application reconciler must fail closed on missing credentials, project membership, SHA evidence, or missing release verification.
6. A read-only scheduled audit reports merged final PRs whose issues remain open, with actionable blockers. Reports do not change issues or labels.
7. Dev automation is permitted only after protections pass. Test and Production require explicit approvals and SHA promotion.
8. Least-privilege: reporting uses contents:read, pull-requests:read, issues:read and actions:read; closure uses separately controlled permissions.

## RecruiterReply integration
- PR template: `moojjoo/recruiterreply/.github/PULL_REQUEST_TEMPLATE.md`
- Read-only audit: `moojjoo/recruiterreply/.github/workflows/issue-reconciliation-audit.yml`
- Dev closure: `moojjoo/recruiterreply/.github/scripts/reconcile-dev-issues.cjs`

Factory changes must pass `scripts/validate_templates.py`; application workflows must pass their own CI and real release verification.

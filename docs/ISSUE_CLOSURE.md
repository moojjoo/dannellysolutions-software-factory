# Acceptance evidence and issue closure contract

This policy is reusable across Dannelly Solutions projects. Applications own deployment and issue reconciliation; the factory provides guardrails and templates.

1. Partial PRs link issues with `Refs #123`; do not use `Closes`, `Fixes`, `Resolves`, or `Dev-Completes` until final completion.
2. Final implementation PRs use `Dev-Completes: #123` only after all acceptance criteria are verified. Record build, test, CodeQL, security and smoke-test evidence tied to immutable commit SHAs.
3. Verified Dev deployment evidence is sufficient for routine issue reconciliation once all other
   fail-closed checks pass. `dev-acceptance-verified` is optional product acceptance: it is not a mandatory Dev gate,
   and applying it is a supported retry signal when a prior reconciliation
   attempt ran before the deployment evidence was available.
4. The application reconciler must fail closed on missing credentials, project membership, required
   environment approval, SHA evidence, or missing release verification.
5. A read-only scheduled audit reports merged final PRs whose issues remain open, with actionable blockers. Reports do not change issues or labels.
6. Dev automation is permitted only after protections pass. Test and Production require explicit
   owner approvals and promotion of the exact verified SHA; a Dev acceptance label cannot approve
   either environment.
7. Least-privilege: reporting uses contents:read, pull-requests:read, issues:read and actions:read; closure uses separately controlled permissions.

## RecruiterReply integration
- PR template: `moojjoo/recruiterreply/.github/PULL_REQUEST_TEMPLATE.md`
- Read-only audit: `moojjoo/recruiterreply/.github/workflows/issue-reconciliation-audit.yml`
- Dev closure: `moojjoo/recruiterreply/.github/scripts/reconcile-dev-issues.cjs`

Factory changes must pass `scripts/validate_templates.py`; application workflows must pass their own CI and real release verification.

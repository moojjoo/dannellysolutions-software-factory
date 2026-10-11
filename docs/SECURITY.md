# Security and operational guardrails

- Principle of least privilege: default `GITHUB_TOKEN` permissions `contents: read`. Elevate only on narrowly scoped workflows.
- Pin third-party GitHub Actions to audited full commit SHAs in production use; examples may use readable major versions and must be reviewed before adoption.
- Store secrets in GitHub Environments and AWS Secrets Manager. Prefer GitHub OIDC to long-lived AWS access keys.
- Configure branch rules and required checks; never auto-merge if checks fail or have not reported.
- Enable Dependabot, dependency review, CodeQL, and secret scanning where available.
- Playwright checks must cover theme changes, auth boundaries, and critical purchase/consent flows as appropriate to each app.
- Do not automatically approve destructive migrations, schema/data deletion, privileged IAM changes, or production deployment.
- Record the exact deployed SHA and artifact digest for Dev, Test, and Prod; rollback to previously verified immutable artifacts.
- Keep cloud costs unchanged unless the owner approves an estimate.

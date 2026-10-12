# Release safety upgrade (Issue #5)

These are **reusable building blocks**, not deployed infrastructure. Each application
must integrate them with its existing workflows and test the integration in Dev.

## Baseline checks
- `scripts/preflight.sh`: AWS account/region, Secrets Manager secret metadata, Docker daemon and existing volumes. Configure AWS_ACCOUNT_ID, AWS_REGION, REQUIRED_SECRET_IDS and REQUIRED_DOCKER_VOLUMES. Never log secret values.
- `scripts/smoke_test.sh`: retries a configured SMOKE_URL; add application-specific authenticated flows and database readiness.
- `scripts/terraform_drift.sh`: `terraform plan -refresh-only -detailed-exitcode`; 0 clean, 2 drift, 1 error. Configure a secure locked remote backend; do not auto-apply.
- `scripts/release_safety.py risk <paths...>`: 0 only for documentation-only changes; 2 for unknown or high-risk changes. **This does not enable auto-merge.** Require successful checks and branch protection, and configure merge automation separately.
- `scripts/release_safety.py promotion --manifest FILE --target test|production --sha SHA --digest sha256:...`: checks trusted source provenance. The manifest must be produced by a trusted deployment workflow and protected from PR modification.

## Mandatory adoption gates
1. Inventory current app AWS resources, SSM access, IAM permissions, mounts, container UID, secrets, Terraform backend and existing deploy workflows.
2. Add checks for actual mount destination, write permission and preservation of Data Protection keys across container recreation; do not modify existing volumes in a preflight.
3. Store signed/immutable deployment manifests with source SHA, image digest, workflow run, environment, timestamp, smoke result and approval audit evidence. Never trust a manifest supplied by a PR.
4. Enforce GitHub Environment required reviewers for Test and Production. Require separate human approval for each promotion. A passing manifest check **cannot substitute** for approval.
5. Promote the exact image digest; do not rebuild in Test or Production. Reject concurrent or stale promotions.
6. Run failure-injection tests and rollback drills in Dev before adopting higher-environment workflows.
7. Risk policy is conservative: only docs-only PRs can be considered for auto-merge; workflow, IAM, secrets, Terraform, Docker, DB and unknown changes require manual review.

No automatic infrastructure changes, no secret disclosure, no destructive Docker operations, and no Test/Production deployments are performed by these scripts.

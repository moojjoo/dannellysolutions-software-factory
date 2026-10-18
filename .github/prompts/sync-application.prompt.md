---
name: sync-application
description: Reconcile an application repository with the Dannelly Solutions Software Factory contract
---

Use the application contract supplied by the target repository and the canonical schema at
`contracts/application-contract.schema.json`.

Configuration fields are intentionally repository-specific. Never infer names from the
application's directory, Git remote, or branch. Resolve these fields from the contract:

- `factory_repo`
- `application_repo`
- `application_name`
- `default_branch`
- `project_name`
- `environments`
- `approval_label`
- `partial_marker`
- `final_marker`
- `dev_workflow`
- `test_workflow`
- `prod_workflow`
- `implementation_overrides`

Tasks:

1. Read the Factory policy, schema, templates, and validation scripts.
2. Read the application repository's agent instructions, architecture, workflows, tests,
   deployment documentation, and local contract.
3. Validate the application contract against the Factory schema.
4. Compare the two repositories and report missing policy, naming mismatches, missing
   evidence, unsafe permissions, and environment-gate differences.
5. Treat the Factory as the source of reusable policy. Treat the application contract as
   the source of names, paths, environments, and implementation-specific behavior.
6. Preserve application-specific deployment, secret, IAM, database, and test mechanisms.
7. Do not modify workflows, deployment settings, environments, IAM, secrets, or databases
   without an issue-linked change and explicit approval.
8. Produce a machine-readable reconciliation report containing repository, file, contract
   field, current value, expected value, status, required test, and approval requirement.
9. Implement only approved changes, then run the Factory validator and the application's
   required tests.
10. Never add auto-close keywords or a final completion marker to a partial change.

The final response must distinguish `pass`, `drift`, `blocked`, and `not-applicable`, and
must include exact commit, workflow, and deployment evidence where available.

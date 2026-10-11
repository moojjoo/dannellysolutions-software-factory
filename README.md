# Dannelly Solutions Software Factory

Reusable GitHub delivery standards, policy checks, and templates for Dannelly Solutions applications.

## Command contract

| Command | Result | Approval |
| --- | --- | --- |
| `/feature <description>` | Plan and create a scoped GitHub issue assigned to the owner | Issue creation |
| `/execute <issue>` | Implement, open a **ready-for-review** PR, validate, automatically merge **only after all required checks pass**, then deploy Dev | The command authorizes Dev only |
| `/execute test` | Promote the **exact verified Dev commit SHA** to Test | Explicit command required |
| `/execute prod` | Promote the **same verified Test commit SHA** to Production | Explicit command required |

## Contents

- [Workflow and adoption guide](docs/WORKFLOW.md)
- [Security and release guardrails](docs/SECURITY.md)
- [GitHub settings checklist](docs/REPOSITORY_SETUP.md)
- [Reusable PR verification workflow](templates/verify.yml)
- [Reusable SHA-pinned promotion workflow](templates/promote.yml)
- [GitHub Actions template validator](scripts/validate_templates.py)

## Principles

1. Each application owns its AWS infrastructure, secrets, and deployment commands.
2. Required build, Playwright, and CodeQL checks must pass before merge. Do not bypass branch protection.
3. Never auto-promote Test or Production. Verify environment SHA provenance.
4. No credentials, tokens, customer data, or private keys in Git.
5. A ChatGPT instruction alone cannot trigger future unattended merges. Configure repository auto-merge, branch protection, and required GitHub Actions checks separately.

This repository is the **factory**, not a deployment target for RecruiterReply or DannellySolutions.com. Templates require adaptation to each application's build and release workflows.

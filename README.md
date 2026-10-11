# Dannelly Solutions Software Factory

**Reusable engineering workflow standards and GitHub automation templates for Dannelly Solutions Inc.**

This repository provides a common foundation for planning features, implementing changes through GitHub pull requests, validating code, and promoting a single verified commit across environments. It is **not** a running CI/CD orchestration service and does **not** deploy applications by itself.

## How the factory works

```text
Idea → /feature → GitHub Issue
                   ↓
              /execute <issue>
                   ↓
         Feature branch + PR
                   ↓
          Required CI checks
                   ↓
      Merge to main (only if green)
                   ↓
              Deploy to Dev
                   ↓
         Owner: /execute test
                   ↓
        Promote same SHA to Test
                   ↓
         Owner: /execute prod
                   ↓
     Promote verified SHA to Prod
```

The **application repository** owns its actual build, tests, secrets, deployments, and promotion workflows. This factory supplies shared policy and starter templates.

## Command reference

| Command | Expected behavior | Approval boundary |
| --- | --- | --- |
| `/feature <description>` | Inspect relevant code, define acceptance criteria, create a GitHub issue, assign owner | Planning only; no deployment |
| `/execute <issue-number>` | Implement on issue-linked branch, open a non-draft PR, validate, merge when required checks pass, deploy to Dev using existing app workflow | Explicit authorization for Dev only |
| `/execute test` | Promote the **exact SHA** verified on Dev | Requires separate owner instruction |
| `/execute prod` | Promote the **same SHA** verified on Test | Requires separate owner instruction |

**Important:** These slash commands are conversational conventions used with the development assistant. They are **not** shell commands or executable GitHub CLI commands supplied by this repository. Fully unattended merging requires GitHub settings and automation to be configured in the relevant application repository.

## Repository contents

| Path | Purpose |
| --- | --- |
| [`docs/WORKFLOW.md`](docs/WORKFLOW.md) | Detailed planning, implementation, CI and promotion process |
| [`docs/SECURITY.md`](docs/SECURITY.md) | Least privilege, secret handling, scanning and deployment guardrails |
| [`docs/REPOSITORY_SETUP.md`](docs/REPOSITORY_SETUP.md) | Checklist for repository rules, auto-merge and environments |
| [`templates/verify.yml`](templates/verify.yml) | Example PR verification workflow; replace placeholder build/test steps |
| [`templates/promote.yml`](templates/promote.yml) | Example manual SHA input validation; intentionally **does not deploy** |
| [`scripts/validate_templates.py`](scripts/validate_templates.py) | Dependency-free structural validator |
| [`.github/workflows/validate.yml`](.github/workflows/validate.yml) | GitHub Actions workflow validating factory templates |

## Quick start

### 1. Clone and validate this repository

```bash
git clone https://github.com/moojjoo/dannellysolutions-software-factory.git
cd dannellysolutions-software-factory
python3 scripts/validate_templates.py
```

### 2. Configure an application repository

Use [the setup checklist](docs/REPOSITORY_SETUP.md) to:

1. Enable **Allow auto-merge** in GitHub repository settings.
2. Protect `main` with required PR status checks; ensure actual build, Playwright and CodeQL checks run and pass. Never bypass failing checks.
3. Keep PRs **ready for review**, rather than drafts, when using automatic merging.
4. Configure Dev deployment on verified merges to `main`.
5. Configure protected Test and Production environments with separate owner approvals and immutable SHA/artifact verification.
6. Store credentials in GitHub Environments or AWS Secrets Manager; never commit them.

### 3. Adapt templates rather than deploying them unchanged

Copy only the relevant templates into the application's `.github/workflows/` directory. Replace all placeholder verification steps with real application commands. The promotion template **validates SHA syntax only**: it does not prove deployment provenance or promote artifacts. Implement those checks in the application before enabling release jobs.

### 4. Exercise the workflow

Create a harmless feature PR. Confirm that a failing required check prevents merging, a passing PR merges and deploys to Dev, and Test/Production remain unchanged until their explicit promotion commands.

## Current implementation status

| Capability | Status |
| --- | --- |
| Factory repository and documentation | Implemented |
| Factory template validation workflow | Implemented; initial PR validation passed |
| Reusable verification and promotion examples | Present, **not production-ready without adaptation** |
| Automatic merging of application PRs | **Not verified**; must configure and test per repository |
| Branch protection and required status checks | **Not verified** |
| Dev deployment integration for RecruiterReply | **Not implemented by this repository** |
| Test/Production immutable artifact promotion | **Not implemented by this repository** |
| AWS deployment and secret provisioning | Not included; owned by each application |

## Applications

- [RecruiterReply](https://github.com/moojjoo/recruiterreply) — AI-assisted recruiter communication application.
- [Dannelly Solutions website](https://github.com/moojjoo/dannellysolutions) — Company website.

Each application is independently deployable. The factory must never introduce cross-application credentials or shared production deployment permissions.

## Security and release policy

- Require passing CI and security checks; no bypasses or force-merges.
- Use least-privilege GitHub tokens and scoped cloud identities.
- Never commit secrets, API keys, private customer data, or production credentials.
- Keep Test and Production promotions owner-controlled.
- Use immutable commit SHAs and verify artifact provenance before promotion.
- Require separate review for destructive database migrations, IAM privilege increases and unexpected cloud costs.

## Next milestones

1. Verify repository auto-merge and enforce required CI checks/rulesets.
2. Run a harmless end-to-end PR to demonstrate blocked failures and automatic green merges.
3. Add an **application-specific** RecruiterReply integration using its existing workflows, without altering working deployments unexpectedly.
4. Implement and test verified SHA/artifact promotion gates for Test and Production.

## Ownership

Maintained by **Dannelly Solutions Inc.** for its software projects. For changes, open a GitHub issue with acceptance criteria and submit a CI-validated pull request.

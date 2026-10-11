# Solo-developer delivery workflow

## Plan: `/feature <description>`

Inspect the application repository, identify existing related issues, create an issue with scope, acceptance criteria, security/privacy, tests, and cost impact. Assign to `moojjoo`; add to the appropriate GitHub Project when supported. Do not modify source until `/execute`.

## Implement: `/execute <issue>`

1. Read `AGENTS.md`, current architecture, existing workflows, and issue requirements.
2. Create `feature/<issue>-<slug>` from the latest `main`.
3. Make focused changes and add tests. Never commit secrets.
4. Open a **non-draft** PR linked to the issue. No mandatory Copilot reviewer for a solo-developer account.
5. Run all required build, unit, Playwright, CodeQL, and secret checks. Repair failures on the branch; never bypass a red check.
6. Enable GitHub auto-merge where supported; the GitHub platform merges only when required checks and branch rules pass. If not supported, leave the PR open and report the blocker.
7. After merge, verify the app's existing `main` workflow deployed **Dev**, and record its immutable commit SHA. Never claim deployment merely because a PR exists.

## Promote: `/execute test` and `/execute prod`

Promote the **same immutable commit SHA** verified in Dev. Explicit owner commands authorize each environment separately. Use protected GitHub Environments, artifact digest verification, and workflow permissions. Production must use the SHA that passed Test; never rebuild from an unverified moving branch. Failed deployment must not advance the release pointer.

## Exceptions

Security-sensitive changes, destructive database migrations, IAM expansions, or unexpected costs require separate review. A factory template is not a substitute for a real application's verified deployment process.

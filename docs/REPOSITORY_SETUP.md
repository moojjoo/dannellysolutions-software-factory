# GitHub repository setup checklist

These are **manual administrator settings** for each application repository; adding templates does not turn them on automatically.

1. Settings → General → Pull Requests: enable **Allow auto-merge** and your chosen merge method (prefer squash).
2. Settings → Rules → Rulesets (or Branch protection): protect `main`, require PRs and all relevant status checks. Require up-to-date checks when appropriate. Do **not** require another human review for a one-person team unless intentionally desired.
3. Ensure `verify`, Playwright, and CodeQL checks actually run on pull requests; add their exact reported check names to required checks.
4. GitHub Actions: allow necessary actions and least-privilege token permissions. Do not grant broad write permissions to untrusted PR code.
5. Environments: create `dev`, `test`, `production`. Configure manual approvals for Test and Production, with restricted deployment branches as appropriate.
6. Verify application workflows: PR → verify only; merged `main` SHA → Dev; manually selected **SHA** → Test; same SHA → Production.
7. Confirm GitHub plan supports your desired ruleset and environment protection features, especially on public vs private repositories.
8. Test with a harmless PR: failing check must block merge; passing checks must merge and deploy Dev; Test/Prod must remain unchanged.

**Important:** ChatGPT cannot by itself enable background auto-merge or repository settings. A GitHub App or authorized `gh`/API workflow must perform those actions.

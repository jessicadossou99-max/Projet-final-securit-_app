# Security automation

`security-gates` is the security pipeline. It is executed on pull requests and pushes to `main`.

- **SAST:** Bandit scans the deployable Django code in `config/` and `incidents/`.
- **Dependency audit:** pip-audit checks the resolved production requirements.
- **Secret scan:** Gitleaks checks repository history and the submitted change.
- **Dynamic hardening:** the isolated SQLite training test replays SQL-shaped payloads and checks that an owner cannot read another user's data. It is a local-only lab and is never routed or deployed by the normal application.
- **DAST baseline:** ZAP scans only a disposable file-backed SQLite app launched inside the GitHub runner. It never receives a Vercel, Neon, or production URL. The authenticated SQL injection behavior is covered by the separate dynamic hardening tests; the baseline scan is intentionally not represented as authenticated coverage.

The baseline ZAP report is an artifact, not proof that the application is secure. Before release, review the report, the CI result, and the access-control tests. Configure branch protection in GitHub to require passing `starter-tests` and `security-gates` checks before merging to `main` when the plan permits it.

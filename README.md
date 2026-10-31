# pr-checks-demo

A small, working example of an industry-standard pull request pipeline for a
Python service with Docker, Terraform (AWS), and Kubernetes manifests.

## Layout

```
.github/
  workflows/pr-checks.yml     # all PR gates (see table below)
  CODEOWNERS                  # review routing by path
  pull_request_template.md    # author checklist
src/app/main.py               # FastAPI service (/healthz, /items)
tests/test_main.py            # pytest suite
Dockerfile                    # non-root, slim image
terraform/                    # ECR repo (KMS-encrypted, immutable tags, scan on push)
k8s/                          # Deployment + Service (hardened security context)
pyproject.toml                # ruff, mypy (strict), pytest config
```

## What each job checks

| Job | Tool | Fails the PR when |
|---|---|---|
| `pr-title` | action-semantic-pull-request | Title isn't Conventional Commits |
| `lint-test` | ruff, mypy, pytest-cov | Lint/format/type errors, tests fail, coverage < 80% |
| `secrets-scan` | gitleaks | A secret is found in the diff or history |
| `sast` | CodeQL | Code scanning finds issues |
| `dependency-review` | dependency-review-action | New dependency has a high CVE or a denied license |
| `iac-scan` | terraform fmt/validate, TFLint, Checkov | IaC or manifest misconfigurations |
| `terraform-plan` | terraform plan | Plan errors (output is posted to the PR) |
| `container-scan` | Docker build + Trivy | CRITICAL/HIGH fixable CVEs in the image |
| `k8s-manifests` | kubeconform | Invalid Kubernetes manifests |
| `all-checks` | aggregate | Any of the above failed. **This is the one required status check.** |

## Run the checks locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

ruff check . && ruff format --check .
mypy src/
pytest --cov=src --cov-fail-under=80

# Optional, if installed
terraform -chdir=terraform fmt -check -recursive
docker build -t pr-checks-demo .
trivy image --severity CRITICAL,HIGH --ignore-unfixed pr-checks-demo
```

## Try it on GitHub

1. Create a repo and push this code to `main`.
2. Replace `@your-org/...` teams in `.github/CODEOWNERS`.
3. Settings > Rules (or Branches) > protect `main`:
   - Require a pull request with 1+ approval and review from Code Owners
   - Dismiss stale approvals on new commits
   - Require status check: **All checks passed**
   - Require branches to be up to date; block force pushes
4. Settings > Code security: enable Dependabot alerts, dependency graph, and code scanning.
5. Optional (for `terraform-plan`): create a read-only AWS OIDC role and set the repo variable
   `AWS_PLAN_ROLE_ARN`. Otherwise delete that job.
6. Open a PR with a title like `feat: add item endpoint` and watch the checks run.

## Break it on purpose (to see the gates work)

| Change | Expected failure |
|---|---|
| PR titled `updated stuff` | `pr-title` |
| Add `x = 1` unused import or bad formatting | `lint-test` (ruff) |
| Remove a test so coverage drops under 80% | `lint-test` (coverage) |
| Commit `AWS_SECRET_ACCESS_KEY=...` in a file | `secrets-scan` |
| Remove `readOnlyRootFilesystem` / add `privileged: true` in k8s | `iac-scan` (Checkov) |
| Add `runAsUser: 0` or `USER root` in Dockerfile | `iac-scan` (Checkov) |
| Set `image_tag_mutability = "MUTABLE"` in Terraform | `iac-scan` (Checkov) |
| Pin an old vulnerable package in `requirements.txt` | `dependency-review` / `container-scan` |

## Notes

- Third-party actions are pinned to major tags for readability. In production, pin to commit SHAs.
- The image reference in `k8s/deployment.yaml` uses a placeholder AWS account ID.

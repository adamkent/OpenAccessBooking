# GitHub Actions Workflows

## Overview

Automated CI/CD pipelines for testing and deployment.

## Workflows

### 1. `tests.yml` - Continuous Integration

**Triggers:**
- Push to `main` or `develop`
- Pull requests to `main` or `develop`

**Jobs:**
- `backend-tests` - Run pytest
- `frontend-tests` - Run Jest with coverage

**Duration:** ~2-3 minutes

### 2. `deploy.yml` - Continuous Deployment

**Triggers:**
- Push to `main` branch
- Manual trigger (workflow_dispatch)

**Jobs:**
1. `deploy-backend` - Build and deploy Lambda functions
2. `deploy-frontend` - Build React app and deploy to S3

**Duration:** ~5-8 minutes

## Setup

### Required Secrets

Add these in GitHub → Settings → Secrets and variables → Actions:

```
AWS_ACCESS_KEY_ID          # AWS credentials
AWS_SECRET_ACCESS_KEY      # AWS credentials
S3_BUCKET_NAME            # Frontend bucket
CLOUDFRONT_DISTRIBUTION_ID # CloudFront ID
REACT_APP_API_URL         # Backend API URL
```

### Optional: Branch Protection

Recommended settings for `main` branch:
- ✅ Require status checks to pass
- ✅ Require branches to be up to date
- ✅ Require pull request reviews
- ✅ Include administrators

## Usage

### Automatic Deployment

```bash
# Commit and push to main
git add .
git commit -m "New feature"
git push origin main

# Watch deployment
# https://github.com/YOUR_USERNAME/OpenAccessBooking/actions
```

### Manual Deployment

1. Go to Actions tab
2. Select "Deploy to AWS"
3. Click "Run workflow"
4. Select branch
5. Click "Run workflow"

### View Logs

```bash
# In GitHub Actions UI
Actions → Select workflow run → Select job → View logs
```

## Workflow Status Badges

Add to README.md:

```markdown
![Tests](https://github.com/YOUR_USERNAME/OpenAccessBooking/workflows/Tests/badge.svg)
![Deploy](https://github.com/YOUR_USERNAME/OpenAccessBooking/workflows/Deploy%20to%20AWS/badge.svg)
```

## Troubleshooting

### Tests Failing

```bash
# Run locally first
cd backend && pytest -v
cd frontend && npm test
```

### Deployment Failing

1. Check AWS credentials are valid
2. Verify all secrets are set
3. Check AWS service limits
4. Review CloudFormation stack events

### Slow Workflows

- Use caching for dependencies
- Run jobs in parallel where possible
- Optimize test suites

## Customization

### Add New Environment

```yaml
# In deploy.yml
deploy-staging:
  if: github.ref == 'refs/heads/develop'
  # ... deployment steps
```

### Add Notifications

```yaml
# Add to end of workflow
- name: Notify Slack
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Add Code Quality Checks

```yaml
# Add to tests.yml
- name: Lint
  run: |
    cd backend
    flake8 src/
```

## Best Practices

1. ✅ Keep workflows simple
2. ✅ Use caching for dependencies
3. ✅ Fail fast on errors
4. ✅ Use secrets for sensitive data
5. ✅ Add status checks to PRs
6. ✅ Monitor workflow usage/costs

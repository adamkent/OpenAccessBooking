# CI/CD Setup Summary

## What's Been Created

### 1. GitHub Actions Workflows

**`.github/workflows/tests.yml`**
- Runs on every push/PR
- Backend: pytest
- Frontend: Jest with coverage
- ~2-3 minutes

**`.github/workflows/deploy.yml`**
- Runs on push to main
- Deploys backend (SAM)
- Deploys frontend (S3 + CloudFront)
- ~5-8 minutes

### 2. Infrastructure as Code

**`terraform/main.tf`**
- S3 bucket for frontend
- CloudFront distribution
- DynamoDB tables (appointments, patients, practices)
- Cognito User Pool
- All with proper configuration

### 3. Deployment Scripts

**`deploy-setup.sh`**
- Interactive setup wizard
- Creates Terraform state bucket
- Deploys infrastructure
- Deploys backend and frontend
- Saves outputs for GitHub Secrets

## Quick Start

### Option 1: Automated (Recommended)

1. **Set up infrastructure once:**
   ```bash
   ./deploy-setup.sh
   ```

2. **Add GitHub Secrets:**
   - Go to: Settings → Secrets and variables → Actions
   - Add the values from deploy-setup.sh output

3. **Push to deploy:**
   ```bash
   git push origin main
   ```

### Option 2: Manual

1. **Deploy infrastructure:**
   ```bash
   cd terraform
   terraform init
   terraform apply
   ```

2. **Deploy backend:**
   ```bash
   cd backend
   sam build
   sam deploy --guided
   ```

3. **Deploy frontend:**
   ```bash
   cd frontend
   npm run build
   aws s3 sync build/ s3://your-bucket --delete
   ```

## GitHub Secrets Required

```
AWS_ACCESS_KEY_ID          # From AWS IAM
AWS_SECRET_ACCESS_KEY      # From AWS IAM
S3_BUCKET_NAME            # From Terraform output
CLOUDFRONT_DISTRIBUTION_ID # From Terraform output
REACT_APP_API_URL         # From SAM output
```

## Workflow

```
Developer pushes code
        ↓
GitHub Actions triggered
        ↓
    Run tests
        ↓
   Tests pass? ──No──→ Fail & notify
        ↓ Yes
  Deploy backend
        ↓
  Deploy frontend
        ↓
Invalidate CloudFront
        ↓
    Success! 🎉
```

## Key Features

✅ **Automated testing** - Every push runs tests
✅ **Automated deployment** - Push to main = auto-deploy
✅ **Infrastructure as Code** - Terraform manages AWS resources
✅ **Simple & maintainable** - No complex pipelines
✅ **Cost-effective** - Pay only for what you use (~£15-50/month)
✅ **Scalable** - Serverless architecture

## Files Created

```
.github/workflows/
├── tests.yml           # CI pipeline
├── deploy.yml          # CD pipeline
└── README.md          # Workflow docs

terraform/
├── main.tf            # Infrastructure definition
└── README.md          # Terraform guide

deploy-setup.sh        # Interactive setup script
DEPLOYMENT.md          # Full deployment guide
CI-CD-SETUP.md         # This file
```

## Testing the Pipeline

1. **Make a change:**
   ```bash
   echo "test" >> README.md
   ```

2. **Commit and push:**
   ```bash
   git add .
   git commit -m "Test CI/CD"
   git push origin main
   ```

3. **Watch it deploy:**
   - Go to: https://github.com/YOUR_USERNAME/OpenAccessBooking/actions
   - See tests run
   - See deployment happen
   - Check AWS console for changes

## Monitoring

- **GitHub Actions**: View workflow runs
- **AWS CloudWatch**: Backend logs
- **AWS CloudFront**: CDN metrics
- **AWS DynamoDB**: Table metrics

## Rollback

```bash
# Backend
cd backend
sam deploy --parameter-overrides Version=previous

# Frontend
aws s3 sync s3://backup-bucket/ s3://frontend-bucket/
aws cloudfront create-invalidation --distribution-id ID --paths "/*"
```

## Cost Optimisation

- CloudFront caching reduces S3 requests
- DynamoDB on-demand pricing
- Lambda free tier (1M requests/month)
- S3 lifecycle policies for old data

## Security

✅ Secrets stored in GitHub Secrets
✅ IAM roles with least privilege
✅ HTTPS only via CloudFront
✅ DynamoDB encryption at rest
✅ Cognito for authentication

## Next Steps

- [ ] Set up staging environment
- [ ] Add performance monitoring
- [ ] Configure custom domain
- [ ] Set up SSL certificate
- [ ] Enable automated backups
- [ ] Add error tracking (Sentry)
- [ ] Set up billing alerts

## Support

- **Terraform docs**: https://registry.terraform.io/providers/hashicorp/aws
- **AWS SAM docs**: https://docs.aws.amazon.com/serverless-application-model/
- **GitHub Actions docs**: https://docs.github.com/en/actions

## Troubleshooting

**Tests failing?**
```bash
cd backend && pytest -v
cd frontend && npm test
```

**Deployment failing?**
- Check GitHub Secrets are set
- Verify AWS credentials
- Check CloudFormation events in AWS Console

**CloudFront not updating?**
```bash
aws cloudfront create-invalidation --distribution-id ID --paths "/*"
```

---

**Simple, automated, production-ready CI/CD! 🚀**

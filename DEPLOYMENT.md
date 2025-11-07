# Deployment Guide

## Overview

This project uses a simple CI/CD pipeline with GitHub Actions for automated testing and deployment.

## Architecture

```
┌─────────────────┐
│  GitHub Repo    │
└────────┬────────┘
         │
         ├─── Push to main ───┐
         │                    │
         ▼                    ▼
┌─────────────────┐  ┌─────────────────┐
│  Run Tests      │  │  Deploy to AWS  │
│  (GitHub Actions)│  │  (GitHub Actions)│
└─────────────────┘  └────────┬────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
            ┌──────────────┐    ┌──────────────┐
            │   Backend    │    │   Frontend   │
            │   (Lambda)   │    │ (S3+CloudFront)│
            └──────────────┘    └──────────────┘
```

## Prerequisites

### 1. AWS Account Setup

Create an IAM user with these permissions:
- AmazonS3FullAccess
- AWSLambdaFullAccess
- AmazonDynamoDBFullAccess
- AmazonCognitoPowerUser
- CloudFrontFullAccess
- IAMFullAccess (for SAM deployment)

### 2. GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

```
AWS_ACCESS_KEY_ID          # Your AWS access key
AWS_SECRET_ACCESS_KEY      # Your AWS secret key
S3_BUCKET_NAME            # Frontend S3 bucket name
CLOUDFRONT_DISTRIBUTION_ID # CloudFront distribution ID
REACT_APP_API_URL         # Backend API URL
```

## Deployment Steps

### Option 1: Automated (Recommended)

**Push to main branch triggers automatic deployment:**

```bash
git add .
git commit -m "Deploy to production"
git push origin main
```

GitHub Actions will:
1. ✅ Run backend tests
2. ✅ Run frontend tests
3. ✅ Deploy backend (SAM)
4. ✅ Deploy frontend (S3)
5. ✅ Invalidate CloudFront cache

### Option 2: Manual Deployment

#### Deploy Infrastructure (One-time)

```bash
cd terraform
terraform init
terraform apply
```

Note the outputs for later use.

#### Deploy Backend

```bash
cd backend
sam build
sam deploy --guided
```

First time, answer the prompts:
- Stack Name: `nhs-appointments-backend`
- AWS Region: `eu-west-2`
- Confirm changes: `Y`
- Allow SAM CLI IAM role creation: `Y`
- Save arguments to config: `Y`

#### Deploy Frontend

```bash
cd frontend

# Build
npm run build

# Deploy to S3
aws s3 sync build/ s3://your-bucket-name --delete

# Invalidate CloudFront
aws cloudfront create-invalidation \
  --distribution-id YOUR_DIST_ID \
  --paths "/*"
```

## CI/CD Pipeline

### Workflow Files

**`.github/workflows/tests.yml`** - Runs on every push/PR
- Backend: pytest
- Frontend: Jest

**`.github/workflows/deploy.yml`** - Runs on push to main
- Tests → Backend deploy → Frontend deploy

### Pipeline Stages

```
┌──────────────┐
│  Code Push   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Run Tests   │  ← Fails if tests don't pass
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Build Backend│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│Deploy Backend│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│Build Frontend│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│Deploy Frontend│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Success!   │
└──────────────┘
```

## Monitoring Deployments

### GitHub Actions

View deployment status:
```
https://github.com/YOUR_USERNAME/OpenAccessBooking/actions
```

### AWS Console

- **Lambda**: Check function logs in CloudWatch
- **S3**: Verify files uploaded
- **CloudFront**: Check distribution status
- **DynamoDB**: Verify tables exist

### Logs

```bash
# Backend logs
sam logs -n AuthFunction --stack-name nhs-appointments-backend --tail

# Frontend (CloudFront)
# View in AWS Console → CloudFront → Monitoring
```

## Rollback

### Backend
```bash
cd backend
sam deploy --parameter-overrides Version=previous-version
```

### Frontend
```bash
# Restore previous S3 version
aws s3 sync s3://backup-bucket/ s3://frontend-bucket/
aws cloudfront create-invalidation --distribution-id ID --paths "/*"
```

## Environment Management

### Production
- Branch: `main`
- Auto-deploy: Yes
- Tests required: Yes

### Staging (Optional)
```bash
# Create staging branch
git checkout -b staging

# Deploy to staging
terraform workspace select staging
terraform apply -var="environment=staging"
```

## Troubleshooting

### Deployment Fails

1. **Check GitHub Actions logs**
   - Go to Actions tab
   - Click failed workflow
   - Review error messages

2. **Check AWS permissions**
   ```bash
   aws sts get-caller-identity
   ```

3. **Verify secrets are set**
   - GitHub → Settings → Secrets

### Tests Fail

```bash
# Run locally first
cd backend && pytest
cd frontend && npm test
```

### CloudFront Not Updating

```bash
# Force invalidation
aws cloudfront create-invalidation \
  --distribution-id YOUR_ID \
  --paths "/*"
```

## Cost Optimisation

- **Use CloudFront caching** - Reduces S3 requests
- **DynamoDB on-demand** - Pay only for what you use
- **Lambda reserved concurrency** - Prevent runaway costs
- **Set up billing alerts** - Get notified at £10, £50, £100

## Security Best Practices

1. ✅ Never commit secrets to git
2. ✅ Use IAM roles with least privilege
3. ✅ Enable CloudFront HTTPS only
4. ✅ Enable DynamoDB encryption
5. ✅ Use Cognito for authentication
6. ✅ Enable CloudWatch logging
7. ✅ Regular security updates

## Next Steps

- [ ] Set up staging environment
- [ ] Add performance monitoring
- [ ] Configure custom domain
- [ ] Set up SSL certificate
- [ ] Enable automated backups
- [ ] Add error tracking (Sentry)

# Infrastructure as Code (Terraform)

## Overview

This directory contains Terraform configuration for deploying the NHS Appointments infrastructure to AWS.

## Prerequisites

1. **Install Terraform**
   ```bash
   # Ubuntu/WSL
   wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
   echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
   sudo apt update && sudo apt install terraform
   ```

2. **Configure AWS CLI**
   ```bash
   aws configure
   ```

3. **Create S3 bucket for Terraform state** (one-time)
   ```bash
   aws s3 mb s3://nhs-appointments-terraform-state --region eu-west-2
   aws s3api put-bucket-versioning --bucket nhs-appointments-terraform-state --versioning-configuration Status=Enabled
   ```

## Infrastructure Components

- **S3 + CloudFront** - Frontend hosting with CDN
- **DynamoDB** - NoSQL database tables (appointments, patients, practices)
- **Cognito** - User authentication and management
- **Lambda** - Serverless backend functions (deployed via SAM)
- **API Gateway** - REST API endpoints (deployed via SAM)

## Deployment

### 1. Initialize Terraform
```bash
cd terraform
terraform init
```

### 2. Plan Changes
```bash
terraform plan
```

### 3. Apply Infrastructure
```bash
terraform apply
```

### 4. Get Outputs
```bash
terraform output
```

## Environment Variables

After deployment, update your application with these values:

```bash
# From Terraform outputs
export USER_POOL_ID=$(terraform output -raw user_pool_id)
export USER_POOL_CLIENT_ID=$(terraform output -raw user_pool_client_id)
export CLOUDFRONT_DOMAIN=$(terraform output -raw cloudfront_domain)
export S3_BUCKET=$(terraform output -raw frontend_bucket)
```

## Destroy Infrastructure

**⚠️ Warning: This will delete all resources**

```bash
terraform destroy
```

## Cost Estimate

**Monthly costs (approximate):**
- DynamoDB (Pay per request): ~£5-20
- Lambda: ~£0-5 (1M requests free tier)
- S3: ~£1-5
- CloudFront: ~£5-20
- Cognito: Free (50,000 MAU)

**Total: ~£15-50/month** (depending on usage)

## State Management

Terraform state is stored in S3 with versioning enabled. Never commit `terraform.tfstate` to git.

## Multi-Environment Setup

To deploy multiple environments:

```bash
# Production
terraform workspace new production
terraform apply -var="environment=production"

# Staging
terraform workspace new staging
terraform apply -var="environment=staging"
```

## Troubleshooting

### State Lock Issues
```bash
# Force unlock if needed
terraform force-unlock <LOCK_ID>
```

### Import Existing Resources
```bash
terraform import aws_s3_bucket.frontend existing-bucket-name
```

### Refresh State
```bash
terraform refresh
```

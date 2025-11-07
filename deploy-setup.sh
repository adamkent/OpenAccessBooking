#!/bin/bash

# NHS Appointments - Deployment Setup Script
# This script helps you set up the deployment pipeline

set -e

echo "🚀 NHS Appointments - Deployment Setup"
echo "======================================"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Install it first:"
    echo "   curl 'https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip' -o 'awscliv2.zip'"
    echo "   unzip awscliv2.zip"
    echo "   sudo ./aws/install"
    exit 1
fi

if ! command -v terraform &> /dev/null; then
    echo "⚠️  Terraform not found. Install it for infrastructure management:"
    echo "   https://developer.hashicorp.com/terraform/install"
fi

if ! command -v sam &> /dev/null; then
    echo "⚠️  AWS SAM CLI not found. Install it for Lambda deployment:"
    echo "   pip install aws-sam-cli"
fi

echo "✅ Prerequisites check complete"
echo ""

# AWS Configuration
echo "🔧 AWS Configuration"
echo "-------------------"
echo "Make sure you have configured AWS CLI:"
echo "  aws configure"
echo ""
read -p "Have you configured AWS CLI? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please run 'aws configure' first"
    exit 1
fi

# Test AWS credentials
echo "Testing AWS credentials..."
if aws sts get-caller-identity &> /dev/null; then
    echo "✅ AWS credentials valid"
    aws sts get-caller-identity
else
    echo "❌ AWS credentials invalid"
    exit 1
fi
echo ""

# Terraform State Bucket
echo "📦 Terraform State Bucket"
echo "------------------------"
BUCKET_NAME="nhs-appointments-terraform-state"
echo "Creating S3 bucket for Terraform state: $BUCKET_NAME"

if aws s3 ls "s3://$BUCKET_NAME" 2>&1 | grep -q 'NoSuchBucket'; then
    aws s3 mb "s3://$BUCKET_NAME" --region eu-west-2
    aws s3api put-bucket-versioning --bucket "$BUCKET_NAME" --versioning-configuration Status=Enabled
    echo "✅ Terraform state bucket created"
else
    echo "✅ Terraform state bucket already exists"
fi
echo ""

# Deploy Infrastructure
echo "🏗️  Infrastructure Deployment"
echo "----------------------------"
read -p "Deploy infrastructure with Terraform? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd terraform
    terraform init
    terraform plan
    read -p "Apply this plan? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        terraform apply
        echo "✅ Infrastructure deployed"
        
        # Save outputs
        echo ""
        echo "📝 Saving outputs..."
        terraform output -json > ../terraform-outputs.json
        
        USER_POOL_ID=$(terraform output -raw user_pool_id)
        USER_POOL_CLIENT_ID=$(terraform output -raw user_pool_client_id)
        S3_BUCKET=$(terraform output -raw frontend_bucket)
        CLOUDFRONT_ID=$(terraform output -raw cloudfront_distribution_id)
        CLOUDFRONT_DOMAIN=$(terraform output -raw cloudfront_domain)
        
        echo ""
        echo "🎉 Infrastructure deployed successfully!"
        echo ""
        echo "📋 Important values (save these):"
        echo "================================"
        echo "USER_POOL_ID=$USER_POOL_ID"
        echo "USER_POOL_CLIENT_ID=$USER_POOL_CLIENT_ID"
        echo "S3_BUCKET=$S3_BUCKET"
        echo "CLOUDFRONT_DISTRIBUTION_ID=$CLOUDFRONT_ID"
        echo "CLOUDFRONT_DOMAIN=$CLOUDFRONT_DOMAIN"
        echo ""
        echo "Add these to your GitHub Secrets:"
        echo "1. Go to: https://github.com/YOUR_USERNAME/OpenAccessBooking/settings/secrets/actions"
        echo "2. Add each secret above"
        echo ""
    fi
    cd ..
fi

# Backend Deployment
echo ""
echo "🔧 Backend Deployment"
echo "--------------------"
read -p "Deploy backend with SAM? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd backend
    sam build
    sam deploy --guided
    echo "✅ Backend deployed"
    cd ..
fi

# Frontend Deployment
echo ""
echo "🎨 Frontend Deployment"
echo "---------------------"
read -p "Deploy frontend to S3? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd frontend
    
    # Get API URL
    if [ -f ../terraform-outputs.json ]; then
        echo "Using Terraform outputs for API URL"
        # You'll need to add API Gateway URL to Terraform outputs
        read -p "Enter your API Gateway URL: " API_URL
    else
        read -p "Enter your API Gateway URL: " API_URL
    fi
    
    # Build
    echo "Building frontend..."
    REACT_APP_API_URL=$API_URL npm run build
    
    # Deploy
    if [ -f ../terraform-outputs.json ]; then
        S3_BUCKET=$(jq -r '.frontend_bucket.value' ../terraform-outputs.json)
        CLOUDFRONT_ID=$(jq -r '.cloudfront_distribution_id.value' ../terraform-outputs.json)
    else
        read -p "Enter S3 bucket name: " S3_BUCKET
        read -p "Enter CloudFront distribution ID: " CLOUDFRONT_ID
    fi
    
    echo "Deploying to S3..."
    aws s3 sync build/ "s3://$S3_BUCKET" --delete
    
    echo "Invalidating CloudFront cache..."
    aws cloudfront create-invalidation --distribution-id "$CLOUDFRONT_ID" --paths "/*"
    
    echo "✅ Frontend deployed"
    cd ..
fi

echo ""
echo "🎉 Setup Complete!"
echo "================="
echo ""
echo "Next steps:"
echo "1. Set up GitHub Secrets for CI/CD"
echo "2. Push to main branch to trigger automatic deployment"
echo "3. Monitor deployments in GitHub Actions"
echo ""
echo "Useful commands:"
echo "  ./start-local.sh          # Start local development"
echo "  cd backend && pytest      # Run backend tests"
echo "  cd frontend && npm test   # Run frontend tests"
echo ""

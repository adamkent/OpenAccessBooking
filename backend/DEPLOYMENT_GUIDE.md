# NHS Appointment Booking System - Deployment Guide

This guide provides step-by-step instructions for deploying the NHS appointment booking backend to AWS.

## 📋 Prerequisites

### 1. AWS Account Setup
- AWS account with appropriate permissions
- AWS CLI installed and configured
- AWS SAM CLI installed
- Python 3.11+ installed

### 2. Required AWS Permissions
Your AWS user/role needs the following permissions:
- CloudFormation (full access)
- Lambda (full access)
- API Gateway (full access)
- DynamoDB (full access)
- Cognito (full access)
- IAM (create/manage roles)
- S3 (create buckets, upload objects)
- SES (optional, for email notifications)
- SNS (optional, for SMS notifications)

### 3. Installation Commands
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Install SAM CLI
pip install aws-sam-cli

# Verify installations
aws --version
sam --version
```

## 🚀 Deployment Steps

### Step 1: Configure AWS Credentials
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your default region (eu-west-2 recommended for UK)
# Enter output format (json)

# Verify configuration
aws sts get-caller-identity
```

### Step 2: Clone and Navigate to Project
```bash
cd backend/
```

### Step 3: First-Time Deployment (Guided)
```bash
# Make deployment script executable
chmod +x deploy.sh

# Run guided deployment
./deploy.sh --guided
```

During guided deployment, you'll be prompted for:
- Stack name (default: nhs-appointment-booking)
- AWS region (default: eu-west-2)
- Environment (dev/staging/prod)
- Confirmation for resource creation

### Step 4: Note the Outputs
After successful deployment, note these important values:
- **API Gateway URL**: Your API endpoint
- **User Pool ID**: For Cognito authentication
- **User Pool Client ID**: For frontend integration

These will be automatically saved to your `.env` file.

## 🔧 Configuration Options

### Environment Variables
Edit `.env` file to customise:
```bash
# Environment Configuration
ENVIRONMENT=dev
AWS_REGION=eu-west-2

# These are auto-populated after deployment
API_GATEWAY_URL=https://abc123.execute-api.eu-west-2.amazonaws.com/dev/
USER_POOL_ID=eu-west-2_ABC123DEF
USER_POOL_CLIENT_ID=1a2b3c4d5e6f7g8h9i0j
```

### SAM Template Parameters
Modify `template.yaml` for advanced configuration:
- DynamoDB billing mode (PAY_PER_REQUEST vs PROVISIONED)
- Lambda memory allocation
- API Gateway throttling limits
- Cognito password policies

## 🧪 Post-Deployment Testing

### Step 1: Seed Test Data
```bash
# Create sample practices, patients, and appointments
python scripts/seed_data.py --environment dev --region eu-west-2
```

### Step 2: Test API Endpoints
```bash
# Run comprehensive API tests
python scripts/test_api.py https://your-api-url --verbose
```

### Step 3: Manual Testing
Test key endpoints manually:

1. **Register a user**:
```bash
curl -X POST https://your-api-url/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "role": "patient"
  }'
```

2. **Login**:
```bash
curl -X POST https://your-api-url/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

3. **Create appointment** (use token from login):
```bash
curl -X POST https://your-api-url/appointments \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "your-user-id",
    "practice_id": "practice-001",
    "appointment_datetime": "2024-12-15T10:30:00Z",
    "appointment_type": "routine"
  }'
```

## 🔄 Subsequent Deployments

### Quick Deployment
```bash
./deploy.sh
```

### Environment-Specific Deployments
```bash
# Deploy to staging
./deploy.sh --environment staging

# Deploy to production
./deploy.sh --environment prod
```

### Using Makefile
```bash
# Development deployment with data seeding
make dev

# Production deployment (with confirmation)
make prod-deploy

# View deployment info
make info
```

## 🏗️ Infrastructure Overview

### Created AWS Resources
- **CloudFormation Stack**: `nhs-appointment-booking-{env}`
- **Lambda Functions**: 8 functions for different operations
- **API Gateway**: RESTful API with Cognito authorisation
- **DynamoDB Tables**: 3 tables with GSIs
- **Cognito User Pool**: User authentication and management
- **IAM Roles**: Least-privilege access for Lambda functions
- **S3 Bucket**: Deployment artifacts storage

### Cost Estimation (Development)
- **Lambda**: ~$0 (generous free tier)
- **API Gateway**: ~$0-5/month (1M requests free)
- **DynamoDB**: ~$0-2/month (25GB free tier)
- **Cognito**: ~$0 (50,000 MAU free)
- **Total**: ~$0-10/month for development use

## 🔍 Monitoring and Logging

### CloudWatch Logs
View logs for each Lambda function:
```bash
# View all logs
make logs

# View specific function logs
aws logs tail /aws/lambda/nhs-appointment-CreateAppointmentFunction --follow
```

### CloudWatch Metrics
Monitor key metrics:
- API Gateway: Request count, latency, 4xx/5xx errors
- Lambda: Invocations, duration, errors, throttles
- DynamoDB: Read/write capacity, throttled requests
- Cognito: Sign-ups, sign-ins, authentication failures

### Setting Up Alarms
```bash
# Example: Create alarm for high error rate
aws cloudwatch put-metric-alarm \
  --alarm-name "NHS-API-HighErrorRate" \
  --alarm-description "High error rate on NHS API" \
  --metric-name 4XXError \
  --namespace AWS/ApiGateway \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold
```

## 🔐 Security Considerations

### Production Checklist
- [ ] Enable AWS CloudTrail for audit logging
- [ ] Set up AWS Config for compliance monitoring
- [ ] Configure VPC endpoints for DynamoDB (if using VPC)
- [ ] Enable API Gateway access logging
- [ ] Set up AWS WAF for API protection
- [ ] Configure backup policies for DynamoDB
- [ ] Review and minimize IAM permissions
- [ ] Enable MFA for AWS console access

### Data Protection
- All data encrypted at rest (DynamoDB, S3)
- All data encrypted in transit (HTTPS/TLS)
- JWT tokens for API authentication
- Role-based access control implemented
- Input validation and sanitization

## 🚨 Troubleshooting

### Common Issues

1. **Deployment Fails - Insufficient Permissions**
```bash
# Check your AWS permissions
aws iam get-user
aws sts get-caller-identity

# Ensure you have the required policies attached
```

2. **Lambda Function Errors**
```bash
# Check CloudWatch logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/nhs-appointment"

# View recent errors
aws logs filter-log-events --log-group-name "/aws/lambda/nhs-appointment-CreateAppointmentFunction" --start-time $(date -d '1 hour ago' +%s)000
```

3. **API Gateway 403 Errors**
- Check Cognito User Pool configuration
- Verify JWT token is valid and not expired
- Ensure user has correct role permissions

4. **DynamoDB Throttling**
```bash
# Check DynamoDB metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ThrottledRequests \
  --dimensions Name=TableName,Value=dev-appointments \
  --start-time $(date -d '1 hour ago' --iso-8601) \
  --end-time $(date --iso-8601) \
  --period 300 \
  --statistics Sum
```

### Debug Mode
Enable detailed logging:
```bash
# Set environment variable for debug logging
aws lambda update-function-configuration \
  --function-name nhs-appointment-CreateAppointmentFunction \
  --environment Variables='{LOG_LEVEL=DEBUG}'
```

## 🔄 Backup and Recovery

### DynamoDB Backups
```bash
# Enable point-in-time recovery
aws dynamodb update-continuous-backups \
  --table-name dev-appointments \
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true

# Create on-demand backup
aws dynamodb create-backup \
  --table-name dev-appointments \
  --backup-name "appointments-backup-$(date +%Y%m%d)"
```

### Export Data
```bash
# Use the seeding script to export data
python scripts/seed_data.py --export --environment dev
```

## 🗑️ Cleanup

### Delete Stack
```bash
# Using Makefile (with confirmation)
make destroy

# Using AWS CLI directly
aws cloudformation delete-stack --stack-name nhs-appointment-booking
```

### Manual Cleanup
If stack deletion fails, manually delete:
1. S3 buckets (empty them first)
2. DynamoDB tables
3. CloudWatch log groups
4. Cognito User Pools

## 📞 Support

### Getting Help
1. Check CloudWatch logs for detailed error messages
2. Review AWS CloudFormation events for deployment issues
3. Validate SAM template: `sam validate`
4. Test locally: `sam local start-api`

### Useful Commands
```bash
# Validate template
sam validate --template template.yaml

# Build locally
sam build

# Test locally
sam local start-api --port 3000

# Package for deployment
sam package --s3-bucket your-bucket --output-template-file packaged.yaml

# Deploy from package
sam deploy --template-file packaged.yaml --stack-name your-stack --capabilities CAPABILITY_IAM
```

---

**Note**: This deployment creates a prototype system. For production NHS use, additional security reviews, compliance checks, and NHS Digital approval processes are required.

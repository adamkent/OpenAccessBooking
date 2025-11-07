#!/bin/bash

# NHS Appointment Booking System - Deployment Script
# This script deploys the serverless backend to AWS using SAM

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STACK_NAME="nhs-appointment-booking"
REGION="eu-west-2"
ENVIRONMENT="dev"
S3_BUCKET=""

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if AWS CLI is installed and configured
check_aws_cli() {
    print_status "Checking AWS CLI configuration..."
    
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS CLI is not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    print_success "AWS CLI is configured"
}

# Function to check if SAM CLI is installed
check_sam_cli() {
    print_status "Checking SAM CLI installation..."
    
    if ! command -v sam &> /dev/null; then
        print_error "SAM CLI is not installed. Please install it first."
        print_status "Install instructions: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html"
        exit 1
    fi
    
    print_success "SAM CLI is installed"
}

# Function to create S3 bucket for deployment artifacts
create_s3_bucket() {
    if [ -z "$S3_BUCKET" ]; then
        # Generate unique bucket name
        ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
        S3_BUCKET="nhs-appointment-sam-artifacts-${ACCOUNT_ID}-${REGION}"
    fi
    
    print_status "Creating S3 bucket for deployment artifacts: $S3_BUCKET"
    
    # Check if bucket exists
    if aws s3 ls "s3://$S3_BUCKET" 2>&1 | grep -q 'NoSuchBucket'; then
        if [ "$REGION" = "us-east-1" ]; then
            aws s3 mb s3://$S3_BUCKET
        else
            aws s3 mb s3://$S3_BUCKET --region $REGION
        fi
        print_success "S3 bucket created: $S3_BUCKET"
    else
        print_status "S3 bucket already exists: $S3_BUCKET"
    fi
}

# Function to install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    # Create requirements.txt if it doesn't exist
    if [ ! -f "requirements.txt" ]; then
        print_warning "requirements.txt not found, creating basic one..."
        cat > requirements.txt << EOF
boto3==1.34.0
botocore==1.34.0
pyjwt==2.8.0
cryptography==41.0.7
requests==2.31.0
python-dateutil==2.8.2
validators==0.22.0
pydantic==2.5.0
fastapi==0.104.1
mangum==0.17.0
EOF
    fi
    
    # Install dependencies in each Lambda function directory
    for dir in src/*/; do
        if [ -d "$dir" ] && [ "$(basename "$dir")" != "utils" ]; then
            print_status "Installing dependencies for $(basename "$dir")..."
            cp requirements.txt "$dir"
        fi
    done
    
    print_success "Dependencies installed"
}

# Function to validate SAM template
validate_template() {
    print_status "Validating SAM template..."
    
    if sam validate --template template.yaml; then
        print_success "SAM template is valid"
    else
        print_error "SAM template validation failed"
        exit 1
    fi
}

# Function to build the application
build_application() {
    print_status "Building SAM application..."
    
    if sam build --template template.yaml; then
        print_success "Application built successfully"
    else
        print_error "Build failed"
        exit 1
    fi
}

# Function to deploy the application
deploy_application() {
    print_status "Deploying application to AWS..."
    
    # Deploy with guided deployment for first time
    if [ "$1" = "--guided" ]; then
        sam deploy --guided \
            --stack-name $STACK_NAME \
            --s3-bucket $S3_BUCKET \
            --region $REGION \
            --capabilities CAPABILITY_IAM \
            --parameter-overrides Environment=$ENVIRONMENT
    else
        # Deploy with existing configuration
        sam deploy \
            --stack-name $STACK_NAME \
            --s3-bucket $S3_BUCKET \
            --region $REGION \
            --capabilities CAPABILITY_IAM \
            --parameter-overrides Environment=$ENVIRONMENT \
            --no-confirm-changeset
    fi
    
    if [ $? -eq 0 ]; then
        print_success "Deployment completed successfully"
    else
        print_error "Deployment failed"
        exit 1
    fi
}

# Function to get stack outputs
get_stack_outputs() {
    print_status "Retrieving stack outputs..."
    
    API_URL=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
        --output text)
    
    USER_POOL_ID=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' \
        --output text)
    
    USER_POOL_CLIENT_ID=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`UserPoolClientId`].OutputValue' \
        --output text)
    
    echo ""
    print_success "Deployment Information:"
    echo "API Gateway URL: $API_URL"
    echo "User Pool ID: $USER_POOL_ID"
    echo "User Pool Client ID: $USER_POOL_CLIENT_ID"
    echo ""
    
    # Update .env file
    print_status "Updating .env file with deployment information..."
    sed -i.bak "s|API_GATEWAY_URL=.*|API_GATEWAY_URL=$API_URL|" .env
    sed -i.bak "s|USER_POOL_ID=.*|USER_POOL_ID=$USER_POOL_ID|" .env
    sed -i.bak "s|USER_POOL_CLIENT_ID=.*|USER_POOL_CLIENT_ID=$USER_POOL_CLIENT_ID|" .env
    rm .env.bak
    
    print_success ".env file updated"
}

# Function to run tests
run_tests() {
    print_status "Running basic API tests..."
    
    if [ -n "$API_URL" ]; then
        # Test health endpoint (if exists)
        if curl -s "$API_URL/health" > /dev/null; then
            print_success "API is responding"
        else
            print_warning "API health check failed or endpoint doesn't exist"
        fi
    else
        print_warning "API URL not available for testing"
    fi
}

# Function to clean up build artifacts
cleanup() {
    print_status "Cleaning up build artifacts..."
    
    # Remove requirements.txt from function directories
    for dir in src/*/; do
        if [ -d "$dir" ] && [ "$(basename "$dir")" != "utils" ]; then
            rm -f "$dir/requirements.txt"
        fi
    done
    
    # Remove SAM build directory
    rm -rf .aws-sam
    
    print_success "Cleanup completed"
}

# Main deployment function
main() {
    echo "========================================="
    echo "NHS Appointment Booking System Deployment"
    echo "========================================="
    echo ""
    
    # Parse command line arguments
    GUIDED=false
    CLEANUP_ONLY=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --guided)
                GUIDED=true
                shift
                ;;
            --environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --region)
                REGION="$2"
                shift 2
                ;;
            --cleanup)
                CLEANUP_ONLY=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --guided          Run guided deployment (for first time)"
                echo "  --environment ENV Set environment (default: dev)"
                echo "  --region REGION   Set AWS region (default: eu-west-2)"
                echo "  --cleanup         Only cleanup build artifacts"
                echo "  --help            Show this help message"
                echo ""
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    if [ "$CLEANUP_ONLY" = true ]; then
        cleanup
        exit 0
    fi
    
    # Run deployment steps
    check_aws_cli
    check_sam_cli
    create_s3_bucket
    install_dependencies
    validate_template
    build_application
    
    if [ "$GUIDED" = true ]; then
        deploy_application --guided
    else
        deploy_application
    fi
    
    get_stack_outputs
    run_tests
    
    echo ""
    print_success "Deployment completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Test the API endpoints using the provided URL"
    echo "2. Create test users via the registration endpoint"
    echo "3. Set up the frontend application with the API URL"
    echo ""
}

# Run main function with all arguments
main "$@"

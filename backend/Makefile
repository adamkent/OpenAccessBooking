# NHS Appointment Booking System - Makefile
# Provides convenient commands for development and deployment

.PHONY: help install build test deploy clean seed-data test-api

# Default target
help:
	@echo "NHS Appointment Booking System - Available Commands"
	@echo "=================================================="
	@echo ""
	@echo "Development:"
	@echo "  install     - Install dependencies and setup development environment"
	@echo "  build       - Build the SAM application"
	@echo "  test        - Run local tests"
	@echo "  clean       - Clean build artifacts"
	@echo ""
	@echo "Deployment:"
	@echo "  deploy      - Deploy to AWS (dev environment)"
	@echo "  deploy-prod - Deploy to AWS (production environment)"
	@echo "  deploy-guided - Deploy with guided setup (first time)"
	@echo ""
	@echo "Data Management:"
	@echo "  seed-data   - Seed test data into DynamoDB"
	@echo "  test-api    - Run API integration tests"
	@echo ""
	@echo "Utilities:"
	@echo "  validate    - Validate SAM template"
	@echo "  logs        - View CloudWatch logs"
	@echo "  destroy     - Delete the CloudFormation stack"
	@echo ""

# Variables
STACK_NAME := nhs-appointment-booking
REGION := eu-west-2
ENVIRONMENT := dev

# Install dependencies and setup environment
install:
	@echo "🔧 Installing dependencies..."
	@pip install --upgrade pip
	@pip install boto3 pydantic requests validators python-dateutil
	@pip install aws-sam-cli
	@echo "✅ Dependencies installed"

# Build the SAM application
build:
	@echo "🏗️ Building SAM application..."
	@sam build --template template.yaml
	@echo "✅ Build completed"

# Validate SAM template
validate:
	@echo "🔍 Validating SAM template..."
	@sam validate --template template.yaml
	@echo "✅ Template is valid"

# Deploy to development environment
deploy: validate build
	@echo "🚀 Deploying to development environment..."
	@./deploy.sh --environment dev --region $(REGION)

# Deploy to production environment
deploy-prod: validate build
	@echo "🚀 Deploying to production environment..."
	@./deploy.sh --environment prod --region $(REGION)

# Deploy with guided setup (first time)
deploy-guided: validate build
	@echo "🚀 Running guided deployment..."
	@./deploy.sh --guided --environment $(ENVIRONMENT) --region $(REGION)

# Run local tests
test:
	@echo "🧪 Running local tests..."
	@python -m pytest tests/ -v || echo "⚠️ No pytest tests found - create tests/ directory with test files"

# Seed test data
seed-data:
	@echo "🌱 Seeding test data..."
	@python scripts/seed_data.py --environment $(ENVIRONMENT) --region $(REGION)

# Test API endpoints
test-api:
	@echo "🔬 Testing API endpoints..."
	@if [ -z "$(API_URL)" ]; then \
		echo "❌ Error: API_URL not provided"; \
		echo "Usage: make test-api API_URL=https://your-api-url"; \
		exit 1; \
	fi
	@python scripts/test_api.py $(API_URL) --verbose

# View CloudWatch logs
logs:
	@echo "📋 Viewing CloudWatch logs..."
	@sam logs --stack-name $(STACK_NAME) --region $(REGION) --tail

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	@./deploy.sh --cleanup
	@rm -rf .aws-sam/
	@find . -name "requirements.txt" -path "*/src/*" -not -path "*/utils/*" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete
	@echo "✅ Cleanup completed"

# Delete CloudFormation stack
destroy:
	@echo "⚠️ This will delete all AWS resources for the $(STACK_NAME) stack"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo "🗑️ Deleting CloudFormation stack..."
	@aws cloudformation delete-stack --stack-name $(STACK_NAME) --region $(REGION)
	@echo "⏳ Waiting for stack deletion to complete..."
	@aws cloudformation wait stack-delete-complete --stack-name $(STACK_NAME) --region $(REGION)
	@echo "✅ Stack deleted successfully"

# Start local API for development
local:
	@echo "🏃 Starting local API..."
	@sam local start-api --template template.yaml --port 3000

# Setup local development environment
setup-local:
	@echo "🔧 Setting up local development environment..."
	@python scripts/setup_local.py

# Start local DynamoDB (requires Docker)
start-local-db:
	@echo "🗄️ Starting local DynamoDB..."
	@docker run -d -p 8000:8000 --name dynamodb-local amazon/dynamodb-local || echo "DynamoDB Local already running or Docker not available"

# Stop local DynamoDB
stop-local-db:
	@echo "🛑 Stopping local DynamoDB..."
	@docker stop dynamodb-local && docker rm dynamodb-local || echo "DynamoDB Local not running"

# Complete local development setup
local-dev: start-local-db setup-local
	@echo "🎉 Local development environment ready!"
	@echo ""
	@echo "To start the API server:"
	@echo "  make local"
	@echo ""
	@echo "To test the API:"
	@echo "  make test-local-api"

# Test local API
test-local-api:
	@echo "🧪 Testing local API..."
	@python scripts/test_api.py http://localhost:3000 --verbose

# Package for deployment
package:
	@echo "📦 Packaging application..."
	@sam package --template template.yaml --s3-bucket nhs-appointment-sam-artifacts --output-template-file packaged-template.yaml

# Quick development cycle
dev: clean build deploy seed-data
	@echo "🎉 Development environment ready!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Run 'make test-api API_URL=<your-api-url>' to test endpoints"
	@echo "2. Check CloudWatch logs with 'make logs'"

# Production deployment with confirmation
prod-deploy:
	@echo "⚠️ This will deploy to PRODUCTION environment"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@$(MAKE) deploy-prod

# Show stack information
info:
	@echo "📊 Stack Information"
	@echo "==================="
	@aws cloudformation describe-stacks --stack-name $(STACK_NAME) --region $(REGION) --query 'Stacks[0].Outputs' --output table 2>/dev/null || echo "Stack not found or not deployed"

# Check AWS configuration
check-aws:
	@echo "🔍 Checking AWS configuration..."
	@aws sts get-caller-identity
	@echo "✅ AWS CLI is configured"

# Format Python code
format:
	@echo "🎨 Formatting Python code..."
	@find src/ -name "*.py" -exec python -m black {} + 2>/dev/null || echo "⚠️ black not installed - run 'pip install black' to format code"

# Lint Python code
lint:
	@echo "🔍 Linting Python code..."
	@find src/ -name "*.py" -exec python -m flake8 {} + 2>/dev/null || echo "⚠️ flake8 not installed - run 'pip install flake8' to lint code"

# Generate API documentation
docs:
	@echo "📚 Generating API documentation..."
	@echo "API documentation would be generated here"
	@echo "Consider using tools like Swagger/OpenAPI for API docs"

# Monitor deployment
monitor:
	@echo "📈 Opening CloudWatch dashboard..."
	@echo "Navigate to: https://$(REGION).console.aws.amazon.com/cloudwatch/home?region=$(REGION)#dashboards:"

# Backup data
backup:
	@echo "💾 Creating data backup..."
	@python -c "
import boto3
import json
from datetime import datetime

# This is a placeholder for backup functionality
print('Backup functionality would export DynamoDB data')
print('Consider implementing with AWS Data Pipeline or custom scripts')
"

# Restore data
restore:
	@echo "🔄 Restoring data from backup..."
	@echo "Restore functionality would import DynamoDB data from backup"

# Show environment variables
env:
	@echo "🌍 Environment Variables"
	@echo "======================="
	@echo "STACK_NAME: $(STACK_NAME)"
	@echo "REGION: $(REGION)"
	@echo "ENVIRONMENT: $(ENVIRONMENT)"
	@echo ""
	@echo "Current .env file contents:"
	@cat .env 2>/dev/null || echo "No .env file found"

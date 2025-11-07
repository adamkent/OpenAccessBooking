# Local Development Guide

This guide will help you set up and run the complete NHS Appointment Booking System locally without any cloud resources.

## Prerequisites

- **Node.js 16+** and npm
- **Python 3.11+** and pip
- **Docker** and Docker Compose (for local DynamoDB)
- **Git** for version control

**For WSL Users (Windows):**
- WSL 2 installed and configured
- Access applications via WSL IP address (not localhost) from Windows browser
- `sudo apt install pythonispython3` if running start-local scripts
- Find WSL IP with: `hostname -I | awk '{print $1}'`

## Quick Start

**Automated Setup (Recommended):**

```bash
# Make scripts executable
chmod +x start-local.sh stop-local.sh

# Start everything with one command
./start-local.sh
```

This script will:
- Check prerequisites
- Install dependencies
- Start DynamoDB Local and DynamoDB Admin
- Initialize database with test data
- Start backend and frontend servers

**Manual Setup (Alternative):**

### 1. Clone and Setup

```bash
# Clone the repository (if not already done)
cd /home/adamkent/projects/OpenAccessBooking

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install
```

### 2. Start Local DynamoDB

```bash
cd backend
docker-compose up -d dynamodb dynamodb-admin
```

### 3. Configure Environment

**Backend (.env):**
```bash
cd backend
cp .env.example .env
```

Update `backend/.env`:
```bash
# Local Development Configuration
ENVIRONMENT=local
AWS_REGION=eu-west-2
AWS_PROFILE=default

# Local DynamoDB
DYNAMODB_ENDPOINT=http://localhost:8000
APPOINTMENTS_TABLE=local-appointments
PATIENTS_TABLE=local-patients
PRACTICES_TABLE=local-practices

# Cognito (Mock for local development)
USER_POOL_ID=local-user-pool
USER_POOL_CLIENT_ID=local-client-id

# API Configuration
API_GATEWAY_URL=http://localhost:5000
CORS_ORIGINS=http://localhost:3000

# Local Development
USE_LOCAL_DB=true
MOCK_AUTH=true
LOG_LEVEL=DEBUG
```

**Frontend (.env):**
```bash
cd frontend
cp .env.example .env
```

Update `frontend/.env`:
```bash
# Local Development Configuration
REACT_APP_ENV=development
REACT_APP_API_URL=http://localhost:5000
REACT_APP_ENABLE_MOCK_DATA=true
REACT_APP_ENABLE_DEBUG=true
REACT_APP_LOG_LEVEL=debug
```

### 4. Initialize Database and Test Data

```bash
cd backend
python3 scripts/setup_local_dev.py
```

### 5. Start Services

**Terminal 1 - Backend:**
```bash
cd backend
python3 app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

### 6. Access the Application

**If running in WSL (Windows Subsystem for Linux):**

First, find your WSL IP address:
```bash
hostname -I | awk '{print $1}'
```

Then access from Windows browser using that IP (e.g., `172.x.x.x`):
- **Frontend**: http://[WSL_IP]:3000 (e.g., http://172.20.7.150:3000)
- **Backend API**: http://[WSL_IP]:5000 (e.g., http://172.20.7.150:5000)
- **DynamoDB Admin**: http://[WSL_IP]:8001 (e.g., http://172.20.7.150:8001)

**If running natively on Linux/Mac:**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **DynamoDB Admin**: http://localhost:8001

**Note:** WSL's `localhost` is isolated from Windows. You must use the WSL IP address when accessing from Windows browsers.

**Management Commands:**
```bash
# Stop all services
./stop-local.sh

# View logs
tail -f logs/backend.log
tail -f logs/frontend.log

# Reset database
cd backend && python3 scripts/setup_local_dev.py
```

## Test Data

The system comes with pre-seeded test data:

### Test Users

**Patients:**
- Email: `john.smith@email.com` / Password: `TestPass123!`
- Email: `jane.doe@email.com` / Password: `TestPass123!`
- Email: `bob.wilson@email.com` / Password: `TestPass123!`

**Staff:**
- Email: `dr.sarah.jones@riverside.nhs.uk` / Password: `StaffPass123!`
- Email: `nurse.mary.brown@riverside.nhs.uk` / Password: `StaffPass123!`

### Test Practice

- **Name**: Riverside Medical Centre
- **Address**: 123 High Street, London, SW1A 1AA
- **Phone**: 020 7123 4567

## Testing Guide

### 1. Patient Journey Testing

**Registration Flow:**
1. Go to http://[WSL_IP]:3000 (or http://localhost:3000 if not using WSL)
2. Click "Register"
3. Complete registration with a valid test NHS number: `943 476 5919` or `401 023 2137`
4. Verify email validation and NHS number validation

**Note:** NHS numbers use Modulus 11 check digit validation. Use the valid test numbers above.

**Appointment Booking:**
1. Login as a patient
2. Navigate to "Book Appointment"
3. Select appointment type and reason
4. Choose available date and time
5. Confirm booking

**Appointment Management:**
1. View appointments in "My Appointments"
2. Test cancellation functionality
3. Check appointment history

### 2. Staff Journey Testing

**Staff Dashboard:**
1. Login as staff member
2. Review today's appointments
3. Check practice statistics

**Appointment Management:**
1. Navigate to "Manage Appointments"
2. Test search and filtering
3. Update appointment statuses
4. View patient details

**Patient Management:**
1. Search for patients
2. View patient records
3. Check appointment history

### 3. API Testing

**Using curl:**
```bash
# Health check
curl http://localhost:5000/health

# Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john.smith@email.com","password":"TestPass123!"}'

# Get appointments (with token)
curl http://localhost:5000/appointments \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Database Testing

**View DynamoDB data with DynamoDB Admin:**

Access the web UI at:
- **WSL**: http://[WSL_IP]:8001
- **Native**: http://localhost:8001

This provides a visual interface to:
- Browse all tables
- View table data
- Query and scan tables
- Create/update/delete items
- Monitor table metrics

## Development Workflow

### Making Changes

1. **Backend Changes:**
   - Modify Python files in `backend/src/`
   - Restart the backend server
   - Test API endpoints

2. **Frontend Changes:**
   - Modify React files in `frontend/src/`
   - Hot reload will update automatically
   - Test in browser

### Adding New Features

1. **New API Endpoint:**
   ```bash
   # Create new Lambda function
   cd backend/src/appointments
   cp create_appointment.py new_feature.py
   # Modify as needed
   
   # Add route to app.py
   # Test with curl or frontend
   ```

2. **New Frontend Page:**
   ```bash
   # Create new page component
   cd frontend/src/pages
   mkdir new-feature
   # Add component and routing
   ```

### Database Schema Changes

```bash
# Update table definitions
cd backend/scripts
python create_tables.py

# Migrate existing data if needed
python migrate_data.py
```

## Troubleshooting

### Common Issues

**DynamoDB Connection Error:**
```bash
# Check if DynamoDB is running
docker ps | grep dynamodb

# Restart if needed
docker restart dynamodb-local
```

**CORS Issues:**
- Ensure `CORS_ORIGINS` in backend `.env` includes `http://localhost:3000`
- Check browser console for CORS errors

**Authentication Issues:**
- Verify `MOCK_AUTH=true` in backend `.env` for local development
- Check JWT token format in browser localStorage

**Port Conflicts:**
```bash
# Check what's using ports
lsof -i :3000  # Frontend
lsof -i :5000  # Backend
lsof -i :8000  # DynamoDB

# Kill processes if needed
kill -9 PID
```

### Logs and Debugging

**Backend Logs:**
```bash
# Set debug level in .env
LOG_LEVEL=DEBUG

# View logs in terminal where backend is running
```

**Frontend Logs:**
- Open browser Developer Tools
- Check Console tab for errors
- Network tab for API calls

**Database Logs:**
```bash
# DynamoDB container logs
docker logs dynamodb-local
```

## Performance Testing

### Load Testing

```bash
# Install artillery
npm install -g artillery

# Run load tests
cd backend/tests
artillery run load-test.yml
```

### Frontend Performance

```bash
cd frontend

# Build and analyse bundle
npm install -g webpack-bundle-analyzer
npx webpack-bundle-analyzer build/static/js/*.js
```

## Data Management

### Backup Test Data

```bash
cd backend/scripts
python backup_local_data.py
```

### Reset Database

```bash
# Clear all tables
python scripts/clear_tables.py

# Recreate with fresh test data
python scripts/seed_test_data.py
```

### Custom Test Scenarios

```bash
# Create specific test scenarios
python scripts/create_test_scenario.py --scenario busy_day
python scripts/create_test_scenario.py --scenario empty_practice
```

## Integration Testing

### End-to-End Tests

```bash
cd frontend

# Install Cypress (if not already installed)
npm install --save-dev cypress

# Run E2E tests
npm run test:e2e
```

### API Integration Tests

```bash
cd backend

# Run integration tests
python -m pytest tests/integration/
```

## Production Simulation

### Environment Switching

```bash
# Switch to production-like environment
cd backend
cp .env.production.local .env

cd frontend
cp .env.production.local .env

# Restart services
```

### Security Testing

```bash
# Test authentication
python scripts/test_security.py

# Check for vulnerabilities
cd frontend
npm audit

cd backend
pip-audit
```

## Next Steps

Once local development is working:

1. **Deploy to AWS** - Use the deployment guides
2. **Set up CI/CD** - Automate testing and deployment
3. **Monitor Performance** - Add logging and metrics
4. **Scale Testing** - Test with larger datasets

## Getting Help

- **Backend Issues**: Check `backend/README.md`
- **Frontend Issues**: Check `frontend/README.md`
- **API Documentation**: http://localhost:5000/docs (when running)
- **Create GitHub Issues**: For bugs or feature requests

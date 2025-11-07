#!/bin/bash

# NHS Appointment Booking System - Local Development Startup Script

set -e

echo "🏥 NHS Appointment Booking System - Local Development Setup"
echo "=========================================================="

# Check prerequisites
check_prerequisites() {
    echo "📋 Checking prerequisites..."
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js is not installed. Please install Node.js 16+ and npm"
        exit 1
    fi
    
    # Check Python
    if ! command -v python &> /dev/null; then
        echo "❌ Python is not installed. Please install Python 3.11+"
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker"
        exit 1
    fi
    
    echo "✅ Prerequisites check passed"
}

# Setup backend
setup_backend() {
    echo "🔧 Setting up backend..."
    
    cd backend
    
    # Install Python dependencies
    echo "Installing Python dependencies..."
    pip install -r requirements.txt --break-system-packages
    
    # Setup environment
    if [ ! -f ".env" ]; then
        echo "Creating backend .env file..."
        
        # Detect WSL IP for CORS
        WSL_IP=$(hostname -I | awk '{print $1}')
        
        cat > .env << EOF
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
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://${WSL_IP}:3000

# Local Development
USE_LOCAL_DB=true
USE_LOCAL_AUTH=true
MOCK_AUTH=true
LOG_LEVEL=DEBUG
EOF
    fi
    
    cd ..
    echo "✅ Backend setup complete"
}

# Setup frontend
setup_frontend() {
    echo "🎨 Setting up frontend..."
    
    cd frontend
    
    # Install Node.js dependencies
    if [ ! -d "node_modules" ]; then
        echo "Installing Node.js dependencies..."
        npm install
    fi
    
    # Setup environment
    if [ ! -f ".env" ]; then
        echo "Creating frontend .env file..."
        
        # Detect WSL IP for API URL
        WSL_IP=$(hostname -I | awk '{print $1}')
        
        cat > .env << EOF
# Local Development Configuration
REACT_APP_ENV=development
REACT_APP_API_URL=http://${WSL_IP}:5000
REACT_APP_ENABLE_MOCK_DATA=true
REACT_APP_ENABLE_DEBUG=true
REACT_APP_LOG_LEVEL=debug
EOF
    fi
    
    cd ..
    echo "✅ Frontend setup complete"
}

# Start DynamoDB
start_dynamodb() {
    echo "🗄️  Starting DynamoDB Local..."
    
    cd backend
    
    # Check if DynamoDB container is already running
    if docker ps | grep -q "nhs-dynamodb-local"; then
        echo "DynamoDB Local is already running"
    else
        # Start DynamoDB using Docker Compose
        docker-compose up -d dynamodb dynamodb-admin
        
        # Wait for DynamoDB to be ready
        echo "Waiting for DynamoDB to be ready..."
        sleep 5
        
        # Check if DynamoDB is responding
        max_retries=30
        for i in $(seq 1 $max_retries); do
            if curl -s http://localhost:8000 > /dev/null 2>&1; then
                echo "✅ DynamoDB Local is ready"
                break
            fi
            
            if [ $i -eq $max_retries ]; then
                echo "❌ DynamoDB Local failed to start"
                exit 1
            fi
            
            echo "Waiting for DynamoDB... ($i/$max_retries)"
            sleep 2
        done
    fi
    
    cd ..
}

# Initialize database
init_database() {
    echo "🏗️  Initializing database and test data..."
    
    cd backend
    
    # Run setup script
    python scripts/setup_local_dev.py
    
    cd ..
    echo "✅ Database initialized with test data"
}

# Start services
start_services() {
    echo "🚀 Starting services..."
    
    # Create log directory
    mkdir -p logs
    
    # Start backend in background
    echo "Starting backend server..."
    cd backend
    nohup python app.py > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../logs/backend.pid
    cd ..
    
    # Wait for backend to start
    echo "Waiting for backend to start..."
    sleep 5
    
    # Check if backend is running (try multiple addresses)
    if curl -s http://127.0.0.1:5000/health > /dev/null 2>&1 || curl -s http://0.0.0.0:5000/health > /dev/null 2>&1; then
        echo "✅ Backend server is running on http://localhost:5000"
    else
        echo "⚠️  Backend server may still be starting (check logs/backend.log)"
    fi
    
    # Start frontend in background
    echo "Starting frontend server..."
    cd frontend
    nohup npm start > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../logs/frontend.pid
    cd ..
    
    echo "✅ Frontend server is starting on http://localhost:3000"
}

# Show status
show_status() {
    # Detect WSL IP
    WSL_IP=$(hostname -I | awk '{print $1}')
    
    echo ""
    echo "🎉 NHS Appointment Booking System is now running!"
    echo "=========================================================="
    echo ""
    
    # Check if running in WSL
    if grep -qi microsoft /proc/version 2>/dev/null; then
        echo "⚠️  WSL Detected - Access from Windows browser using:"
        echo ""
        echo "📱 Frontend:           http://${WSL_IP}:3000"
        echo "🔧 Backend API:        http://${WSL_IP}:5000"
        echo "🗄️  DynamoDB Local:     http://${WSL_IP}:8000"
        echo "📊 DynamoDB Admin:     http://${WSL_IP}:8001"
        echo ""
        echo "💡 From WSL terminal, use: http://localhost:3000"
    else
        echo "📱 Frontend:           http://localhost:3000"
        echo "🔧 Backend API:        http://localhost:5000"
        echo "🗄️  DynamoDB Local:     http://localhost:8000"
        echo "📊 DynamoDB Admin:     http://localhost:8001"
    fi
    
    echo ""
    echo "👥 Test Accounts:"
    echo "   Patient: john.smith@email.com / TestPass123!"
    echo "   Staff:   dr.sarah.jones@riverside.nhs.uk / StaffPass123!"
    echo ""
    echo "📋 Management Commands:"
    echo "   Stop services:  ./stop-local.sh"
    echo "   View logs:      tail -f logs/backend.log"
    echo "                   tail -f logs/frontend.log"
    echo "   Reset data:     cd backend && python scripts/setup_local_dev.py"
    echo ""
}

# Main execution
main() {
    check_prerequisites
    setup_backend
    setup_frontend
    start_dynamodb
    init_database
    start_services
    show_status
}

# Handle script arguments
case "${1:-}" in
    "setup")
        check_prerequisites
        setup_backend
        setup_frontend
        echo "✅ Setup complete. Run './start-local.sh' to start services."
        ;;
    "db")
        start_dynamodb
        init_database
        ;;
    "services")
        start_services
        show_status
        ;;
    *)
        main
        ;;
esac

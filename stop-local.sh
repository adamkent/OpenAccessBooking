#!/bin/bash

# NHS Appointment Booking System - Stop Local Development Services

set -e

echo "🛑 Stopping NHS Appointment Booking System - Local Development"
echo "=============================================================="

# Stop backend server
stop_backend() {
    if [ -f "logs/backend.pid" ]; then
        BACKEND_PID=$(cat logs/backend.pid)
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            echo "🔧 Stopping backend server (PID: $BACKEND_PID)..."
            kill $BACKEND_PID
            rm logs/backend.pid
            echo "✅ Backend server stopped"
        else
            echo "⚠️  Backend server was not running"
            rm -f logs/backend.pid
        fi
    else
        echo "⚠️  No backend PID file found"
    fi
}

# Stop frontend server
stop_frontend() {
    if [ -f "logs/frontend.pid" ]; then
        FRONTEND_PID=$(cat logs/frontend.pid)
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            echo "🎨 Stopping frontend server (PID: $FRONTEND_PID)..."
            kill $FRONTEND_PID
            rm logs/frontend.pid
            echo "✅ Frontend server stopped"
        else
            echo "⚠️  Frontend server was not running"
            rm -f logs/frontend.pid
        fi
    else
        echo "⚠️  No frontend PID file found"
    fi
    
    # Also kill any remaining npm processes
    pkill -f "npm start" 2>/dev/null || true
    pkill -f "react-scripts start" 2>/dev/null || true
}

# Stop DynamoDB
stop_dynamodb() {
    echo "🗄️  Stopping DynamoDB Local..."
    
    cd backend
    
    # Stop Docker Compose services
    if docker-compose ps | grep -q "Up"; then
        docker-compose down
        echo "✅ DynamoDB Local stopped"
    else
        echo "⚠️  DynamoDB Local was not running"
    fi
    
    cd ..
}

# Clean up processes
cleanup_processes() {
    echo "🧹 Cleaning up any remaining processes..."
    
    # Kill any remaining Python processes running app.py
    pkill -f "python.*app.py" 2>/dev/null || true
    
    # Kill any remaining Node.js processes on port 3000
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    
    # Kill any remaining Python processes on port 5000
    lsof -ti:5000 | xargs kill -9 2>/dev/null || true
}

# Show final status
show_status() {
    echo ""
    echo "✅ All services stopped successfully!"
    echo ""
    echo "📋 To restart the system:"
    echo "   ./start-local.sh"
    echo ""
    echo "🗄️  To preserve data between restarts:"
    echo "   DynamoDB data is persisted in Docker volume"
    echo ""
    echo "🔄 To reset all data:"
    echo "   docker volume rm openaccessbooking_dynamodb_data"
    echo "   ./start-local.sh"
    echo ""
}

# Handle script arguments
case "${1:-}" in
    "backend")
        stop_backend
        ;;
    "frontend")
        stop_frontend
        ;;
    "db")
        stop_dynamodb
        ;;
    "clean")
        stop_backend
        stop_frontend
        stop_dynamodb
        cleanup_processes
        echo "🧹 Cleaned up all processes and containers"
        ;;
    *)
        stop_backend
        stop_frontend
        stop_dynamodb
        cleanup_processes
        show_status
        ;;
esac

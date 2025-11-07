#!/usr/bin/env python3
"""
Local development server for NHS Appointment Booking System
Runs Flask app with all Lambda functions as local endpoints
"""

import os
import sys
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If python-dotenv is not installed, manually load .env
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ.setdefault(key, value)

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import Lambda functions
from appointments.create_appointment import lambda_handler as create_appointment
from appointments.get_appointments import lambda_handler as get_appointments
from appointments.update_appointment import lambda_handler as update_appointment
from appointments.delete_appointment import lambda_handler as delete_appointment
from patients.create_patient import lambda_handler as create_patient
from patients.get_patient import lambda_handler as get_patient
from auth.auth import lambda_handler as auth_handler

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv('LOG_LEVEL') == 'DEBUG' else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app, origins=os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(','))

def create_lambda_event(method, path, body=None, query_params=None, path_params=None):
    """Create a Lambda event from Flask request"""
    return {
        'httpMethod': method,
        'path': path,
        'pathParameters': path_params or {},
        'queryStringParameters': query_params or {},
        'body': json.dumps(body) if body else None,
        'headers': dict(request.headers),
        'requestContext': {
            'requestId': 'local-dev',
            'stage': 'local',
            'identity': {
                'sourceIp': request.remote_addr
            }
        }
    }

def create_lambda_context():
    """Create a mock Lambda context"""
    class MockContext:
        def __init__(self):
            self.function_name = 'local-dev'
            self.function_version = '1.0'
            self.invoked_function_arn = 'arn:aws:lambda:local:123456789012:function:local-dev'
            self.memory_limit_in_mb = 128
            self.remaining_time_in_millis = lambda: 30000
            self.aws_request_id = 'local-request-id'
    
    return MockContext()

def handle_lambda_response(response):
    """Convert Lambda response to Flask response"""
    if not response:
        return jsonify({'error': 'No response from handler'}), 500
    
    status_code = response.get('statusCode', 500)
    body = response.get('body', '{}')
    
    try:
        if isinstance(body, str):
            body = json.loads(body)
    except json.JSONDecodeError:
        pass
    
    return jsonify(body), status_code

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'environment': os.getenv('ENVIRONMENT', 'local'),
        'version': '1.0.0'
    })

# Authentication endpoints
@app.route('/auth/login', methods=['POST'])
def login():
    """User login"""
    event = create_lambda_event('POST', '/auth/login', request.get_json())
    context = create_lambda_context()
    response = auth_handler(event, context)
    return handle_lambda_response(response)

@app.route('/auth/register', methods=['POST'])
def register():
    """User registration"""
    event = create_lambda_event('POST', '/auth/register', request.get_json())
    context = create_lambda_context()
    response = auth_handler(event, context)
    return handle_lambda_response(response)

# Appointment endpoints
@app.route('/appointments', methods=['GET'])
def get_appointments_endpoint():
    """Get appointments"""
    event = create_lambda_event('GET', '/appointments', query_params=dict(request.args))
    context = create_lambda_context()
    response = get_appointments(event, context)
    return handle_lambda_response(response)

@app.route('/appointments', methods=['POST'])
def create_appointment_endpoint():
    """Create appointment"""
    event = create_lambda_event('POST', '/appointments', request.get_json())
    context = create_lambda_context()
    response = create_appointment(event, context)
    return handle_lambda_response(response)

@app.route('/appointments/<appointment_id>', methods=['GET'])
def get_appointment_endpoint(appointment_id):
    """Get specific appointment"""
    event = create_lambda_event('GET', f'/appointments/{appointment_id}', 
                               path_params={'appointment_id': appointment_id})
    context = create_lambda_context()
    response = get_appointments(event, context)
    return handle_lambda_response(response)

@app.route('/appointments/<appointment_id>', methods=['PUT'])
def update_appointment_endpoint(appointment_id):
    """Update appointment"""
    event = create_lambda_event('PUT', f'/appointments/{appointment_id}', 
                               request.get_json(), 
                               path_params={'appointment_id': appointment_id})
    context = create_lambda_context()
    response = update_appointment(event, context)
    return handle_lambda_response(response)

@app.route('/appointments/<appointment_id>', methods=['DELETE'])
def delete_appointment_endpoint(appointment_id):
    """Delete appointment"""
    event = create_lambda_event('DELETE', f'/appointments/{appointment_id}', 
                               path_params={'appointment_id': appointment_id})
    context = create_lambda_context()
    response = delete_appointment(event, context)
    return handle_lambda_response(response)

@app.route('/appointments/available-slots', methods=['GET'])
def get_available_slots():
    """Get available appointment slots"""
    # Mock implementation for local development
    practice_id = request.args.get('practice_id')
    date = request.args.get('date')
    
    if not practice_id or not date:
        return jsonify({'error': 'practice_id and date are required'}), 400
    
    # Generate mock time slots
    slots = []
    for hour in range(9, 17):  # 9 AM to 5 PM
        for minute in [0, 30]:  # Every 30 minutes
            time_str = f"{hour:02d}:{minute:02d}"
            slots.append({
                'time': time_str,
                'available': True,
                'duration': 30
            })
    
    return jsonify({'slots': slots})

# Patient endpoints
@app.route('/patients', methods=['POST'])
def create_patient_endpoint():
    """Create patient"""
    event = create_lambda_event('POST', '/patients', request.get_json())
    context = create_lambda_context()
    response = create_patient(event, context)
    return handle_lambda_response(response)

@app.route('/patients/<patient_id>', methods=['GET'])
def get_patient_endpoint(patient_id):
    """Get patient"""
    event = create_lambda_event('GET', f'/patients/{patient_id}', 
                               path_params={'patient_id': patient_id})
    context = create_lambda_context()
    response = get_patient(event, context)
    return handle_lambda_response(response)

@app.route('/patients/search', methods=['GET'])
def search_patients():
    """Search patients"""
    # Mock implementation for local development
    search_term = request.args.get('q', '')
    
    # Return mock patient data
    patients = [
        {
            'patient_id': 'patient-1',
            'first_name': 'John',
            'last_name': 'Smith',
            'nhs_number': '1234567890',
            'email': 'john.smith@email.com',
            'phone_number': '07123456789',
            'date_of_birth': '1980-01-15',
            'address': {
                'line1': '123 Main Street',
                'city': 'London',
                'postcode': 'SW1A 1AA'
            }
        },
        {
            'patient_id': 'patient-2',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'nhs_number': '0987654321',
            'email': 'jane.doe@email.com',
            'phone_number': '07987654321',
            'date_of_birth': '1975-06-20',
            'address': {
                'line1': '456 Oak Avenue',
                'city': 'London',
                'postcode': 'SW2B 2BB'
            }
        }
    ]
    
    # Filter by search term if provided
    if search_term:
        search_lower = search_term.lower()
        patients = [p for p in patients if 
                   search_lower in p['first_name'].lower() or
                   search_lower in p['last_name'].lower() or
                   search_lower in p['nhs_number'] or
                   search_lower in p['email'].lower()]
    
    return jsonify({'patients': patients})

# Practice endpoints
@app.route('/practices/<practice_id>', methods=['GET'])
def get_practice(practice_id):
    """Get practice information"""
    # Mock practice data
    practice = {
        'practice_id': practice_id,
        'name': 'Riverside Medical Centre',
        'address': {
            'line1': '123 High Street',
            'line2': '',
            'city': 'London',
            'postcode': 'SW1A 1AA'
        },
        'phone': '020 7123 4567',
        'email': 'info@riverside.nhs.uk',
        'website': 'https://www.riverside.nhs.uk',
        'services': [
            'General Practice',
            'Vaccinations',
            'Health Checks',
            'Minor Surgery',
            'Family Planning'
        ],
        'operating_hours': {
            'monday': {'open': '08:00', 'close': '18:00'},
            'tuesday': {'open': '08:00', 'close': '18:00'},
            'wednesday': {'open': '08:00', 'close': '18:00'},
            'thursday': {'open': '08:00', 'close': '18:00'},
            'friday': {'open': '08:00', 'close': '18:00'},
            'saturday': {'open': '09:00', 'close': '13:00'},
            'sunday': {'closed': True}
        }
    }
    
    # Include stats if requested
    if request.args.get('include_stats'):
        practice['stats'] = {
            'total_patients': 1250,
            'week_appointments': 45,
            'completion_rate': 95
        }
    
    return jsonify(practice)

@app.route('/practices', methods=['GET'])
def get_practices():
    """Get all practices"""
    practices = [
        {
            'practice_id': 'practice-001',
            'name': 'Riverside Medical Centre',
            'address': {
                'city': 'London',
                'postcode': 'SW1A 1AA'
            },
            'phone': '020 7123 4567'
        }
    ]
    
    return jsonify({'practices': practices})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f'Internal error: {error}')
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Set up environment for local development
    os.environ.setdefault('ENVIRONMENT', 'local')
    os.environ.setdefault('USE_LOCAL_DB', 'true')
    os.environ.setdefault('MOCK_AUTH', 'true')
    
    logger.info('Starting NHS Appointment Booking System - Local Development Server')
    logger.info(f'Environment: {os.getenv("ENVIRONMENT")}')
    logger.info(f'DynamoDB Endpoint: {os.getenv("DYNAMODB_ENDPOINT", "http://localhost:8000")}')
    logger.info('Server starting on http://localhost:5000')
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )

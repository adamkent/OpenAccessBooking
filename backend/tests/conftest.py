"""
Pytest configuration and fixtures for backend tests.
"""

import os
import sys
import pytest
from unittest.mock import MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Set test environment
os.environ['ENVIRONMENT'] = 'test'
os.environ['USE_LOCAL_AUTH'] = 'true'
os.environ['DYNAMODB_ENDPOINT'] = 'http://localhost:8000'
os.environ['AWS_REGION'] = 'eu-west-2'
os.environ['APPOINTMENTS_TABLE'] = 'test-appointments'
os.environ['PATIENTS_TABLE'] = 'test-patients'
os.environ['PRACTICES_TABLE'] = 'test-practices'
os.environ['AWS_ACCESS_KEY_ID'] = 'test'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'


@pytest.fixture
def mock_db():
    """Mock database manager."""
    db = MagicMock()
    db.create_item = MagicMock(return_value=True)
    db.get_item = MagicMock(return_value=None)
    db.query_items = MagicMock(return_value=[])
    db.update_item = MagicMock(return_value=True)
    db.delete_item = MagicMock(return_value=True)
    return db


@pytest.fixture
def sample_patient():
    """Sample patient data for testing."""
    return {
        'patient_id': 'test-patient-123',
        'email': 'test@example.com',
        'password': 'TestPass123!',
        'nhs_number': '9434765919',
        'first_name': 'Test',
        'last_name': 'User',
        'date_of_birth': '1990-01-01',
        'phone': '07123456789',
        'user_type': 'patient',
        'status': 'active'
    }


@pytest.fixture
def sample_appointment():
    """Sample appointment data for testing."""
    return {
        'appointment_id': 'test-appt-123',
        'patient_id': 'test-patient-123',
        'practice_id': 'test-practice-123',
        'appointment_type': 'gp_consultation',
        'appointment_date': '2024-12-01',
        'appointment_time': '10:00',
        'status': 'scheduled',
        'reason': 'Annual checkup'
    }


@pytest.fixture
def lambda_event():
    """Base Lambda event structure."""
    def _event(method='GET', path='/', body=None, headers=None):
        return {
            'httpMethod': method,
            'path': path,
            'body': body,
            'headers': headers or {},
            'queryStringParameters': {},
            'pathParameters': {}
        }
    return _event

#!/usr/bin/env python3
"""
Setup script for local development environment
Creates DynamoDB tables and seeds test data
"""

import os
import sys
import boto3
import json
import time
from datetime import datetime, timedelta
import uuid

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Set up environment variables first
def setup_environment():
    """Set up environment variables for local development"""
    os.environ.setdefault('ENVIRONMENT', 'local')
    os.environ.setdefault('DYNAMODB_ENDPOINT', 'http://localhost:8000')
    os.environ.setdefault('AWS_REGION', 'eu-west-2')
    os.environ.setdefault('AWS_ACCESS_KEY_ID', 'local')
    os.environ.setdefault('AWS_SECRET_ACCESS_KEY', 'local')
    os.environ.setdefault('APPOINTMENTS_TABLE', 'local-appointments')
    os.environ.setdefault('PATIENTS_TABLE', 'local-patients')
    os.environ.setdefault('PRACTICES_TABLE', 'local-practices')

# Call setup_environment before importing database
setup_environment()

from utils.database import DatabaseManager
from utils.validators import validate_nhs_number

def create_dynamodb_client():
    """Create DynamoDB client for local development"""
    return boto3.client(
        'dynamodb',
        endpoint_url=os.getenv('DYNAMODB_ENDPOINT'),
        region_name=os.getenv('AWS_REGION'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )

def create_tables():
    """Create DynamoDB tables for local development"""
    dynamodb = create_dynamodb_client()
    
    tables = [
        {
            'TableName': os.getenv('APPOINTMENTS_TABLE'),
            'KeySchema': [
                {'AttributeName': 'appointment_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'appointment_id', 'AttributeType': 'S'},
                {'AttributeName': 'patient_id', 'AttributeType': 'S'},
                {'AttributeName': 'practice_id', 'AttributeType': 'S'},
                {'AttributeName': 'appointment_date', 'AttributeType': 'S'},
                {'AttributeName': 'status', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'PatientIndex',
                    'KeySchema': [
                        {'AttributeName': 'patient_id', 'KeyType': 'HASH'},
                        {'AttributeName': 'appointment_date', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                },
                {
                    'IndexName': 'PracticeIndex',
                    'KeySchema': [
                        {'AttributeName': 'practice_id', 'KeyType': 'HASH'},
                        {'AttributeName': 'appointment_date', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                },
                {
                    'IndexName': 'StatusIndex',
                    'KeySchema': [
                        {'AttributeName': 'status', 'KeyType': 'HASH'},
                        {'AttributeName': 'appointment_date', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                }
            ],
            'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        },
        {
            'TableName': os.getenv('PATIENTS_TABLE'),
            'KeySchema': [
                {'AttributeName': 'patient_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'patient_id', 'AttributeType': 'S'},
                {'AttributeName': 'nhs_number', 'AttributeType': 'S'},
                {'AttributeName': 'email', 'AttributeType': 'S'},
                {'AttributeName': 'practice_id', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'NHSNumberIndex',
                    'KeySchema': [
                        {'AttributeName': 'nhs_number', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                },
                {
                    'IndexName': 'EmailIndex',
                    'KeySchema': [
                        {'AttributeName': 'email', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                },
                {
                    'IndexName': 'PracticePatientIndex',
                    'KeySchema': [
                        {'AttributeName': 'practice_id', 'KeyType': 'HASH'},
                        {'AttributeName': 'patient_id', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                }
            ],
            'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        },
        {
            'TableName': os.getenv('PRACTICES_TABLE'),
            'KeySchema': [
                {'AttributeName': 'practice_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'practice_id', 'AttributeType': 'S'},
                {'AttributeName': 'postcode', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'PostcodeIndex',
                    'KeySchema': [
                        {'AttributeName': 'postcode', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                }
            ],
            'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        }
    ]
    
    for table_config in tables:
        table_name = table_config['TableName']
        
        try:
            # Check if table exists
            dynamodb.describe_table(TableName=table_name)
            print(f"Table {table_name} already exists")
        except dynamodb.exceptions.ResourceNotFoundException:
            # Create table
            print(f"Creating table {table_name}...")
            dynamodb.create_table(**table_config)
            
            # Wait for table to be created
            waiter = dynamodb.get_waiter('table_exists')
            waiter.wait(TableName=table_name)
            print(f"Table {table_name} created successfully")
        except Exception as e:
            print(f"Error with table {table_name}: {e}")

def seed_test_data():
    """Seed database with test data"""
    db = DatabaseManager()
    
    # Test practice
    practice_data = {
        'practice_id': 'practice-001',
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
        },
        'postcode': 'SW1A 1AA'  # For GSI
    }
    
    print("Creating test practice...")
    db.create_item('practices', practice_data)
    
    # Test patients
    patients = [
        {
            'patient_id': 'patient-001',
            'first_name': 'John',
            'last_name': 'Smith',
            'nhs_number': '1234567890',
            'email': 'john.smith@email.com',
            'phone_number': '07123456789',
            'date_of_birth': '1980-01-15',
            'address': {
                'line1': '123 Main Street',
                'line2': '',
                'city': 'London',
                'postcode': 'SW1A 1AA'
            },
            'practice_id': 'practice-001',
            'emergency_contact': {
                'name': 'Jane Smith',
                'relationship': 'Spouse',
                'phone': '07987654321'
            },
            'medical_conditions': ['Hypertension'],
            'allergies': ['Penicillin'],
            'user_type': 'patient'
        },
        {
            'patient_id': 'patient-002',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'nhs_number': '0987654321',
            'email': 'jane.doe@email.com',
            'phone_number': '07987654321',
            'date_of_birth': '1975-06-20',
            'address': {
                'line1': '456 Oak Avenue',
                'line2': '',
                'city': 'London',
                'postcode': 'SW2B 2BB'
            },
            'practice_id': 'practice-001',
            'emergency_contact': {
                'name': 'Bob Doe',
                'relationship': 'Brother',
                'phone': '07123456789'
            },
            'medical_conditions': [],
            'allergies': [],
            'user_type': 'patient'
        },
        {
            'patient_id': 'patient-003',
            'first_name': 'Bob',
            'last_name': 'Wilson',
            'nhs_number': '1122334455',
            'email': 'bob.wilson@email.com',
            'phone_number': '07555666777',
            'date_of_birth': '1990-12-10',
            'address': {
                'line1': '789 Pine Road',
                'line2': 'Flat 2B',
                'city': 'London',
                'postcode': 'SW3C 3CC'
            },
            'practice_id': 'practice-001',
            'emergency_contact': {
                'name': 'Sarah Wilson',
                'relationship': 'Mother',
                'phone': '07444555666'
            },
            'medical_conditions': ['Asthma'],
            'allergies': ['Nuts'],
            'user_type': 'patient'
        }
    ]
    
    print("Creating test patients...")
    for patient in patients:
        db.create_item('patients', patient)
    
    # Test staff (stored in patients table with different user_type)
    staff = [
        {
            'patient_id': 'staff-001',
            'first_name': 'Dr. Sarah',
            'last_name': 'Jones',
            'email': 'dr.sarah.jones@riverside.nhs.uk',
            'phone_number': '020 7123 4567',
            'practice_id': 'practice-001',
            'user_type': 'staff',
            'role': 'doctor',
            'specialization': 'General Practice',
            'gmc_number': 'GMC123456'
        },
        {
            'patient_id': 'staff-002',
            'first_name': 'Nurse Mary',
            'last_name': 'Brown',
            'email': 'nurse.mary.brown@riverside.nhs.uk',
            'phone_number': '020 7123 4568',
            'practice_id': 'practice-001',
            'user_type': 'staff',
            'role': 'nurse',
            'nmc_number': 'NMC789012'
        }
    ]
    
    print("Creating test staff...")
    for staff_member in staff:
        db.create_item('patients', staff_member)
    
    # Test appointments
    today = datetime.now()
    appointments = []
    
    # Create appointments for the next 30 days
    for i in range(30):
        appointment_date = (today + timedelta(days=i)).strftime('%Y-%m-%d')
        
        # Create 2-3 appointments per day
        for j in range(2 if i % 3 == 0 else 3):
            appointment_time = f"{9 + j * 2}:00"
            appointment_id = str(uuid.uuid4())
            
            # Vary patient and status
            patient_id = f"patient-{(i + j) % 3 + 1:03d}"
            statuses = ['scheduled', 'completed', 'cancelled']
            status = statuses[0] if i >= 0 else statuses[(i + j) % 3]
            
            appointment = {
                'appointment_id': appointment_id,
                'patient_id': patient_id,
                'practice_id': 'practice-001',
                'appointment_date': appointment_date,
                'appointment_time': appointment_time,
                'duration': 30,
                'type': ['consultation', 'check-up', 'vaccination'][j % 3],
                'reason': ['General consultation', 'Annual check-up', 'Flu vaccination'][j % 3],
                'status': status,
                'staff_id': 'staff-001' if j % 2 == 0 else 'staff-002',
                'notes': f'Test appointment {i+1}-{j+1}',
                'created_at': (today - timedelta(days=i+1)).isoformat(),
                'updated_at': (today - timedelta(days=i)).isoformat()
            }
            
            appointments.append(appointment)
    
    print(f"Creating {len(appointments)} test appointments...")
    for appointment in appointments:
        db.create_item('appointments', appointment)
    
    print("Test data seeded successfully!")

def main():
    """Main setup function"""
    print("Setting up NHS Appointment Booking System - Local Development")
    print("=" * 60)
    
    # Setup environment
    setup_environment()
    
    # Wait for DynamoDB to be ready
    print("Waiting for DynamoDB to be ready...")
    dynamodb = create_dynamodb_client()
    
    max_retries = 30
    for i in range(max_retries):
        try:
            dynamodb.list_tables()
            print("DynamoDB is ready!")
            break
        except Exception as e:
            if i == max_retries - 1:
                print(f"Failed to connect to DynamoDB: {e}")
                print("Make sure DynamoDB Local is running on http://localhost:8000")
                sys.exit(1)
            print(f"Waiting for DynamoDB... ({i+1}/{max_retries})")
            time.sleep(2)
    
    # Create tables
    print("\nCreating DynamoDB tables...")
    create_tables()
    
    # Seed test data
    print("\nSeeding test data...")
    seed_test_data()
    
    print("\n" + "=" * 60)
    print("Local development setup complete!")
    print("\nNext steps:")
    print("1. Start the backend server: python app.py")
    print("2. Start the frontend server: cd ../frontend && npm start")
    print("3. Access the application at http://localhost:3000")
    print("\nTest accounts:")
    print("- Patient: john.smith@email.com / TestPass123!")
    print("- Staff: dr.sarah.jones@riverside.nhs.uk / StaffPass123!")

if __name__ == '__main__':
    main()

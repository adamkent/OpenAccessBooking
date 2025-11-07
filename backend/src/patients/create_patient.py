"""
AWS Lambda function for creating patient records.
Handles patient registration with NHS number validation and data integrity.
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any

# Import utilities
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from database import db
from utils.auth import require_auth
from responses import (
    created_response, bad_request_response, conflict_response,
    internal_error_response, handle_lambda_error
)
from utils.validators import validate_patient_data

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def process_medical_info(medical_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process medical information to support dual storage format.
    Handles both legacy string arrays and new coded medical data.
    """
    from datetime import datetime, timezone
    
    processed = {
        'allergies_legacy': [],
        'conditions_legacy': [],
        'medications_legacy': [],
        'allergies': [],
        'conditions': [],
        'medications': [],
        'notes': medical_data.get('notes', ''),
        'last_updated': datetime.now(timezone.utc).isoformat(),
        'data_source': 'user_entered'
    }
    
    # Handle legacy string format (backward compatibility)
    if 'allergies' in medical_data and isinstance(medical_data['allergies'], list):
        if medical_data['allergies'] and isinstance(medical_data['allergies'][0], str):
            # Legacy string format
            processed['allergies_legacy'] = medical_data['allergies']
            # Auto-convert to coded format with basic structure
            processed['allergies'] = [
                {
                    'display_text': allergy,
                    'code': None,
                    'system': None,
                    'verified': False,
                    'severity': None,
                    'reaction': [],
                    'onset_date': None
                }
                for allergy in medical_data['allergies']
            ]
        else:
            # New coded format
            processed['allergies'] = medical_data['allergies']
            # Extract display text for legacy compatibility
            processed['allergies_legacy'] = [
                item.get('display_text', '') for item in medical_data['allergies']
            ]
    
    # Handle conditions (same logic)
    if 'conditions' in medical_data and isinstance(medical_data['conditions'], list):
        if medical_data['conditions'] and isinstance(medical_data['conditions'][0], str):
            processed['conditions_legacy'] = medical_data['conditions']
            processed['conditions'] = [
                {
                    'display_text': condition,
                    'code': None,
                    'system': None,
                    'verified': False,
                    'clinical_status': 'active',
                    'onset_date': None,
                    'resolved_date': None
                }
                for condition in medical_data['conditions']
            ]
        else:
            processed['conditions'] = medical_data['conditions']
            processed['conditions_legacy'] = [
                item.get('display_text', '') for item in medical_data['conditions']
            ]
    
    # Handle medications (same logic)
    if 'medications' in medical_data and isinstance(medical_data['medications'], list):
        if medical_data['medications'] and isinstance(medical_data['medications'][0], str):
            processed['medications_legacy'] = medical_data['medications']
            processed['medications'] = [
                {
                    'display_text': medication,
                    'code': None,
                    'system': None,
                    'verified': False,
                    'dosage': None,
                    'frequency': None,
                    'route': None,
                    'start_date': None,
                    'end_date': None,
                    'prescriber': None
                }
                for medication in medical_data['medications']
            ]
        else:
            processed['medications'] = medical_data['medications']
            processed['medications_legacy'] = [
                item.get('display_text', '') for item in medical_data['medications']
            ]
    
    # Handle explicit legacy fields if provided
    if 'allergies_legacy' in medical_data:
        processed['allergies_legacy'] = medical_data['allergies_legacy']
    if 'conditions_legacy' in medical_data:
        processed['conditions_legacy'] = medical_data['conditions_legacy']
    if 'medications_legacy' in medical_data:
        processed['medications_legacy'] = medical_data['medications_legacy']
    
    return processed

@handle_lambda_error
@require_auth(allowed_roles=['staff', 'admin', 'patient'])
def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Create a new patient record.
    
    Expected request body:
    {
        "first_name": "John",
        "last_name": "Smith",
        "date_of_birth": "1990-01-15",
        "email": "john.smith@email.com",
        "phone": "07123456789",
        "nhs_number": "1234567890",
        "address": {
            "line1": "123 Main Street",
            "line2": "Apartment 4B",
            "city": "London",
            "postcode": "SW1A 1AA",
            "country": "UK"
        },
        "emergency_contact": {
            "name": "Jane Smith",
            "relationship": "Spouse",
            "phone": "07987654321"
        },
        "medical_info": {
            "allergies_legacy": ["Penicillin"],
            "conditions_legacy": ["Diabetes Type 2"],
            "medications_legacy": ["Metformin 500mg"],
            "allergies": [
                {
                    "display_text": "Penicillin allergy",
                    "severity": "moderate",
                    "reaction": ["rash", "swelling"]
                }
            ],
            "conditions": [
                {
                    "display_text": "Type 2 Diabetes Mellitus",
                    "clinical_status": "active",
                    "onset_date": "2020-03-15"
                }
            ],
            "medications": [
                {
                    "display_text": "Metformin 500mg",
                    "dosage": "500mg",
                    "frequency": "twice daily",
                    "route": "oral"
                }
            ]
        },
        "practice_id": "practice123",
        "preferred_gp_id": "gp456"
    }
    """
    
    try:
        # Parse request body
        if 'body' not in event:
            return bad_request_response("Request body is required")
        
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        user = event.get('user', {})
        
        # Validate input data
        validation_result = validate_patient_data(body)
        if not validation_result['valid']:
            return bad_request_response("Validation failed", validation_result['errors'])
        
        # Authorization check
        user_role = user.get('role')
        user_id = user.get('user_id')
        
        # If patient is creating their own record, ensure they can only create for themselves
        if user_role == 'patient':
            # For self-registration, use the authenticated user's ID
            patient_id = user_id
        else:
            # Staff/admin can create records for others
            patient_id = str(uuid.uuid4())
        
        # Check if patient with NHS number already exists
        if body.get('nhs_number'):
            existing_patient = check_existing_patient_by_nhs(body['nhs_number'])
            if existing_patient:
                return conflict_response("Patient with this NHS number already exists")
        
        # Check if patient with email already exists
        existing_patient_email = check_existing_patient_by_email(body['email'])
        if existing_patient_email:
            return conflict_response("Patient with this email already exists")
        
        # Create patient record
        patient_data = {
            'patient_id': patient_id,
            'first_name': body['first_name'].strip(),
            'last_name': body['last_name'].strip(),
            'date_of_birth': body['date_of_birth'],
            'email': body['email'].lower().strip(),
            'phone': body.get('phone', '').strip(),
            'nhs_number': body.get('nhs_number', '').strip(),
            'address': body.get('address', {}),
            'emergency_contact': body.get('emergency_contact', {}),
            'medical_info': process_medical_info(body.get('medical_info', {})),
            'practice_id': body.get('practice_id', ''),
            'preferred_gp_id': body.get('preferred_gp_id', ''),
            'registration_date': datetime.now(timezone.utc).isoformat(),
            'status': 'active',
            'created_by': user_id,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Verify practice exists if specified
        if patient_data['practice_id']:
            practice = db.get_item('practices', {'practice_id': patient_data['practice_id']})
            if not practice:
                return bad_request_response("Practice not found")
        
        # Create the patient record
        created_patient = db.create_item('patients', patient_data)
        
        # Remove sensitive information from response
        response_patient = created_patient.copy()
        if 'medical_info' in response_patient:
            # Only include medical info for staff/admin
            if user_role == 'patient':
                response_patient.pop('medical_info', None)
        
        logger.info(f"Patient created: {created_patient['patient_id']}")
        
        return created_response(
            response_patient,
            "Patient record created successfully"
        )
        
    except json.JSONDecodeError:
        return bad_request_response("Invalid JSON in request body")
    except Exception as e:
        logger.error(f"Error creating patient: {str(e)}")
        return internal_error_response("Failed to create patient record")

def check_existing_patient_by_nhs(nhs_number: str) -> Dict[str, Any]:
    """Check if a patient with the given NHS number already exists."""
    try:
        patients = db.query_items(
            'patients',
            index_name='NHSNumberIndex',
            key_condition='nhs_number = :nhs_number',
            expression_values={':nhs_number': nhs_number}
        )
        return patients[0] if patients else None
    except Exception as e:
        logger.error(f"Error checking existing patient by NHS number: {str(e)}")
        return None

def check_existing_patient_by_email(email: str) -> Dict[str, Any]:
    """Check if a patient with the given email already exists."""
    try:
        patients = db.scan_items(
            'patients',
            filter_expression='email = :email',
            expression_values={':email': email.lower().strip()}
        )
        return patients[0] if patients else None
    except Exception as e:
        logger.error(f"Error checking existing patient by email: {str(e)}")
        return None

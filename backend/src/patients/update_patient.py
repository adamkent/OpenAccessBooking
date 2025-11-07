"""
AWS Lambda function for updating patient records.
Handles patient data updates with dual storage medical information and proper authorization.
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
    success_response, bad_request_response, not_found_response,
    forbidden_response, internal_error_response, handle_lambda_error
)
from utils.validators import validate_patient_data

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def process_medical_info_update(medical_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process medical information updates to support dual storage format.
    Handles both legacy string arrays and new coded medical data.
    """
    processed = {
        'allergies_legacy': [],
        'conditions_legacy': [],
        'medications_legacy': [],
        'allergies': [],
        'conditions': [],
        'medications': [],
        'notes': medical_data.get('notes', ''),
        'last_updated': datetime.now(timezone.utc).isoformat(),
        'data_source': medical_data.get('data_source', 'user_entered')
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
@require_auth(allowed_roles=['patient', 'staff', 'admin'])
def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Update patient information.
    
    Path parameters:
    - patient_id: The ID of the patient to update
    
    Expected request body (all fields optional):
    {
        "first_name": "John",
        "last_name": "Smith",
        "email": "john.smith@email.com",
        "phone": "07123456789",
        "address": {
            "line1": "123 Main Street",
            "city": "London",
            "postcode": "SW1A 1AA"
        },
        "emergency_contact": {
            "name": "Jane Smith",
            "relationship": "Spouse",
            "phone": "07987654321"
        },
        "medical_info": {
            "allergies": [
                {
                    "display_text": "Penicillin allergy",
                    "severity": "moderate",
                    "reaction": ["rash", "swelling"]
                }
            ],
            "conditions": [...],
            "medications": [...],
            "notes": "Updated medical notes"
        }
    }
    """
    
    try:
        # Extract patient ID from path
        path_params = event.get('pathParameters') or {}
        patient_id = path_params.get('patient_id')
        
        if not patient_id:
            return bad_request_response("Patient ID is required")
        
        # Parse request body
        if 'body' not in event:
            return bad_request_response("Request body is required")
        
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        user = event.get('user', {})
        
        # Get existing patient record
        existing_patient = db.get_item('patients', {'patient_id': patient_id})
        if not existing_patient:
            return not_found_response("Patient not found")
        
        # Authorization check
        user_role = user.get('role')
        user_id = user.get('user_id')
        user_practice_id = user.get('practice_id')
        
        if user_role == 'patient':
            # Patients can only update their own records
            if patient_id != user_id:
                return forbidden_response("Patients can only update their own records")
        elif user_role in ['staff', 'admin']:
            # Staff can only update patients from their practice
            if existing_patient.get('practice_id') != user_practice_id:
                return forbidden_response("Staff can only update patients from their practice")
        
        # Prepare update data
        update_data = {}
        updatable_fields = [
            'first_name', 'last_name', 'email', 'phone', 'address', 
            'emergency_contact', 'preferred_gp_id'
        ]
        
        # Only staff/admin can update certain fields
        if user_role in ['staff', 'admin']:
            updatable_fields.extend(['practice_id', 'status'])
        
        # Process standard fields
        for field in updatable_fields:
            if field in body:
                if field in ['first_name', 'last_name', 'email']:
                    # Validate and clean string fields
                    value = str(body[field]).strip()
                    if value:
                        update_data[field] = value
                else:
                    update_data[field] = body[field]
        
        # Process medical information with dual storage
        if 'medical_info' in body and user_role in ['staff', 'admin']:
            # Only staff/admin can update medical information
            update_data['medical_info'] = process_medical_info_update(body['medical_info'])
        
        # Add update timestamp and user
        update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
        
        # Validate updated data
        if any(field in update_data for field in ['first_name', 'last_name', 'email']):
            # Create validation data by merging existing and new data
            validation_data = {**existing_patient, **update_data}
            validation_result = validate_patient_data(validation_data)
            if not validation_result['valid']:
                return bad_request_response("Validation failed", validation_result['errors'])
        
        # Update the patient record
        updated_patient = db.update_item('patients', {'patient_id': patient_id}, update_data)
        
        # Prepare response (exclude sensitive information based on user role)
        response_data = prepare_update_response(updated_patient, user_role)
        
        logger.info(f"Patient updated: {patient_id} by {user_id}")
        
        return success_response(response_data, "Patient updated successfully")
        
    except json.JSONDecodeError:
        return bad_request_response("Invalid JSON in request body")
    except Exception as e:
        logger.error(f"Error updating patient: {str(e)}")
        return internal_error_response("Failed to update patient record")

def prepare_update_response(patient: Dict[str, Any], user_role: str) -> Dict[str, Any]:
    """
    Prepare patient data for update response based on user role.
    """
    response_data = {
        'patient_id': patient['patient_id'],
        'first_name': patient['first_name'],
        'last_name': patient['last_name'],
        'email': patient['email'],
        'phone': patient.get('phone', ''),
        'address': patient.get('address', {}),
        'practice_id': patient.get('practice_id', ''),
        'preferred_gp_id': patient.get('preferred_gp_id', ''),
        'status': patient.get('status', 'active'),
        'updated_at': patient.get('updated_at')
    }
    
    # Include additional fields for staff/admin
    if user_role in ['staff', 'admin']:
        response_data.update({
            'nhs_number': patient.get('nhs_number', ''),
            'date_of_birth': patient.get('date_of_birth', ''),
            'emergency_contact': patient.get('emergency_contact', {}),
            'registration_date': patient.get('registration_date', ''),
            'medical_info': patient.get('medical_info', {})
        })
    
    return response_data

"""
AWS Lambda function for retrieving patient records.
Handles patient data retrieval with proper authorization and privacy controls.
"""

import json
import logging
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

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@handle_lambda_error
@require_auth(allowed_roles=['patient', 'staff', 'admin'])
def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Retrieve patient information.
    
    Path parameters:
    - patient_id: The ID of the patient to retrieve
    
    Query parameters:
    - include_medical: true/false (default: false) - Include medical information
    - include_appointments: true/false (default: false) - Include recent appointments
    """
    
    try:
        # Extract patient ID from path
        path_params = event.get('pathParameters') or {}
        patient_id = path_params.get('patient_id')
        
        if not patient_id:
            return bad_request_response("Patient ID is required")
        
        # Extract query parameters
        query_params = event.get('queryStringParameters') or {}
        include_medical = query_params.get('include_medical', 'false').lower() == 'true'
        include_appointments = query_params.get('include_appointments', 'false').lower() == 'true'
        
        user = event.get('user', {})
        
        # Get patient record
        patient = db.get_item('patients', {'patient_id': patient_id})
        if not patient:
            return not_found_response("Patient not found")
        
        # Authorization check
        user_role = user.get('role')
        user_id = user.get('user_id')
        user_practice_id = user.get('practice_id')
        
        if user_role == 'patient':
            # Patients can only view their own records
            if patient_id != user_id:
                return forbidden_response("Patients can only view their own records")
        elif user_role in ['staff', 'admin']:
            # Staff can only view patients from their practice
            if patient.get('practice_id') != user_practice_id:
                return forbidden_response("Staff can only view patients from their practice")
        
        # Prepare response data
        response_data = prepare_patient_response(
            patient, 
            user_role, 
            include_medical, 
            include_appointments
        )
        
        logger.info(f"Patient data retrieved: {patient_id} by {user_id}")
        
        return success_response(response_data)
        
    except Exception as e:
        logger.error(f"Error retrieving patient: {str(e)}")
        return internal_error_response("Failed to retrieve patient record")

def prepare_patient_response(
    patient: Dict[str, Any], 
    user_role: str, 
    include_medical: bool = False, 
    include_appointments: bool = False
) -> Dict[str, Any]:
    """
    Prepare patient data for response based on user role and requested information.
    """
    
    # Base patient information (always included)
    response_data = {
        'patient_id': patient['patient_id'],
        'first_name': patient['first_name'],
        'last_name': patient['last_name'],
        'date_of_birth': patient['date_of_birth'],
        'email': patient['email'],
        'phone': patient.get('phone', ''),
        'address': patient.get('address', {}),
        'practice_id': patient.get('practice_id', ''),
        'preferred_gp_id': patient.get('preferred_gp_id', ''),
        'registration_date': patient.get('registration_date', ''),
        'status': patient.get('status', 'active')
    }
    
    # NHS number - only for staff/admin or patient viewing their own record
    if user_role in ['staff', 'admin']:
        response_data['nhs_number'] = patient.get('nhs_number', '')
    
    # Emergency contact - only for staff/admin
    if user_role in ['staff', 'admin']:
        response_data['emergency_contact'] = patient.get('emergency_contact', {})
    
    # Medical information - only if requested and authorized
    if include_medical and user_role in ['staff', 'admin']:
        medical_info = patient.get('medical_info', {})
        response_data['medical_info'] = prepare_medical_info_response(medical_info)
    
    # Recent appointments - if requested
    if include_appointments:
        try:
            recent_appointments = get_recent_appointments(patient['patient_id'])
            response_data['recent_appointments'] = recent_appointments
        except Exception as e:
            logger.error(f"Error retrieving recent appointments: {str(e)}")
            response_data['recent_appointments'] = []
    
    return response_data

def prepare_medical_info_response(medical_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare medical information for response, handling both legacy and new formats.
    Returns comprehensive medical data with backward compatibility.
    """
    if not medical_info:
        return {
            'allergies_legacy': [],
            'conditions_legacy': [],
            'medications_legacy': [],
            'allergies': [],
            'conditions': [],
            'medications': [],
            'notes': '',
            'last_updated': None,
            'data_source': 'user_entered'
        }
    
    # Ensure all fields are present for API consistency
    response = {
        'allergies_legacy': medical_info.get('allergies_legacy', []),
        'conditions_legacy': medical_info.get('conditions_legacy', []),
        'medications_legacy': medical_info.get('medications_legacy', []),
        'allergies': medical_info.get('allergies', []),
        'conditions': medical_info.get('conditions', []),
        'medications': medical_info.get('medications', []),
        'notes': medical_info.get('notes', ''),
        'last_updated': medical_info.get('last_updated'),
        'data_source': medical_info.get('data_source', 'user_entered')
    }
    
    # If only legacy data exists, ensure coded fields are populated
    if not response['allergies'] and response['allergies_legacy']:
        response['allergies'] = [
            {
                'display_text': allergy,
                'code': None,
                'system': None,
                'verified': False,
                'severity': None,
                'reaction': [],
                'onset_date': None
            }
            for allergy in response['allergies_legacy']
        ]
    
    if not response['conditions'] and response['conditions_legacy']:
        response['conditions'] = [
            {
                'display_text': condition,
                'code': None,
                'system': None,
                'verified': False,
                'clinical_status': 'active',
                'onset_date': None,
                'resolved_date': None
            }
            for condition in response['conditions_legacy']
        ]
    
    if not response['medications'] and response['medications_legacy']:
        response['medications'] = [
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
            for medication in response['medications_legacy']
        ]
    
    return response

def get_recent_appointments(patient_id: str, limit: int = 10) -> list:
    """
    Get recent appointments for a patient.
    """
    try:
        from datetime import datetime, timezone, timedelta
        
        # Get appointments from the last 6 months
        start_date = (datetime.now(timezone.utc) - timedelta(days=180)).strftime('%Y-%m-%d')
        end_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
        appointments = db.query_items(
            'appointments',
            index_name='PatientIndex',
            key_condition='patient_id = :patient_id AND appointment_date BETWEEN :start_date AND :end_date',
            expression_values={
                ':patient_id': patient_id,
                ':start_date': start_date,
                ':end_date': end_date
            },
            limit=limit
        )
        
        # Sort by appointment datetime (most recent first)
        appointments.sort(
            key=lambda x: x.get('appointment_datetime', ''), 
            reverse=True
        )
        
        # Return simplified appointment data
        simplified_appointments = []
        for appt in appointments:
            simplified_appointments.append({
                'appointment_id': appt['appointment_id'],
                'appointment_datetime': appt['appointment_datetime'],
                'appointment_type': appt.get('appointment_type', ''),
                'status': appt.get('status', ''),
                'reason': appt.get('reason', ''),
                'practice_id': appt.get('practice_id', ''),
                'practitioner_id': appt.get('practitioner_id', '')
            })
        
        return simplified_appointments
        
    except Exception as e:
        logger.error(f"Error getting recent appointments: {str(e)}")
        return []

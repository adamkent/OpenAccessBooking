"""
AWS Lambda function for retrieving appointments.
Supports filtering by patient, practice, date range, and status.
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

# Import utilities
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from database import db
from utils.auth import require_auth
from responses import (
    success_response, bad_request_response, forbidden_response,
    internal_error_response, handle_lambda_error
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@handle_lambda_error
@require_auth(allowed_roles=['patient', 'staff', 'admin'])
def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Retrieve appointments based on query parameters.
    
    Query parameters:
    - patient_id: Filter by patient (patients can only see their own)
    - practice_id: Filter by practice (staff can only see their practice)
    - start_date: Start date for date range (YYYY-MM-DD)
    - end_date: End date for date range (YYYY-MM-DD)
    - status: Filter by status (scheduled, completed, cancelled)
    - limit: Maximum number of results (default: 50)
    """
    
    try:
        user = event.get('user', {})
        query_params = event.get('queryStringParameters') or {}
        
        # Extract query parameters
        patient_id = query_params.get('patient_id')
        practice_id = query_params.get('practice_id')
        start_date = query_params.get('start_date')
        end_date = query_params.get('end_date')
        status = query_params.get('status')
        limit = int(query_params.get('limit', 50))
        
        # Authorization checks
        user_role = user.get('role')
        user_id = user.get('user_id')
        user_practice_id = user.get('practice_id')
        
        if user_role == 'patient':
            # Patients can only see their own appointments
            if patient_id and patient_id != user_id:
                return forbidden_response("Patients can only view their own appointments")
            patient_id = user_id
            
        elif user_role in ['staff', 'admin']:
            # Staff can only see appointments for their practice
            if practice_id and practice_id != user_practice_id:
                return forbidden_response("Staff can only view appointments for their practice")
            if not practice_id:
                practice_id = user_practice_id
        
        # Set default date range if not provided
        if not start_date:
            start_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        if not end_date:
            end_date = (datetime.now(timezone.utc) + timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Retrieve appointments
        appointments = []
        
        if patient_id:
            # Query by patient
            appointments = get_appointments_by_patient(
                patient_id, start_date, end_date, status, limit
            )
        elif practice_id:
            # Query by practice
            appointments = get_appointments_by_practice(
                practice_id, start_date, end_date, status, limit
            )
        else:
            return bad_request_response("Either patient_id or practice_id must be specified")
        
        # Enrich appointments with patient/practice details
        enriched_appointments = enrich_appointments(appointments)
        
        logger.info(f"Retrieved {len(enriched_appointments)} appointments for user {user_id}")
        
        return success_response({
            'appointments': enriched_appointments,
            'total': len(enriched_appointments),
            'filters': {
                'patient_id': patient_id,
                'practice_id': practice_id,
                'start_date': start_date,
                'end_date': end_date,
                'status': status
            }
        })
        
    except ValueError as e:
        return bad_request_response(str(e))
    except Exception as e:
        logger.error(f"Error retrieving appointments: {str(e)}")
        return internal_error_response("Failed to retrieve appointments")

def get_appointments_by_patient(
    patient_id: str, 
    start_date: str, 
    end_date: str, 
    status: str = None, 
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Get appointments for a specific patient."""
    
    try:
        # Build the key condition for date range
        key_condition = 'patient_id = :patient_id'
        expression_values = {':patient_id': patient_id}
        
        if start_date and end_date:
            key_condition += ' AND appointment_date BETWEEN :start_date AND :end_date'
            expression_values.update({
                ':start_date': start_date,
                ':end_date': end_date
            })
        
        # Add status filter if specified
        filter_expression = None
        if status:
            filter_expression = '#status = :status'
            expression_values[':status'] = status
        
        appointments = db.query_items(
            'appointments',
            index_name='PatientIndex',
            key_condition=key_condition,
            expression_values=expression_values,
            filter_expression=filter_expression,
            limit=limit
        )
        
        return appointments
        
    except Exception as e:
        logger.error(f"Error getting appointments by patient: {str(e)}")
        return []

def get_appointments_by_practice(
    practice_id: str, 
    start_date: str, 
    end_date: str, 
    status: str = None, 
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Get appointments for a specific practice."""
    
    try:
        # Build the key condition for date range
        key_condition = 'practice_id = :practice_id'
        expression_values = {':practice_id': practice_id}
        
        if start_date and end_date:
            key_condition += ' AND appointment_date BETWEEN :start_date AND :end_date'
            expression_values.update({
                ':start_date': start_date,
                ':end_date': end_date
            })
        
        # Add status filter if specified
        filter_expression = None
        if status:
            filter_expression = '#status = :status'
            expression_values[':status'] = status
        
        appointments = db.query_items(
            'appointments',
            index_name='PracticeIndex',
            key_condition=key_condition,
            expression_values=expression_values,
            filter_expression=filter_expression,
            limit=limit
        )
        
        return appointments
        
    except Exception as e:
        logger.error(f"Error getting appointments by practice: {str(e)}")
        return []

def enrich_appointments(appointments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Enrich appointments with patient and practice details."""
    
    enriched = []
    
    for appointment in appointments:
        try:
            # Get patient details
            patient = db.get_item('patients', {'patient_id': appointment['patient_id']})
            
            # Get practice details
            practice = db.get_item('practices', {'practice_id': appointment['practice_id']})
            
            # Create enriched appointment
            enriched_appointment = appointment.copy()
            
            if patient:
                enriched_appointment['patient'] = {
                    'first_name': patient.get('first_name'),
                    'last_name': patient.get('last_name'),
                    'nhs_number': patient.get('nhs_number'),
                    'date_of_birth': patient.get('date_of_birth')
                }
            
            if practice:
                enriched_appointment['practice'] = {
                    'name': practice.get('name'),
                    'address': practice.get('address'),
                    'phone': practice.get('phone')
                }
            
            enriched.append(enriched_appointment)
            
        except Exception as e:
            logger.error(f"Error enriching appointment {appointment.get('appointment_id')}: {str(e)}")
            # Include appointment without enrichment
            enriched.append(appointment)
    
    return enriched

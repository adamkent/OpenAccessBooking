"""
AWS Lambda function for creating new appointments.
Handles appointment booking with validation and conflict checking.
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
from utils.validators import validate_appointment_data

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@handle_lambda_error
@require_auth(allowed_roles=['patient', 'staff', 'admin'])
def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Create a new appointment.
    
    Expected request body:
    {
        "patient_id": "string",
        "practice_id": "string", 
        "practitioner_id": "string" (optional),
        "appointment_datetime": "2024-01-15T10:30:00Z",
        "appointment_type": "routine|urgent|follow_up|consultation|vaccination",
        "duration_minutes": 30,
        "reason": "string" (optional),
        "notes": "string" (optional)
    }
    """
    
    try:
        # Parse request body
        if 'body' not in event:
            return bad_request_response("Request body is required")
        
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        user = event.get('user', {})
        
        # Validate input data
        validation_result = validate_appointment_data(body)
        if not validation_result['valid']:
            return bad_request_response("Validation failed", validation_result['errors'])
        
        # Extract appointment data
        appointment_data = {
            'appointment_id': str(uuid.uuid4()),
            'patient_id': body['patient_id'],
            'practice_id': body['practice_id'],
            'practitioner_id': body.get('practitioner_id'),
            'appointment_datetime': body['appointment_datetime'],
            'appointment_type': body['appointment_type'],
            'duration_minutes': body.get('duration_minutes', 30),
            'reason': body.get('reason', ''),
            'notes': body.get('notes', ''),
            'status': 'scheduled',
            'created_by': user.get('user_id'),
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Authorization check: patients can only book for themselves
        if user.get('role') == 'patient' and appointment_data['patient_id'] != user.get('user_id'):
            return bad_request_response("Patients can only book appointments for themselves")
        
        # Check for conflicts (same time slot)
        existing_appointments = check_appointment_conflicts(
            appointment_data['practice_id'],
            appointment_data['appointment_datetime'],
            appointment_data['duration_minutes'],
            appointment_data.get('practitioner_id')
        )
        
        if existing_appointments:
            return conflict_response("Time slot is already booked")
        
        # Verify patient exists
        patient = db.get_item('patients', {'patient_id': appointment_data['patient_id']})
        if not patient:
            return bad_request_response("Patient not found")
        
        # Verify practice exists
        practice = db.get_item('practices', {'practice_id': appointment_data['practice_id']})
        if not practice:
            return bad_request_response("Practice not found")
        
        # Create the appointment
        created_appointment = db.create_item('appointments', appointment_data)
        
        logger.info(f"Appointment created: {created_appointment['appointment_id']}")
        
        return created_response(
            created_appointment,
            "Appointment created successfully"
        )
        
    except json.JSONDecodeError:
        return bad_request_response("Invalid JSON in request body")
    except Exception as e:
        logger.error(f"Error creating appointment: {str(e)}")
        return internal_error_response("Failed to create appointment")

def check_appointment_conflicts(
    practice_id: str, 
    appointment_datetime: str, 
    duration_minutes: int,
    practitioner_id: str = None
) -> list:
    """
    Check for conflicting appointments at the same time.
    """
    try:
        # Parse the appointment datetime
        appt_time = datetime.fromisoformat(appointment_datetime.replace('Z', '+00:00'))
        
        # Create time window for conflict checking
        start_time = appt_time
        end_time = appt_time.replace(minute=appt_time.minute + duration_minutes)
        
        # Query appointments for the practice on the same date
        date_str = appt_time.strftime('%Y-%m-%d')
        
        existing_appointments = db.query_items(
            'appointments',
            index_name='PracticeIndex',
            key_condition='practice_id = :practice_id AND begins_with(appointment_date, :date)',
            expression_values={
                ':practice_id': practice_id,
                ':date': date_str
            }
        )
        
        conflicts = []
        for existing in existing_appointments:
            if existing.get('status') in ['cancelled', 'completed']:
                continue
                
            existing_time = datetime.fromisoformat(
                existing['appointment_datetime'].replace('Z', '+00:00')
            )
            existing_duration = existing.get('duration_minutes', 30)
            existing_end = existing_time.replace(
                minute=existing_time.minute + existing_duration
            )
            
            # Check for time overlap
            if (start_time < existing_end and end_time > existing_time):
                # If practitioner specified, only conflict if same practitioner
                if practitioner_id:
                    if existing.get('practitioner_id') == practitioner_id:
                        conflicts.append(existing)
                else:
                    # General practice conflict
                    conflicts.append(existing)
        
        return conflicts
        
    except Exception as e:
        logger.error(f"Error checking appointment conflicts: {str(e)}")
        return []  # Assume no conflicts on error to allow booking
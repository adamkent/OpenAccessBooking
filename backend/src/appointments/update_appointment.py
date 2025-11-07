"""
AWS Lambda function for updating existing appointments.
Handles appointment modifications with proper authorization and validation.
"""

import json
import logging
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
    forbidden_response, conflict_response, internal_error_response, handle_lambda_error
)
from utils.validators import validate_appointment_time

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@handle_lambda_error
@require_auth(allowed_roles=['patient', 'staff', 'admin'])
def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Update an existing appointment.
    
    Path parameters:
    - appointment_id: The ID of the appointment to update
    
    Request body (partial update supported):
    {
        "appointment_datetime": "2024-01-15T10:30:00Z",
        "appointment_type": "routine|urgent|follow_up|consultation|vaccination",
        "duration_minutes": 30,
        "reason": "string",
        "notes": "string",
        "status": "scheduled|completed|cancelled"
    }
    """
    
    try:
        # Extract appointment ID from path
        path_params = event.get('pathParameters') or {}
        appointment_id = path_params.get('appointment_id')
        
        if not appointment_id:
            return bad_request_response("Appointment ID is required")
        
        # Parse request body
        if 'body' not in event:
            return bad_request_response("Request body is required")
        
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        user = event.get('user', {})
        
        # Get existing appointment
        existing_appointment = db.get_item('appointments', {'appointment_id': appointment_id})
        if not existing_appointment:
            return not_found_response("Appointment not found")
        
        # Authorization check
        user_role = user.get('role')
        user_id = user.get('user_id')
        user_practice_id = user.get('practice_id')
        
        if user_role == 'patient':
            # Patients can only update their own appointments
            if existing_appointment['patient_id'] != user_id:
                return forbidden_response("Patients can only update their own appointments")
        elif user_role in ['staff', 'admin']:
            # Staff can only update appointments for their practice
            if existing_appointment['practice_id'] != user_practice_id:
                return forbidden_response("Staff can only update appointments for their practice")
        
        # Validate updatable fields
        updatable_fields = [
            'appointment_datetime', 'appointment_type', 'duration_minutes',
            'reason', 'notes', 'status', 'practitioner_id'
        ]
        
        update_data = {}
        for field in updatable_fields:
            if field in body:
                update_data[field] = body[field]
        
        if not update_data:
            return bad_request_response("No valid fields to update")
        
        # Validate specific fields
        errors = {}
        
        # Validate appointment datetime if being updated
        if 'appointment_datetime' in update_data:
            time_validation = validate_appointment_time(update_data['appointment_datetime'])
            if not time_validation['valid']:
                errors['appointment_datetime'] = time_validation['errors']
        
        # Validate appointment type
        if 'appointment_type' in update_data:
            valid_types = ['routine', 'urgent', 'follow_up', 'consultation', 'vaccination']
            if update_data['appointment_type'] not in valid_types:
                errors['appointment_type'] = f'Must be one of: {", ".join(valid_types)}'
        
        # Validate status
        if 'status' in update_data:
            valid_statuses = ['scheduled', 'completed', 'cancelled', 'no_show']
            if update_data['status'] not in valid_statuses:
                errors['status'] = f'Must be one of: {", ".join(valid_statuses)}'
        
        # Validate duration
        if 'duration_minutes' in update_data:
            try:
                duration = int(update_data['duration_minutes'])
                if duration < 5 or duration > 120:
                    errors['duration_minutes'] = 'Duration must be between 5 and 120 minutes'
            except (ValueError, TypeError):
                errors['duration_minutes'] = 'Duration must be a number'
        
        if errors:
            return bad_request_response("Validation failed", errors)
        
        # Check for scheduling conflicts if datetime is being changed
        if 'appointment_datetime' in update_data:
            conflicts = check_appointment_conflicts(
                existing_appointment['practice_id'],
                update_data['appointment_datetime'],
                update_data.get('duration_minutes', existing_appointment.get('duration_minutes', 30)),
                update_data.get('practitioner_id', existing_appointment.get('practitioner_id')),
                exclude_appointment_id=appointment_id
            )
            
            if conflicts:
                return conflict_response("New time slot conflicts with existing appointment")
        
        # Build update expression
        update_expression_parts = []
        expression_values = {}
        
        for field, value in update_data.items():
            update_expression_parts.append(f"{field} = :{field}")
            expression_values[f":{field}"] = value
        
        update_expression = "SET " + ", ".join(update_expression_parts)
        
        # Update the appointment
        updated_appointment = db.update_item(
            'appointments',
            {'appointment_id': appointment_id},
            update_expression,
            expression_values
        )
        
        logger.info(f"Appointment updated: {appointment_id}")
        
        return success_response(
            updated_appointment,
            "Appointment updated successfully"
        )
        
    except json.JSONDecodeError:
        return bad_request_response("Invalid JSON in request body")
    except Exception as e:
        logger.error(f"Error updating appointment: {str(e)}")
        return internal_error_response("Failed to update appointment")

def check_appointment_conflicts(
    practice_id: str, 
    appointment_datetime: str, 
    duration_minutes: int,
    practitioner_id: str = None,
    exclude_appointment_id: str = None
) -> list:
    """
    Check for conflicting appointments, excluding the current appointment being updated.
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
            # Skip the appointment being updated
            if existing.get('appointment_id') == exclude_appointment_id:
                continue
                
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
        return []  # Assume no conflicts on error

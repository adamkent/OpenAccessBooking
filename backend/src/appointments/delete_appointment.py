"""
AWS Lambda function for deleting/cancelling appointments.
Handles appointment cancellation with proper authorization.
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
    forbidden_response, internal_error_response, handle_lambda_error
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@handle_lambda_error
@require_auth(allowed_roles=['patient', 'staff', 'admin'])
def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Cancel/delete an appointment.
    
    Path parameters:
    - appointment_id: The ID of the appointment to cancel
    
    Query parameters:
    - hard_delete: true/false (default: false) - Only admins can hard delete
    """
    
    try:
        # Extract appointment ID from path
        path_params = event.get('pathParameters') or {}
        appointment_id = path_params.get('appointment_id')
        
        if not appointment_id:
            return bad_request_response("Appointment ID is required")
        
        # Check for hard delete option
        query_params = event.get('queryStringParameters') or {}
        hard_delete = query_params.get('hard_delete', 'false').lower() == 'true'
        
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
            # Patients can only cancel their own appointments
            if existing_appointment['patient_id'] != user_id:
                return forbidden_response("Patients can only cancel their own appointments")
            
            # Patients cannot hard delete
            if hard_delete:
                return forbidden_response("Patients cannot permanently delete appointments")
                
        elif user_role == 'staff':
            # Staff can cancel appointments for their practice
            if existing_appointment['practice_id'] != user_practice_id:
                return forbidden_response("Staff can only cancel appointments for their practice")
            
            # Staff cannot hard delete
            if hard_delete:
                return forbidden_response("Staff cannot permanently delete appointments")
                
        elif user_role == 'admin':
            # Admins can cancel/delete any appointment in their practice
            if existing_appointment['practice_id'] != user_practice_id:
                return forbidden_response("Admins can only manage appointments for their practice")
        
        # Check if appointment is already cancelled
        if existing_appointment.get('status') == 'cancelled':
            return bad_request_response("Appointment is already cancelled")
        
        # Check if appointment is in the past and completed
        appointment_time = datetime.fromisoformat(
            existing_appointment['appointment_datetime'].replace('Z', '+00:00')
        )
        now = datetime.now(timezone.utc)
        
        if appointment_time < now and existing_appointment.get('status') == 'completed':
            return bad_request_response("Cannot cancel a completed appointment")
        
        if hard_delete:
            # Permanently delete the appointment (admin only)
            db.delete_item('appointments', {'appointment_id': appointment_id})
            
            logger.info(f"Appointment permanently deleted: {appointment_id} by {user_id}")
            
            return success_response(
                {'appointment_id': appointment_id},
                "Appointment permanently deleted"
            )
        else:
            # Soft delete - mark as cancelled
            updated_appointment = db.update_item(
                'appointments',
                {'appointment_id': appointment_id},
                'SET #status = :status, cancelled_at = :cancelled_at, cancelled_by = :cancelled_by',
                {
                    ':status': 'cancelled',
                    ':cancelled_at': datetime.now(timezone.utc).isoformat(),
                    ':cancelled_by': user_id
                }
            )
            
            logger.info(f"Appointment cancelled: {appointment_id} by {user_id}")
            
            return success_response(
                updated_appointment,
                "Appointment cancelled successfully"
            )
        
    except Exception as e:
        logger.error(f"Error deleting appointment: {str(e)}")
        return internal_error_response("Failed to cancel appointment")

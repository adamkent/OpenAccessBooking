"""
AWS Lambda function for retrieving practice information.
Handles practice data retrieval for patients and staff.
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
    internal_error_response, handle_lambda_error
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@handle_lambda_error
@require_auth(allowed_roles=['patient', 'staff', 'admin'])
def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Retrieve practice information.
    
    Path parameters:
    - practice_id: The ID of the practice to retrieve
    
    Query parameters:
    - include_staff: true/false (default: false) - Include staff information
    - include_schedule: true/false (default: false) - Include practice schedule
    """
    
    try:
        # Extract practice ID from path
        path_params = event.get('pathParameters') or {}
        practice_id = path_params.get('practice_id')
        
        if not practice_id:
            return bad_request_response("Practice ID is required")
        
        # Extract query parameters
        query_params = event.get('queryStringParameters') or {}
        include_staff = query_params.get('include_staff', 'false').lower() == 'true'
        include_schedule = query_params.get('include_schedule', 'false').lower() == 'true'
        
        user = event.get('user', {})
        
        # Get practice record
        practice = db.get_item('practices', {'practice_id': practice_id})
        if not practice:
            return not_found_response("Practice not found")
        
        # Prepare response data
        response_data = prepare_practice_response(
            practice, 
            user.get('role'), 
            include_staff, 
            include_schedule
        )
        
        logger.info(f"Practice data retrieved: {practice_id} by {user.get('user_id')}")
        
        return success_response(response_data)
        
    except Exception as e:
        logger.error(f"Error retrieving practice: {str(e)}")
        return internal_error_response("Failed to retrieve practice information")

def prepare_practice_response(
    practice: Dict[str, Any], 
    user_role: str, 
    include_staff: bool = False, 
    include_schedule: bool = False
) -> Dict[str, Any]:
    """
    Prepare practice data for response based on user role and requested information.
    """
    
    # Base practice information (always included)
    response_data = {
        'practice_id': practice['practice_id'],
        'name': practice['name'],
        'address': practice.get('address', {}),
        'phone': practice.get('phone', ''),
        'email': practice.get('email', ''),
        'website': practice.get('website', ''),
        'services': practice.get('services', []),
        'opening_hours': practice.get('opening_hours', {}),
        'status': practice.get('status', 'active')
    }
    
    # Additional information for staff/admin
    if user_role in ['staff', 'admin']:
        response_data.update({
            'registration_number': practice.get('registration_number', ''),
            'ccg_code': practice.get('ccg_code', ''),
            'ods_code': practice.get('ods_code', ''),
            'created_at': practice.get('created_at', ''),
            'updated_at': practice.get('updated_at', '')
        })
    
    # Staff information - if requested and authorized
    if include_staff and user_role in ['staff', 'admin']:
        try:
            staff_list = get_practice_staff(practice['practice_id'])
            response_data['staff'] = staff_list
        except Exception as e:
            logger.error(f"Error retrieving practice staff: {str(e)}")
            response_data['staff'] = []
    
    # Practice schedule - if requested
    if include_schedule:
        response_data['schedule'] = practice.get('schedule', {})
    
    return response_data

def get_practice_staff(practice_id: str) -> list:
    """
    Get staff members for a practice.
    Note: This would typically query a separate staff/practitioners table
    """
    try:
        # For now, return mock data - in a real implementation,
        # this would query a practitioners/staff table
        staff_data = [
            {
                'practitioner_id': 'gp001',
                'name': 'Dr. Sarah Johnson',
                'role': 'GP',
                'specialties': ['General Practice', 'Women\'s Health'],
                'available_days': ['Monday', 'Tuesday', 'Wednesday', 'Friday'],
                'status': 'active'
            },
            {
                'practitioner_id': 'gp002',
                'name': 'Dr. Michael Brown',
                'role': 'GP',
                'specialties': ['General Practice', 'Diabetes Care'],
                'available_days': ['Tuesday', 'Wednesday', 'Thursday', 'Friday'],
                'status': 'active'
            }
        ]
        
        return staff_data
        
    except Exception as e:
        logger.error(f"Error getting practice staff: {str(e)}")
        return []

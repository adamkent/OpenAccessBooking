"""
AWS Lambda function for user authentication and registration.
Handles login, registration, and token management with AWS Cognito.
"""

import json
import logging
from typing import Dict, Any

# Import utilities
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from database import db
from responses import (
    success_response, created_response, bad_request_response,
    unauthorized_response, internal_error_response, handle_lambda_error
)
from utils.validators import validate_email, validate_nhs_number
import uuid
from datetime import datetime, timezone
import jwt

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@handle_lambda_error
def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Handle authentication requests (login and registration).
    Routes based on the HTTP path.
    """
    
    try:
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        
        if path.endswith('/auth/login') and http_method == 'POST':
            return handle_login(event)
        elif path.endswith('/auth/register') and http_method == 'POST':
            return handle_register(event)
        else:
            return bad_request_response("Invalid endpoint or method")
            
    except Exception as e:
        logger.error(f"Error in auth handler: {str(e)}")
        return internal_error_response("Authentication service error")

def handle_login(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle user login.
    
    Expected request body:
    {
        "email": "user@example.com",
        "password": "password123"
    }
    """
    
    try:
        if 'body' not in event:
            return bad_request_response("Request body is required")
        
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        
        # Validate required fields
        email = body.get('email', '').strip().lower()
        password = body.get('password', '')
        
        if not email or not password:
            return bad_request_response("Email and password are required")
        
        if not validate_email(email):
            return bad_request_response("Invalid email format")
        
        # Local dev: simple DynamoDB auth
        if os.getenv('USE_LOCAL_AUTH') == 'true':
            try:
                users = db.query_items(
                    'patients',
                    index_name='EmailIndex',
                    key_condition='email = :email',
                    expression_values={':email': email}
                )
                
                if not users or users[0].get('password') != password:
                    return unauthorized_response("Invalid email or password")
                
                user = users[0]
                token = jwt.encode({
                    'sub': user['patient_id'],
                    'email': user['email'],
                    'user_type': user.get('user_type', 'patient'),
                    'exp': int((datetime.now(timezone.utc).timestamp() + 86400))
                }, 'local-dev-secret', algorithm='HS256')
                
                user_type = user.get('user_type', 'patient')
                response_data = {
                    'access_token': token,
                    'id_token': token,
                    'refresh_token': token,
                    'user': {
                        'user_id': user['patient_id'],
                        'email': user['email'],
                        'user_type': user_type,
                        'role': user_type,  # Frontend expects 'role'
                        'first_name': user.get('first_name', ''),
                        'last_name': user.get('last_name', '')
                    }
                }
                
                logger.info(f"User logged in successfully: {email}")
                return success_response(response_data, "Login successful")
                
            except Exception as e:
                logger.error(f"Authentication failed for {email}: {str(e)}")
                return unauthorized_response("Invalid email or password")
        
        # AWS: use Cognito (TODO: implement when deploying)
        else:
            return internal_error_response("Cognito authentication not yet implemented")
            
    except json.JSONDecodeError:
        return bad_request_response("Invalid JSON in request body")
    except Exception as e:
        logger.error(f"Error in login handler: {str(e)}")
        return internal_error_response("Login failed")

def handle_register(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle user registration.
    
    Expected request body:
    {
        "email": "user@example.com",
        "password": "password123",
        "nhs_number": "1234567890" (optional),
        "role": "patient|staff|admin" (default: patient),
        "practice_id": "practice123" (required for staff/admin)
    }
    """
    
    try:
        if 'body' not in event:
            return bad_request_response("Request body is required")
        
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        
        # Extract and validate fields
        email = body.get('email', '').strip().lower()
        password = body.get('password', '')
        nhs_number = body.get('nhs_number', '').strip()
        role = body.get('role', 'patient').lower()
        practice_id = body.get('practice_id', '').strip()
        
        # Validation
        errors = {}
        
        if not email:
            errors['email'] = 'Email is required'
        elif not validate_email(email):
            errors['email'] = 'Invalid email format'
        
        if not password:
            errors['password'] = 'Password is required'
        elif len(password) < 8:
            errors['password'] = 'Password must be at least 8 characters long'
        
        if nhs_number and not validate_nhs_number(nhs_number):
            errors['nhs_number'] = 'Invalid NHS number format'
        
        if role not in ['patient', 'staff', 'admin']:
            errors['role'] = 'Role must be patient, staff, or admin'
        
        if role in ['staff', 'admin'] and not practice_id:
            errors['practice_id'] = 'Practice ID is required for staff and admin users'
        
        if errors:
            return bad_request_response("Validation failed", errors)
        
        # Local dev: create user in DynamoDB
        if os.getenv('USE_LOCAL_AUTH') == 'true':
            try:
                # Check if user exists
                try:
                    existing = db.query_items(
                        'patients',
                        index_name='EmailIndex',
                        key_condition='email = :email',
                        expression_values={':email': email}
                    )
                    if existing:
                        return bad_request_response("User with this email already exists")
                except:
                    pass  # Index might not exist
                
                patient_id = str(uuid.uuid4())
                body_data = json.loads(event.get('body', '{}'))
                
                new_patient = {
                    'patient_id': patient_id,
                    'email': email,
                    'password': password,
                    'nhs_number': nhs_number or '',
                    'first_name': body_data.get('first_name', ''),
                    'last_name': body_data.get('last_name', ''),
                    'date_of_birth': body_data.get('date_of_birth', ''),
                    'phone': body_data.get('phone_number', ''),
                    'user_type': role,
                    'practice_id': practice_id or '',
                    'address': body_data.get('address', {}),
                    'emergency_contact': body_data.get('emergency_contact', {}),
                    'medical_info': {
                        'allergies_legacy': [],
                        'conditions_legacy': [],
                        'medications_legacy': [],
                        'allergies': [],
                        'conditions': [],
                        'medications': [],
                        'notes': '',
                        'last_updated': datetime.now(timezone.utc).isoformat(),
                        'data_source': 'user_entered'
                    },
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'updated_at': datetime.now(timezone.utc).isoformat(),
                    'status': 'active'
                }
                
                db.create_item('patients', new_patient)
                
                logger.info(f"User registered successfully: {email}")
                return created_response({
                    'user_id': patient_id,
                    'email': email,
                    'role': role,
                    'message': 'Registration successful. You can now log in.'
                }, "User registered successfully")
                
            except Exception as e:
                logger.error(f"Registration failed for {email}: {str(e)}")
                return internal_error_response("Registration failed")
        
        # AWS: use Cognito (TODO: implement when deploying)
        else:
            return internal_error_response("Cognito registration not yet implemented")
                
    except json.JSONDecodeError:
        return bad_request_response("Invalid JSON in request body")
    except Exception as e:
        logger.error(f"Error in registration handler: {str(e)}")
        return internal_error_response("Registration failed")

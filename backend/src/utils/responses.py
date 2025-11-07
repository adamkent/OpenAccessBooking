"""
Standard HTTP response utilities for Lambda functions.
Provides consistent response formatting across all API endpoints.
"""

import json
import logging
from typing import Any, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

def create_response(
    status_code: int,
    body: Any = None,
    headers: Optional[Dict[str, str]] = None,
    cors_enabled: bool = True
) -> Dict[str, Any]:
    """Create a standardized HTTP response for API Gateway."""
    
    default_headers = {
        'Content-Type': 'application/json'
    }
    
    if cors_enabled:
        default_headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        })
    
    if headers:
        default_headers.update(headers)
    
    response_body = body
    if body is not None and not isinstance(body, str):
        response_body = json.dumps(body, default=str)
    
    return {
        'statusCode': status_code,
        'headers': default_headers,
        'body': response_body or ''
    }

def success_response(data: Any = None, message: str = None) -> Dict[str, Any]:
    """Create a successful response (200)."""
    body = {}
    if data is not None:
        body['data'] = data
    if message:
        body['message'] = message
    body['timestamp'] = datetime.utcnow().isoformat()
    
    return create_response(200, body)

def created_response(data: Any = None, message: str = None) -> Dict[str, Any]:
    """Create a resource created response (201)."""
    body = {}
    if data is not None:
        body['data'] = data
    if message:
        body['message'] = message
    body['timestamp'] = datetime.utcnow().isoformat()
    
    return create_response(201, body)

def bad_request_response(message: str = "Bad request", errors: Any = None) -> Dict[str, Any]:
    """Create a bad request response (400)."""
    body = {
        'error': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    if errors:
        body['errors'] = errors
    
    return create_response(400, body)

def unauthorized_response(message: str = "Unauthorized") -> Dict[str, Any]:
    """Create an unauthorized response (401)."""
    body = {
        'error': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    return create_response(401, body)

def forbidden_response(message: str = "Forbidden") -> Dict[str, Any]:
    """Create a forbidden response (403)."""
    body = {
        'error': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    return create_response(403, body)

def not_found_response(message: str = "Resource not found") -> Dict[str, Any]:
    """Create a not found response (404)."""
    body = {
        'error': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    return create_response(404, body)

def conflict_response(message: str = "Conflict") -> Dict[str, Any]:
    """Create a conflict response (409)."""
    body = {
        'error': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    return create_response(409, body)

def internal_error_response(message: str = "Internal server error") -> Dict[str, Any]:
    """Create an internal server error response (500)."""
    body = {
        'error': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    return create_response(500, body)

def validation_error_response(errors: Dict[str, Any]) -> Dict[str, Any]:
    """Create a validation error response (422)."""
    body = {
        'error': 'Validation failed',
        'errors': errors,
        'timestamp': datetime.utcnow().isoformat()
    }
    return create_response(422, body)

def handle_lambda_error(func):
    """Decorator to handle common Lambda function errors."""
    def wrapper(event, context):
        try:
            return func(event, context)
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return bad_request_response(str(e))
        except PermissionError as e:
            logger.error(f"Permission error: {e}")
            return forbidden_response(str(e))
        except FileNotFoundError as e:
            logger.error(f"Resource not found: {e}")
            return not_found_response(str(e))
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return internal_error_response("An unexpected error occurred")
    
    return wrapper

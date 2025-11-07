"""
Authentication utilities for JWT token validation and user management.
Integrates with AWS Cognito for secure user authentication.
"""

import jwt
import boto3
import os
import logging
import requests
from typing import Dict, Optional, Any
from functools import wraps
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class AuthManager:
    """Handles JWT token validation and user authentication."""
    
    def __init__(self):
        self.cognito_client = boto3.client('cognito-idp', region_name=os.getenv('AWS_REGION', 'eu-west-2'))
        self.user_pool_id = os.getenv('USER_POOL_ID')
        self.client_id = os.getenv('USER_POOL_CLIENT_ID')
        self.region = os.getenv('AWS_REGION', 'eu-west-2')
        self._jwks = None
    
    def get_jwks(self) -> Dict[str, Any]:
        """Get JSON Web Key Set from Cognito."""
        if not self._jwks:
            jwks_url = f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}/.well-known/jwks.json"
            response = requests.get(jwks_url)
            self._jwks = response.json()
        return self._jwks
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token and return user claims."""
        try:
            # Get the key ID from token header
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header['kid']
            
            # Find the correct key
            jwks = self.get_jwks()
            key = None
            for jwk in jwks['keys']:
                if jwk['kid'] == kid:
                    key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)
                    break
            
            if not key:
                logger.error("Unable to find appropriate key")
                return None
            
            # Verify the token
            payload = jwt.decode(
                token,
                key,
                algorithms=['RS256'],
                audience=self.client_id,
                issuer=f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}"
            )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {e}")
            return None
    
    def get_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Extract user information from validated token."""
        payload = self.validate_token(token)
        if not payload:
            return None
        
        return {
            'user_id': payload.get('sub'),
            'email': payload.get('email'),
            'nhs_number': payload.get('custom:nhs_number'),
            'role': payload.get('custom:role', 'patient'),
            'practice_id': payload.get('custom:practice_id'),
            'username': payload.get('cognito:username')
        }
    
    def register_user(self, email: str, password: str, nhs_number: str = None, 
                     role: str = 'patient', practice_id: str = None) -> Dict[str, Any]:
        """Register a new user in Cognito."""
        try:
            user_attributes = [
                {'Name': 'email', 'Value': email},
                {'Name': 'email_verified', 'Value': 'true'}
            ]
            
            if nhs_number:
                user_attributes.append({'Name': 'custom:nhs_number', 'Value': nhs_number})
            
            user_attributes.append({'Name': 'custom:role', 'Value': role})
            
            if practice_id:
                user_attributes.append({'Name': 'custom:practice_id', 'Value': practice_id})
            
            response = self.cognito_client.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=email,
                UserAttributes=user_attributes,
                TemporaryPassword=password,
                MessageAction='SUPPRESS'
            )
            
            # Set permanent password
            self.cognito_client.admin_set_user_password(
                UserPoolId=self.user_pool_id,
                Username=email,
                Password=password,
                Permanent=True
            )
            
            logger.info(f"User registered successfully: {email}")
            return {'user_id': response['User']['Username'], 'email': email}
            
        except ClientError as e:
            logger.error(f"Error registering user: {e}")
            raise
    
    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user and return tokens."""
        try:
            response = self.cognito_client.admin_initiate_auth(
                UserPoolId=self.user_pool_id,
                ClientId=self.client_id,
                AuthFlow='ADMIN_NO_SRP_AUTH',
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password
                }
            )
            
            return {
                'access_token': response['AuthenticationResult']['AccessToken'],
                'id_token': response['AuthenticationResult']['IdToken'],
                'refresh_token': response['AuthenticationResult']['RefreshToken'],
                'expires_in': response['AuthenticationResult']['ExpiresIn']
            }
            
        except ClientError as e:
            logger.error(f"Authentication failed: {e}")
            raise

def require_auth(allowed_roles: list = None):
    """Decorator to require authentication for Lambda functions."""
    def decorator(func):
        @wraps(func)
        def wrapper(event, context):
            try:
                # Extract token from Authorization header
                auth_header = event.get('headers', {}).get('Authorization', '')
                if not auth_header.startswith('Bearer '):
                    return {
                        'statusCode': 401,
                        'body': '{"error": "Missing or invalid authorization header"}'
                    }
                
                token = auth_header.split(' ')[1]
                auth_manager = AuthManager()
                user = auth_manager.get_user_from_token(token)
                
                if not user:
                    return {
                        'statusCode': 401,
                        'body': '{"error": "Invalid token"}'
                    }
                
                # Check role if specified
                if allowed_roles and user.get('role') not in allowed_roles:
                    return {
                        'statusCode': 403,
                        'body': '{"error": "Insufficient permissions"}'
                    }
                
                # Add user to event for use in function
                event['user'] = user
                return func(event, context)
                
            except Exception as e:
                logger.error(f"Auth error: {e}")
                return {
                    'statusCode': 500,
                    'body': '{"error": "Internal server error"}'
                }
        return wrapper
    return decorator

# Global auth manager instance
auth = AuthManager()

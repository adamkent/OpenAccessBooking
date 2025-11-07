"""
Tests for authentication functions.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestLogin:
    """Test login functionality."""
    
    @patch('auth.auth.db')
    def test_login_success(self, mock_db, lambda_event, sample_patient):
        """Test successful login."""
        from auth.auth import handle_login
        
        # Mock database response
        mock_db.query_items.return_value = [sample_patient]
        
        event = lambda_event(
            method='POST',
            path='/auth/login',
            body=json.dumps({
                'email': 'test@example.com',
                'password': 'TestPass123!'
            })
        )
        
        response = handle_login(event)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'access_token' in body
        assert body['user']['email'] == 'test@example.com'
    
    @patch('auth.auth.db')
    def test_login_invalid_credentials(self, mock_db, lambda_event):
        """Test login with invalid credentials."""
        from auth.auth import handle_login
        
        # Mock no user found
        mock_db.query_items.return_value = []
        
        event = lambda_event(
            method='POST',
            path='/auth/login',
            body=json.dumps({
                'email': 'test@example.com',
                'password': 'WrongPassword'
            })
        )
        
        response = handle_login(event)
        
        assert response['statusCode'] == 401
    
    def test_login_missing_fields(self, lambda_event):
        """Test login with missing fields."""
        from auth.auth import handle_login
        
        event = lambda_event(
            method='POST',
            path='/auth/login',
            body=json.dumps({'email': 'test@example.com'})
        )
        
        response = handle_login(event)
        
        assert response['statusCode'] == 400


class TestRegistration:
    """Test registration functionality."""
    
    @patch('auth.auth.db')
    def test_register_success(self, mock_db, lambda_event):
        """Test successful registration."""
        from auth.auth import handle_register
        
        # Mock no existing user
        mock_db.query_items.return_value = []
        mock_db.create_item.return_value = True
        
        event = lambda_event(
            method='POST',
            path='/auth/register',
            body=json.dumps({
                'email': 'newuser@example.com',
                'password': 'TestPass123!',
                'nhs_number': '9434765919',
                'first_name': 'New',
                'last_name': 'User',
                'date_of_birth': '1990-01-01',
                'phone_number': '07123456789',
                'role': 'patient'
            })
        )
        
        response = handle_register(event)
        
        assert response['statusCode'] == 201
        body = json.loads(response['body'])
        assert body['email'] == 'newuser@example.com'
        assert 'user_id' in body
    
    @patch('auth.auth.db')
    def test_register_duplicate_email(self, mock_db, lambda_event, sample_patient):
        """Test registration with existing email."""
        from auth.auth import handle_register
        
        # Mock existing user
        mock_db.query_items.return_value = [sample_patient]
        
        event = lambda_event(
            method='POST',
            path='/auth/register',
            body=json.dumps({
                'email': 'test@example.com',
                'password': 'TestPass123!',
                'nhs_number': '9434765919',
                'first_name': 'Test',
                'last_name': 'User',
                'role': 'patient'
            })
        )
        
        response = handle_register(event)
        
        assert response['statusCode'] == 400
    
    def test_register_invalid_email(self, lambda_event):
        """Test registration with invalid email."""
        from auth.auth import handle_register
        
        event = lambda_event(
            method='POST',
            path='/auth/register',
            body=json.dumps({
                'email': 'invalid-email',
                'password': 'TestPass123!',
                'role': 'patient'
            })
        )
        
        response = handle_register(event)
        
        assert response['statusCode'] == 400
    
    def test_register_invalid_nhs_number(self, lambda_event):
        """Test registration with invalid NHS number."""
        from auth.auth import handle_register
        
        event = lambda_event(
            method='POST',
            path='/auth/register',
            body=json.dumps({
                'email': 'test@example.com',
                'password': 'TestPass123!',
                'nhs_number': '1234567890',  # Invalid
                'role': 'patient'
            })
        )
        
        response = handle_register(event)
        
        assert response['statusCode'] == 400

"""
Tests for patient functions.
"""

import pytest
import json
from unittest.mock import patch
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestGetPatient:
    """Test patient retrieval."""
    
    @patch('patients.get_patient.db')
    def test_get_patient_success(self, mock_db, lambda_event, sample_patient):
        """Test successful patient retrieval."""
        from patients.get_patient import lambda_handler
        
        mock_db.get_item.return_value = sample_patient
        
        event = lambda_event(
            method='GET',
            path='/patients/test-patient-123'
        )
        event['pathParameters'] = {'patient_id': 'test-patient-123'}
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['patient_id'] == 'test-patient-123'
    
    @patch('patients.get_patient.db')
    def test_get_nonexistent_patient(self, mock_db, lambda_event):
        """Test getting non-existent patient."""
        from patients.get_patient import lambda_handler
        
        mock_db.get_item.return_value = None
        
        event = lambda_event(
            method='GET',
            path='/patients/nonexistent'
        )
        event['pathParameters'] = {'patient_id': 'nonexistent'}
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 404


class TestUpdatePatient:
    """Test patient updates."""
    
    @patch('patients.update_patient.db')
    def test_update_patient_success(self, mock_db, lambda_event, sample_patient):
        """Test successful patient update."""
        from patients.update_patient import lambda_handler
        
        mock_db.get_item.return_value = sample_patient
        mock_db.update_item.return_value = {**sample_patient, 'phone': '07999888777'}
        
        event = lambda_event(
            method='PUT',
            path='/patients/test-patient-123',
            body=json.dumps({
                'phone': '07999888777'
            })
        )
        event['pathParameters'] = {'patient_id': 'test-patient-123'}
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 200
    
    def test_update_patient_invalid_phone(self, lambda_event):
        """Test patient update with invalid phone."""
        from patients.update_patient import lambda_handler
        
        event = lambda_event(
            method='PUT',
            path='/patients/test-patient-123',
            body=json.dumps({
                'phone': 'invalid'
            })
        )
        event['pathParameters'] = {'patient_id': 'test-patient-123'}
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 400

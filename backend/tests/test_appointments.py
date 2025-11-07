"""
Tests for appointment functions.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestCreateAppointment:
    """Test appointment creation."""
    
    @patch('appointments.create_appointment.db')
    def test_create_appointment_success(self, mock_db, lambda_event):
        """Test successful appointment creation."""
        from appointments.create_appointment import lambda_handler
        
        mock_db.create_item.return_value = True
        mock_db.get_item.return_value = {'practice_id': 'test-practice'}
        
        event = lambda_event(
            method='POST',
            path='/appointments',
            body=json.dumps({
                'patient_id': 'test-patient-123',
                'practice_id': 'test-practice-123',
                'appointment_type': 'gp_consultation',
                'appointment_date': '2024-12-01',
                'appointment_time': '10:00',
                'reason': 'Annual checkup'
            })
        )
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 201
        body = json.loads(response['body'])
        assert 'appointment_id' in body
    
    def test_create_appointment_missing_fields(self, lambda_event):
        """Test appointment creation with missing required fields."""
        from appointments.create_appointment import lambda_handler
        
        event = lambda_event(
            method='POST',
            path='/appointments',
            body=json.dumps({
                'patient_id': 'test-patient-123'
                # Missing required fields
            })
        )
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 400


class TestGetAppointments:
    """Test appointment retrieval."""
    
    @patch('appointments.get_appointments.db')
    def test_get_appointments_by_patient(self, mock_db, lambda_event, sample_appointment):
        """Test getting appointments for a patient."""
        from appointments.get_appointments import lambda_handler
        
        mock_db.query_items.return_value = [sample_appointment]
        
        event = lambda_event(
            method='GET',
            path='/appointments'
        )
        event['queryStringParameters'] = {'patient_id': 'test-patient-123'}
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'appointments' in body
        assert len(body['appointments']) > 0


class TestUpdateAppointment:
    """Test appointment updates."""
    
    @patch('appointments.update_appointment.db')
    def test_update_appointment_success(self, mock_db, lambda_event, sample_appointment):
        """Test successful appointment update."""
        from appointments.update_appointment import lambda_handler
        
        mock_db.get_item.return_value = sample_appointment
        mock_db.update_item.return_value = {**sample_appointment, 'status': 'cancelled'}
        
        event = lambda_event(
            method='PUT',
            path='/appointments/test-appt-123',
            body=json.dumps({
                'status': 'cancelled'
            })
        )
        event['pathParameters'] = {'appointment_id': 'test-appt-123'}
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 200
    
    @patch('appointments.update_appointment.db')
    def test_update_nonexistent_appointment(self, mock_db, lambda_event):
        """Test updating non-existent appointment."""
        from appointments.update_appointment import lambda_handler
        
        mock_db.get_item.return_value = None
        
        event = lambda_event(
            method='PUT',
            path='/appointments/nonexistent',
            body=json.dumps({'status': 'cancelled'})
        )
        event['pathParameters'] = {'appointment_id': 'nonexistent'}
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 404


class TestDeleteAppointment:
    """Test appointment deletion."""
    
    @patch('appointments.delete_appointment.db')
    def test_delete_appointment_success(self, mock_db, lambda_event, sample_appointment):
        """Test successful appointment deletion."""
        from appointments.delete_appointment import lambda_handler
        
        mock_db.get_item.return_value = sample_appointment
        mock_db.update_item.return_value = True
        
        event = lambda_event(
            method='DELETE',
            path='/appointments/test-appt-123'
        )
        event['pathParameters'] = {'appointment_id': 'test-appt-123'}
        
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 200

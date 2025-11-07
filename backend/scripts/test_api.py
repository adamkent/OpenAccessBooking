#!/usr/bin/env python3
"""
API testing script for NHS Appointment Booking System.
Tests all major endpoints with sample data.
"""

import requests
import json
import sys
import os
from datetime import datetime, timezone, timedelta
import argparse

class APITester:
    """Tests the NHS Appointment Booking API."""
    
    def __init__(self, api_url, verbose=False):
        self.api_url = api_url.rstrip('/')
        self.verbose = verbose
        self.access_token = None
        self.user_id = None
        self.test_results = []
    
    def log(self, message, level="INFO"):
        """Log messages with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def verbose_log(self, message):
        """Log verbose messages."""
        if self.verbose:
            self.log(message, "DEBUG")
    
    def make_request(self, method, endpoint, data=None, headers=None, auth_required=True):
        """Make HTTP request with error handling."""
        url = f"{self.api_url}{endpoint}"
        
        # Default headers
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)
        
        # Add authorization if required and available
        if auth_required and self.access_token:
            default_headers['Authorization'] = f'Bearer {self.access_token}'
        
        self.verbose_log(f"{method} {url}")
        if data and self.verbose:
            self.verbose_log(f"Request body: {json.dumps(data, indent=2)}")
        
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                headers=default_headers,
                timeout=30
            )
            
            self.verbose_log(f"Response status: {response.status_code}")
            if self.verbose and response.text:
                try:
                    response_json = response.json()
                    self.verbose_log(f"Response body: {json.dumps(response_json, indent=2)}")
                except:
                    self.verbose_log(f"Response body: {response.text}")
            
            return response
            
        except requests.exceptions.RequestException as e:
            self.log(f"Request failed: {e}", "ERROR")
            return None
    
    def test_user_registration(self):
        """Test user registration endpoint."""
        self.log("Testing user registration...")
        
        test_user = {
            "email": "test.patient@example.com",
            "password": "TestPass123!",
            "role": "patient"
        }
        
        response = self.make_request('POST', '/auth/register', test_user, auth_required=False)
        
        if response and response.status_code in [201, 400]:  # 400 if user already exists
            if response.status_code == 201:
                self.log("✓ User registration successful")
                self.test_results.append(("User Registration", "PASS"))
            else:
                self.log("ℹ User already exists (expected for repeated tests)")
                self.test_results.append(("User Registration", "SKIP"))
            return True
        else:
            self.log("✗ User registration failed", "ERROR")
            self.test_results.append(("User Registration", "FAIL"))
            return False
    
    def test_user_login(self):
        """Test user login endpoint."""
        self.log("Testing user login...")
        
        login_data = {
            "email": "test.patient@example.com",
            "password": "TestPass123!"
        }
        
        response = self.make_request('POST', '/auth/login', login_data, auth_required=False)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                self.access_token = data['data']['access_token']
                self.user_id = data['data']['user']['user_id']
                self.log("✓ User login successful")
                self.test_results.append(("User Login", "PASS"))
                return True
            except (KeyError, json.JSONDecodeError) as e:
                self.log(f"✗ Invalid login response format: {e}", "ERROR")
                self.test_results.append(("User Login", "FAIL"))
                return False
        else:
            self.log("✗ User login failed", "ERROR")
            self.test_results.append(("User Login", "FAIL"))
            return False
    
    def test_create_patient(self):
        """Test patient creation endpoint."""
        self.log("Testing patient creation...")
        
        patient_data = {
            "first_name": "Test",
            "last_name": "Patient",
            "date_of_birth": "1990-01-15",
            "email": "test.patient@example.com",
            "phone": "07123456789",
            "nhs_number": "9876543210",
            "address": {
                "line1": "123 Test Street",
                "city": "London",
                "postcode": "SW1A 1AA",
                "country": "UK"
            },
            "practice_id": "practice-001"
        }
        
        response = self.make_request('POST', '/patients', patient_data)
        
        if response and response.status_code in [201, 409]:  # 409 if patient already exists
            if response.status_code == 201:
                self.log("✓ Patient creation successful")
                self.test_results.append(("Patient Creation", "PASS"))
            else:
                self.log("ℹ Patient already exists (expected for repeated tests)")
                self.test_results.append(("Patient Creation", "SKIP"))
            return True
        else:
            self.log("✗ Patient creation failed", "ERROR")
            self.test_results.append(("Patient Creation", "FAIL"))
            return False
    
    def test_get_patient(self):
        """Test patient retrieval endpoint."""
        self.log("Testing patient retrieval...")
        
        if not self.user_id:
            self.log("✗ No user ID available for patient retrieval", "ERROR")
            self.test_results.append(("Patient Retrieval", "FAIL"))
            return False
        
        response = self.make_request('GET', f'/patients/{self.user_id}')
        
        if response and response.status_code == 200:
            self.log("✓ Patient retrieval successful")
            self.test_results.append(("Patient Retrieval", "PASS"))
            return True
        else:
            self.log("✗ Patient retrieval failed", "ERROR")
            self.test_results.append(("Patient Retrieval", "FAIL"))
            return False
    
    def test_create_appointment(self):
        """Test appointment creation endpoint."""
        self.log("Testing appointment creation...")
        
        if not self.user_id:
            self.log("✗ No user ID available for appointment creation", "ERROR")
            self.test_results.append(("Appointment Creation", "FAIL"))
            return False
        
        # Create appointment for tomorrow at 10:30 AM
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        appointment_time = tomorrow.replace(hour=10, minute=30, second=0, microsecond=0)
        
        appointment_data = {
            "patient_id": self.user_id,
            "practice_id": "practice-001",
            "appointment_datetime": appointment_time.isoformat(),
            "appointment_type": "routine",
            "duration_minutes": 30,
            "reason": "API test appointment"
        }
        
        response = self.make_request('POST', '/appointments', appointment_data)
        
        if response and response.status_code == 201:
            try:
                data = response.json()
                self.test_appointment_id = data['data']['appointment_id']
                self.log("✓ Appointment creation successful")
                self.test_results.append(("Appointment Creation", "PASS"))
                return True
            except (KeyError, json.JSONDecodeError):
                self.log("✗ Invalid appointment creation response", "ERROR")
                self.test_results.append(("Appointment Creation", "FAIL"))
                return False
        else:
            self.log("✗ Appointment creation failed", "ERROR")
            self.test_results.append(("Appointment Creation", "FAIL"))
            return False
    
    def test_get_appointments(self):
        """Test appointment retrieval endpoint."""
        self.log("Testing appointment retrieval...")
        
        if not self.user_id:
            self.log("✗ No user ID available for appointment retrieval", "ERROR")
            self.test_results.append(("Appointment Retrieval", "FAIL"))
            return False
        
        # Get appointments for the current user
        today = datetime.now().strftime('%Y-%m-%d')
        future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        response = self.make_request(
            'GET', 
            f'/appointments?patient_id={self.user_id}&start_date={today}&end_date={future_date}'
        )
        
        if response and response.status_code == 200:
            self.log("✓ Appointment retrieval successful")
            self.test_results.append(("Appointment Retrieval", "PASS"))
            return True
        else:
            self.log("✗ Appointment retrieval failed", "ERROR")
            self.test_results.append(("Appointment Retrieval", "FAIL"))
            return False
    
    def test_update_appointment(self):
        """Test appointment update endpoint."""
        self.log("Testing appointment update...")
        
        if not hasattr(self, 'test_appointment_id'):
            self.log("ℹ No test appointment available for update", "WARN")
            self.test_results.append(("Appointment Update", "SKIP"))
            return True
        
        update_data = {
            "reason": "Updated API test appointment",
            "notes": "This appointment was updated via API test"
        }
        
        response = self.make_request(
            'PUT', 
            f'/appointments/{self.test_appointment_id}', 
            update_data
        )
        
        if response and response.status_code == 200:
            self.log("✓ Appointment update successful")
            self.test_results.append(("Appointment Update", "PASS"))
            return True
        else:
            self.log("✗ Appointment update failed", "ERROR")
            self.test_results.append(("Appointment Update", "FAIL"))
            return False
    
    def test_cancel_appointment(self):
        """Test appointment cancellation endpoint."""
        self.log("Testing appointment cancellation...")
        
        if not hasattr(self, 'test_appointment_id'):
            self.log("ℹ No test appointment available for cancellation", "WARN")
            self.test_results.append(("Appointment Cancellation", "SKIP"))
            return True
        
        response = self.make_request('DELETE', f'/appointments/{self.test_appointment_id}')
        
        if response and response.status_code == 200:
            self.log("✓ Appointment cancellation successful")
            self.test_results.append(("Appointment Cancellation", "PASS"))
            return True
        else:
            self.log("✗ Appointment cancellation failed", "ERROR")
            self.test_results.append(("Appointment Cancellation", "FAIL"))
            return False
    
    def test_get_practice(self):
        """Test practice retrieval endpoint."""
        self.log("Testing practice retrieval...")
        
        response = self.make_request('GET', '/practices/practice-001')
        
        if response and response.status_code == 200:
            self.log("✓ Practice retrieval successful")
            self.test_results.append(("Practice Retrieval", "PASS"))
            return True
        else:
            self.log("✗ Practice retrieval failed", "ERROR")
            self.test_results.append(("Practice Retrieval", "FAIL"))
            return False
    
    def run_all_tests(self):
        """Run all API tests."""
        self.log("🚀 Starting NHS Appointment Booking API Tests")
        self.log("=" * 60)
        
        # Test sequence
        tests = [
            self.test_user_registration,
            self.test_user_login,
            self.test_create_patient,
            self.test_get_patient,
            self.test_get_practice,
            self.test_create_appointment,
            self.test_get_appointments,
            self.test_update_appointment,
            self.test_cancel_appointment
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log(f"✗ Test {test.__name__} failed with exception: {e}", "ERROR")
                self.test_results.append((test.__name__.replace('test_', '').replace('_', ' ').title(), "ERROR"))
            
            print()  # Add spacing between tests
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test results summary."""
        self.log("📊 Test Results Summary")
        self.log("=" * 60)
        
        passed = sum(1 for _, result in self.test_results if result == "PASS")
        failed = sum(1 for _, result in self.test_results if result == "FAIL")
        skipped = sum(1 for _, result in self.test_results if result == "SKIP")
        errors = sum(1 for _, result in self.test_results if result == "ERROR")
        
        for test_name, result in self.test_results:
            status_icon = {
                "PASS": "✓",
                "FAIL": "✗",
                "SKIP": "⊝",
                "ERROR": "⚠"
            }.get(result, "?")
            
            self.log(f"{status_icon} {test_name}: {result}")
        
        self.log("=" * 60)
        self.log(f"Total Tests: {len(self.test_results)}")
        self.log(f"Passed: {passed}")
        self.log(f"Failed: {failed}")
        self.log(f"Skipped: {skipped}")
        self.log(f"Errors: {errors}")
        
        if failed > 0 or errors > 0:
            self.log("❌ Some tests failed. Check the logs above for details.", "ERROR")
            return False
        else:
            self.log("✅ All tests passed successfully!")
            return True

def main():
    """Main function to run API tests."""
    parser = argparse.ArgumentParser(description='Test NHS Appointment Booking API')
    parser.add_argument('api_url', help='API Gateway URL (e.g., https://abc123.execute-api.eu-west-2.amazonaws.com/dev)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Validate URL
    if not args.api_url.startswith(('http://', 'https://')):
        print("❌ Error: API URL must start with http:// or https://")
        sys.exit(1)
    
    try:
        tester = APITester(args.api_url, args.verbose)
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⏹ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

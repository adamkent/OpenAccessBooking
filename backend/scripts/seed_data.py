#!/usr/bin/env python3
"""
Data seeding script for NHS Appointment Booking System.
Creates test data for development and testing purposes.
"""

import boto3
import json
import uuid
from datetime import datetime, timezone, timedelta
import os
import sys

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'utils'))

from database import DatabaseManager

class DataSeeder:
    """Seeds test data into DynamoDB tables."""
    
    def __init__(self, environment='dev'):
        self.environment = environment
        self.db = DatabaseManager()
        
        # Set table names based on environment
        os.environ['APPOINTMENTS_TABLE'] = f'{environment}-appointments'
        os.environ['PATIENTS_TABLE'] = f'{environment}-patients'
        os.environ['PRACTICES_TABLE'] = f'{environment}-practices'
    
    def seed_practices(self):
        """Create test GP practices."""
        practices = [
            {
                'practice_id': 'practice-001',
                'name': 'Riverside Medical Centre',
                'address': {
                    'line1': '123 High Street',
                    'city': 'London',
                    'postcode': 'SW1A 1AA',
                    'country': 'UK'
                },
                'phone': '020 7123 4567',
                'email': 'reception@riverside-medical.nhs.uk',
                'website': 'https://riverside-medical.nhs.uk',
                'registration_number': 'P12345',
                'ccg_code': 'CCG001',
                'ods_code': 'A12345',
                'services': [
                    'General Practice',
                    'Vaccinations',
                    'Health Checks',
                    'Minor Surgery',
                    'Family Planning'
                ],
                'opening_hours': {
                    'monday': '08:00-18:00',
                    'tuesday': '08:00-18:00',
                    'wednesday': '08:00-18:00',
                    'thursday': '08:00-18:00',
                    'friday': '08:00-18:00',
                    'saturday': 'Closed',
                    'sunday': 'Closed'
                },
                'status': 'active'
            },
            {
                'practice_id': 'practice-002',
                'name': 'Oakwood Family Practice',
                'address': {
                    'line1': '456 Oak Avenue',
                    'city': 'Manchester',
                    'postcode': 'M1 2AB',
                    'country': 'UK'
                },
                'phone': '0161 234 5678',
                'email': 'info@oakwood-practice.nhs.uk',
                'website': 'https://oakwood-practice.nhs.uk',
                'registration_number': 'P67890',
                'ccg_code': 'CCG002',
                'ods_code': 'B67890',
                'services': [
                    'General Practice',
                    'Chronic Disease Management',
                    'Mental Health Support',
                    'Travel Clinic',
                    'Physiotherapy'
                ],
                'opening_hours': {
                    'monday': '07:30-19:00',
                    'tuesday': '07:30-19:00',
                    'wednesday': '07:30-19:00',
                    'thursday': '07:30-19:00',
                    'friday': '07:30-18:00',
                    'saturday': '09:00-12:00',
                    'sunday': 'Closed'
                },
                'status': 'active'
            },
            {
                'practice_id': 'practice-003',
                'name': 'City Centre Health Hub',
                'address': {
                    'line1': '789 Market Square',
                    'city': 'Birmingham',
                    'postcode': 'B1 3CD',
                    'country': 'UK'
                },
                'phone': '0121 345 6789',
                'email': 'contact@citycentre-health.nhs.uk',
                'website': 'https://citycentre-health.nhs.uk',
                'registration_number': 'P11111',
                'ccg_code': 'CCG003',
                'ods_code': 'C11111',
                'services': [
                    'General Practice',
                    'Emergency Appointments',
                    'Sexual Health',
                    'Occupational Health',
                    'Specialist Clinics'
                ],
                'opening_hours': {
                    'monday': '08:00-20:00',
                    'tuesday': '08:00-20:00',
                    'wednesday': '08:00-20:00',
                    'thursday': '08:00-20:00',
                    'friday': '08:00-20:00',
                    'saturday': '10:00-16:00',
                    'sunday': '10:00-14:00'
                },
                'status': 'active'
            }
        ]
        
        for practice in practices:
            try:
                self.db.create_item('practices', practice)
                print(f"✓ Created practice: {practice['name']}")
            except Exception as e:
                print(f"✗ Error creating practice {practice['name']}: {e}")
    
    def seed_patients(self):
        """Create test patients."""
        patients = [
            {
                'patient_id': 'patient-001',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'date_of_birth': '1985-03-15',
                'email': 'sarah.johnson@email.com',
                'phone': '07123456789',
                'nhs_number': '9434765919',
                'address': {
                    'line1': '12 Victoria Street',
                    'city': 'London',
                    'postcode': 'SW1A 2BB',
                    'country': 'UK'
                },
                'emergency_contact': {
                    'name': 'David Johnson',
                    'relationship': 'Spouse',
                    'phone': '07987654321'
                },
                'medical_info': {
                    'allergies_legacy': ['Penicillin'],
                    'conditions_legacy': ['Asthma'],
                    'medications_legacy': ['Salbutamol inhaler'],
                    'allergies': [
                        {
                            'display_text': 'Penicillin allergy',
                            'severity': 'moderate',
                            'reaction': ['skin rash', 'itching'],
                            'onset_date': '2018-03-10'
                        }
                    ],
                    'conditions': [
                        {
                            'display_text': 'Asthma',
                            'clinical_status': 'active',
                            'onset_date': '2005-09-15'
                        }
                    ],
                    'medications': [
                        {
                            'display_text': 'Salbutamol inhaler',
                            'dosage': '100mcg per puff',
                            'frequency': 'as needed',
                            'route': 'inhalation',
                            'start_date': '2005-09-20',
                            'prescriber': 'Dr. Williams'
                        }
                    ],
                    'notes': 'Well-controlled asthma. Patient uses inhaler appropriately.',
                    'data_source': 'gp_records'
                },
                'practice_id': 'practice-001',
                'preferred_gp_id': 'gp-001',
                'registration_date': '2020-01-15',
                'status': 'active'
            },
            {
                'patient_id': 'patient-002',
                'first_name': 'Michael',
                'last_name': 'Brown',
                'date_of_birth': '1978-11-22',
                'email': 'michael.brown@email.com',
                'phone': '07234567890',
                'nhs_number': '4010232137',
                'address': {
                    'line1': '34 Elm Road',
                    'city': 'Manchester',
                    'postcode': 'M2 3CD',
                    'country': 'UK'
                },
                'emergency_contact': {
                    'name': 'Emma Brown',
                    'relationship': 'Wife',
                    'phone': '07876543210'
                },
                'medical_info': {
                    'allergies_legacy': [],
                    'conditions_legacy': ['Diabetes Type 2', 'Hypertension'],
                    'medications_legacy': ['Metformin 500mg', 'Lisinopril 10mg'],
                    'allergies': [],
                    'conditions': [
                        {
                            'display_text': 'Type 2 Diabetes Mellitus',
                            'clinical_status': 'active',
                            'onset_date': '2019-04-12'
                        },
                        {
                            'display_text': 'Essential Hypertension',
                            'clinical_status': 'active',
                            'onset_date': '2020-08-05'
                        }
                    ],
                    'medications': [
                        {
                            'display_text': 'Metformin 500mg',
                            'dosage': '500mg',
                            'frequency': 'twice daily with meals',
                            'route': 'oral',
                            'start_date': '2019-04-15',
                            'prescriber': 'Dr. Thompson'
                        },
                        {
                            'display_text': 'Lisinopril 10mg',
                            'dosage': '10mg',
                            'frequency': 'once daily',
                            'route': 'oral',
                            'start_date': '2020-08-10',
                            'prescriber': 'Dr. Thompson'
                        }
                    ],
                    'notes': 'Good diabetic control. Blood pressure well managed. Regular monitoring required.',
                    'data_source': 'gp_records'
                },
                'practice_id': 'practice-002',
                'preferred_gp_id': 'gp-002',
                'registration_date': '2019-06-10',
                'status': 'active'
            },
            {
                'patient_id': 'patient-003',
                'first_name': 'Emily',
                'last_name': 'Davis',
                'date_of_birth': '1992-07-08',
                'email': 'emily.davis@email.com',
                'phone': '07345678901',
                'nhs_number': '5990128088',
                'address': {
                    'line1': '56 Park Lane',
                    'city': 'Birmingham',
                    'postcode': 'B4 5EF',
                    'country': 'UK'
                },
                'emergency_contact': {
                    'name': 'Robert Davis',
                    'relationship': 'Father',
                    'phone': '07765432109'
                },
                'medical_info': {
                    'allergies_legacy': ['Nuts', 'Shellfish'],
                    'conditions_legacy': [],
                    'medications_legacy': [],
                    'allergies': [
                        {
                            'display_text': 'Tree nuts allergy',
                            'severity': 'severe',
                            'reaction': ['anaphylaxis', 'swelling'],
                            'onset_date': '2010-05-15'
                        },
                        {
                            'display_text': 'Shellfish allergy',
                            'severity': 'moderate',
                            'reaction': ['hives', 'nausea'],
                            'onset_date': '2015-08-20'
                        }
                    ],
                    'conditions': [],
                    'medications': [],
                    'notes': 'Patient carries EpiPen for severe allergic reactions',
                    'data_source': 'gp_records'
                },
                'practice_id': 'practice-003',
                'preferred_gp_id': 'gp-003',
                'registration_date': '2021-03-20',
                'status': 'active'
            },
            {
                'patient_id': 'patient-004',
                'first_name': 'James',
                'last_name': 'Wilson',
                'date_of_birth': '1965-12-03',
                'email': 'james.wilson@email.com',
                'phone': '07456789012',
                'nhs_number': '6304695787',
                'address': {
                    'line1': '78 Queen Street',
                    'city': 'London',
                    'postcode': 'SW1A 3GH',
                    'country': 'UK'
                },
                'emergency_contact': {
                    'name': 'Margaret Wilson',
                    'relationship': 'Wife',
                    'phone': '07654321098'
                },
                'medical_info': {
                    'allergies_legacy': ['Aspirin'],
                    'conditions_legacy': ['Arthritis', 'High Cholesterol'],
                    'medications_legacy': ['Ibuprofen 400mg', 'Atorvastatin 20mg'],
                    'allergies': [
                        {
                            'display_text': 'Aspirin allergy',
                            'severity': 'mild',
                            'reaction': ['stomach upset', 'nausea'],
                            'onset_date': '2018-02-10'
                        }
                    ],
                    'conditions': [
                        {
                            'display_text': 'Osteoarthritis',
                            'clinical_status': 'active',
                            'onset_date': '2015-06-12'
                        },
                        {
                            'display_text': 'Hypercholesterolemia',
                            'clinical_status': 'active',
                            'onset_date': '2017-09-08'
                        }
                    ],
                    'medications': [
                        {
                            'display_text': 'Ibuprofen 400mg',
                            'dosage': '400mg',
                            'frequency': 'three times daily',
                            'route': 'oral',
                            'start_date': '2015-06-15',
                            'prescriber': 'Dr. Smith'
                        },
                        {
                            'display_text': 'Atorvastatin 20mg',
                            'dosage': '20mg',
                            'frequency': 'once daily at bedtime',
                            'route': 'oral',
                            'start_date': '2017-09-15',
                            'prescriber': 'Dr. Johnson'
                        }
                    ],
                    'notes': 'Patient responds well to current medication regimen. Regular cholesterol monitoring required.',
                    'data_source': 'gp_records'
                },
                'practice_id': 'practice-001',
                'preferred_gp_id': 'gp-001',
                'registration_date': '2018-09-12',
                'status': 'active'
            }
        ]
        
        for patient in patients:
            try:
                self.db.create_item('patients', patient)
                print(f"✓ Created patient: {patient['first_name']} {patient['last_name']}")
            except Exception as e:
                print(f"✗ Error creating patient {patient['first_name']} {patient['last_name']}: {e}")
    
    def seed_appointments(self):
        """Create test appointments."""
        base_date = datetime.now(timezone.utc)
        
        appointments = []
        
        # Create appointments for the next 30 days
        for i in range(20):
            appointment_date = base_date + timedelta(days=(i % 30) + 1)
            appointment_time = appointment_date.replace(
                hour=9 + (i % 8),  # 9 AM to 4 PM
                minute=0 if i % 2 == 0 else 30,  # On the hour or half-hour
                second=0,
                microsecond=0
            )
            
            patient_id = f"patient-{str((i % 4) + 1).zfill(3)}"
            practice_id = f"practice-{str((i % 3) + 1).zfill(3)}"
            
            appointment = {
                'appointment_id': str(uuid.uuid4()),
                'patient_id': patient_id,
                'practice_id': practice_id,
                'practitioner_id': f"gp-{str((i % 3) + 1).zfill(3)}",
                'appointment_datetime': appointment_time.isoformat(),
                'appointment_date': appointment_time.strftime('%Y-%m-%d'),
                'appointment_type': ['routine', 'urgent', 'follow_up', 'consultation'][i % 4],
                'duration_minutes': 30 if i % 2 == 0 else 15,
                'reason': [
                    'Annual check-up',
                    'Blood pressure monitoring',
                    'Medication review',
                    'Vaccination',
                    'Follow-up consultation',
                    'Health screening'
                ][i % 6],
                'notes': f'Test appointment {i + 1}',
                'status': 'scheduled' if i < 15 else ['completed', 'cancelled'][i % 2],
                'created_by': patient_id,
                'created_at': base_date.isoformat(),
                'updated_at': base_date.isoformat()
            }
            
            appointments.append(appointment)
        
        for appointment in appointments:
            try:
                self.db.create_item('appointments', appointment)
                print(f"✓ Created appointment: {appointment['appointment_id'][:8]}... on {appointment['appointment_date']}")
            except Exception as e:
                print(f"✗ Error creating appointment: {e}")
    
    def seed_all(self):
        """Seed all test data."""
        print("🌱 Starting data seeding process...")
        print(f"Environment: {self.environment}")
        print("=" * 50)
        
        print("\n📍 Seeding practices...")
        self.seed_practices()
        
        print("\n👥 Seeding patients...")
        self.seed_patients()
        
        print("\n📅 Seeding appointments...")
        self.seed_appointments()
        
        print("\n" + "=" * 50)
        print("✅ Data seeding completed successfully!")
        print("\nTest data created:")
        print("- 3 GP practices")
        print("- 4 patients")
        print("- 20 appointments")
        print("\nYou can now test the API with this sample data.")

def main():
    """Main function to run data seeding."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Seed test data for NHS Appointment Booking System')
    parser.add_argument('--environment', '-e', default='dev', 
                       help='Environment to seed (default: dev)')
    parser.add_argument('--region', '-r', default='eu-west-2',
                       help='AWS region (default: eu-west-2)')
    
    args = parser.parse_args()
    
    # Set AWS region
    os.environ['AWS_REGION'] = args.region
    
    try:
        seeder = DataSeeder(args.environment)
        seeder.seed_all()
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

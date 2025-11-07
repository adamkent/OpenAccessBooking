"""
Data validation utilities for the NHS appointment booking system.
Provides validation for NHS numbers, dates, and other healthcare-specific data.
"""

import re
import validators
from datetime import datetime, date, timezone
from typing import Dict, List, Any, Optional

def validate_nhs_number(nhs_number: str) -> bool:
    """
    Validate NHS number using the official NHS number format and check digit algorithm.
    NHS numbers are 10 digits with a specific check digit calculation.
    """
    if not nhs_number or not isinstance(nhs_number, str):
        return False
    
    # Remove spaces and hyphens
    clean_number = re.sub(r'[\s-]', '', nhs_number)
    
    # Must be exactly 10 digits
    if not re.match(r'^\d{10}$', clean_number):
        return False
    
    # Calculate check digit (Modulus 11 algorithm)
    digits = [int(d) for d in clean_number[:9]]
    check_digit = int(clean_number[9])
    
    total = sum(digit * (10 - i) for i, digit in enumerate(digits))
    remainder = total % 11
    
    if remainder == 0:
        expected_check = 0
    elif remainder == 1:
        return False  # Invalid NHS number
    else:
        expected_check = 11 - remainder
    
    return check_digit == expected_check

def validate_email(email: str) -> bool:
    """Validate email address format."""
    if not email or not isinstance(email, str):
        return False
    return validators.email(email)

def validate_phone_number(phone: str) -> bool:
    """Validate UK phone number format."""
    if not phone or not isinstance(phone, str):
        return False
    
    # Remove spaces, hyphens, and brackets
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # UK phone number patterns
    uk_patterns = [
        r'^(\+44|0044|44)?[1-9]\d{8,9}$',  # Standard UK numbers
        r'^(\+44|0044|44)?7\d{9}$',        # Mobile numbers
        r'^(\+44|0044|44)?800\d{7}$',      # Freephone
        r'^(\+44|0044|44)?845\d{7}$',      # Local rate
    ]
    
    return any(re.match(pattern, clean_phone) for pattern in uk_patterns)

def validate_postcode(postcode: str) -> bool:
    """Validate UK postcode format."""
    if not postcode or not isinstance(postcode, str):
        return False
    
    # UK postcode pattern
    pattern = r'^[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}$'
    return bool(re.match(pattern, postcode.upper().strip()))

def validate_date_string(date_string: str, format: str = '%Y-%m-%d') -> bool:
    """Validate date string format."""
    if not date_string or not isinstance(date_string, str):
        return False
    
    try:
        datetime.strptime(date_string, format)
        return True
    except ValueError:
        return False

def validate_datetime_string(datetime_string: str) -> bool:
    """Validate ISO datetime string format."""
    if not datetime_string or not isinstance(datetime_string, str):
        return False
    
    try:
        datetime.fromisoformat(datetime_string.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False

def validate_appointment_time(appointment_datetime: str) -> Dict[str, Any]:
    """
    Validate appointment datetime with NHS-specific rules.
    Returns validation result with details.
    """
    result = {
        'valid': False,
        'errors': []
    }
    
    if not validate_datetime_string(appointment_datetime):
        result['errors'].append('Invalid datetime format')
        return result
    
    try:
        appt_time = datetime.fromisoformat(appointment_datetime.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        
        # Must be in the future
        if appt_time <= now:
            result['errors'].append('Appointment must be in the future')
        
        # Must be within reasonable booking window (e.g., 6 months)
        max_advance_days = 180
        if (appt_time - now).days > max_advance_days:
            result['errors'].append(f'Appointment cannot be more than {max_advance_days} days in advance')
        
        # Check if it's during typical GP hours (8 AM - 6 PM, Monday-Friday)
        if appt_time.weekday() >= 5:  # Saturday or Sunday
            result['errors'].append('Appointments are typically not available on weekends')
        
        hour = appt_time.hour
        if hour < 8 or hour >= 18:
            result['errors'].append('Appointments are typically available between 8 AM and 6 PM')
        
        # Must be on the hour or half-hour
        if appt_time.minute not in [0, 30]:
            result['errors'].append('Appointments must be scheduled on the hour or half-hour')
        
        result['valid'] = len(result['errors']) == 0
        
    except Exception as e:
        result['errors'].append(f'Error validating appointment time: {str(e)}')
    
    return result

def validate_patient_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate patient registration/update data."""
    result = {
        'valid': False,
        'errors': {}
    }
    
    required_fields = ['first_name', 'last_name', 'date_of_birth', 'email']
    
    # Check required fields
    for field in required_fields:
        if field not in data or not data[field]:
            result['errors'][field] = 'This field is required'
    
    # Validate email
    if 'email' in data and data['email']:
        if not validate_email(data['email']):
            result['errors']['email'] = 'Invalid email format'
    
    # Validate NHS number if provided
    if 'nhs_number' in data and data['nhs_number']:
        if not validate_nhs_number(data['nhs_number']):
            result['errors']['nhs_number'] = 'Invalid NHS number format'
    
    # Validate phone number if provided
    if 'phone' in data and data['phone']:
        if not validate_phone_number(data['phone']):
            result['errors']['phone'] = 'Invalid UK phone number format'
    
    # Validate postcode if provided
    if 'postcode' in data and data['postcode']:
        if not validate_postcode(data['postcode']):
            result['errors']['postcode'] = 'Invalid UK postcode format'
    
    # Validate date of birth
    if 'date_of_birth' in data and data['date_of_birth']:
        if not validate_date_string(data['date_of_birth']):
            result['errors']['date_of_birth'] = 'Invalid date format (YYYY-MM-DD expected)'
        else:
            try:
                dob = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
                today = date.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                
                if age < 0:
                    result['errors']['date_of_birth'] = 'Date of birth cannot be in the future'
                elif age > 150:
                    result['errors']['date_of_birth'] = 'Invalid date of birth'
            except ValueError:
                result['errors']['date_of_birth'] = 'Invalid date format'
    
    # Validate medical information if provided
    if 'medical_info' in data and data['medical_info']:
        medical_validation = validate_medical_info(data['medical_info'])
        if not medical_validation['valid']:
            result['errors']['medical_info'] = medical_validation['errors']
    
    result['valid'] = len(result['errors']) == 0
    return result

def validate_appointment_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate appointment booking data."""
    result = {
        'valid': False,
        'errors': {}
    }
    
    required_fields = ['patient_id', 'practice_id', 'appointment_datetime', 'appointment_type']
    
    # Check required fields
    for field in required_fields:
        if field not in data or not data[field]:
            result['errors'][field] = 'This field is required'
    
    # Validate appointment datetime
    if 'appointment_datetime' in data and data['appointment_datetime']:
        time_validation = validate_appointment_time(data['appointment_datetime'])
        if not time_validation['valid']:
            result['errors']['appointment_datetime'] = time_validation['errors']
    
    # Validate appointment type
    valid_types = ['routine', 'urgent', 'follow_up', 'consultation', 'vaccination']
    if 'appointment_type' in data and data['appointment_type']:
        if data['appointment_type'] not in valid_types:
            result['errors']['appointment_type'] = f'Must be one of: {", ".join(valid_types)}'
    
    # Validate duration if provided
    if 'duration_minutes' in data and data['duration_minutes']:
        try:
            duration = int(data['duration_minutes'])
            if duration < 5 or duration > 120:
                result['errors']['duration_minutes'] = 'Duration must be between 5 and 120 minutes'
        except (ValueError, TypeError):
            result['errors']['duration_minutes'] = 'Duration must be a number'
    
    result['valid'] = len(result['errors']) == 0
    return result

def validate_medical_info(medical_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate medical information with dual storage format support.
    """
    result = {
        'valid': True,
        'errors': {}
    }
    
    # Validate allergies
    if 'allergies' in medical_info:
        allergy_errors = validate_medical_items(
            medical_info['allergies'], 
            'allergy',
            ['severity', 'reaction', 'onset_date']
        )
        if allergy_errors:
            result['errors']['allergies'] = allergy_errors
    
    # Validate conditions
    if 'conditions' in medical_info:
        condition_errors = validate_medical_items(
            medical_info['conditions'],
            'condition', 
            ['clinical_status', 'onset_date', 'resolved_date']
        )
        if condition_errors:
            result['errors']['conditions'] = condition_errors
    
    # Validate medications
    if 'medications' in medical_info:
        medication_errors = validate_medical_items(
            medical_info['medications'],
            'medication',
            ['dosage', 'frequency', 'route', 'start_date', 'end_date', 'prescriber']
        )
        if medication_errors:
            result['errors']['medications'] = medication_errors
    
    # Validate notes length
    if 'notes' in medical_info and medical_info['notes']:
        if len(medical_info['notes']) > 2000:
            result['errors']['notes'] = 'Notes cannot exceed 2000 characters'
    
    result['valid'] = len(result['errors']) == 0
    return result

def validate_medical_items(items: list, item_type: str, optional_fields: list) -> list:
    """
    Validate a list of medical items (allergies, conditions, medications).
    """
    errors = []
    
    if not isinstance(items, list):
        return [f'{item_type.capitalize()} must be a list']
    
    for i, item in enumerate(items):
        item_errors = {}
        
        # Handle legacy string format
        if isinstance(item, str):
            if not item.strip():
                item_errors['display_text'] = 'Cannot be empty'
        # Handle new coded format
        elif isinstance(item, dict):
            # Validate required display_text
            if 'display_text' not in item or not item['display_text']:
                item_errors['display_text'] = 'Display text is required'
            elif len(item['display_text']) > 200:
                item_errors['display_text'] = 'Display text cannot exceed 200 characters'
            
            # Validate optional code fields
            if 'code' in item and item['code']:
                if len(item['code']) > 50:
                    item_errors['code'] = 'Code cannot exceed 50 characters'
            
            if 'system' in item and item['system']:
                if len(item['system']) > 100:
                    item_errors['system'] = 'System URI cannot exceed 100 characters'
            
            # Validate dates if present
            date_fields = ['onset_date', 'resolved_date', 'start_date', 'end_date']
            for date_field in date_fields:
                if date_field in item and item[date_field]:
                    if not validate_date_string(item[date_field]):
                        item_errors[date_field] = 'Invalid date format (YYYY-MM-DD expected)'
            
            # Validate severity for allergies
            if item_type == 'allergy' and 'severity' in item and item['severity']:
                valid_severities = ['mild', 'moderate', 'severe', 'life-threatening']
                if item['severity'] not in valid_severities:
                    item_errors['severity'] = f'Severity must be one of: {", ".join(valid_severities)}'
            
            # Validate clinical status for conditions
            if item_type == 'condition' and 'clinical_status' in item and item['clinical_status']:
                valid_statuses = ['active', 'resolved', 'inactive']
                if item['clinical_status'] not in valid_statuses:
                    item_errors['clinical_status'] = f'Clinical status must be one of: {", ".join(valid_statuses)}'
        else:
            item_errors['format'] = f'{item_type.capitalize()} must be a string or object'
        
        if item_errors:
            errors.append({f'{item_type}_{i}': item_errors})
    
    return errors

"""
Tests for validation functions.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'utils'))

from validators import (
    validate_email,
    validate_nhs_number,
    validate_phone_number,
    validate_postcode,
    validate_date_string
)


class TestEmailValidation:
    """Test email validation."""
    
    def test_valid_emails(self):
        assert validate_email('test@example.com') == True
        assert validate_email('user.name@domain.co.uk') == True
        assert validate_email('test+tag@gmail.com') == True
    
    def test_invalid_emails(self):
        assert validate_email('invalid') == False
        assert validate_email('test@') == False
        assert validate_email('@example.com') == False
        assert validate_email('') == False


class TestNHSNumberValidation:
    """Test NHS number validation with Modulus 11 algorithm."""
    
    def test_valid_nhs_numbers(self):
        assert validate_nhs_number('9434765919') == True
        assert validate_nhs_number('943 476 5919') == True
        assert validate_nhs_number('401 023 2137') == True
        assert validate_nhs_number('4010232137') == True
    
    def test_invalid_nhs_numbers(self):
        assert validate_nhs_number('1234567890') == False
        assert validate_nhs_number('123456789') == False  # Too short
        assert validate_nhs_number('12345678901') == False  # Too long
        assert validate_nhs_number('') == False
        assert validate_nhs_number('abcdefghij') == False
    
    def test_nhs_number_with_invalid_check_digit(self):
        assert validate_nhs_number('9434765918') == False  # Wrong check digit


class TestPhoneNumberValidation:
    """Test UK phone number validation."""
    
    def test_valid_phone_numbers(self):
        assert validate_phone_number('07123456789') == True
        assert validate_phone_number('07123 456789') == True
        assert validate_phone_number('+447123456789') == True
        assert validate_phone_number('020 7123 4567') == True
        assert validate_phone_number('01234567890') == True
    
    def test_invalid_phone_numbers(self):
        assert validate_phone_number('123') == False
        assert validate_phone_number('') == False
        assert validate_phone_number('abcdefghijk') == False
        assert validate_phone_number('9999999999') == False  # Invalid prefix


class TestPostcodeValidation:
    """Test UK postcode validation."""
    
    def test_valid_postcodes(self):
        assert validate_postcode('SW1A 1AA') == True
        assert validate_postcode('M1 1AE') == True
        assert validate_postcode('B33 8TH') == True
        assert validate_postcode('CR2 6XH') == True
        assert validate_postcode('DN55 1PT') == True
    
    def test_invalid_postcodes(self):
        assert validate_postcode('INVALID') == False
        assert validate_postcode('') == False
        assert validate_postcode('12345') == False


class TestDateValidation:
    """Test date string validation."""
    
    def test_valid_dates(self):
        assert validate_date_string('2024-01-01') == True
        assert validate_date_string('1990-12-31') == True
        assert validate_date_string('2000-06-15') == True
    
    def test_invalid_dates(self):
        assert validate_date_string('2024-13-01') == False  # Invalid month
        assert validate_date_string('2024-01-32') == False  # Invalid day
        assert validate_date_string('01-01-2024') == False  # Wrong format
        assert validate_date_string('2024/01/01') == False  # Wrong separator
        assert validate_date_string('') == False
        assert validate_date_string('not-a-date') == False

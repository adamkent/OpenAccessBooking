// Validation utilities for NHS appointment booking system

/**
 * Validate NHS Number using Modulus 11 algorithm
 */
export const validateNHSNumber = (nhsNumber) => {
  if (!nhsNumber) return { isValid: false, error: 'NHS number is required' };
  
  // Remove spaces and validate format
  const cleaned = nhsNumber.replace(/\s/g, '');
  
  if (!/^\d{10}$/.test(cleaned)) {
    return { isValid: false, error: 'NHS number must be 10 digits' };
  }

  // Modulus 11 check
  const digits = cleaned.split('').map(Number);
  const checkDigit = digits[9];
  
  let sum = 0;
  for (let i = 0; i < 9; i++) {
    sum += digits[i] * (10 - i);
  }
  
  const remainder = sum % 11;
  const calculatedCheck = 11 - remainder;
  
  let isValid = false;
  if (calculatedCheck === 11) {
    isValid = checkDigit === 0;
  } else if (calculatedCheck === 10) {
    isValid = false;
  } else {
    isValid = calculatedCheck === checkDigit;
  }
  
  return {
    isValid,
    error: isValid ? null : 'Invalid NHS number'
  };
};

/**
 * Validate UK postcode
 */
export const validatePostcode = (postcode) => {
  if (!postcode) return { isValid: false, error: 'Postcode is required' };
  
  const ukPostcodeRegex = /^[A-Z]{1,2}[0-9][A-Z0-9]?\s?[0-9][A-Z]{2}$/i;
  const isValid = ukPostcodeRegex.test(postcode.trim());
  
  return {
    isValid,
    error: isValid ? null : 'Invalid UK postcode format'
  };
};

/**
 * Validate UK phone number
 */
export const validatePhoneNumber = (phoneNumber) => {
  if (!phoneNumber) return { isValid: false, error: 'Phone number is required' };
  
  const cleaned = phoneNumber.replace(/\s/g, '');
  const ukPhoneRegex = /^(\+44|0)[0-9]{10}$/;
  const isValid = ukPhoneRegex.test(cleaned);
  
  return {
    isValid,
    error: isValid ? null : 'Invalid UK phone number format'
  };
};

/**
 * Validate email address
 */
export const validateEmail = (email) => {
  if (!email) return { isValid: false, error: 'Email is required' };
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const isValid = emailRegex.test(email);
  
  return {
    isValid,
    error: isValid ? null : 'Invalid email format'
  };
};

/**
 * Validate password strength
 */
export const validatePassword = (password) => {
  if (!password) return { isValid: false, error: 'Password is required' };
  
  const errors = [];
  
  if (password.length < 8) {
    errors.push('Password must be at least 8 characters long');
  }
  
  if (!/(?=.*[a-z])/.test(password)) {
    errors.push('Password must contain at least one lowercase letter');
  }
  
  if (!/(?=.*[A-Z])/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  }
  
  if (!/(?=.*\d)/.test(password)) {
    errors.push('Password must contain at least one number');
  }
  
  if (!/(?=.*[!@#$%^&*])/.test(password)) {
    errors.push('Password must contain at least one special character');
  }
  
  return {
    isValid: errors.length === 0,
    error: errors.length > 0 ? errors[0] : null,
    errors
  };
};

/**
 * Validate date of birth
 */
export const validateDateOfBirth = (dateOfBirth) => {
  if (!dateOfBirth) return { isValid: false, error: 'Date of birth is required' };
  
  const dob = new Date(dateOfBirth);
  const today = new Date();
  const age = today.getFullYear() - dob.getFullYear();
  const monthDiff = today.getMonth() - dob.getMonth();
  
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dob.getDate())) {
    age--;
  }
  
  if (isNaN(dob.getTime())) {
    return { isValid: false, error: 'Invalid date format' };
  }
  
  if (dob > today) {
    return { isValid: false, error: 'Date of birth cannot be in the future' };
  }
  
  if (age < 0 || age > 150) {
    return { isValid: false, error: 'Please enter a valid date of birth' };
  }
  
  return { isValid: true, error: null };
};

/**
 * Validate appointment date
 */
export const validateAppointmentDate = (appointmentDate) => {
  if (!appointmentDate) return { isValid: false, error: 'Appointment date is required' };
  
  const date = new Date(appointmentDate);
  const today = new Date();
  const maxDate = new Date();
  maxDate.setDate(today.getDate() + 60); // 60 days from now
  
  // Reset time to compare dates only
  today.setHours(0, 0, 0, 0);
  date.setHours(0, 0, 0, 0);
  maxDate.setHours(0, 0, 0, 0);
  
  if (isNaN(date.getTime())) {
    return { isValid: false, error: 'Invalid date format' };
  }
  
  if (date < today) {
    return { isValid: false, error: 'Appointment date cannot be in the past' };
  }
  
  if (date > maxDate) {
    return { isValid: false, error: 'Appointments can only be booked up to 60 days in advance' };
  }
  
  return { isValid: true, error: null };
};

/**
 * Validate required field
 */
export const validateRequired = (value, fieldName) => {
  const isEmpty = !value || (typeof value === 'string' && !value.trim());
  
  return {
    isValid: !isEmpty,
    error: isEmpty ? `${fieldName} is required` : null
  };
};

/**
 * Validate form with multiple fields
 */
export const validateForm = (formData, validationRules) => {
  const errors = {};
  let isValid = true;
  
  Object.keys(validationRules).forEach(field => {
    const rules = validationRules[field];
    const value = formData[field];
    
    for (const rule of rules) {
      const result = rule(value);
      if (!result.isValid) {
        errors[field] = result.error;
        isValid = false;
        break; // Stop at first error for this field
      }
    }
  });
  
  return { isValid, errors };
};

/**
 * Format NHS number for display
 */
export const formatNHSNumber = (nhsNumber) => {
  if (!nhsNumber) return '';
  const cleaned = nhsNumber.replace(/\s/g, '');
  const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
  if (match) {
    return `${match[1]} ${match[2]} ${match[3]}`;
  }
  return nhsNumber;
};

/**
 * Format phone number for display
 */
export const formatPhoneNumber = (phoneNumber) => {
  if (!phoneNumber) return '';
  const cleaned = phoneNumber.replace(/\D/g, '');
  
  // UK mobile format: 07XXX XXXXXX
  if (cleaned.startsWith('07') && cleaned.length === 11) {
    return `${cleaned.slice(0, 5)} ${cleaned.slice(5)}`;
  }
  
  // UK landline format: 0XX XXXX XXXX
  if (cleaned.startsWith('0') && cleaned.length === 11) {
    return `${cleaned.slice(0, 3)} ${cleaned.slice(3, 7)} ${cleaned.slice(7)}`;
  }
  
  return phoneNumber;
};

/**
 * Sanitize input to prevent XSS
 */
export const sanitizeInput = (input) => {
  if (typeof input !== 'string') return input;
  
  return input
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;');
};

/**
 * Validation rules for common forms
 */
export const validationRules = {
  registration: {
    firstName: [(value) => validateRequired(value, 'First name')],
    lastName: [(value) => validateRequired(value, 'Last name')],
    email: [(value) => validateRequired(value, 'Email'), validateEmail],
    password: [(value) => validateRequired(value, 'Password'), validatePassword],
    nhsNumber: [(value) => validateRequired(value, 'NHS number'), validateNHSNumber],
    dateOfBirth: [(value) => validateRequired(value, 'Date of birth'), validateDateOfBirth],
    phoneNumber: [(value) => validateRequired(value, 'Phone number'), validatePhoneNumber],
    postcode: [(value) => validateRequired(value, 'Postcode'), validatePostcode]
  },
  
  appointment: {
    appointmentType: [(value) => validateRequired(value, 'Appointment type')],
    reason: [(value) => validateRequired(value, 'Reason for appointment')],
    appointmentDate: [(value) => validateRequired(value, 'Appointment date'), validateAppointmentDate]
  },
  
  login: {
    email: [(value) => validateRequired(value, 'Email'), validateEmail],
    password: [(value) => validateRequired(value, 'Password')]
  }
};

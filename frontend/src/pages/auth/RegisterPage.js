import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Eye, 
  EyeOff, 
  Mail, 
  Lock, 
  User, 
  Phone, 
  MapPin, 
  AlertCircle,
  CheckCircle,
  Calendar
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import LoadingSpinner from '../../components/UI/LoadingSpinner';

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
    nhsNumber: '',
    dateOfBirth: '',
    phoneNumber: '',
    address: {
      line1: '',
      line2: '',
      city: '',
      postcode: ''
    },
    acceptTerms: false
  });
  
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [step, setStep] = useState(1);
  
  const { register, loading, error, clearError } = useAuth();
  const navigate = useNavigate();

  const validateNHSNumber = (nhsNumber) => {
    // Remove spaces and validate format
    const cleaned = nhsNumber.replace(/\s/g, '');
    if (!/^\d{10}$/.test(cleaned)) {
      return false;
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
    
    if (calculatedCheck === 11) return checkDigit === 0;
    if (calculatedCheck === 10) return false;
    return calculatedCheck === checkDigit;
  };

  const validatePostcode = (postcode) => {
    const ukPostcodeRegex = /^[A-Z]{1,2}[0-9][A-Z0-9]?\s?[0-9][A-Z]{2}$/i;
    return ukPostcodeRegex.test(postcode);
  };

  const validateStep1 = () => {
    const newErrors = {};

    if (!formData.firstName.trim()) {
      newErrors.firstName = 'First name is required';
    }

    if (!formData.lastName.trim()) {
      newErrors.lastName = 'Last name is required';
    }

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
      newErrors.password = 'Password must contain uppercase, lowercase, and number';
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStep2 = () => {
    const newErrors = {};

    if (!formData.nhsNumber) {
      newErrors.nhsNumber = 'NHS number is required';
    } else if (!validateNHSNumber(formData.nhsNumber)) {
      newErrors.nhsNumber = 'Please enter a valid NHS number';
    }

    if (!formData.dateOfBirth) {
      newErrors.dateOfBirth = 'Date of birth is required';
    } else {
      const dob = new Date(formData.dateOfBirth);
      const today = new Date();
      const age = today.getFullYear() - dob.getFullYear();
      if (age < 16 || age > 120) {
        newErrors.dateOfBirth = 'Please enter a valid date of birth';
      }
    }

    if (!formData.phoneNumber) {
      newErrors.phoneNumber = 'Phone number is required';
    } else if (!/^(\+44|0)[0-9]{10}$/.test(formData.phoneNumber.replace(/\s/g, ''))) {
      newErrors.phoneNumber = 'Please enter a valid UK phone number';
    }

    if (!formData.address.line1.trim()) {
      newErrors['address.line1'] = 'Address line 1 is required';
    }

    if (!formData.address.city.trim()) {
      newErrors['address.city'] = 'City is required';
    }

    if (!formData.address.postcode) {
      newErrors['address.postcode'] = 'Postcode is required';
    } else if (!validatePostcode(formData.address.postcode)) {
      newErrors['address.postcode'] = 'Please enter a valid UK postcode';
    }

    if (!formData.acceptTerms) {
      newErrors.acceptTerms = 'You must accept the terms and conditions';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    clearError();

    if (step === 1) {
      if (validateStep1()) {
        setStep(2);
      }
      return;
    }

    if (!validateStep2()) {
      return;
    }

    // Prepare registration data
    const registrationData = {
      email: formData.email,
      password: formData.password,
      first_name: formData.firstName,
      last_name: formData.lastName,
      nhs_number: formData.nhsNumber.replace(/\s/g, ''),
      date_of_birth: formData.dateOfBirth,
      phone_number: formData.phoneNumber,
      address: formData.address,
      role: 'patient'
    };

    const result = await register(registrationData);
    
    if (result.success) {
      navigate('/login', { 
        state: { 
          message: 'Registration successful! Please sign in with your new account.' 
        }
      });
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    if (name.startsWith('address.')) {
      const addressField = name.split('.')[1];
      setFormData(prev => ({
        ...prev,
        address: {
          ...prev.address,
          [addressField]: value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: type === 'checkbox' ? checked : value
      }));
    }
    
    // Clear field error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const formatNHSNumber = (value) => {
    const cleaned = value.replace(/\D/g, '');
    const match = cleaned.match(/^(\d{0,3})(\d{0,3})(\d{0,4})$/);
    if (match) {
      return [match[1], match[2], match[3]].filter(Boolean).join(' ');
    }
    return value;
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-nhs-black">
            Create your account
          </h2>
          <p className="mt-2 text-nhs-mid-grey">
            Join the NHS online appointment system
          </p>
        </div>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow-lg sm:rounded-lg sm:px-10">
          {/* Progress Indicator */}
          <div className="mb-8">
            <div className="flex items-center">
              <div className={`flex items-center justify-center w-8 h-8 rounded-full ${
                step >= 1 ? 'bg-nhs-blue text-white' : 'bg-nhs-pale-grey text-nhs-mid-grey'
              }`}>
                {step > 1 ? <CheckCircle className="h-5 w-5" /> : '1'}
              </div>
              <div className={`flex-1 h-1 mx-2 ${
                step > 1 ? 'bg-nhs-blue' : 'bg-nhs-pale-grey'
              }`} />
              <div className={`flex items-center justify-center w-8 h-8 rounded-full ${
                step >= 2 ? 'bg-nhs-blue text-white' : 'bg-nhs-pale-grey text-nhs-mid-grey'
              }`}>
                2
              </div>
            </div>
            <div className="flex justify-between mt-2 text-sm">
              <span className={step >= 1 ? 'text-nhs-blue' : 'text-nhs-mid-grey'}>
                Account Details
              </span>
              <span className={step >= 2 ? 'text-nhs-blue' : 'text-nhs-mid-grey'}>
                Personal Information
              </span>
            </div>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="alert-error mb-6">
              <div className="flex items-center">
                <AlertCircle className="h-5 w-5 mr-2" />
                <span>{error}</span>
              </div>
            </div>
          )}

          <form className="space-y-6" onSubmit={handleSubmit}>
            {step === 1 && (
              <>
                {/* Name Fields */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="firstName" className="form-label">
                      First name
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <User className="h-5 w-5 text-nhs-mid-grey" />
                      </div>
                      <input
                        id="firstName"
                        name="firstName"
                        type="text"
                        required
                        value={formData.firstName}
                        onChange={handleChange}
                        className={`form-input pl-10 ${errors.firstName ? 'border-nhs-red' : ''}`}
                        placeholder="First name"
                      />
                    </div>
                    {errors.firstName && (
                      <p className="form-error">{errors.firstName}</p>
                    )}
                  </div>

                  <div>
                    <label htmlFor="lastName" className="form-label">
                      Last name
                    </label>
                    <input
                      id="lastName"
                      name="lastName"
                      type="text"
                      required
                      value={formData.lastName}
                      onChange={handleChange}
                      className={`form-input ${errors.lastName ? 'border-nhs-red' : ''}`}
                      placeholder="Last name"
                    />
                    {errors.lastName && (
                      <p className="form-error">{errors.lastName}</p>
                    )}
                  </div>
                </div>

                {/* Email Field */}
                <div>
                  <label htmlFor="email" className="form-label">
                    Email address
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Mail className="h-5 w-5 text-nhs-mid-grey" />
                    </div>
                    <input
                      id="email"
                      name="email"
                      type="email"
                      autoComplete="email"
                      required
                      value={formData.email}
                      onChange={handleChange}
                      className={`form-input pl-10 ${errors.email ? 'border-nhs-red' : ''}`}
                      placeholder="Enter your email"
                    />
                  </div>
                  {errors.email && (
                    <p className="form-error">{errors.email}</p>
                  )}
                </div>

                {/* Password Fields */}
                <div>
                  <label htmlFor="password" className="form-label">
                    Password
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Lock className="h-5 w-5 text-nhs-mid-grey" />
                    </div>
                    <input
                      id="password"
                      name="password"
                      type={showPassword ? 'text' : 'password'}
                      required
                      value={formData.password}
                      onChange={handleChange}
                      className={`form-input pl-10 pr-10 ${errors.password ? 'border-nhs-red' : ''}`}
                      placeholder="Create a password"
                    />
                    <button
                      type="button"
                      className="absolute inset-y-0 right-0 pr-3 flex items-center"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? (
                        <EyeOff className="h-5 w-5 text-nhs-mid-grey hover:text-nhs-blue" />
                      ) : (
                        <Eye className="h-5 w-5 text-nhs-mid-grey hover:text-nhs-blue" />
                      )}
                    </button>
                  </div>
                  {errors.password && (
                    <p className="form-error">{errors.password}</p>
                  )}
                  <p className="form-help">
                    Must be 8+ characters with uppercase, lowercase, and number
                  </p>
                </div>

                <div>
                  <label htmlFor="confirmPassword" className="form-label">
                    Confirm password
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Lock className="h-5 w-5 text-nhs-mid-grey" />
                    </div>
                    <input
                      id="confirmPassword"
                      name="confirmPassword"
                      type={showConfirmPassword ? 'text' : 'password'}
                      required
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      className={`form-input pl-10 pr-10 ${errors.confirmPassword ? 'border-nhs-red' : ''}`}
                      placeholder="Confirm your password"
                    />
                    <button
                      type="button"
                      className="absolute inset-y-0 right-0 pr-3 flex items-center"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    >
                      {showConfirmPassword ? (
                        <EyeOff className="h-5 w-5 text-nhs-mid-grey hover:text-nhs-blue" />
                      ) : (
                        <Eye className="h-5 w-5 text-nhs-mid-grey hover:text-nhs-blue" />
                      )}
                    </button>
                  </div>
                  {errors.confirmPassword && (
                    <p className="form-error">{errors.confirmPassword}</p>
                  )}
                </div>
              </>
            )}

            {step === 2 && (
              <>
                {/* NHS Number */}
                <div>
                  <label htmlFor="nhsNumber" className="form-label">
                    NHS Number
                  </label>
                  <input
                    id="nhsNumber"
                    name="nhsNumber"
                    type="text"
                    required
                    value={formatNHSNumber(formData.nhsNumber)}
                    onChange={(e) => handleChange({
                      target: {
                        name: 'nhsNumber',
                        value: e.target.value.replace(/\s/g, '')
                      }
                    })}
                    className={`form-input ${errors.nhsNumber ? 'border-nhs-red' : ''}`}
                    placeholder="123 456 7890"
                    maxLength="12"
                  />
                  {errors.nhsNumber && (
                    <p className="form-error">{errors.nhsNumber}</p>
                  )}
                  <p className="form-help">
                    Your 10-digit NHS number (found on your NHS card)
                  </p>
                </div>

                {/* Date of Birth */}
                <div>
                  <label htmlFor="dateOfBirth" className="form-label">
                    Date of birth
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Calendar className="h-5 w-5 text-nhs-mid-grey" />
                    </div>
                    <input
                      id="dateOfBirth"
                      name="dateOfBirth"
                      type="date"
                      required
                      value={formData.dateOfBirth}
                      onChange={handleChange}
                      className={`form-input pl-10 ${errors.dateOfBirth ? 'border-nhs-red' : ''}`}
                    />
                  </div>
                  {errors.dateOfBirth && (
                    <p className="form-error">{errors.dateOfBirth}</p>
                  )}
                </div>

                {/* Phone Number */}
                <div>
                  <label htmlFor="phoneNumber" className="form-label">
                    Phone number
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Phone className="h-5 w-5 text-nhs-mid-grey" />
                    </div>
                    <input
                      id="phoneNumber"
                      name="phoneNumber"
                      type="tel"
                      required
                      value={formData.phoneNumber}
                      onChange={handleChange}
                      className={`form-input pl-10 ${errors.phoneNumber ? 'border-nhs-red' : ''}`}
                      placeholder="07123 456789"
                    />
                  </div>
                  {errors.phoneNumber && (
                    <p className="form-error">{errors.phoneNumber}</p>
                  )}
                </div>

                {/* Address */}
                <div className="space-y-4">
                  <div>
                    <label htmlFor="address.line1" className="form-label">
                      Address
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <MapPin className="h-5 w-5 text-nhs-mid-grey" />
                      </div>
                      <input
                        id="address.line1"
                        name="address.line1"
                        type="text"
                        required
                        value={formData.address.line1}
                        onChange={handleChange}
                        className={`form-input pl-10 ${errors['address.line1'] ? 'border-nhs-red' : ''}`}
                        placeholder="Address line 1"
                      />
                    </div>
                    {errors['address.line1'] && (
                      <p className="form-error">{errors['address.line1']}</p>
                    )}
                  </div>

                  <input
                    name="address.line2"
                    type="text"
                    value={formData.address.line2}
                    onChange={handleChange}
                    className="form-input"
                    placeholder="Address line 2 (optional)"
                  />

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <input
                        name="address.city"
                        type="text"
                        required
                        value={formData.address.city}
                        onChange={handleChange}
                        className={`form-input ${errors['address.city'] ? 'border-nhs-red' : ''}`}
                        placeholder="City"
                      />
                      {errors['address.city'] && (
                        <p className="form-error">{errors['address.city']}</p>
                      )}
                    </div>

                    <div>
                      <input
                        name="address.postcode"
                        type="text"
                        required
                        value={formData.address.postcode}
                        onChange={handleChange}
                        className={`form-input ${errors['address.postcode'] ? 'border-nhs-red' : ''}`}
                        placeholder="Postcode"
                      />
                      {errors['address.postcode'] && (
                        <p className="form-error">{errors['address.postcode']}</p>
                      )}
                    </div>
                  </div>
                </div>

                {/* Terms and Conditions */}
                <div>
                  <div className="flex items-start">
                    <input
                      id="acceptTerms"
                      name="acceptTerms"
                      type="checkbox"
                      required
                      checked={formData.acceptTerms}
                      onChange={handleChange}
                      className="h-4 w-4 text-nhs-blue focus:ring-nhs-blue border-nhs-mid-grey rounded mt-1"
                    />
                    <label htmlFor="acceptTerms" className="ml-3 text-sm text-nhs-black">
                      I accept the{' '}
                      <a href="#" className="text-nhs-blue hover:text-nhs-dark-blue">
                        Terms and Conditions
                      </a>{' '}
                      and{' '}
                      <a href="#" className="text-nhs-blue hover:text-nhs-dark-blue">
                        Privacy Policy
                      </a>
                    </label>
                  </div>
                  {errors.acceptTerms && (
                    <p className="form-error">{errors.acceptTerms}</p>
                  )}
                </div>
              </>
            )}

            {/* Navigation Buttons */}
            <div className="flex space-x-4">
              {step === 2 && (
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="btn-outline flex-1"
                >
                  Back
                </button>
              )}
              
              <button
                type="submit"
                disabled={loading}
                className="btn-primary flex-1 flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <LoadingSpinner size="sm" color="white" />
                    <span className="ml-2">Creating account...</span>
                  </>
                ) : step === 1 ? (
                  'Continue'
                ) : (
                  'Create Account'
                )}
              </button>
            </div>
          </form>

          {/* Login Link */}
          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-nhs-pale-grey" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-nhs-mid-grey">
                  Already have an account?
                </span>
              </div>
            </div>

            <div className="mt-6 text-center">
              <Link
                to="/login"
                className="font-medium text-nhs-blue hover:text-nhs-dark-blue"
              >
                Sign in here
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;

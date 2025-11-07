import axios from 'axios';

// API Base URL - will use proxy in development, actual URL in production
const API_BASE_URL = process.env.REACT_APP_API_URL || '';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('nhs_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle common errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('nhs_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
};

// Appointments API
export const appointmentsAPI = {
  // Get appointments with optional filters
  getAppointments: (params = {}) => api.get('/appointments', { params }),
  
  // Get specific appointment
  getAppointment: (appointmentId) => api.get(`/appointments/${appointmentId}`),
  
  // Create new appointment
  createAppointment: (appointmentData) => api.post('/appointments', appointmentData),
  
  // Update appointment
  updateAppointment: (appointmentId, updateData) => 
    api.put(`/appointments/${appointmentId}`, updateData),
  
  // Cancel appointment
  cancelAppointment: (appointmentId) => api.delete(`/appointments/${appointmentId}`),
  
  // Get available time slots
  getAvailableSlots: (practiceId, date) => 
    api.get(`/appointments/available-slots`, { 
      params: { practice_id: practiceId, date } 
    }),
};

// Patients API
export const patientsAPI = {
  // Get patient profile
  getPatient: (patientId) => api.get(`/patients/${patientId}`),
  
  // Create patient record
  createPatient: (patientData) => api.post('/patients', patientData),
  
  // Update patient profile
  updatePatient: (patientId, updateData) => 
    api.put(`/patients/${patientId}`, updateData),
  
  // Search patients (staff only)
  searchPatients: (searchTerm) => 
    api.get('/patients/search', { params: { q: searchTerm } }),
};

// Practices API
export const practicesAPI = {
  // Get practice information
  getPractice: (practiceId, params = {}) => 
    api.get(`/practices/${practiceId}`, { params }),
  
  // Get all practices (for selection)
  getPractices: () => api.get('/practices'),
  
  // Update practice settings (admin only)
  updatePractice: (practiceId, updateData) => 
    api.put(`/practices/${practiceId}`, updateData),
};

// Utility functions for common API patterns
export const apiUtils = {
  // Handle API errors consistently
  handleError: (error) => {
    if (error.response) {
      // Server responded with error status
      return {
        message: error.response.data?.error || 'An error occurred',
        status: error.response.status,
        errors: error.response.data?.errors || {},
      };
    } else if (error.request) {
      // Request made but no response
      return {
        message: 'Network error - please check your connection',
        status: 0,
      };
    } else {
      // Something else happened
      return {
        message: error.message || 'An unexpected error occurred',
        status: 0,
      };
    }
  },

  // Format date for API calls
  formatDate: (date) => {
    if (date instanceof Date) {
      return date.toISOString().split('T')[0];
    }
    return date;
  },

  // Format datetime for API calls
  formatDateTime: (date) => {
    if (date instanceof Date) {
      return date.toISOString();
    }
    return date;
  },

  // Parse API date response
  parseDate: (dateString) => {
    return new Date(dateString);
  },

  // Create query string from object
  createQueryString: (params) => {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        searchParams.append(key, value);
      }
    });
    return searchParams.toString();
  },
};

// Mock data for development (when backend is not available)
export const mockAPI = {
  // Mock appointments
  appointments: [
    {
      appointment_id: 'mock-1',
      patient_id: 'patient-1',
      practice_id: 'practice-001',
      appointment_datetime: '2024-12-15T10:30:00Z',
      appointment_type: 'routine',
      status: 'scheduled',
      reason: 'Annual check-up',
      duration_minutes: 30,
      patient: {
        first_name: 'John',
        last_name: 'Smith',
        nhs_number: '1234567890',
      },
      practice: {
        name: 'Riverside Medical Centre',
        phone: '020 7123 4567',
      },
    },
  ],

  // Mock practices
  practices: [
    {
      practice_id: 'practice-001',
      name: 'Riverside Medical Centre',
      address: {
        line1: '123 High Street',
        city: 'London',
        postcode: 'SW1A 1AA',
      },
      phone: '020 7123 4567',
      services: ['General Practice', 'Vaccinations', 'Health Checks'],
    },
  ],

  // Mock user
  user: {
    user_id: 'patient-1',
    email: 'john.smith@email.com',
    role: 'patient',
    first_name: 'John',
    last_name: 'Smith',
  },
};

export default api;

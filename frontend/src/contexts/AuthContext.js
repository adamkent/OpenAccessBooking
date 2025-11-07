import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { toast } from 'react-toastify';
import { authAPI } from '../services/api';

// Auth Context
const AuthContext = createContext();

// Auth Actions
const AUTH_ACTIONS = {
  LOGIN_START: 'LOGIN_START',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGIN_FAILURE: 'LOGIN_FAILURE',
  LOGOUT: 'LOGOUT',
  REGISTER_START: 'REGISTER_START',
  REGISTER_SUCCESS: 'REGISTER_SUCCESS',
  REGISTER_FAILURE: 'REGISTER_FAILURE',
  LOAD_USER: 'LOAD_USER',
  CLEAR_ERROR: 'CLEAR_ERROR',
};

// Initial State
const initialState = {
  user: null,
  token: localStorage.getItem('nhs_token'),
  loading: true,
  error: null,
  isAuthenticated: false,
};

// Auth Reducer
const authReducer = (state, action) => {
  switch (action.type) {
    case AUTH_ACTIONS.LOGIN_START:
    case AUTH_ACTIONS.REGISTER_START:
      return {
        ...state,
        loading: true,
        error: null,
      };

    case AUTH_ACTIONS.LOGIN_SUCCESS:
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.access_token,
        loading: false,
        error: null,
        isAuthenticated: true,
      };

    case AUTH_ACTIONS.REGISTER_SUCCESS:
      return {
        ...state,
        loading: false,
        error: null,
      };

    case AUTH_ACTIONS.LOGIN_FAILURE:
    case AUTH_ACTIONS.REGISTER_FAILURE:
      return {
        ...state,
        user: null,
        token: null,
        loading: false,
        error: action.payload,
        isAuthenticated: false,
      };

    case AUTH_ACTIONS.LOGOUT:
      return {
        ...state,
        user: null,
        token: null,
        loading: false,
        error: null,
        isAuthenticated: false,
      };

    case AUTH_ACTIONS.LOAD_USER:
      return {
        ...state,
        user: action.payload,
        loading: false,
        isAuthenticated: !!action.payload,
      };

    case AUTH_ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null,
      };

    default:
      return state;
  }
};

// Auth Provider Component
export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Load user on mount if token exists
  useEffect(() => {
    const loadUser = async () => {
      const token = localStorage.getItem('nhs_token');
      
      if (token) {
        try {
          // Decode JWT to get user info (basic validation)
          const payload = JSON.parse(atob(token.split('.')[1]));
          
          // Check if token is expired
          if (payload.exp * 1000 < Date.now()) {
            localStorage.removeItem('nhs_token');
            dispatch({ type: AUTH_ACTIONS.LOGOUT });
            return;
          }

          // Set user from token payload
          const user = {
            user_id: payload.sub,
            email: payload.email,
            role: payload['custom:role'] || 'patient',
            nhs_number: payload['custom:nhs_number'],
            practice_id: payload['custom:practice_id'],
          };

          dispatch({ type: AUTH_ACTIONS.LOAD_USER, payload: user });
        } catch (error) {
          console.error('Error loading user:', error);
          localStorage.removeItem('nhs_token');
          dispatch({ type: AUTH_ACTIONS.LOGOUT });
        }
      } else {
        dispatch({ type: AUTH_ACTIONS.LOAD_USER, payload: null });
      }
    };

    loadUser();
  }, []);

  // Login function
  const login = async (email, password) => {
    dispatch({ type: AUTH_ACTIONS.LOGIN_START });

    try {
      const response = await authAPI.login({ email, password });
      
      if (response.data) {
        const { access_token, user } = response.data;
        
        // Store token
        localStorage.setItem('nhs_token', access_token);
        
        dispatch({
          type: AUTH_ACTIONS.LOGIN_SUCCESS,
          payload: { access_token, user },
        });

        toast.success('Login successful!');
        return { success: true };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Login failed';
      
      dispatch({
        type: AUTH_ACTIONS.LOGIN_FAILURE,
        payload: errorMessage,
      });

      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Register function
  const register = async (userData) => {
    dispatch({ type: AUTH_ACTIONS.REGISTER_START });

    try {
      const response = await authAPI.register(userData);
      
      if (response.data) {
        dispatch({ type: AUTH_ACTIONS.REGISTER_SUCCESS });
        toast.success('Registration successful! Please log in.');
        return { success: true };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Registration failed';
      const errors = error.response?.data?.errors || {};
      
      dispatch({
        type: AUTH_ACTIONS.REGISTER_FAILURE,
        payload: errorMessage,
      });

      toast.error(errorMessage);
      return { success: false, error: errorMessage, errors };
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('nhs_token');
    dispatch({ type: AUTH_ACTIONS.LOGOUT });
    toast.info('You have been logged out');
  };

  // Clear error function
  const clearError = () => {
    dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
  };

  // Check if user has specific role
  const hasRole = (role) => {
    return state.user?.role === role;
  };

  // Check if user has any of the specified roles
  const hasAnyRole = (roles) => {
    return roles.includes(state.user?.role);
  };

  // Get authorization header for API calls
  const getAuthHeader = () => {
    return state.token ? { Authorization: `Bearer ${state.token}` } : {};
  };

  const value = {
    // State
    user: state.user,
    token: state.token,
    loading: state.loading,
    error: state.error,
    isAuthenticated: state.isAuthenticated,
    
    // Actions
    login,
    register,
    logout,
    clearError,
    
    // Utilities
    hasRole,
    hasAnyRole,
    getAuthHeader,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
};

export default AuthContext;

import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';

// Layout Components
import Layout from './components/Layout/Layout';
import PublicLayout from './components/Layout/PublicLayout';

// Public Pages
import HomePage from './pages/public/HomePage';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';

// Patient Pages
import PatientDashboard from './pages/patient/PatientDashboard';
import BookAppointment from './pages/patient/BookAppointment';
import MyAppointments from './pages/patient/MyAppointments';
import MyProfile from './pages/patient/MyProfile';

// Staff Pages
import StaffDashboard from './pages/staff/StaffDashboard';
import ManageAppointments from './pages/staff/ManageAppointments';
import PatientManagement from './pages/staff/PatientManagement';
import PracticeSettings from './pages/staff/PracticeSettings';

// Shared Components
import LoadingSpinner from './components/UI/LoadingSpinner';
import ErrorBoundary from './components/ErrorBoundary/ErrorBoundary';

// Protected Route Component
const ProtectedRoute = ({ children, allowedRoles = [] }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <LoadingSpinner />;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
};

// Public Route Component (redirect if authenticated)
const PublicRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <LoadingSpinner />;
  }

  if (user) {
    // Redirect based on user role
    switch (user.role) {
      case 'patient':
        return <Navigate to="/patient/dashboard" replace />;
      case 'staff':
      case 'admin':
        return <Navigate to="/staff/dashboard" replace />;
      default:
        return <Navigate to="/" replace />;
    }
  }

  return children;
};

function App() {
  return (
    <ErrorBoundary>
      <div className="App min-h-screen bg-gray-50">
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={
            <PublicLayout>
              <HomePage />
            </PublicLayout>
          } />
          
          <Route path="/login" element={
            <PublicRoute>
              <PublicLayout>
                <LoginPage />
              </PublicLayout>
            </PublicRoute>
          } />
          
          <Route path="/register" element={
            <PublicRoute>
              <PublicLayout>
                <RegisterPage />
              </PublicLayout>
            </PublicRoute>
          } />

          {/* Patient Routes */}
          <Route path="/patient/*" element={
            <ProtectedRoute allowedRoles={['patient']}>
              <Layout userType="patient">
                <Routes>
                  <Route path="dashboard" element={<PatientDashboard />} />
                  <Route path="book-appointment" element={<BookAppointment />} />
                  <Route path="appointments" element={<MyAppointments />} />
                  <Route path="profile" element={<MyProfile />} />
                  <Route path="*" element={<Navigate to="/patient/dashboard" replace />} />
                </Routes>
              </Layout>
            </ProtectedRoute>
          } />

          {/* Staff Routes */}
          <Route path="/staff/*" element={
            <ProtectedRoute allowedRoles={['staff', 'admin']}>
              <Layout userType="staff">
                <Routes>
                  <Route path="dashboard" element={<StaffDashboard />} />
                  <Route path="appointments" element={<ManageAppointments />} />
                  <Route path="patients" element={<PatientManagement />} />
                  <Route path="settings" element={<PracticeSettings />} />
                  <Route path="*" element={<Navigate to="/staff/dashboard" replace />} />
                </Routes>
              </Layout>
            </ProtectedRoute>
          } />

          {/* Unauthorized Page */}
          <Route path="/unauthorized" element={
            <PublicLayout>
              <div className="container mx-auto px-4 py-12 text-center">
                <h1 className="text-3xl font-bold text-nhs-red mb-4">Access Denied</h1>
                <p className="text-nhs-mid-grey mb-6">
                  You don't have permission to access this page.
                </p>
                <button 
                  onClick={() => window.history.back()}
                  className="btn-primary"
                >
                  Go Back
                </button>
              </div>
            </PublicLayout>
          } />

          {/* 404 Page */}
          <Route path="*" element={
            <PublicLayout>
              <div className="container mx-auto px-4 py-12 text-center">
                <h1 className="text-3xl font-bold text-nhs-black mb-4">Page Not Found</h1>
                <p className="text-nhs-mid-grey mb-6">
                  The page you're looking for doesn't exist.
                </p>
                <a href="/" className="btn-primary">
                  Return Home
                </a>
              </div>
            </PublicLayout>
          } />
        </Routes>
      </div>
    </ErrorBoundary>
  );
}

export default App;

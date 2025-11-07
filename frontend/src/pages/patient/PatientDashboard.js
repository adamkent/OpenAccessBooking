import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { 
  Calendar, 
  Clock, 
  User, 
  Plus, 
  AlertCircle, 
  CheckCircle,
  XCircle,
  Phone,
  MapPin,
  Bell
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { appointmentsAPI, practicesAPI } from '../../services/api';
import LoadingSpinner from '../../components/UI/LoadingSpinner';

const PatientDashboard = () => {
  const { user } = useAuth();
  const [greeting, setGreeting] = useState('');

  // Set greeting based on time of day
  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting('Good morning');
    else if (hour < 17) setGreeting('Good afternoon');
    else setGreeting('Good evening');
  }, []);

  // Fetch upcoming appointments
  const { 
    data: appointments, 
    isLoading: appointmentsLoading, 
    error: appointmentsError 
  } = useQuery(
    ['appointments', user?.user_id],
    () => appointmentsAPI.getAppointments({ 
      patient_id: user?.user_id,
      status: 'scheduled',
      limit: 5 
    }),
    {
      enabled: !!user?.user_id,
      select: (response) => response.data?.appointments || []
    }
  );

  // Fetch user's practice info
  const { 
    data: practice, 
    isLoading: practiceLoading 
  } = useQuery(
    ['practice', user?.practice_id],
    () => practicesAPI.getPractice(user?.practice_id),
    {
      enabled: !!user?.practice_id,
      select: (response) => response.data
    }
  );

  const getStatusIcon = (status) => {
    switch (status) {
      case 'scheduled':
        return <CheckCircle className="h-5 w-5 text-nhs-green" />;
      case 'cancelled':
        return <XCircle className="h-5 w-5 text-nhs-red" />;
      default:
        return <Clock className="h-5 w-5 text-nhs-blue" />;
    }
  };

  const formatDateTime = (dateTimeString) => {
    const date = new Date(dateTimeString);
    return {
      date: date.toLocaleDateString('en-GB', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      }),
      time: date.toLocaleTimeString('en-GB', { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    };
  };

  const quickActions = [
    {
      title: 'Book Appointment',
      description: 'Schedule a new appointment',
      icon: Plus,
      href: '/patient/book-appointment',
      color: 'bg-nhs-blue'
    },
    {
      title: 'View Appointments',
      description: 'See all your appointments',
      icon: Calendar,
      href: '/patient/appointments',
      color: 'bg-nhs-green'
    },
    {
      title: 'Update Profile',
      description: 'Manage your information',
      icon: User,
      href: '/patient/profile',
      color: 'bg-nhs-purple'
    }
  ];

  return (
    <div className="container mx-auto px-4 py-6">
      {/* Welcome Section */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-nhs-black mb-2">
          {greeting}, {user?.first_name || user?.email?.split('@')[0] || 'Patient'}!
        </h1>
        <p className="text-nhs-mid-grey">
          Welcome to your NHS appointment dashboard
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {quickActions.map((action, index) => {
          const Icon = action.icon;
          return (
            <Link
              key={index}
              to={action.href}
              className="card hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1"
            >
              <div className="card-body">
                <div className="flex items-center">
                  <div className={`${action.color} p-3 rounded-lg mr-4`}>
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-nhs-black mb-1">
                      {action.title}
                    </h3>
                    <p className="text-sm text-nhs-mid-grey">
                      {action.description}
                    </p>
                  </div>
                </div>
              </div>
            </Link>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Upcoming Appointments */}
        <div className="lg:col-span-2">
          <div className="card">
            <div className="card-header">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-nhs-black flex items-center">
                  <Calendar className="h-5 w-5 mr-2" />
                  Upcoming Appointments
                </h2>
                <Link 
                  to="/patient/appointments"
                  className="text-nhs-blue hover:text-nhs-dark-blue text-sm font-medium"
                >
                  View all
                </Link>
              </div>
            </div>
            
            <div className="card-body">
              {appointmentsLoading ? (
                <div className="flex justify-center py-8">
                  <LoadingSpinner text="Loading appointments..." />
                </div>
              ) : appointmentsError ? (
                <div className="alert-error">
                  <AlertCircle className="h-5 w-5 mr-2" />
                  Failed to load appointments
                </div>
              ) : appointments?.length === 0 ? (
                <div className="text-center py-8">
                  <Calendar className="h-12 w-12 text-nhs-mid-grey mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-nhs-black mb-2">
                    No upcoming appointments
                  </h3>
                  <p className="text-nhs-mid-grey mb-4">
                    You don't have any scheduled appointments
                  </p>
                  <Link to="/patient/book-appointment" className="btn-primary">
                    Book your first appointment
                  </Link>
                </div>
              ) : (
                <div className="space-y-4">
                  {appointments?.slice(0, 3).map((appointment) => {
                    const { date, time } = formatDateTime(appointment.appointment_datetime);
                    return (
                      <div 
                        key={appointment.appointment_id}
                        className="flex items-center justify-between p-4 bg-nhs-pale-grey rounded-lg"
                      >
                        <div className="flex items-center space-x-4">
                          {getStatusIcon(appointment.status)}
                          <div>
                            <h4 className="font-medium text-nhs-black">
                              {appointment.appointment_type || 'General Appointment'}
                            </h4>
                            <p className="text-sm text-nhs-mid-grey">
                              {date} at {time}
                            </p>
                            {appointment.reason && (
                              <p className="text-sm text-nhs-mid-grey">
                                {appointment.reason}
                              </p>
                            )}
                          </div>
                        </div>
                        <div className="text-right">
                          <span className={`badge ${
                            appointment.status === 'scheduled' ? 'badge-success' : 'badge-grey'
                          }`}>
                            {appointment.status}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Practice Information & Notifications */}
        <div className="space-y-6">
          {/* Practice Info */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-nhs-black flex items-center">
                <MapPin className="h-5 w-5 mr-2" />
                Your GP Practice
              </h3>
            </div>
            
            <div className="card-body">
              {practiceLoading ? (
                <LoadingSpinner size="sm" />
              ) : practice ? (
                <div className="space-y-3">
                  <h4 className="font-medium text-nhs-black">
                    {practice.name}
                  </h4>
                  
                  {practice.address && (
                    <div className="text-sm text-nhs-mid-grey">
                      <p>{practice.address.line1}</p>
                      {practice.address.line2 && <p>{practice.address.line2}</p>}
                      <p>{practice.address.city} {practice.address.postcode}</p>
                    </div>
                  )}
                  
                  {practice.phone && (
                    <div className="flex items-center text-sm text-nhs-mid-grey">
                      <Phone className="h-4 w-4 mr-2" />
                      {practice.phone}
                    </div>
                  )}
                  
                  {practice.services && (
                    <div className="mt-4">
                      <h5 className="text-sm font-medium text-nhs-black mb-2">
                        Services Available:
                      </h5>
                      <div className="flex flex-wrap gap-1">
                        {practice.services.slice(0, 3).map((service, index) => (
                          <span key={index} className="badge badge-grey text-xs">
                            {service}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-nhs-mid-grey text-sm">
                  Practice information not available
                </p>
              )}
            </div>
          </div>

          {/* Notifications */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-nhs-black flex items-center">
                <Bell className="h-5 w-5 mr-2" />
                Notifications
              </h3>
            </div>
            
            <div className="card-body">
              <div className="space-y-3">
                <div className="alert-info">
                  <div className="flex items-start">
                    <AlertCircle className="h-5 w-5 mr-2 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium">Appointment Reminder</p>
                      <p className="text-xs mt-1">
                        Don't forget your upcoming appointment. You'll receive SMS reminders.
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="alert-success">
                  <div className="flex items-start">
                    <CheckCircle className="h-5 w-5 mr-2 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium">Profile Updated</p>
                      <p className="text-xs mt-1">
                        Your contact information has been successfully updated.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Health Tips */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-nhs-black">
                Health Tips
              </h3>
            </div>
            
            <div className="card-body">
              <div className="space-y-3 text-sm">
                <div className="p-3 bg-blue-50 rounded-lg">
                  <h4 className="font-medium text-nhs-blue mb-1">
                    Stay Hydrated
                  </h4>
                  <p className="text-nhs-mid-grey">
                    Drink at least 8 glasses of water daily for optimal health.
                  </p>
                </div>
                
                <div className="p-3 bg-green-50 rounded-lg">
                  <h4 className="font-medium text-nhs-green mb-1">
                    Regular Exercise
                  </h4>
                  <p className="text-nhs-mid-grey">
                    Aim for 150 minutes of moderate exercise per week.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PatientDashboard;

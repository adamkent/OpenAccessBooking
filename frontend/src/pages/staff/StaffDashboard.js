import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { 
  Calendar, 
  Users, 
  Clock, 
  TrendingUp, 
  AlertCircle,
  CheckCircle,
  XCircle,
  User,
  Phone,
  MapPin
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { appointmentsAPI, patientsAPI, practicesAPI } from '../../services/api';
import LoadingSpinner from '../../components/UI/LoadingSpinner';

const StaffDashboard = () => {
  const [greeting, setGreeting] = useState('');
  const { user } = useAuth();

  // Set greeting based on time of day
  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting('Good morning');
    else if (hour < 17) setGreeting('Good afternoon');
    else setGreeting('Good evening');
  }, []);

  // Fetch today's appointments
  const { data: todayAppointments, isLoading: appointmentsLoading } = useQuery(
    ['appointments', 'today'],
    () => appointmentsAPI.getAppointments({ 
      practice_id: user?.practice_id,
      date: new Date().toISOString().split('T')[0],
      limit: 20
    }),
    {
      enabled: !!user?.practice_id,
      select: (response) => response.data?.appointments || []
    }
  );

  // Fetch practice statistics
  const { data: stats, isLoading: statsLoading } = useQuery(
    ['practice-stats', user?.practice_id],
    () => practicesAPI.getPractice(user?.practice_id, { include_stats: true }),
    {
      enabled: !!user?.practice_id,
      select: (response) => response.data?.stats || {}
    }
  );

  // Fetch practice info
  const { data: practice } = useQuery(
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
        return <Clock className="h-4 w-4 text-nhs-blue" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-nhs-green" />;
      case 'cancelled':
        return <XCircle className="h-4 w-4 text-nhs-red" />;
      default:
        return <AlertCircle className="h-4 w-4 text-nhs-mid-grey" />;
    }
  };

  const formatTime = (dateTimeString) => {
    return new Date(dateTimeString).toLocaleTimeString('en-GB', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const quickStats = [
    {
      title: 'Today\'s Appointments',
      value: todayAppointments?.length || 0,
      icon: Calendar,
      color: 'bg-nhs-blue',
      change: '+12%',
      changeType: 'increase'
    },
    {
      title: 'Total Patients',
      value: stats?.total_patients || 0,
      icon: Users,
      color: 'bg-nhs-green',
      change: '+5%',
      changeType: 'increase'
    },
    {
      title: 'This Week',
      value: stats?.week_appointments || 0,
      icon: TrendingUp,
      color: 'bg-nhs-purple',
      change: '+8%',
      changeType: 'increase'
    },
    {
      title: 'Completion Rate',
      value: `${stats?.completion_rate || 95}%`,
      icon: CheckCircle,
      color: 'bg-nhs-green',
      change: '+2%',
      changeType: 'increase'
    }
  ];

  return (
    <div className="container mx-auto px-4 py-6">
      {/* Welcome Section */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-nhs-black mb-2">
          {greeting}, {user?.first_name || 'Staff Member'}!
        </h1>
        <p className="text-nhs-mid-grey">
          Welcome to your practice management dashboard
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {quickStats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div key={index} className="card hover:shadow-lg transition-shadow">
              <div className="card-body">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-nhs-mid-grey mb-1">{stat.title}</p>
                    <p className="text-2xl font-bold text-nhs-black">{stat.value}</p>
                    <div className="flex items-center mt-2">
                      <span className={`text-xs ${
                        stat.changeType === 'increase' ? 'text-nhs-green' : 'text-nhs-red'
                      }`}>
                        {stat.change}
                      </span>
                      <span className="text-xs text-nhs-mid-grey ml-1">vs last period</span>
                    </div>
                  </div>
                  <div className={`${stat.color} p-3 rounded-lg`}>
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Today's Schedule */}
        <div className="lg:col-span-2">
          <div className="card">
            <div className="card-header">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-nhs-black flex items-center">
                  <Calendar className="h-5 w-5 mr-2" />
                  Today's Schedule
                </h2>
                <span className="text-sm text-nhs-mid-grey">
                  {new Date().toLocaleDateString('en-GB', { 
                    weekday: 'long', 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}
                </span>
              </div>
            </div>
            
            <div className="card-body">
              {appointmentsLoading ? (
                <div className="flex justify-center py-8">
                  <LoadingSpinner text="Loading appointments..." />
                </div>
              ) : todayAppointments?.length === 0 ? (
                <div className="text-center py-8">
                  <Calendar className="h-12 w-12 text-nhs-mid-grey mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-nhs-black mb-2">
                    No appointments today
                  </h3>
                  <p className="text-nhs-mid-grey">
                    Enjoy your day off or use this time for administrative tasks
                  </p>
                </div>
              ) : (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {todayAppointments?.map((appointment) => (
                    <div 
                      key={appointment.appointment_id}
                      className="flex items-center justify-between p-4 bg-nhs-pale-grey rounded-lg hover:shadow-sm transition-shadow"
                    >
                      <div className="flex items-center space-x-4">
                        {getStatusIcon(appointment.status)}
                        <div>
                          <h4 className="font-medium text-nhs-black">
                            {appointment.patient?.first_name} {appointment.patient?.last_name}
                          </h4>
                          <p className="text-sm text-nhs-mid-grey">
                            {appointment.appointment_type || 'General'} • {formatTime(appointment.appointment_datetime)}
                          </p>
                          {appointment.reason && (
                            <p className="text-sm text-nhs-mid-grey mt-1">
                              {appointment.reason}
                            </p>
                          )}
                        </div>
                      </div>
                      
                      <div className="text-right">
                        <span className={`badge ${
                          appointment.status === 'scheduled' ? 'badge-primary' :
                          appointment.status === 'completed' ? 'badge-success' :
                          appointment.status === 'cancelled' ? 'badge-error' : 'badge-grey'
                        }`}>
                          {appointment.status}
                        </span>
                        <p className="text-xs text-nhs-mid-grey mt-1">
                          {appointment.duration_minutes} min
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Practice Info & Quick Actions */}
        <div className="space-y-6">
          {/* Practice Information */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-nhs-black flex items-center">
                <MapPin className="h-5 w-5 mr-2" />
                Practice Information
              </h3>
            </div>
            
            <div className="card-body">
              {practice ? (
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
                  
                  <div className="mt-4 pt-4 border-t border-nhs-pale-grey">
                    <h5 className="text-sm font-medium text-nhs-black mb-2">
                      Operating Hours
                    </h5>
                    <div className="text-sm text-nhs-mid-grey space-y-1">
                      <div className="flex justify-between">
                        <span>Monday - Friday</span>
                        <span>8:00 AM - 6:00 PM</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Saturday</span>
                        <span>9:00 AM - 1:00 PM</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Sunday</span>
                        <span>Closed</span>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <LoadingSpinner size="sm" />
              )}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-nhs-black">Quick Actions</h3>
            </div>
            
            <div className="card-body">
              <div className="space-y-3">
                <button className="w-full btn-primary text-left">
                  <Calendar className="h-4 w-4 mr-2" />
                  View All Appointments
                </button>
                
                <button className="w-full btn-outline text-left">
                  <Users className="h-4 w-4 mr-2" />
                  Patient Management
                </button>
                
                <button className="w-full btn-outline text-left">
                  <TrendingUp className="h-4 w-4 mr-2" />
                  Generate Reports
                </button>
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-nhs-black">Recent Activity</h3>
            </div>
            
            <div className="card-body">
              <div className="space-y-3 text-sm">
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-nhs-green rounded-full"></div>
                  <div>
                    <p className="text-nhs-black">New patient registered</p>
                    <p className="text-nhs-mid-grey">2 minutes ago</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-nhs-blue rounded-full"></div>
                  <div>
                    <p className="text-nhs-black">Appointment completed</p>
                    <p className="text-nhs-mid-grey">15 minutes ago</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-nhs-orange rounded-full"></div>
                  <div>
                    <p className="text-nhs-black">Appointment rescheduled</p>
                    <p className="text-nhs-mid-grey">1 hour ago</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StaffDashboard;

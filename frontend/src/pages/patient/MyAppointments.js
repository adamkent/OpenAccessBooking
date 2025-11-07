import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { Calendar, Clock, User, Edit, Trash2, Phone } from 'lucide-react';
import { toast } from 'react-toastify';
import { useAuth } from '../../contexts/AuthContext';
import { appointmentsAPI } from '../../services/api';
import LoadingSpinner from '../../components/UI/LoadingSpinner';

const MyAppointments = () => {
  const [filter, setFilter] = useState('all');
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const { data: appointments, isLoading } = useQuery(
    ['appointments', user?.user_id, filter],
    () => appointmentsAPI.getAppointments({ 
      patient_id: user?.user_id,
      status: filter === 'all' ? undefined : filter
    }),
    {
      enabled: !!user?.user_id,
      select: (response) => response.data?.appointments || []
    }
  );

  const cancelMutation = useMutation(
    (appointmentId) => appointmentsAPI.cancelAppointment(appointmentId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['appointments']);
        toast.success('Appointment cancelled successfully');
      },
      onError: () => toast.error('Failed to cancel appointment')
    }
  );

  const formatDateTime = (dateTimeString) => {
    const date = new Date(dateTimeString);
    return {
      date: date.toLocaleDateString('en-GB'),
      time: date.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
    };
  };

  const getStatusBadge = (status) => {
    const badges = {
      scheduled: 'badge-success',
      completed: 'badge-primary',
      cancelled: 'badge-error',
      'no-show': 'badge-grey'
    };
    return badges[status] || 'badge-grey';
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-6">
        <LoadingSpinner fullScreen text="Loading appointments..." />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-nhs-black mb-2">My Appointments</h1>
        <p className="text-nhs-mid-grey">View and manage your appointments</p>
      </div>

      {/* Filter Tabs */}
      <div className="mb-6">
        <div className="border-b border-nhs-pale-grey">
          <nav className="-mb-px flex space-x-8">
            {[
              { key: 'all', label: 'All Appointments' },
              { key: 'scheduled', label: 'Upcoming' },
              { key: 'completed', label: 'Past' },
              { key: 'cancelled', label: 'Cancelled' }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setFilter(tab.key)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  filter === tab.key
                    ? 'border-nhs-blue text-nhs-blue'
                    : 'border-transparent text-nhs-mid-grey hover:text-nhs-blue'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Appointments List */}
      {appointments?.length === 0 ? (
        <div className="text-center py-12">
          <Calendar className="h-12 w-12 text-nhs-mid-grey mx-auto mb-4" />
          <h3 className="text-lg font-medium text-nhs-black mb-2">No appointments found</h3>
          <p className="text-nhs-mid-grey">You don't have any appointments matching this filter</p>
        </div>
      ) : (
        <div className="space-y-4">
          {appointments?.map((appointment) => {
            const { date, time } = formatDateTime(appointment.appointment_datetime);
            return (
              <div key={appointment.appointment_id} className="card hover:shadow-md transition-shadow">
                <div className="card-body">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="flex-shrink-0">
                        <div className="w-12 h-12 bg-nhs-blue bg-opacity-10 rounded-lg flex items-center justify-center">
                          <Calendar className="h-6 w-6 text-nhs-blue" />
                        </div>
                      </div>
                      
                      <div className="flex-1">
                        <h3 className="text-lg font-medium text-nhs-black">
                          {appointment.appointment_type || 'General Appointment'}
                        </h3>
                        <div className="flex items-center space-x-4 text-sm text-nhs-mid-grey mt-1">
                          <div className="flex items-center">
                            <Calendar className="h-4 w-4 mr-1" />
                            {date}
                          </div>
                          <div className="flex items-center">
                            <Clock className="h-4 w-4 mr-1" />
                            {time}
                          </div>
                          <div className="flex items-center">
                            <User className="h-4 w-4 mr-1" />
                            {appointment.duration_minutes} minutes
                          </div>
                        </div>
                        {appointment.reason && (
                          <p className="text-sm text-nhs-mid-grey mt-2">{appointment.reason}</p>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center space-x-3">
                      <span className={`badge ${getStatusBadge(appointment.status)}`}>
                        {appointment.status}
                      </span>
                      
                      {appointment.status === 'scheduled' && (
                        <div className="flex space-x-2">
                          <button
                            onClick={() => cancelMutation.mutate(appointment.appointment_id)}
                            disabled={cancelMutation.isLoading}
                            className="p-2 text-nhs-red hover:bg-red-50 rounded-md transition-colors"
                            title="Cancel appointment"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default MyAppointments;

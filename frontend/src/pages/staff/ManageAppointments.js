import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { 
  Calendar, 
  Clock, 
  User, 
  Search, 
  Filter, 
  Edit, 
  Trash2, 
  CheckCircle,
  XCircle,
  Phone,
  Mail,
  Plus
} from 'lucide-react';
import { toast } from 'react-toastify';
import { useAuth } from '../../contexts/AuthContext';
import { appointmentsAPI } from '../../services/api';
import LoadingSpinner from '../../components/UI/LoadingSpinner';

const ManageAppointments = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [dateFilter, setDateFilter] = useState('today');
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  
  const { user } = useAuth();
  const queryClient = useQueryClient();

  // Calculate date range based on filter
  const getDateRange = () => {
    const today = new Date();
    const startDate = new Date(today);
    const endDate = new Date(today);

    switch (dateFilter) {
      case 'today':
        break;
      case 'week':
        startDate.setDate(today.getDate() - today.getDay());
        endDate.setDate(startDate.getDate() + 6);
        break;
      case 'month':
        startDate.setDate(1);
        endDate.setMonth(endDate.getMonth() + 1, 0);
        break;
      default:
        break;
    }

    return {
      start: startDate.toISOString().split('T')[0],
      end: endDate.toISOString().split('T')[0]
    };
  };

  // Fetch appointments
  const { data: appointments, isLoading } = useQuery(
    ['appointments', 'staff', statusFilter, dateFilter, searchTerm],
    () => {
      const { start, end } = getDateRange();
      return appointmentsAPI.getAppointments({
        practice_id: user?.practice_id,
        status: statusFilter === 'all' ? undefined : statusFilter,
        date_from: start,
        date_to: end,
        search: searchTerm || undefined
      });
    },
    {
      enabled: !!user?.practice_id,
      select: (response) => response.data?.appointments || []
    }
  );

  // Update appointment status mutation
  const updateStatusMutation = useMutation(
    ({ appointmentId, status }) => 
      appointmentsAPI.updateAppointment(appointmentId, { status }),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['appointments']);
        toast.success('Appointment status updated');
      },
      onError: () => toast.error('Failed to update appointment')
    }
  );

  // Cancel appointment mutation
  const cancelMutation = useMutation(
    (appointmentId) => appointmentsAPI.cancelAppointment(appointmentId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['appointments']);
        toast.success('Appointment cancelled');
      },
      onError: () => toast.error('Failed to cancel appointment')
    }
  );

  const formatDateTime = (dateTimeString) => {
    const date = new Date(dateTimeString);
    return {
      date: date.toLocaleDateString('en-GB', { 
        weekday: 'short',
        day: 'numeric',
        month: 'short'
      }),
      time: date.toLocaleTimeString('en-GB', { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    };
  };

  const getStatusBadge = (status) => {
    const badges = {
      scheduled: 'badge-primary',
      completed: 'badge-success',
      cancelled: 'badge-error',
      'no-show': 'badge-grey'
    };
    return badges[status] || 'badge-grey';
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'scheduled':
        return <Clock className="h-4 w-4 text-nhs-blue" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-nhs-green" />;
      case 'cancelled':
        return <XCircle className="h-4 w-4 text-nhs-red" />;
      default:
        return <Clock className="h-4 w-4 text-nhs-mid-grey" />;
    }
  };

  const handleStatusChange = (appointmentId, newStatus) => {
    updateStatusMutation.mutate({ appointmentId, status: newStatus });
  };

  const handleViewDetails = (appointment) => {
    setSelectedAppointment(appointment);
    setShowDetailsModal(true);
  };

  const filteredAppointments = appointments?.filter(appointment => {
    if (!searchTerm) return true;
    
    const searchLower = searchTerm.toLowerCase();
    const patientName = `${appointment.patient?.first_name} ${appointment.patient?.last_name}`.toLowerCase();
    const nhsNumber = appointment.patient?.nhs_number?.toLowerCase() || '';
    const reason = appointment.reason?.toLowerCase() || '';
    
    return patientName.includes(searchLower) || 
           nhsNumber.includes(searchLower) || 
           reason.includes(searchLower);
  });

  return (
    <div className="container mx-auto px-4 py-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-nhs-black mb-2">
              Manage Appointments
            </h1>
            <p className="text-nhs-mid-grey">
              View and manage all practice appointments
            </p>
          </div>
          
          <button className="btn-primary flex items-center">
            <Plus className="h-4 w-4 mr-2" />
            New Appointment
          </button>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="card mb-6">
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-nhs-mid-grey" />
              </div>
              <input
                type="text"
                placeholder="Search patients, NHS number..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="form-input pl-10"
              />
            </div>

            {/* Status Filter */}
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Filter className="h-5 w-5 text-nhs-mid-grey" />
              </div>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="form-input pl-10"
              >
                <option value="all">All Status</option>
                <option value="scheduled">Scheduled</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
                <option value="no-show">No Show</option>
              </select>
            </div>

            {/* Date Filter */}
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Calendar className="h-5 w-5 text-nhs-mid-grey" />
              </div>
              <select
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
                className="form-input pl-10"
              >
                <option value="today">Today</option>
                <option value="week">This Week</option>
                <option value="month">This Month</option>
              </select>
            </div>

            {/* Results Count */}
            <div className="flex items-center text-nhs-mid-grey">
              <span className="text-sm">
                {filteredAppointments?.length || 0} appointments found
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Appointments Table */}
      <div className="card">
        <div className="card-body p-0">
          {isLoading ? (
            <div className="flex justify-center py-12">
              <LoadingSpinner text="Loading appointments..." />
            </div>
          ) : filteredAppointments?.length === 0 ? (
            <div className="text-center py-12">
              <Calendar className="h-12 w-12 text-nhs-mid-grey mx-auto mb-4" />
              <h3 className="text-lg font-medium text-nhs-black mb-2">
                No appointments found
              </h3>
              <p className="text-nhs-mid-grey">
                No appointments match your current filters
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-nhs-pale-grey">
                <thead className="bg-nhs-pale-grey">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-nhs-mid-grey uppercase tracking-wider">
                      Patient
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-nhs-mid-grey uppercase tracking-wider">
                      Date & Time
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-nhs-mid-grey uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-nhs-mid-grey uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-nhs-mid-grey uppercase tracking-wider">
                      Contact
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-nhs-mid-grey uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                
                <tbody className="bg-white divide-y divide-nhs-pale-grey">
                  {filteredAppointments?.map((appointment) => {
                    const { date, time } = formatDateTime(appointment.appointment_datetime);
                    return (
                      <tr key={appointment.appointment_id} className="hover:bg-nhs-pale-grey">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="flex-shrink-0 h-10 w-10">
                              <div className="h-10 w-10 rounded-full bg-nhs-blue bg-opacity-10 flex items-center justify-center">
                                <User className="h-5 w-5 text-nhs-blue" />
                              </div>
                            </div>
                            <div className="ml-4">
                              <div className="text-sm font-medium text-nhs-black">
                                {appointment.patient?.first_name} {appointment.patient?.last_name}
                              </div>
                              <div className="text-sm text-nhs-mid-grey">
                                NHS: {appointment.patient?.nhs_number}
                              </div>
                            </div>
                          </div>
                        </td>
                        
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-nhs-black">{date}</div>
                          <div className="text-sm text-nhs-mid-grey">{time}</div>
                        </td>
                        
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-nhs-black">
                            {appointment.appointment_type || 'General'}
                          </div>
                          <div className="text-sm text-nhs-mid-grey">
                            {appointment.duration_minutes} min
                          </div>
                        </td>
                        
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            {getStatusIcon(appointment.status)}
                            <span className={`ml-2 badge ${getStatusBadge(appointment.status)}`}>
                              {appointment.status}
                            </span>
                          </div>
                        </td>
                        
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-nhs-mid-grey">
                          {appointment.patient?.phone_number && (
                            <div className="flex items-center mb-1">
                              <Phone className="h-3 w-3 mr-1" />
                              {appointment.patient.phone_number}
                            </div>
                          )}
                          {appointment.patient?.email && (
                            <div className="flex items-center">
                              <Mail className="h-3 w-3 mr-1" />
                              {appointment.patient.email}
                            </div>
                          )}
                        </td>
                        
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex items-center justify-end space-x-2">
                            <button
                              onClick={() => handleViewDetails(appointment)}
                              className="text-nhs-blue hover:text-nhs-dark-blue"
                              title="View details"
                            >
                              <Edit className="h-4 w-4" />
                            </button>
                            
                            {appointment.status === 'scheduled' && (
                              <>
                                <button
                                  onClick={() => handleStatusChange(appointment.appointment_id, 'completed')}
                                  className="text-nhs-green hover:text-nhs-dark-green"
                                  title="Mark as completed"
                                >
                                  <CheckCircle className="h-4 w-4" />
                                </button>
                                
                                <button
                                  onClick={() => cancelMutation.mutate(appointment.appointment_id)}
                                  className="text-nhs-red hover:text-red-700"
                                  title="Cancel appointment"
                                >
                                  <Trash2 className="h-4 w-4" />
                                </button>
                              </>
                            )}
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Appointment Details Modal */}
      {showDetailsModal && selectedAppointment && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-nhs-black">
                  Appointment Details
                </h3>
                <button
                  onClick={() => setShowDetailsModal(false)}
                  className="text-nhs-mid-grey hover:text-nhs-black"
                >
                  <XCircle className="h-6 w-6" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-nhs-mid-grey">Patient</label>
                  <p className="text-nhs-black">
                    {selectedAppointment.patient?.first_name} {selectedAppointment.patient?.last_name}
                  </p>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-nhs-mid-grey">NHS Number</label>
                  <p className="text-nhs-black">{selectedAppointment.patient?.nhs_number}</p>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-nhs-mid-grey">Date & Time</label>
                  <p className="text-nhs-black">
                    {formatDateTime(selectedAppointment.appointment_datetime).date} at{' '}
                    {formatDateTime(selectedAppointment.appointment_datetime).time}
                  </p>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-nhs-mid-grey">Type</label>
                  <p className="text-nhs-black">
                    {selectedAppointment.appointment_type || 'General'}
                  </p>
                </div>
                
                {selectedAppointment.reason && (
                  <div>
                    <label className="text-sm font-medium text-nhs-mid-grey">Reason</label>
                    <p className="text-nhs-black">{selectedAppointment.reason}</p>
                  </div>
                )}
                
                {selectedAppointment.notes && (
                  <div>
                    <label className="text-sm font-medium text-nhs-mid-grey">Notes</label>
                    <p className="text-nhs-black">{selectedAppointment.notes}</p>
                  </div>
                )}
                
                <div>
                  <label className="text-sm font-medium text-nhs-mid-grey">Status</label>
                  <span className={`badge ${getStatusBadge(selectedAppointment.status)}`}>
                    {selectedAppointment.status}
                  </span>
                </div>
              </div>
              
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => setShowDetailsModal(false)}
                  className="btn-outline"
                >
                  Close
                </button>
                
                {selectedAppointment.status === 'scheduled' && (
                  <button
                    onClick={() => {
                      handleStatusChange(selectedAppointment.appointment_id, 'completed');
                      setShowDetailsModal(false);
                    }}
                    className="btn-success"
                  >
                    Mark Complete
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ManageAppointments;

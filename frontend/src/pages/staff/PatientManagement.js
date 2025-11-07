import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { 
  Users, 
  Search, 
  User, 
  Phone, 
  Mail, 
  Calendar, 
  MapPin,
  Edit,
  Eye,
  Plus,
  Filter
} from 'lucide-react';
import { toast } from 'react-toastify';
import { useAuth } from '../../contexts/AuthContext';
import { patientsAPI, appointmentsAPI } from '../../services/api';
import LoadingSpinner from '../../components/UI/LoadingSpinner';

const PatientManagement = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [showPatientModal, setShowPatientModal] = useState(false);
  const [modalType, setModalType] = useState('view'); // 'view', 'edit', 'create'
  
  const { user } = useAuth();
  const queryClient = useQueryClient();

  // Fetch patients
  const { data: patients, isLoading } = useQuery(
    ['patients', searchTerm],
    () => patientsAPI.searchPatients(searchTerm),
    {
      enabled: !!user?.practice_id,
      select: (response) => response.data?.patients || []
    }
  );

  // Fetch patient appointments when viewing details
  const { data: patientAppointments, isLoading: appointmentsLoading } = useQuery(
    ['patient-appointments', selectedPatient?.patient_id],
    () => appointmentsAPI.getAppointments({ 
      patient_id: selectedPatient?.patient_id,
      limit: 10 
    }),
    {
      enabled: !!selectedPatient?.patient_id,
      select: (response) => response.data?.appointments || []
    }
  );

  const formatNHSNumber = (nhsNumber) => {
    if (!nhsNumber) return '';
    const cleaned = nhsNumber.replace(/\s/g, '');
    const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
    if (match) {
      return `${match[1]} ${match[2]} ${match[3]}`;
    }
    return nhsNumber;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not provided';
    return new Date(dateString).toLocaleDateString('en-GB');
  };

  const calculateAge = (dateOfBirth) => {
    if (!dateOfBirth) return 'Unknown';
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    
    return age;
  };

  const handleViewPatient = (patient) => {
    setSelectedPatient(patient);
    setModalType('view');
    setShowPatientModal(true);
  };

  const handleEditPatient = (patient) => {
    setSelectedPatient(patient);
    setModalType('edit');
    setShowPatientModal(true);
  };

  const handleCreatePatient = () => {
    setSelectedPatient(null);
    setModalType('create');
    setShowPatientModal(true);
  };

  const filteredPatients = patients?.filter(patient => {
    if (!searchTerm) return true;
    
    const searchLower = searchTerm.toLowerCase();
    const fullName = `${patient.first_name} ${patient.last_name}`.toLowerCase();
    const nhsNumber = patient.nhs_number?.toLowerCase() || '';
    const email = patient.email?.toLowerCase() || '';
    
    return fullName.includes(searchLower) || 
           nhsNumber.includes(searchLower) || 
           email.includes(searchLower);
  });

  return (
    <div className="container mx-auto px-4 py-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-nhs-black mb-2">
              Patient Management
            </h1>
            <p className="text-nhs-mid-grey">
              View and manage patient records
            </p>
          </div>
          
          <button 
            onClick={handleCreatePatient}
            className="btn-primary flex items-center"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Patient
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="card mb-6">
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div className="relative md:col-span-2">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-nhs-mid-grey" />
              </div>
              <input
                type="text"
                placeholder="Search by name, NHS number, or email..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="form-input pl-10"
              />
            </div>

            {/* Results Count */}
            <div className="flex items-center text-nhs-mid-grey">
              <Users className="h-5 w-5 mr-2" />
              <span className="text-sm">
                {filteredPatients?.length || 0} patients found
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Patients Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {isLoading ? (
          <div className="col-span-full flex justify-center py-12">
            <LoadingSpinner text="Loading patients..." />
          </div>
        ) : filteredPatients?.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <Users className="h-12 w-12 text-nhs-mid-grey mx-auto mb-4" />
            <h3 className="text-lg font-medium text-nhs-black mb-2">
              No patients found
            </h3>
            <p className="text-nhs-mid-grey">
              {searchTerm ? 'No patients match your search criteria' : 'No patients registered yet'}
            </p>
          </div>
        ) : (
          filteredPatients?.map((patient) => (
            <div key={patient.patient_id} className="card hover:shadow-lg transition-shadow">
              <div className="card-body">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center">
                    <div className="w-12 h-12 bg-nhs-blue bg-opacity-10 rounded-full flex items-center justify-center mr-3">
                      <User className="h-6 w-6 text-nhs-blue" />
                    </div>
                    <div>
                      <h3 className="text-lg font-medium text-nhs-black">
                        {patient.first_name} {patient.last_name}
                      </h3>
                      <p className="text-sm text-nhs-mid-grey">
                        NHS: {formatNHSNumber(patient.nhs_number)}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleViewPatient(patient)}
                      className="p-2 text-nhs-blue hover:bg-blue-50 rounded-md transition-colors"
                      title="View details"
                    >
                      <Eye className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleEditPatient(patient)}
                      className="p-2 text-nhs-mid-grey hover:bg-gray-50 rounded-md transition-colors"
                      title="Edit patient"
                    >
                      <Edit className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                <div className="space-y-2 text-sm">
                  {patient.email && (
                    <div className="flex items-center text-nhs-mid-grey">
                      <Mail className="h-4 w-4 mr-2" />
                      {patient.email}
                    </div>
                  )}
                  
                  {patient.phone_number && (
                    <div className="flex items-center text-nhs-mid-grey">
                      <Phone className="h-4 w-4 mr-2" />
                      {patient.phone_number}
                    </div>
                  )}
                  
                  {patient.date_of_birth && (
                    <div className="flex items-center text-nhs-mid-grey">
                      <Calendar className="h-4 w-4 mr-2" />
                      Age {calculateAge(patient.date_of_birth)}
                    </div>
                  )}
                  
                  {patient.address?.city && (
                    <div className="flex items-center text-nhs-mid-grey">
                      <MapPin className="h-4 w-4 mr-2" />
                      {patient.address.city}, {patient.address.postcode}
                    </div>
                  )}
                </div>

                <div className="mt-4 pt-4 border-t border-nhs-pale-grey">
                  <div className="flex justify-between text-sm">
                    <span className="text-nhs-mid-grey">Last Visit:</span>
                    <span className="text-nhs-black">
                      {patient.last_appointment_date 
                        ? formatDate(patient.last_appointment_date)
                        : 'No visits'
                      }
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Patient Details Modal */}
      {showPatientModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-10 mx-auto p-5 border max-w-4xl shadow-lg rounded-md bg-white">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-nhs-black">
                {modalType === 'create' ? 'Add New Patient' : 
                 modalType === 'edit' ? 'Edit Patient' : 'Patient Details'}
              </h3>
              <button
                onClick={() => setShowPatientModal(false)}
                className="text-nhs-mid-grey hover:text-nhs-black"
              >
                ✕
              </button>
            </div>

            {modalType === 'view' && selectedPatient && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Patient Information */}
                <div>
                  <h4 className="text-lg font-medium text-nhs-black mb-4">
                    Personal Information
                  </h4>
                  
                  <div className="space-y-4">
                    <div className="flex items-center">
                      <div className="w-16 h-16 bg-nhs-blue bg-opacity-10 rounded-full flex items-center justify-center mr-4">
                        <User className="h-8 w-8 text-nhs-blue" />
                      </div>
                      <div>
                        <h5 className="text-lg font-medium text-nhs-black">
                          {selectedPatient.first_name} {selectedPatient.last_name}
                        </h5>
                        <p className="text-nhs-mid-grey">
                          NHS: {formatNHSNumber(selectedPatient.nhs_number)}
                        </p>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <label className="font-medium text-nhs-mid-grey">Date of Birth</label>
                        <p className="text-nhs-black">{formatDate(selectedPatient.date_of_birth)}</p>
                      </div>
                      
                      <div>
                        <label className="font-medium text-nhs-mid-grey">Age</label>
                        <p className="text-nhs-black">{calculateAge(selectedPatient.date_of_birth)}</p>
                      </div>
                      
                      <div>
                        <label className="font-medium text-nhs-mid-grey">Email</label>
                        <p className="text-nhs-black">{selectedPatient.email || 'Not provided'}</p>
                      </div>
                      
                      <div>
                        <label className="font-medium text-nhs-mid-grey">Phone</label>
                        <p className="text-nhs-black">{selectedPatient.phone_number || 'Not provided'}</p>
                      </div>
                    </div>

                    {selectedPatient.address && (
                      <div>
                        <label className="font-medium text-nhs-mid-grey">Address</label>
                        <div className="text-nhs-black text-sm">
                          <p>{selectedPatient.address.line1}</p>
                          {selectedPatient.address.line2 && <p>{selectedPatient.address.line2}</p>}
                          <p>{selectedPatient.address.city} {selectedPatient.address.postcode}</p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Recent Appointments */}
                <div>
                  <h4 className="text-lg font-medium text-nhs-black mb-4">
                    Recent Appointments
                  </h4>
                  
                  {appointmentsLoading ? (
                    <LoadingSpinner size="sm" />
                  ) : patientAppointments?.length === 0 ? (
                    <p className="text-nhs-mid-grey">No appointments found</p>
                  ) : (
                    <div className="space-y-3 max-h-64 overflow-y-auto">
                      {patientAppointments?.map((appointment) => (
                        <div key={appointment.appointment_id} className="p-3 bg-nhs-pale-grey rounded-lg">
                          <div className="flex justify-between items-start">
                            <div>
                              <p className="font-medium text-nhs-black">
                                {appointment.appointment_type || 'General'}
                              </p>
                              <p className="text-sm text-nhs-mid-grey">
                                {formatDate(appointment.appointment_datetime)}
                              </p>
                              {appointment.reason && (
                                <p className="text-sm text-nhs-mid-grey mt-1">
                                  {appointment.reason}
                                </p>
                              )}
                            </div>
                            <span className={`badge ${
                              appointment.status === 'completed' ? 'badge-success' :
                              appointment.status === 'scheduled' ? 'badge-primary' :
                              appointment.status === 'cancelled' ? 'badge-error' : 'badge-grey'
                            }`}>
                              {appointment.status}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            <div className="flex justify-end space-x-3 mt-8">
              <button
                onClick={() => setShowPatientModal(false)}
                className="btn-outline"
              >
                Close
              </button>
              
              {modalType === 'view' && (
                <button
                  onClick={() => handleEditPatient(selectedPatient)}
                  className="btn-primary"
                >
                  Edit Patient
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PatientManagement;

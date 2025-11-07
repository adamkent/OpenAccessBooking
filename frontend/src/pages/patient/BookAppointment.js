import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { 
  Calendar, 
  Clock, 
  MapPin, 
  User, 
  FileText, 
  AlertCircle,
  CheckCircle,
  ArrowLeft,
  ArrowRight
} from 'lucide-react';
import { toast } from 'react-toastify';
import { useAuth } from '../../contexts/AuthContext';
import { appointmentsAPI, practicesAPI } from '../../services/api';
import LoadingSpinner from '../../components/UI/LoadingSpinner';

const BookAppointment = () => {
  const [step, setStep] = useState(1);
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [appointmentData, setAppointmentData] = useState({
    appointment_type: 'routine',
    reason: '',
    duration_minutes: 30,
    notes: ''
  });

  const { user } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Fetch user's practice
  const { data: practice, isLoading: practiceLoading } = useQuery(
    ['practice', user?.practice_id],
    () => practicesAPI.getPractice(user?.practice_id),
    {
      enabled: !!user?.practice_id,
      select: (response) => response.data
    }
  );

  // Fetch available slots for selected date
  const { 
    data: availableSlots, 
    isLoading: slotsLoading,
    refetch: refetchSlots 
  } = useQuery(
    ['available-slots', user?.practice_id, selectedDate],
    () => appointmentsAPI.getAvailableSlots(user?.practice_id, selectedDate),
    {
      enabled: !!user?.practice_id && !!selectedDate,
      select: (response) => response.data?.slots || []
    }
  );

  // Create appointment mutation
  const createAppointmentMutation = useMutation(
    (appointmentPayload) => appointmentsAPI.createAppointment(appointmentPayload),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['appointments']);
        toast.success('Appointment booked successfully!');
        navigate('/patient/appointments');
      },
      onError: (error) => {
        toast.error(error.response?.data?.error || 'Failed to book appointment');
      }
    }
  );

  const appointmentTypes = [
    { value: 'routine', label: 'Routine Check-up', duration: 30 },
    { value: 'urgent', label: 'Urgent Consultation', duration: 20 },
    { value: 'follow-up', label: 'Follow-up Appointment', duration: 15 },
    { value: 'vaccination', label: 'Vaccination', duration: 15 },
    { value: 'blood-test', label: 'Blood Test', duration: 10 },
    { value: 'other', label: 'Other', duration: 30 }
  ];

  const getMinDate = () => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split('T')[0];
  };

  const getMaxDate = () => {
    const maxDate = new Date();
    maxDate.setDate(maxDate.getDate() + 60); // 60 days from now
    return maxDate.toISOString().split('T')[0];
  };

  const handleDateChange = (date) => {
    setSelectedDate(date);
    setSelectedSlot(null);
    if (date) {
      refetchSlots();
    }
  };

  const handleSlotSelect = (slot) => {
    setSelectedSlot(slot);
  };

  const handleTypeChange = (type) => {
    const selectedType = appointmentTypes.find(t => t.value === type);
    setAppointmentData(prev => ({
      ...prev,
      appointment_type: type,
      duration_minutes: selectedType?.duration || 30
    }));
  };

  const handleSubmit = async () => {
    if (!selectedSlot || !appointmentData.reason.trim()) {
      toast.error('Please fill in all required fields');
      return;
    }

    const appointmentPayload = {
      patient_id: user.user_id,
      practice_id: user.practice_id,
      appointment_datetime: `${selectedDate}T${selectedSlot.time}:00Z`,
      appointment_type: appointmentData.appointment_type,
      reason: appointmentData.reason,
      duration_minutes: appointmentData.duration_minutes,
      notes: appointmentData.notes
    };

    createAppointmentMutation.mutate(appointmentPayload);
  };

  const formatSlotTime = (time) => {
    return new Date(`2000-01-01T${time}`).toLocaleTimeString('en-GB', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatSelectedDate = (date) => {
    return new Date(date).toLocaleDateString('en-GB', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (practiceLoading) {
    return (
      <div className="container mx-auto px-4 py-6">
        <LoadingSpinner fullScreen text="Loading practice information..." />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-6 max-w-4xl">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={() => navigate('/patient/dashboard')}
          className="flex items-center text-nhs-blue hover:text-nhs-dark-blue mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </button>
        
        <h1 className="text-3xl font-bold text-nhs-black mb-2">
          Book an Appointment
        </h1>
        <p className="text-nhs-mid-grey">
          Schedule your appointment with {practice?.name || 'your GP practice'}
        </p>
      </div>

      {/* Progress Steps */}
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
            {step > 2 ? <CheckCircle className="h-5 w-5" /> : '2'}
          </div>
          <div className={`flex-1 h-1 mx-2 ${
            step > 2 ? 'bg-nhs-blue' : 'bg-nhs-pale-grey'
          }`} />
          <div className={`flex items-center justify-center w-8 h-8 rounded-full ${
            step >= 3 ? 'bg-nhs-blue text-white' : 'bg-nhs-pale-grey text-nhs-mid-grey'
          }`}>
            3
          </div>
        </div>
        <div className="flex justify-between mt-2 text-sm">
          <span className={step >= 1 ? 'text-nhs-blue' : 'text-nhs-mid-grey'}>
            Appointment Type
          </span>
          <span className={step >= 2 ? 'text-nhs-blue' : 'text-nhs-mid-grey'}>
            Date & Time
          </span>
          <span className={step >= 3 ? 'text-nhs-blue' : 'text-nhs-mid-grey'}>
            Confirmation
          </span>
        </div>
      </div>

      {/* Step Content */}
      <div className="card">
        <div className="card-body">
          {step === 1 && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold text-nhs-black mb-4">
                What type of appointment do you need?
              </h2>

              {/* Appointment Types */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {appointmentTypes.map((type) => (
                  <button
                    key={type.value}
                    onClick={() => handleTypeChange(type.value)}
                    className={`p-4 border-2 rounded-lg text-left transition-all duration-200 ${
                      appointmentData.appointment_type === type.value
                        ? 'border-nhs-blue bg-blue-50'
                        : 'border-nhs-pale-grey hover:border-nhs-blue'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-medium text-nhs-black">
                          {type.label}
                        </h3>
                        <p className="text-sm text-nhs-mid-grey">
                          Duration: {type.duration} minutes
                        </p>
                      </div>
                      {appointmentData.appointment_type === type.value && (
                        <CheckCircle className="h-5 w-5 text-nhs-blue" />
                      )}
                    </div>
                  </button>
                ))}
              </div>

              {/* Reason */}
              <div>
                <label className="form-label">
                  Reason for appointment *
                </label>
                <textarea
                  value={appointmentData.reason}
                  onChange={(e) => setAppointmentData(prev => ({
                    ...prev,
                    reason: e.target.value
                  }))}
                  className="form-input"
                  rows="3"
                  placeholder="Please describe the reason for your appointment..."
                  required
                />
                <p className="form-help">
                  This helps your GP prepare for your appointment
                </p>
              </div>

              {/* Additional Notes */}
              <div>
                <label className="form-label">
                  Additional notes (optional)
                </label>
                <textarea
                  value={appointmentData.notes}
                  onChange={(e) => setAppointmentData(prev => ({
                    ...prev,
                    notes: e.target.value
                  }))}
                  className="form-input"
                  rows="2"
                  placeholder="Any additional information..."
                />
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold text-nhs-black mb-4">
                Choose your preferred date and time
              </h2>

              {/* Date Selection */}
              <div>
                <label className="form-label">
                  Select Date
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Calendar className="h-5 w-5 text-nhs-mid-grey" />
                  </div>
                  <input
                    type="date"
                    value={selectedDate}
                    onChange={(e) => handleDateChange(e.target.value)}
                    min={getMinDate()}
                    max={getMaxDate()}
                    className="form-input pl-10"
                    required
                  />
                </div>
                <p className="form-help">
                  Appointments can be booked up to 60 days in advance
                </p>
              </div>

              {/* Time Slots */}
              {selectedDate && (
                <div>
                  <label className="form-label">
                    Available Times for {formatSelectedDate(selectedDate)}
                  </label>
                  
                  {slotsLoading ? (
                    <div className="flex justify-center py-8">
                      <LoadingSpinner text="Loading available times..." />
                    </div>
                  ) : availableSlots?.length === 0 ? (
                    <div className="alert-warning">
                      <AlertCircle className="h-5 w-5 mr-2" />
                      No appointments available on this date. Please select another date.
                    </div>
                  ) : (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {availableSlots?.map((slot, index) => (
                        <button
                          key={index}
                          onClick={() => handleSlotSelect(slot)}
                          className={`p-3 border-2 rounded-lg text-center transition-all duration-200 ${
                            selectedSlot?.time === slot.time
                              ? 'border-nhs-blue bg-blue-50 text-nhs-blue'
                              : 'border-nhs-pale-grey hover:border-nhs-blue text-nhs-black'
                          }`}
                        >
                          <Clock className="h-4 w-4 mx-auto mb-1" />
                          <div className="text-sm font-medium">
                            {formatSlotTime(slot.time)}
                          </div>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {step === 3 && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold text-nhs-black mb-4">
                Confirm your appointment
              </h2>

              {/* Appointment Summary */}
              <div className="bg-nhs-pale-grey rounded-lg p-6">
                <h3 className="text-lg font-medium text-nhs-black mb-4">
                  Appointment Details
                </h3>
                
                <div className="space-y-3">
                  <div className="flex items-center">
                    <User className="h-5 w-5 text-nhs-blue mr-3" />
                    <div>
                      <span className="font-medium">Type: </span>
                      {appointmentTypes.find(t => t.value === appointmentData.appointment_type)?.label}
                    </div>
                  </div>
                  
                  <div className="flex items-center">
                    <Calendar className="h-5 w-5 text-nhs-blue mr-3" />
                    <div>
                      <span className="font-medium">Date: </span>
                      {formatSelectedDate(selectedDate)}
                    </div>
                  </div>
                  
                  <div className="flex items-center">
                    <Clock className="h-5 w-5 text-nhs-blue mr-3" />
                    <div>
                      <span className="font-medium">Time: </span>
                      {selectedSlot && formatSlotTime(selectedSlot.time)}
                    </div>
                  </div>
                  
                  <div className="flex items-center">
                    <MapPin className="h-5 w-5 text-nhs-blue mr-3" />
                    <div>
                      <span className="font-medium">Practice: </span>
                      {practice?.name}
                    </div>
                  </div>
                  
                  <div className="flex items-start">
                    <FileText className="h-5 w-5 text-nhs-blue mr-3 mt-0.5" />
                    <div>
                      <span className="font-medium">Reason: </span>
                      {appointmentData.reason}
                    </div>
                  </div>
                  
                  {appointmentData.notes && (
                    <div className="flex items-start">
                      <FileText className="h-5 w-5 text-nhs-blue mr-3 mt-0.5" />
                      <div>
                        <span className="font-medium">Notes: </span>
                        {appointmentData.notes}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Important Information */}
              <div className="alert-info">
                <AlertCircle className="h-5 w-5 mr-2" />
                <div>
                  <p className="font-medium">Important Information:</p>
                  <ul className="text-sm mt-1 space-y-1">
                    <li>• Please arrive 10 minutes before your appointment</li>
                    <li>• Bring a valid form of ID and your NHS card</li>
                    <li>• You can cancel or reschedule up to 2 hours before</li>
                    <li>• You'll receive SMS and email confirmations</li>
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Navigation Buttons */}
        <div className="card-footer">
          <div className="flex justify-between">
            <button
              onClick={() => {
                if (step > 1) setStep(step - 1);
                else navigate('/patient/dashboard');
              }}
              className="btn-outline flex items-center"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              {step === 1 ? 'Cancel' : 'Back'}
            </button>

            <button
              onClick={() => {
                if (step < 3) {
                  if (step === 1 && !appointmentData.reason.trim()) {
                    toast.error('Please provide a reason for your appointment');
                    return;
                  }
                  if (step === 2 && (!selectedDate || !selectedSlot)) {
                    toast.error('Please select a date and time');
                    return;
                  }
                  setStep(step + 1);
                } else {
                  handleSubmit();
                }
              }}
              disabled={createAppointmentMutation.isLoading}
              className="btn-primary flex items-center"
            >
              {createAppointmentMutation.isLoading ? (
                <>
                  <LoadingSpinner size="sm" color="white" />
                  <span className="ml-2">Booking...</span>
                </>
              ) : step === 3 ? (
                'Confirm Booking'
              ) : (
                <>
                  Continue
                  <ArrowRight className="h-4 w-4 ml-2" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BookAppointment;

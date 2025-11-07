import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { 
  User, 
  Mail, 
  Phone, 
  MapPin, 
  Calendar, 
  Edit, 
  Save, 
  X,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import { toast } from 'react-toastify';
import { useAuth } from '../../contexts/AuthContext';
import { patientsAPI } from '../../services/api';
import LoadingSpinner from '../../components/UI/LoadingSpinner';

const MyProfile = () => {
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({});
  const { user } = useAuth();
  const queryClient = useQueryClient();

  // Fetch patient profile
  const { data: profile, isLoading } = useQuery(
    ['patient', user?.user_id],
    () => patientsAPI.getPatient(user?.user_id),
    {
      enabled: !!user?.user_id,
      select: (response) => response.data,
      onSuccess: (data) => {
        setFormData(data);
      }
    }
  );

  // Update profile mutation
  const updateMutation = useMutation(
    (updateData) => patientsAPI.updatePatient(user?.user_id, updateData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['patient', user?.user_id]);
        setIsEditing(false);
        toast.success('Profile updated successfully');
      },
      onError: (error) => {
        toast.error(error.response?.data?.error || 'Failed to update profile');
      }
    }
  );

  const handleEdit = () => {
    setFormData(profile);
    setIsEditing(true);
  };

  const handleCancel = () => {
    setFormData(profile);
    setIsEditing(false);
  };

  const handleSave = () => {
    updateMutation.mutate(formData);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
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
        [name]: value
      }));
    }
  };

  const validatePostcode = (postcode) => {
    const ukPostcodeRegex = /^[A-Z]{1,2}[0-9][A-Z0-9]?\s?[0-9][A-Z]{2}$/i;
    return ukPostcodeRegex.test(postcode);
  };

  const formatNHSNumber = (nhsNumber) => {
    if (!nhsNumber) return '';
    const cleaned = nhsNumber.replace(/\s/g, '');
    const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
    if (match) {
      return `${match[1]} ${match[2]} ${match[3]}`;
    }
    return nhsNumber;
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-6">
        <LoadingSpinner fullScreen text="Loading profile..." />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-6 max-w-4xl">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-nhs-black mb-2">My Profile</h1>
            <p className="text-nhs-mid-grey">Manage your personal information</p>
          </div>
          
          {!isEditing && (
            <button
              onClick={handleEdit}
              className="btn-primary flex items-center"
            >
              <Edit className="h-4 w-4 mr-2" />
              Edit Profile
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Profile Summary */}
        <div className="lg:col-span-1">
          <div className="card">
            <div className="card-body text-center">
              <div className="w-20 h-20 bg-nhs-blue rounded-full flex items-center justify-center mx-auto mb-4">
                <User className="h-10 w-10 text-white" />
              </div>
              
              <h2 className="text-xl font-semibold text-nhs-black mb-2">
                {profile?.first_name} {profile?.last_name}
              </h2>
              
              <p className="text-nhs-mid-grey mb-4">
                NHS Number: {formatNHSNumber(profile?.nhs_number)}
              </p>
              
              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-center text-nhs-mid-grey">
                  <Mail className="h-4 w-4 mr-2" />
                  {profile?.email}
                </div>
                
                {profile?.phone_number && (
                  <div className="flex items-center justify-center text-nhs-mid-grey">
                    <Phone className="h-4 w-4 mr-2" />
                    {profile?.phone_number}
                  </div>
                )}
                
                {profile?.date_of_birth && (
                  <div className="flex items-center justify-center text-nhs-mid-grey">
                    <Calendar className="h-4 w-4 mr-2" />
                    {new Date(profile?.date_of_birth).toLocaleDateString('en-GB')}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="card mt-6">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-nhs-black">Account Status</h3>
            </div>
            <div className="card-body">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-nhs-mid-grey">Account Status</span>
                  <span className="badge badge-success">Active</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-nhs-mid-grey">Email Verified</span>
                  <CheckCircle className="h-5 w-5 text-nhs-green" />
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-nhs-mid-grey">Profile Complete</span>
                  <span className="text-nhs-blue font-medium">95%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Profile Details */}
        <div className="lg:col-span-2">
          <div className="card">
            <div className="card-header">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-nhs-black">Personal Information</h3>
                
                {isEditing && (
                  <div className="flex space-x-2">
                    <button
                      onClick={handleCancel}
                      className="btn-outline btn-sm flex items-center"
                    >
                      <X className="h-4 w-4 mr-1" />
                      Cancel
                    </button>
                    
                    <button
                      onClick={handleSave}
                      disabled={updateMutation.isLoading}
                      className="btn-primary btn-sm flex items-center"
                    >
                      {updateMutation.isLoading ? (
                        <LoadingSpinner size="sm" color="white" />
                      ) : (
                        <Save className="h-4 w-4 mr-1" />
                      )}
                      Save
                    </button>
                  </div>
                )}
              </div>
            </div>
            
            <div className="card-body">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* First Name */}
                <div>
                  <label className="form-label">First Name</label>
                  {isEditing ? (
                    <input
                      type="text"
                      name="first_name"
                      value={formData.first_name || ''}
                      onChange={handleChange}
                      className="form-input"
                    />
                  ) : (
                    <p className="text-nhs-black">{profile?.first_name || 'Not provided'}</p>
                  )}
                </div>

                {/* Last Name */}
                <div>
                  <label className="form-label">Last Name</label>
                  {isEditing ? (
                    <input
                      type="text"
                      name="last_name"
                      value={formData.last_name || ''}
                      onChange={handleChange}
                      className="form-input"
                    />
                  ) : (
                    <p className="text-nhs-black">{profile?.last_name || 'Not provided'}</p>
                  )}
                </div>

                {/* Email */}
                <div>
                  <label className="form-label">Email Address</label>
                  <p className="text-nhs-black">{profile?.email}</p>
                  <p className="form-help">Contact support to change your email address</p>
                </div>

                {/* NHS Number */}
                <div>
                  <label className="form-label">NHS Number</label>
                  <p className="text-nhs-black">{formatNHSNumber(profile?.nhs_number)}</p>
                  <p className="form-help">NHS numbers cannot be changed</p>
                </div>

                {/* Date of Birth */}
                <div>
                  <label className="form-label">Date of Birth</label>
                  {isEditing ? (
                    <input
                      type="date"
                      name="date_of_birth"
                      value={formData.date_of_birth || ''}
                      onChange={handleChange}
                      className="form-input"
                    />
                  ) : (
                    <p className="text-nhs-black">
                      {profile?.date_of_birth 
                        ? new Date(profile.date_of_birth).toLocaleDateString('en-GB')
                        : 'Not provided'
                      }
                    </p>
                  )}
                </div>

                {/* Phone Number */}
                <div>
                  <label className="form-label">Phone Number</label>
                  {isEditing ? (
                    <input
                      type="tel"
                      name="phone_number"
                      value={formData.phone_number || ''}
                      onChange={handleChange}
                      className="form-input"
                      placeholder="07123 456789"
                    />
                  ) : (
                    <p className="text-nhs-black">{profile?.phone_number || 'Not provided'}</p>
                  )}
                </div>
              </div>

              {/* Address Section */}
              <div className="mt-8">
                <h4 className="text-lg font-medium text-nhs-black mb-4 flex items-center">
                  <MapPin className="h-5 w-5 mr-2" />
                  Address
                </h4>
                
                <div className="grid grid-cols-1 gap-4">
                  <div>
                    <label className="form-label">Address Line 1</label>
                    {isEditing ? (
                      <input
                        type="text"
                        name="address.line1"
                        value={formData.address?.line1 || ''}
                        onChange={handleChange}
                        className="form-input"
                      />
                    ) : (
                      <p className="text-nhs-black">{profile?.address?.line1 || 'Not provided'}</p>
                    )}
                  </div>

                  <div>
                    <label className="form-label">Address Line 2 (Optional)</label>
                    {isEditing ? (
                      <input
                        type="text"
                        name="address.line2"
                        value={formData.address?.line2 || ''}
                        onChange={handleChange}
                        className="form-input"
                      />
                    ) : (
                      <p className="text-nhs-black">{profile?.address?.line2 || 'Not provided'}</p>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="form-label">City</label>
                      {isEditing ? (
                        <input
                          type="text"
                          name="address.city"
                          value={formData.address?.city || ''}
                          onChange={handleChange}
                          className="form-input"
                        />
                      ) : (
                        <p className="text-nhs-black">{profile?.address?.city || 'Not provided'}</p>
                      )}
                    </div>

                    <div>
                      <label className="form-label">Postcode</label>
                      {isEditing ? (
                        <input
                          type="text"
                          name="address.postcode"
                          value={formData.address?.postcode || ''}
                          onChange={handleChange}
                          className="form-input"
                        />
                      ) : (
                        <p className="text-nhs-black">{profile?.address?.postcode || 'Not provided'}</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Security Section */}
          <div className="card mt-6">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-nhs-black">Security & Privacy</h3>
            </div>
            
            <div className="card-body">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-nhs-black">Password</h4>
                    <p className="text-sm text-nhs-mid-grey">Last changed 30 days ago</p>
                  </div>
                  <button className="btn-outline btn-sm">
                    Change Password
                  </button>
                </div>

                <div className="divider"></div>

                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-nhs-black">Two-Factor Authentication</h4>
                    <p className="text-sm text-nhs-mid-grey">Add an extra layer of security</p>
                  </div>
                  <button className="btn-outline btn-sm">
                    Enable 2FA
                  </button>
                </div>

                <div className="divider"></div>

                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-nhs-black">Data Export</h4>
                    <p className="text-sm text-nhs-mid-grey">Download your personal data</p>
                  </div>
                  <button className="btn-outline btn-sm">
                    Request Export
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MyProfile;

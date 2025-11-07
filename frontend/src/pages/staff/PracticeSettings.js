import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { 
  Settings, 
  MapPin, 
  Phone, 
  Mail, 
  Clock, 
  Users, 
  Save,
  Edit,
  Plus,
  Trash2,
  AlertCircle
} from 'lucide-react';
import { toast } from 'react-toastify';
import { useAuth } from '../../contexts/AuthContext';
import { practicesAPI } from '../../services/api';
import LoadingSpinner from '../../components/UI/LoadingSpinner';

const PracticeSettings = () => {
  const [activeTab, setActiveTab] = useState('general');
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({});
  
  const { user } = useAuth();
  const queryClient = useQueryClient();

  // Fetch practice information
  const { data: practice, isLoading } = useQuery(
    ['practice', user?.practice_id],
    () => practicesAPI.getPractice(user?.practice_id),
    {
      enabled: !!user?.practice_id,
      select: (response) => response.data,
      onSuccess: (data) => {
        setFormData(data);
      }
    }
  );

  // Update practice mutation
  const updateMutation = useMutation(
    (updateData) => practicesAPI.updatePractice(user?.practice_id, updateData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['practice', user?.practice_id]);
        setIsEditing(false);
        toast.success('Practice settings updated successfully');
      },
      onError: (error) => {
        toast.error(error.response?.data?.error || 'Failed to update settings');
      }
    }
  );

  const handleEdit = () => {
    setFormData(practice);
    setIsEditing(true);
  };

  const handleCancel = () => {
    setFormData(practice);
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
    } else if (name.startsWith('operating_hours.')) {
      const [day, field] = name.split('.').slice(1);
      setFormData(prev => ({
        ...prev,
        operating_hours: {
          ...prev.operating_hours,
          [day]: {
            ...prev.operating_hours?.[day],
            [field]: value
          }
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const tabs = [
    { id: 'general', label: 'General Information', icon: Settings },
    { id: 'contact', label: 'Contact Details', icon: Phone },
    { id: 'hours', label: 'Operating Hours', icon: Clock },
    { id: 'services', label: 'Services', icon: Users }
  ];

  const daysOfWeek = [
    { key: 'monday', label: 'Monday' },
    { key: 'tuesday', label: 'Tuesday' },
    { key: 'wednesday', label: 'Wednesday' },
    { key: 'thursday', label: 'Thursday' },
    { key: 'friday', label: 'Friday' },
    { key: 'saturday', label: 'Saturday' },
    { key: 'sunday', label: 'Sunday' }
  ];

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-6">
        <LoadingSpinner fullScreen text="Loading practice settings..." />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-6 max-w-6xl">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-nhs-black mb-2">
              Practice Settings
            </h1>
            <p className="text-nhs-mid-grey">
              Manage your practice information and configuration
            </p>
          </div>
          
          {!isEditing && user?.role === 'admin' && (
            <button
              onClick={handleEdit}
              className="btn-primary flex items-center"
            >
              <Edit className="h-4 w-4 mr-2" />
              Edit Settings
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Sidebar Navigation */}
        <div className="lg:col-span-1">
          <nav className="space-y-2">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center px-4 py-3 text-left rounded-lg transition-colors ${
                    activeTab === tab.id
                      ? 'bg-nhs-blue text-white'
                      : 'text-nhs-mid-grey hover:bg-nhs-pale-grey hover:text-nhs-blue'
                  }`}
                >
                  <Icon className="h-5 w-5 mr-3" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3">
          <div className="card">
            {isEditing && (
              <div className="card-header">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-nhs-black">
                    Editing Practice Settings
                  </h3>
                  <div className="flex space-x-2">
                    <button
                      onClick={handleCancel}
                      className="btn-outline btn-sm"
                    >
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
                      Save Changes
                    </button>
                  </div>
                </div>
              </div>
            )}

            <div className="card-body">
              {/* General Information Tab */}
              {activeTab === 'general' && (
                <div className="space-y-6">
                  <h3 className="text-xl font-semibold text-nhs-black mb-4">
                    General Information
                  </h3>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="form-label">Practice Name</label>
                      {isEditing ? (
                        <input
                          type="text"
                          name="name"
                          value={formData.name || ''}
                          onChange={handleChange}
                          className="form-input"
                        />
                      ) : (
                        <p className="text-nhs-black">{practice?.name || 'Not provided'}</p>
                      )}
                    </div>

                    <div>
                      <label className="form-label">Practice Code</label>
                      <p className="text-nhs-black">{practice?.practice_code || 'Not assigned'}</p>
                      <p className="form-help">Practice codes cannot be changed</p>
                    </div>

                    <div>
                      <label className="form-label">Registration Date</label>
                      <p className="text-nhs-black">
                        {practice?.created_at 
                          ? new Date(practice.created_at).toLocaleDateString('en-GB')
                          : 'Not available'
                        }
                      </p>
                    </div>

                    <div>
                      <label className="form-label">Status</label>
                      <span className="badge badge-success">Active</span>
                    </div>
                  </div>

                  {isEditing && (
                    <div>
                      <label className="form-label">Description</label>
                      <textarea
                        name="description"
                        value={formData.description || ''}
                        onChange={handleChange}
                        className="form-input"
                        rows="3"
                        placeholder="Brief description of your practice..."
                      />
                    </div>
                  )}
                </div>
              )}

              {/* Contact Details Tab */}
              {activeTab === 'contact' && (
                <div className="space-y-6">
                  <h3 className="text-xl font-semibold text-nhs-black mb-4">
                    Contact Details
                  </h3>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="form-label">Phone Number</label>
                      {isEditing ? (
                        <input
                          type="tel"
                          name="phone"
                          value={formData.phone || ''}
                          onChange={handleChange}
                          className="form-input"
                          placeholder="020 7123 4567"
                        />
                      ) : (
                        <p className="text-nhs-black">{practice?.phone || 'Not provided'}</p>
                      )}
                    </div>

                    <div>
                      <label className="form-label">Email Address</label>
                      {isEditing ? (
                        <input
                          type="email"
                          name="email"
                          value={formData.email || ''}
                          onChange={handleChange}
                          className="form-input"
                          placeholder="practice@example.com"
                        />
                      ) : (
                        <p className="text-nhs-black">{practice?.email || 'Not provided'}</p>
                      )}
                    </div>

                    <div>
                      <label className="form-label">Fax Number</label>
                      {isEditing ? (
                        <input
                          type="tel"
                          name="fax"
                          value={formData.fax || ''}
                          onChange={handleChange}
                          className="form-input"
                          placeholder="020 7123 4568"
                        />
                      ) : (
                        <p className="text-nhs-black">{practice?.fax || 'Not provided'}</p>
                      )}
                    </div>

                    <div>
                      <label className="form-label">Website</label>
                      {isEditing ? (
                        <input
                          type="url"
                          name="website"
                          value={formData.website || ''}
                          onChange={handleChange}
                          className="form-input"
                          placeholder="https://www.practice.co.uk"
                        />
                      ) : (
                        <p className="text-nhs-black">{practice?.website || 'Not provided'}</p>
                      )}
                    </div>
                  </div>

                  {/* Address */}
                  <div>
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
                          <p className="text-nhs-black">{practice?.address?.line1 || 'Not provided'}</p>
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
                          <p className="text-nhs-black">{practice?.address?.line2 || 'Not provided'}</p>
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
                            <p className="text-nhs-black">{practice?.address?.city || 'Not provided'}</p>
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
                            <p className="text-nhs-black">{practice?.address?.postcode || 'Not provided'}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Operating Hours Tab */}
              {activeTab === 'hours' && (
                <div className="space-y-6">
                  <h3 className="text-xl font-semibold text-nhs-black mb-4">
                    Operating Hours
                  </h3>

                  <div className="space-y-4">
                    {daysOfWeek.map((day) => (
                      <div key={day.key} className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
                        <div className="font-medium text-nhs-black">
                          {day.label}
                        </div>
                        
                        {isEditing ? (
                          <>
                            <div>
                              <input
                                type="time"
                                name={`operating_hours.${day.key}.open`}
                                value={formData.operating_hours?.[day.key]?.open || ''}
                                onChange={handleChange}
                                className="form-input"
                              />
                            </div>
                            <div>
                              <input
                                type="time"
                                name={`operating_hours.${day.key}.close`}
                                value={formData.operating_hours?.[day.key]?.close || ''}
                                onChange={handleChange}
                                className="form-input"
                              />
                            </div>
                            <div>
                              <label className="flex items-center">
                                <input
                                  type="checkbox"
                                  name={`operating_hours.${day.key}.closed`}
                                  checked={formData.operating_hours?.[day.key]?.closed || false}
                                  onChange={(e) => handleChange({
                                    target: {
                                      name: `operating_hours.${day.key}.closed`,
                                      value: e.target.checked
                                    }
                                  })}
                                  className="mr-2"
                                />
                                Closed
                              </label>
                            </div>
                          </>
                        ) : (
                          <div className="md:col-span-3 text-nhs-mid-grey">
                            {practice?.operating_hours?.[day.key]?.closed ? (
                              'Closed'
                            ) : practice?.operating_hours?.[day.key]?.open ? (
                              `${practice.operating_hours[day.key].open} - ${practice.operating_hours[day.key].close}`
                            ) : (
                              'Not set'
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>

                  {!isEditing && (
                    <div className="alert-info">
                      <AlertCircle className="h-5 w-5 mr-2" />
                      <div>
                        <p className="font-medium">Operating Hours Information</p>
                        <p className="text-sm mt-1">
                          These hours are displayed to patients when booking appointments. 
                          Make sure they reflect your actual availability.
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Services Tab */}
              {activeTab === 'services' && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xl font-semibold text-nhs-black">
                      Services Offered
                    </h3>
                    {isEditing && (
                      <button className="btn-outline btn-sm flex items-center">
                        <Plus className="h-4 w-4 mr-1" />
                        Add Service
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {practice?.services?.map((service, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-nhs-pale-grey rounded-lg">
                        <span className="text-nhs-black">{service}</span>
                        {isEditing && (
                          <button className="text-nhs-red hover:text-red-700">
                            <Trash2 className="h-4 w-4" />
                          </button>
                        )}
                      </div>
                    )) || (
                      <p className="text-nhs-mid-grey col-span-2">No services listed</p>
                    )}
                  </div>

                  {!isEditing && (
                    <div className="alert-info">
                      <AlertCircle className="h-5 w-5 mr-2" />
                      <div>
                        <p className="font-medium">Services Information</p>
                        <p className="text-sm mt-1">
                          List the medical services your practice offers. This helps patients 
                          understand what appointments they can book.
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PracticeSettings;

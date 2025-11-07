// Date utility functions for NHS appointment booking system

/**
 * Format date for display in various formats
 */
export const formatDate = (date, format = 'short') => {
  if (!date) return '';
  
  const dateObj = new Date(date);
  if (isNaN(dateObj.getTime())) return '';
  
  const formats = {
    short: { day: 'numeric', month: 'short', year: 'numeric' },
    long: { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' },
    numeric: { day: '2-digit', month: '2-digit', year: 'numeric' },
    time: { hour: '2-digit', minute: '2-digit' },
    datetime: { 
      weekday: 'short', 
      day: 'numeric', 
      month: 'short', 
      year: 'numeric',
      hour: '2-digit', 
      minute: '2-digit' 
    }
  };
  
  return dateObj.toLocaleDateString('en-GB', formats[format]);
};

/**
 * Format time for display
 */
export const formatTime = (time) => {
  if (!time) return '';
  
  // Handle time string (HH:MM) or Date object
  let timeObj;
  if (typeof time === 'string') {
    timeObj = new Date(`2000-01-01T${time}`);
  } else {
    timeObj = new Date(time);
  }
  
  if (isNaN(timeObj.getTime())) return '';
  
  return timeObj.toLocaleTimeString('en-GB', {
    hour: '2-digit',
    minute: '2-digit'
  });
};

/**
 * Get relative time (e.g., "2 hours ago", "in 3 days")
 */
export const getRelativeTime = (date) => {
  if (!date) return '';
  
  const dateObj = new Date(date);
  const now = new Date();
  const diffMs = dateObj.getTime() - now.getTime();
  const diffMins = Math.round(diffMs / (1000 * 60));
  const diffHours = Math.round(diffMs / (1000 * 60 * 60));
  const diffDays = Math.round(diffMs / (1000 * 60 * 60 * 24));
  
  if (Math.abs(diffMins) < 60) {
    if (diffMins === 0) return 'now';
    return diffMins > 0 ? `in ${diffMins} minutes` : `${Math.abs(diffMins)} minutes ago`;
  }
  
  if (Math.abs(diffHours) < 24) {
    return diffHours > 0 ? `in ${diffHours} hours` : `${Math.abs(diffHours)} hours ago`;
  }
  
  if (Math.abs(diffDays) < 7) {
    return diffDays > 0 ? `in ${diffDays} days` : `${Math.abs(diffDays)} days ago`;
  }
  
  return formatDate(date, 'short');
};

/**
 * Check if date is today
 */
export const isToday = (date) => {
  if (!date) return false;
  
  const dateObj = new Date(date);
  const today = new Date();
  
  return dateObj.toDateString() === today.toDateString();
};

/**
 * Check if date is tomorrow
 */
export const isTomorrow = (date) => {
  if (!date) return false;
  
  const dateObj = new Date(date);
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  
  return dateObj.toDateString() === tomorrow.toDateString();
};

/**
 * Check if date is in the past
 */
export const isPast = (date) => {
  if (!date) return false;
  
  const dateObj = new Date(date);
  const now = new Date();
  
  return dateObj < now;
};

/**
 * Check if date is in the future
 */
export const isFuture = (date) => {
  if (!date) return false;
  
  const dateObj = new Date(date);
  const now = new Date();
  
  return dateObj > now;
};

/**
 * Get age from date of birth
 */
export const calculateAge = (dateOfBirth) => {
  if (!dateOfBirth) return null;
  
  const dob = new Date(dateOfBirth);
  const today = new Date();
  
  let age = today.getFullYear() - dob.getFullYear();
  const monthDiff = today.getMonth() - dob.getMonth();
  
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dob.getDate())) {
    age--;
  }
  
  return age;
};

/**
 * Get date range for common periods
 */
export const getDateRange = (period) => {
  const today = new Date();
  const startDate = new Date(today);
  const endDate = new Date(today);
  
  switch (period) {
    case 'today':
      break;
    case 'yesterday':
      startDate.setDate(today.getDate() - 1);
      endDate.setDate(today.getDate() - 1);
      break;
    case 'tomorrow':
      startDate.setDate(today.getDate() + 1);
      endDate.setDate(today.getDate() + 1);
      break;
    case 'week':
      startDate.setDate(today.getDate() - today.getDay());
      endDate.setDate(startDate.getDate() + 6);
      break;
    case 'month':
      startDate.setDate(1);
      endDate.setMonth(endDate.getMonth() + 1, 0);
      break;
    case 'year':
      startDate.setMonth(0, 1);
      endDate.setMonth(11, 31);
      break;
    default:
      break;
  }
  
  return {
    start: startDate.toISOString().split('T')[0],
    end: endDate.toISOString().split('T')[0]
  };
};

/**
 * Generate time slots for a given date
 */
export const generateTimeSlots = (startTime = '09:00', endTime = '17:00', interval = 30) => {
  const slots = [];
  const start = new Date(`2000-01-01T${startTime}`);
  const end = new Date(`2000-01-01T${endTime}`);
  
  let current = new Date(start);
  
  while (current < end) {
    slots.push(current.toTimeString().slice(0, 5));
    current.setMinutes(current.getMinutes() + interval);
  }
  
  return slots;
};

/**
 * Check if time slot is available (not in the past for today)
 */
export const isTimeSlotAvailable = (date, time) => {
  if (!date || !time) return false;
  
  const slotDateTime = new Date(`${date}T${time}`);
  const now = new Date();
  
  // Add buffer time (e.g., 2 hours) for same-day appointments
  const bufferTime = new Date(now.getTime() + (2 * 60 * 60 * 1000));
  
  return slotDateTime > bufferTime;
};

/**
 * Get next available date (excluding weekends and holidays)
 */
export const getNextAvailableDate = (excludeWeekends = true, holidays = []) => {
  const date = new Date();
  date.setDate(date.getDate() + 1); // Start from tomorrow
  
  while (true) {
    const dayOfWeek = date.getDay();
    const dateString = date.toISOString().split('T')[0];
    
    // Skip weekends if required
    if (excludeWeekends && (dayOfWeek === 0 || dayOfWeek === 6)) {
      date.setDate(date.getDate() + 1);
      continue;
    }
    
    // Skip holidays
    if (holidays.includes(dateString)) {
      date.setDate(date.getDate() + 1);
      continue;
    }
    
    break;
  }
  
  return date.toISOString().split('T')[0];
};

/**
 * Format duration in minutes to human readable format
 */
export const formatDuration = (minutes) => {
  if (!minutes || minutes < 0) return '';
  
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  
  if (hours === 0) {
    return `${mins} min`;
  } else if (mins === 0) {
    return `${hours} hr`;
  } else {
    return `${hours} hr ${mins} min`;
  }
};

/**
 * Get business days between two dates
 */
export const getBusinessDaysBetween = (startDate, endDate) => {
  const start = new Date(startDate);
  const end = new Date(endDate);
  let count = 0;
  
  const current = new Date(start);
  while (current <= end) {
    const dayOfWeek = current.getDay();
    if (dayOfWeek !== 0 && dayOfWeek !== 6) { // Not Sunday or Saturday
      count++;
    }
    current.setDate(current.getDate() + 1);
  }
  
  return count;
};

/**
 * Convert UTC date to local timezone
 */
export const utcToLocal = (utcDate) => {
  if (!utcDate) return null;
  
  const date = new Date(utcDate);
  return new Date(date.getTime() - (date.getTimezoneOffset() * 60000));
};

/**
 * Convert local date to UTC
 */
export const localToUtc = (localDate) => {
  if (!localDate) return null;
  
  const date = new Date(localDate);
  return new Date(date.getTime() + (date.getTimezoneOffset() * 60000));
};

/**
 * Get day name from date
 */
export const getDayName = (date, format = 'long') => {
  if (!date) return '';
  
  const dateObj = new Date(date);
  return dateObj.toLocaleDateString('en-GB', { weekday: format });
};

/**
 * Get month name from date
 */
export const getMonthName = (date, format = 'long') => {
  if (!date) return '';
  
  const dateObj = new Date(date);
  return dateObj.toLocaleDateString('en-GB', { month: format });
};

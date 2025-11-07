import React from 'react';

const LoadingSpinner = ({ 
  size = 'md', 
  color = 'nhs-blue', 
  text = null,
  fullScreen = false 
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16'
  };

  const colorClasses = {
    'nhs-blue': 'border-nhs-blue',
    'nhs-green': 'border-nhs-green',
    'nhs-red': 'border-nhs-red',
    'white': 'border-white',
    'gray': 'border-gray-500'
  };

  const spinner = (
    <div className="flex flex-col items-center justify-center">
      <div 
        className={`
          ${sizeClasses[size]} 
          ${colorClasses[color]} 
          border-2 border-t-transparent rounded-full animate-spin
        `}
      />
      {text && (
        <p className="mt-3 text-sm text-nhs-mid-grey animate-pulse">
          {text}
        </p>
      )}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-white bg-opacity-90 flex items-center justify-center z-50">
        {spinner}
      </div>
    );
  }

  return spinner;
};

export default LoadingSpinner;

import React from 'react';
import LoadingSpinner from './LoadingSpinner';

const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  icon: Icon,
  iconPosition = 'left',
  className = '',
  onClick,
  type = 'button',
  ...props
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-md transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variantClasses = {
    primary: 'bg-nhs-blue text-white hover:bg-nhs-dark-blue focus:ring-nhs-blue',
    secondary: 'bg-nhs-pale-grey text-nhs-black hover:bg-nhs-mid-grey hover:text-white focus:ring-nhs-mid-grey',
    success: 'bg-nhs-green text-white hover:bg-nhs-dark-green focus:ring-nhs-green',
    danger: 'bg-nhs-red text-white hover:bg-red-700 focus:ring-nhs-red',
    outline: 'border-2 border-nhs-blue text-nhs-blue bg-transparent hover:bg-nhs-blue hover:text-white focus:ring-nhs-blue',
    ghost: 'text-nhs-blue bg-transparent hover:bg-nhs-blue hover:bg-opacity-10 focus:ring-nhs-blue'
  };
  
  const sizeClasses = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  };

  const isDisabled = disabled || loading;

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={isDisabled}
      className={`
        ${baseClasses}
        ${variantClasses[variant]}
        ${sizeClasses[size]}
        ${className}
      `}
      {...props}
    >
      {loading && (
        <LoadingSpinner 
          size="sm" 
          color={variant === 'outline' || variant === 'ghost' ? 'nhs-blue' : 'white'} 
        />
      )}
      
      {!loading && Icon && iconPosition === 'left' && (
        <Icon className={`h-4 w-4 ${children ? 'mr-2' : ''}`} />
      )}
      
      {!loading && children}
      
      {!loading && Icon && iconPosition === 'right' && (
        <Icon className={`h-4 w-4 ${children ? 'ml-2' : ''}`} />
      )}
    </button>
  );
};

export default Button;

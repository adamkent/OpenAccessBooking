import React from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error to an error reporting service
    console.error('Error caught by boundary:', error, errorInfo);
    
    this.setState({
      error: error,
      errorInfo: errorInfo
    });

    // You can also log the error to an error reporting service here
    // logErrorToService(error, errorInfo);
  }

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
          <div className="max-w-md w-full">
            <div className="bg-white rounded-lg shadow-lg p-8 text-center">
              {/* Error Icon */}
              <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-6">
                <AlertTriangle className="h-8 w-8 text-nhs-red" />
              </div>

              {/* Error Title */}
              <h1 className="text-2xl font-bold text-nhs-black mb-4">
                Something went wrong
              </h1>

              {/* Error Description */}
              <p className="text-nhs-mid-grey mb-6">
                We're sorry, but something unexpected happened. This error has been logged 
                and we're working to fix it.
              </p>

              {/* Error Details (only in development) */}
              {process.env.NODE_ENV === 'development' && this.state.error && (
                <div className="bg-gray-100 rounded-md p-4 mb-6 text-left">
                  <h3 className="text-sm font-medium text-gray-800 mb-2">
                    Error Details:
                  </h3>
                  <pre className="text-xs text-gray-600 overflow-auto max-h-32">
                    {this.state.error.toString()}
                    {this.state.errorInfo.componentStack}
                  </pre>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <button
                  onClick={this.handleReload}
                  className="btn-primary flex items-center justify-center"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Reload Page
                </button>
                
                <button
                  onClick={this.handleGoHome}
                  className="btn-outline flex items-center justify-center"
                >
                  <Home className="h-4 w-4 mr-2" />
                  Go Home
                </button>
              </div>

              {/* Support Information */}
              <div className="mt-8 pt-6 border-t border-gray-200">
                <p className="text-sm text-nhs-mid-grey">
                  If this problem persists, please contact support at{' '}
                  <a 
                    href="mailto:support@nhs-appointments.uk" 
                    className="text-nhs-blue hover:underline"
                  >
                    support@nhs-appointments.uk
                  </a>
                </p>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

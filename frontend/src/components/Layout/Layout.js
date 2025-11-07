import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  Calendar, 
  User, 
  Settings, 
  LogOut, 
  Menu, 
  X, 
  Home,
  Users,
  Clock,
  FileText
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const Layout = ({ children, userType = 'patient' }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  // Navigation items based on user type
  const getNavigationItems = () => {
    if (userType === 'staff') {
      return [
        { name: 'Dashboard', href: '/staff/dashboard', icon: Home },
        { name: 'Appointments', href: '/staff/appointments', icon: Calendar },
        { name: 'Patients', href: '/staff/patients', icon: Users },
        { name: 'Settings', href: '/staff/settings', icon: Settings },
      ];
    } else {
      return [
        { name: 'Dashboard', href: '/patient/dashboard', icon: Home },
        { name: 'Book Appointment', href: '/patient/book-appointment', icon: Calendar },
        { name: 'My Appointments', href: '/patient/appointments', icon: Clock },
        { name: 'My Profile', href: '/patient/profile', icon: User },
      ];
    }
  };

  const navigationItems = getNavigationItems();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        >
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75" />
        </div>
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex items-center justify-between h-16 px-6 bg-nhs-blue">
          <div className="flex items-center">
            <div className="text-white font-bold text-lg">
              NHS Appointments
            </div>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden text-white hover:text-gray-200"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <nav className="mt-8">
          <div className="px-4 space-y-2">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.href;
              
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`
                    flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors duration-200
                    ${isActive 
                      ? 'bg-nhs-blue text-white' 
                      : 'text-nhs-dark-grey hover:bg-nhs-pale-grey hover:text-nhs-blue'
                    }
                  `}
                  onClick={() => setSidebarOpen(false)}
                >
                  <Icon className="mr-3 h-5 w-5" />
                  {item.name}
                </Link>
              );
            })}
          </div>

          {/* User info and logout */}
          <div className="mt-8 pt-8 border-t border-nhs-pale-grey">
            <div className="px-4 mb-4">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="h-8 w-8 bg-nhs-blue rounded-full flex items-center justify-center">
                    <User className="h-4 w-4 text-white" />
                  </div>
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-nhs-black">
                    {user?.first_name || user?.email?.split('@')[0] || 'User'}
                  </p>
                  <p className="text-xs text-nhs-mid-grey capitalize">
                    {user?.role || 'Patient'}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="px-4">
              <button
                onClick={handleLogout}
                className="flex items-center w-full px-4 py-3 text-sm font-medium text-nhs-red hover:bg-red-50 rounded-lg transition-colors duration-200"
              >
                <LogOut className="mr-3 h-5 w-5" />
                Sign Out
              </button>
            </div>
          </div>
        </nav>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top header */}
        <header className="bg-white shadow-sm border-b border-nhs-pale-grey">
          <div className="flex items-center justify-between h-16 px-6">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden text-nhs-dark-grey hover:text-nhs-blue"
            >
              <Menu className="h-6 w-6" />
            </button>

            <div className="flex items-center space-x-4">
              <div className="hidden sm:block">
                <h1 className="text-lg font-semibold text-nhs-black">
                  {userType === 'staff' ? 'Practice Portal' : 'Patient Portal'}
                </h1>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* Notifications placeholder */}
              <div className="relative">
                <button className="p-2 text-nhs-mid-grey hover:text-nhs-blue rounded-full hover:bg-nhs-pale-grey">
                  <FileText className="h-5 w-5" />
                </button>
              </div>

              {/* User menu for mobile */}
              <div className="lg:hidden">
                <button className="flex items-center p-2 text-nhs-mid-grey hover:text-nhs-blue rounded-full hover:bg-nhs-pale-grey">
                  <User className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1">
          <div className="py-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;

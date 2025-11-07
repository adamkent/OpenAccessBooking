import React from 'react';
import { Link } from 'react-router-dom';
import { Heart, Phone, Mail, MapPin } from 'lucide-react';

const PublicLayout = ({ children }) => {
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="nhs-header">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            {/* NHS Logo and Title */}
            <Link to="/" className="flex items-center space-x-3">
              <div className="flex items-center justify-center w-10 h-10 bg-white rounded">
                <Heart className="h-6 w-6 text-nhs-blue" />
              </div>
              <div>
                <div className="nhs-logo">NHS</div>
                <div className="text-sm opacity-90">Appointment Booking</div>
              </div>
            </Link>

            {/* Navigation */}
            <nav className="hidden md:flex items-center space-x-6">
              <Link 
                to="/" 
                className="text-white hover:text-nhs-pale-grey transition-colors duration-200"
              >
                Home
              </Link>
              <Link 
                to="/about" 
                className="text-white hover:text-nhs-pale-grey transition-colors duration-200"
              >
                About
              </Link>
              <Link 
                to="/help" 
                className="text-white hover:text-nhs-pale-grey transition-colors duration-200"
              >
                Help
              </Link>
            </nav>

            {/* Auth Buttons */}
            <div className="flex items-center space-x-4">
              <Link 
                to="/login" 
                className="text-white hover:text-nhs-pale-grey transition-colors duration-200"
              >
                Sign In
              </Link>
              <Link 
                to="/register" 
                className="bg-white text-nhs-blue px-4 py-2 rounded-md hover:bg-nhs-pale-grey transition-colors duration-200 font-medium"
              >
                Register
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-nhs-dark-grey text-white">
        <div className="container mx-auto px-4 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {/* NHS Info */}
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center space-x-3 mb-4">
                <div className="flex items-center justify-center w-8 h-8 bg-nhs-blue rounded">
                  <Heart className="h-5 w-5 text-white" />
                </div>
                <div className="text-xl font-bold">NHS Appointment Booking</div>
              </div>
              <p className="text-gray-300 mb-4 max-w-md">
                Book and manage your GP appointments online. Part of the NHS digital transformation 
                to make healthcare more accessible and convenient for everyone.
              </p>
              <div className="flex space-x-4">
                <a 
                  href="https://www.nhs.uk" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-nhs-light-blue hover:text-white transition-colors duration-200"
                >
                  NHS.UK
                </a>
                <a 
                  href="https://digital.nhs.uk" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-nhs-light-blue hover:text-white transition-colors duration-200"
                >
                  NHS Digital
                </a>
              </div>
            </div>

            {/* Quick Links */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Quick Links</h3>
              <ul className="space-y-2">
                <li>
                  <Link 
                    to="/register" 
                    className="text-gray-300 hover:text-white transition-colors duration-200"
                  >
                    Register for Account
                  </Link>
                </li>
                <li>
                  <Link 
                    to="/help" 
                    className="text-gray-300 hover:text-white transition-colors duration-200"
                  >
                    Help & Support
                  </Link>
                </li>
                <li>
                  <a 
                    href="#" 
                    className="text-gray-300 hover:text-white transition-colors duration-200"
                  >
                    Find Your GP
                  </a>
                </li>
                <li>
                  <a 
                    href="#" 
                    className="text-gray-300 hover:text-white transition-colors duration-200"
                  >
                    Emergency Services
                  </a>
                </li>
              </ul>
            </div>

            {/* Contact Info */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Support</h3>
              <ul className="space-y-3">
                <li className="flex items-center space-x-3">
                  <Phone className="h-4 w-4 text-nhs-light-blue" />
                  <span className="text-gray-300">111 (NHS Non-Emergency)</span>
                </li>
                <li className="flex items-center space-x-3">
                  <Phone className="h-4 w-4 text-nhs-red" />
                  <span className="text-gray-300">999 (Emergency)</span>
                </li>
                <li className="flex items-center space-x-3">
                  <Mail className="h-4 w-4 text-nhs-light-blue" />
                  <span className="text-gray-300">fakesupportemail@nhs-appointments.uk</span>
                </li>
                <li className="flex items-start space-x-3">
                  <MapPin className="h-4 w-4 text-nhs-light-blue mt-1" />
                  <span className="text-gray-300">
                    NHS Digital<br />
                    7 & 8 Wellington Place<br />
                    Leeds LS1 4AP
                  </span>
                </li>
              </ul>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="border-t border-gray-600 mt-8 pt-8">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <div className="text-gray-400 text-sm mb-4 md:mb-0">
                © 2025 NHS Digital. All rights reserved. This is a prototype system.
              </div>
              <div className="flex space-x-6 text-sm">
                <a 
                  href="#" 
                  className="text-gray-400 hover:text-white transition-colors duration-200"
                >
                  Privacy Policy
                </a>
                <a 
                  href="#" 
                  className="text-gray-400 hover:text-white transition-colors duration-200"
                >
                  Terms of Service
                </a>
                <a 
                  href="#" 
                  className="text-gray-400 hover:text-white transition-colors duration-200"
                >
                  Accessibility
                </a>
                <a 
                  href="#" 
                  className="text-gray-400 hover:text-white transition-colors duration-200"
                >
                  Cookies
                </a>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default PublicLayout;

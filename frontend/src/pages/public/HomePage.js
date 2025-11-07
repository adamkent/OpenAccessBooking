import React from 'react';
import { Link } from 'react-router-dom';
import { Calendar, ArrowRight } from 'lucide-react';

const HomePage = () => {
  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <section className="bg-nhs-blue text-white">
        <div className="container mx-auto px-4 py-16">
          <div className="max-w-3xl mx-auto">
            <h1 className="text-4xl md:text-5xl font-bold mb-6">
              NHS Appointment Booking
            </h1>
            
            <p className="text-xl mb-8 text-blue-100">
              Book, manage, and view your GP appointments online.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4">
              <Link 
                to="/register" 
                className="btn-lg bg-white text-nhs-blue hover:bg-nhs-pale-grey inline-flex items-center justify-center font-semibold"
              >
                Create an account
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
              
              <Link 
                to="/login" 
                className="btn-lg border-2 border-white text-white bg-transparent hover:bg-white hover:text-nhs-blue inline-flex items-center justify-center font-semibold"
              >
                Sign in
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* What you can do */}
      <section className="section">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto">
            <h2 className="text-3xl font-bold text-nhs-black mb-8">
              What you can do
            </h2>

            <div className="space-y-6">
              <div className="border-l-4 border-nhs-blue pl-6 py-2">
                <h3 className="text-xl font-semibold text-nhs-black mb-2">
                  Book appointments
                </h3>
                <p className="text-nhs-mid-grey">
                  Find available appointment slots and book online, 24 hours a day.
                </p>
              </div>

              <div className="border-l-4 border-nhs-blue pl-6 py-2">
                <h3 className="text-xl font-semibold text-nhs-black mb-2">
                  Manage your appointments
                </h3>
                <p className="text-nhs-mid-grey">
                  View, reschedule, or cancel your upcoming appointments.
                </p>
              </div>

              <div className="border-l-4 border-nhs-blue pl-6 py-2">
                <h3 className="text-xl font-semibold text-nhs-black mb-2">
                  Update your details
                </h3>
                <p className="text-nhs-mid-grey">
                  Keep your contact information and medical details up to date.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Before you start */}
      <section className="section bg-nhs-pale-grey">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto">
            <h2 className="text-3xl font-bold text-nhs-black mb-6">
              Before you start
            </h2>
            
            <div className="bg-white border-l-4 border-nhs-blue p-6">
              <p className="text-nhs-black mb-4">
                To use this service, you'll need:
              </p>
              <ul className="list-disc list-inside space-y-2 text-nhs-mid-grey">
                <li>Your NHS number</li>
                <li>An email address</li>
                <li>A mobile phone number</li>
              </ul>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;

# NHS Open Access Appointment Booking System

> **Copyright © 2025 Adam Kent. Licensed under the Apache License 2.0.**  
> This is a prototype demonstration project. Not affiliated with or endorsed by the NHS.

A prototype NHS appointment booking system that breaks down traditional barriers to healthcare access by treating all Primary Care facilities as unified "healthcare access points" - enabling patients to book appointments anywhere in the country without practice registration constraints.

## 🎯 Healthcare Access Challenges

### The Current Problem

The NHS appointment booking system faces significant challenges due to structural barriers that can prevent patients from accessing care when and where they need it:

**Fragmented Private Business Model:**
- GP practices operate as independent private businesses under NHS contracts
- Each practice maintains separate booking systems, patient records, and access controls
- Patients are typically constrained to their "registered" GP practice
- No interoperability between practice management systems

**Registration Barriers:**
- Traditional GP registration creates geographic and administrative barriers to care
- Patients can't easily access care when traveling, working, or living temporarily elsewhere
- Emergency and urgent care becomes unnecessarily complicated
- Practice capacity issues force patients to wait weeks for appointments at their "home" practice while nearby practices have availability

**Funding Model Constraints:**
- Current capitation funding (payment per registered patient) incentivises practices to limit access to registered patients only
- Can create scarcity and gatekeeping effects
- May prevent efficient resource allocation across the NHS
- Can result in a postcode lottery for healthcare access

**Technology Fragmentation:**
- Dozens of incompatible practice management systems (EMIS, SystmOne, etc.)
- No unified booking interface for patients
- Staff waste time managing multiple systems
- Data silos prevent continuity of care

### The Human Impact

**For Patients:**
- "I can never see my actual GP - it's always a locum or healthcare assistant anyway"
- Lengthy waits for routine appointments whilst nearby practices may have availability
- Complex bureaucracy when needing care away from home
- Fragmented medical records across different systems

**For Healthcare Staff:**
- Managing multiple incompatible booking systems
- Inability to efficiently allocate resources across practices
- Administrative burden of registration processes
- Limited visibility into regional capacity and demand

## 🚀 The Open Access Vision

### Unified Healthcare Access Points

This system reimagines NHS primary care by treating all facilities as unified "healthcare access points":

- **GP Surgeries** → Healthcare Access Points
- **Walk-in Centres** → Healthcare Access Points  
- **Urgent Care Centres** → Healthcare Access Points
- **Community Clinics** → Healthcare Access Points

**Key Principle:** Patients should be able to access appropriate care at any NHS facility, just like they can use any NHS hospital A&E department.

### Digital Identity Over Practice Registration

**Replace Practice Registration with NHS Digital Identity:**
- NHS Login/Digital ID becomes the primary patient identifier
- NHS number provides continuity across all access points
- Patient records follow the patient, not tied to a single practice
- Eliminates registration bureaucracy and geographic constraints

### "Money Follows the Patient" Funding

**Transform the Funding Model:**
- Track patient usage across all healthcare access points
- Funding allocated based on actual care delivered, not registration lists
- Incentivises practices to provide excellent care to attract patients
- Enables efficient resource allocation based on real demand patterns

### Unified Booking Platform

**Single Digital Front Door:**
- One booking system for all NHS primary care
- Real-time availability across all local healthcare access points
- Intelligent routing based on urgency, location, and capacity
- Integration with existing NHS App ecosystem

## 🏥 How This System Works

### For Patients
1. **Login with NHS Digital ID** - No practice registration required
2. **See Real-Time Availability** - All nearby healthcare access points
3. **Book Appropriate Care** - Routine, urgent, or specialist appointments
4. **Access Care Anywhere** - Home, work, travel - no geographic restrictions
5. **Continuous Care Records** - Medical history follows via NHS Spine integration

### For Healthcare Providers
1. **Unified Practice Management** - Single system for all appointment types
2. **Cross-Practice Visibility** - See regional capacity and demand
3. **Flexible Staffing** - Allocate resources based on actual demand
4. **Quality Metrics** - Patient satisfaction and outcomes drive reputation
5. **Fair Funding** - Payment based on care delivered, not registration lists

### Technical Implementation
- **NHS Spine Integration** - Patient records and digital identity
- **FHIR Standards** - Interoperable appointment and clinical data
- **Real-Time Availability** - Live booking across all access points
- **Dual Storage Architecture** - Preserves existing data while enabling migration
- **Progressive Enhancement** - Works alongside existing systems during transition

## 🎯 Project Overview

This system provides a complete technical implementation of the open access vision, featuring dual portals for patients and healthcare staff, built to NHS Digital Service Manual standards with comprehensive security, accessibility, and scalability.

### Key Features
- **Dual Portal System**: Separate patient and staff interfaces with role-based access
- **Real-time Booking**: Live availability checking and instant appointment confirmation
- **NHS Compliance**: Follows NHS Digital Service Manual design and accessibility standards
- **Serverless Architecture**: Scalable AWS infrastructure with automatic scaling
- **Security First**: JWT authentication, NHS number validation, and GDPR compliance
- **Mobile Responsive**: Progressive Web App with offline capabilities

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                         │
├─────────────────────────────────────────────────────────────────┤
│  Patient Portal          │         Staff Portal                 │
│  • Registration          │         • Practice Dashboard         │
│  • Appointment Booking   │         • Appointment Management     │
│  • Profile Management    │         • Patient Records           │
│  • Dashboard             │         • Practice Settings         │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  │ HTTPS/REST API
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│                    AWS API Gateway                              │
│                   (Authentication & Routing)                    │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│                     AWS Lambda Functions                        │
├─────────────────────────────────────────────────────────────────┤
│  Auth Service    │  Appointments  │  Patients   │  Practices    │
│  • Registration  │  • Create      │  • Create   │  • Get Info   │
│  • Login         │  • Read        │  • Read     │  • Update     │
│  • JWT Tokens    │  • Update      │  • Update   │  • Settings   │
│                  │  • Delete      │             │               │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│                      AWS DynamoDB                               │
├─────────────────────────────────────────────────────────────────┤
│  Appointments    │    Patients     │    Practices              │
│  • GSI by date   │    • NHS number │    • Practice info        │
│  • GSI by patient│    • Contact    │    • Opening hours        │
│  • GSI by practice│   • Medical    │    • Services             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Supporting Services                          │
├─────────────────────────────────────────────────────────────────┤
│  AWS Cognito     │    AWS SES      │    CloudWatch             │
│  • User pools    │    • Email      │    • Logging              │
│  • Authentication│    • Notifications│  • Monitoring           │
│  • Authorization │    • Confirmations│  • Metrics              │
└─────────────────────────────────────────────────────────────────┘
```

## 🎨 Frontend Architecture

### Technology Stack
- **React 18** with hooks and concurrent features
- **React Router** for client-side routing with protected routes
- **React Query** for server state management and caching
- **Tailwind CSS** with NHS design tokens and components
- **Lucide React** icons for consistent iconography
- **React Hook Form** for efficient form handling and validation

### Component Architecture
```
src/
├── components/           # Reusable UI components
│   ├── ErrorBoundary/   # Error handling and recovery
│   ├── Layout/          # Headers, sidebars, navigation
│   └── UI/              # Buttons, modals, forms, spinners
├── contexts/            # React context providers
│   └── AuthContext.js   # Global authentication state
├── pages/               # Route-based page components
│   ├── auth/           # Login, registration, password reset
│   ├── patient/        # Patient portal pages
│   ├── public/         # Public landing pages
│   └── staff/          # Staff portal pages
├── services/           # API integration layer
│   └── api.js          # HTTP client with interceptors
├── utils/              # Shared utility functions
│   ├── dateUtils.js    # Date formatting and validation
│   └── validation.js   # Form and data validation
└── App.js              # Root component with routing
```

### Key Features
- **NHS Design Compliance**: Implements NHS Digital Service Manual patterns
- **Accessibility**: WCAG 2.1 AA compliant with screen reader support
- **Progressive Web App**: Installable with offline capabilities
- **Responsive Design**: Mobile-first approach with breakpoint optimisation
- **Error Boundaries**: Graceful error handling and recovery
- **Performance**: Code splitting, lazy loading, and optimised bundles

## ⚡ Backend Architecture

### Technology Stack
- **AWS Lambda** for serverless compute with automatic scaling
- **AWS API Gateway** for REST API management and authentication
- **AWS DynamoDB** for NoSQL data storage with GSI optimisation
- **AWS Cognito** for user authentication and authorisation
- **AWS SES/SNS** for email and SMS notifications
- **Python 3.11** with modern async/await patterns

### Service Architecture
```
backend/
├── src/
│   ├── appointments/           # Appointment management
│   │   ├── create_appointment.py
│   │   ├── get_appointments.py
│   │   ├── update_appointment.py
│   │   └── delete_appointment.py
│   ├── patients/              # Patient management
│   │   ├── create_patient.py
│   │   └── get_patient.py
│   ├── practices/             # Practice management
│   │   └── get_practice.py
│   ├── auth/                  # Authentication
│   │   └── auth.py
│   └── utils/                 # Shared utilities
│       ├── database.py        # DynamoDB operations
│       ├── auth.py           # JWT validation
│       ├── responses.py      # HTTP response helpers
│       ├── validators.py     # Data validation
│       ├── models.py         # Data models
│       └── notifications.py  # Email/SMS notifications
├── template.yaml              # AWS SAM infrastructure
├── DEPLOYMENT_GUIDE.md        # Complete deployment instructions
└── requirements.txt          # Python dependencies
```

### Key Features
- **Microservices Architecture**: Domain-driven service separation
- **Auto-scaling**: Serverless functions scale automatically with demand
- **Security**: JWT authentication, input validation, and encryption at rest
- **FHIR Compliance**: Data models aligned for future NHS integration
- **Monitoring**: CloudWatch logging and metrics with alerting
- **CI/CD Ready**: Automated deployment with environment management

## 🔐 Security & Compliance

### Authentication & Authorization
- **JWT Token-based Authentication** with automatic refresh
- **Role-based Access Control** (Patient, Staff, Admin)
- **NHS Number Validation** with proper format checking
- **Multi-factor Authentication** ready for future implementation

### Data Protection
- **Encryption at Rest** (DynamoDB) and in Transit (HTTPS)
- **GDPR Compliance** with data retention and privacy controls
- **Input Validation** and sanitization to prevent injection attacks
- **Audit Logging** for all data access and modifications
- **Session Management** with automatic timeout and secure storage

### NHS Compliance
- **NHS Digital Service Manual** design patterns and components
- **Accessibility Standards** (WCAG 2.1 AA) with screen reader support
- **NHS Login Integration** ready (OpenID Connect compatible)
- **GP Connect API** compatibility for future integration

## 🚀 Deployment & Operations

### Development Environment
```bash
# Start both frontend and backend locally
./start-local.sh

# Frontend: http://localhost:3000
# Backend: http://localhost:3001
```

### Production Deployment
```bash
# Deploy backend to AWS
cd backend/
./deploy.sh --environment prod --region eu-west-2

# Deploy frontend to static hosting
cd frontend/
npm run build
# Deploy build/ directory to Netlify/Vercel/S3
```

### Monitoring & Observability
- **CloudWatch Logs** for centralized logging
- **CloudWatch Metrics** for performance monitoring
- **API Gateway Metrics** for request tracking
- **DynamoDB Metrics** for database performance
- **Custom Alarms** for error rates and latency

## 📊 Alignment with Original Brief

### ✅ Core Requirements Delivered

**1. NHS-Compliant Design System**
- Implemented complete NHS Digital Service Manual compliance
- Used official NHS colour palette, typography, and component patterns
- Achieved WCAG 2.1 AA accessibility standards
- Mobile-responsive design with progressive enhancement

**2. Dual Portal Architecture**
- **Patient Portal**: Registration, booking, profile management, dashboard
- **Staff Portal**: Practice dashboard, appointment management, patient records
- Role-based access control with secure authentication
- Separate user experiences optimised for each user type

**3. Real-time Appointment Management**
- Live availability checking with conflict prevention
- Instant booking confirmation and notifications
- Multi-step booking process with validation at each stage
- Appointment history and management capabilities

**4. Scalable Backend Infrastructure**
- Serverless AWS architecture with automatic scaling
- DynamoDB for high-performance data storage
- API Gateway for secure, managed API endpoints
- CloudWatch for comprehensive monitoring and alerting

**5. Security & Compliance**
- JWT-based authentication with role management
- NHS number validation and UK-specific data handling
- GDPR-compliant data protection and retention
- Encryption at rest and in transit

### 🎯 Additional Value Delivered

**Modern Development Practices**
- React 18 with hooks and modern patterns
- TypeScript-ready architecture for type safety
- Comprehensive error handling and recovery
- Progressive Web App capabilities

**Production-Ready Features**
- Automated deployment scripts and CI/CD readiness
- Comprehensive API documentation and testing
- Environment-specific configuration management
- Performance optimisation and monitoring

**Future NHS Integration**
- FHIR-aligned data models for GP Connect compatibility
- OpenID Connect ready for NHS Login integration
- Modular architecture for easy system integration
- Standards-compliant APIs for interoperability

## 🛠️ Getting Started

### Quick Start (5 minutes)
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd OpenAccessBooking
   ```

2. **Start local development**
   ```bash
   chmod +x start-local.sh
   ./start-local.sh
   ```
   
   The script will automatically detect if you're running in WSL and show the correct URLs.

3. **Access the applications**
   
   The start script will display the correct URLs for your environment.
   
   **Note for WSL users:** Access from Windows browser using the WSL IP address shown by the script (e.g., `http://172.20.7.150:3000`), not `localhost`.

### Full Deployment
- **Backend**: See [backend/DEPLOYMENT_GUIDE.md](./backend/DEPLOYMENT_GUIDE.md) for AWS deployment
- **Frontend**: See [frontend/README.md](./frontend/README.md) for static hosting deployment
- **Local Development**: See [LOCAL_DEVELOPMENT_GUIDE.md](./LOCAL_DEVELOPMENT_GUIDE.md) for detailed setup

## 📚 Documentation

### Core Documentation
- **[Frontend Documentation](./frontend/README.md)** - React app setup, components, and deployment
- **[Backend Documentation](./backend/README.md)** - AWS services, API endpoints, and infrastructure
- **[Local Development Guide](./LOCAL_DEVELOPMENT_GUIDE.md)** - Development environment setup

### Deployment & CI/CD
- **[CI/CD Setup](./CI-CD-SETUP.md)** - Quick start guide for automated deployment
- **[Deployment Guide](./DEPLOYMENT.md)** - Complete deployment instructions
- **[Terraform Guide](./terraform/README.md)** - Infrastructure as Code
- **[GitHub Actions](/.github/workflows/README.md)** - CI/CD pipeline details

### Testing
- **[Testing Guide](./TESTING.md)** - Running tests for backend and frontend
- **[Backend Tests](./backend/tests/README.md)** - pytest documentation
- **[Frontend Tests](./frontend/TESTING.md)** - Jest documentation

## 🤝 Contributing

This project follows NHS Digital standards and modern development practices:

1. **Code Standards**: ESLint, Prettier, and TypeScript for quality
2. **Testing**: Unit, integration, and E2E test coverage
3. **Security**: Regular dependency updates and security scanning
4. **Documentation**: Comprehensive docs for all components
5. **Accessibility**: WCAG 2.1 AA compliance testing

## 📄 License

Copyright © 2025 Adam Kent

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

### Important Notes

- **Prototype Status**: This is a demonstration project showcasing technical capabilities
- **Not NHS-Endorsed**: This project is not affiliated with, endorsed by, or approved by the NHS
- **Production Use**: For live NHS deployment, additional security reviews, compliance audits, and NHS approval processes are required
- **Compliance**: Follows NHS Digital Service Manual standards and WCAG 2.1 AA accessibility guidelines

## 🆘 Support

- **Technical Issues**: Check CloudWatch logs and GitHub issues
- **Security Concerns**: Follow responsible disclosure practices
- **NHS Integration**: Contact NHS Digital for integration guidance
- **Commercial Enquiries**: Available for consultation and development services

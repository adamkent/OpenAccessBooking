# NHS Appointment Booking System - Backend

A serverless backend for the NHS appointment booking system, enabling open-access healthcare booking across all NHS access points (GP surgeries, walk-in centres, urgent care centres) without traditional practice registration requirements.

## 🎯 Vision & Architecture

### The Problem We Solve
Traditional NHS appointment booking requires patients to register with a single GP practice, creating barriers to access. Patients rarely see their "family doctor" anymore, often encountering locum GPs or healthcare assistants. Our system treats all NHS facilities as unified "healthcare access points" accessible via digital identity.

### Core Architecture
Serverless microservices architecture using AWS technologies:

- **API Gateway**: RESTful API endpoints with JWT authentication
- **AWS Lambda**: Serverless functions for business logic (auto-scaling)
- **DynamoDB**: NoSQL database with FHIR-aligned data models
- **Cognito**: User authentication (NHS Login integration ready)
- **NHS Spine Integration**: Ready for Summary Care Record access
- **SES/SNS**: Notifications and appointment reminders

## 📁 Project Structure

```
backend/
├── src/
│   ├── appointments/           # Appointment management functions
│   │   ├── create_appointment.py
│   │   ├── get_appointments.py
│   │   ├── update_appointment.py
│   │   └── delete_appointment.py
│   ├── patients/              # Patient management functions
│   │   ├── create_patient.py
│   │   └── get_patient.py
│   ├── practices/             # Practice management functions
│   │   └── get_practice.py
│   ├── auth/                  # Authentication functions
│   │   └── auth.py
│   └── utils/                 # Shared utilities
│       ├── database.py        # DynamoDB operations
│       ├── auth.py           # JWT validation
│       ├── responses.py      # HTTP response helpers
│       ├── validators.py     # Data validation
│       ├── models.py         # Data models
│       └── notifications.py  # Email/SMS notifications
├── template.yaml              # AWS SAM template
├── requirements.txt           # Python dependencies
├── deploy.sh                 # Deployment script
├── .env                      # Environment variables
└── README.md                 # This file
```

## 📚 API Documentation

### OpenAPI/Swagger Specification

Complete API documentation is available in OpenAPI 3.0 format:

**File:** `openapi.yaml`

**View Documentation:**

```bash
# Install Swagger UI (optional)
npm install -g swagger-ui-watcher

# Serve interactive documentation
swagger-ui-watcher openapi.yaml
```

Or use online viewers:
- [Swagger Editor](https://editor.swagger.io/) - Paste `openapi.yaml` content
- [Redoc](https://redocly.github.io/redoc/) - For beautiful documentation

### API Testing

**Using curl:**
```bash
# Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john.smith@email.com","password":"TestPass123!"}'

# Get appointments (with token)
curl http://localhost:5000/appointments \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Using Python:**
```python
import requests

# Login
response = requests.post('http://localhost:5000/auth/login', json={
    'email': 'john.smith@email.com',
    'password': 'TestPass123!'
})
token = response.json()['token']

# Get appointments
headers = {'Authorization': f'Bearer {token}'}
appointments = requests.get('http://localhost:5000/appointments', headers=headers)
print(appointments.json())
```

## 🚀 Quick Start

### Prerequisites

1. **AWS CLI** - [Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
2. **AWS SAM CLI** - [Installation Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
3. **Python 3.11+**
4. **AWS Account** with appropriate permissions

### 1. Configure AWS Credentials

```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and region (eu-west-2)
```

### 2. Clone and Setup

```bash
cd backend/
chmod +x deploy.sh
```

### 3. Deploy (First Time)

```bash
./deploy.sh --guided
```

This will:
- Create necessary AWS resources
- Set up DynamoDB tables
- Configure Cognito user pools
- Deploy Lambda functions
- Set up API Gateway

### 4. Deploy (Subsequent Deployments)

```bash
./deploy.sh
```

## 🔧 Configuration

### Environment Variables

The `.env` file contains configuration settings:

```bash
# Environment Configuration
ENVIRONMENT=dev
AWS_REGION=eu-west-2

# DynamoDB Tables (auto-populated after deployment)
APPOINTMENTS_TABLE=dev-appointments
PATIENTS_TABLE=dev-patients
PRACTICES_TABLE=dev-practices

# Cognito (auto-populated after deployment)
USER_POOL_ID=
USER_POOL_CLIENT_ID=

# API Configuration (auto-populated after deployment)
API_GATEWAY_URL=
```

### AWS SAM Parameters

You can customise deployment parameters in `template.yaml`:

- `Environment`: dev/staging/prod
- Table names and configurations
- Lambda function settings
- API Gateway configuration

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "nhs_number": "1234567890",
  "role": "patient"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

### Appointment Endpoints

#### Create Appointment
```http
POST /appointments
Authorization: Bearer <token>
Content-Type: application/json

{
  "patient_id": "patient-123",
  "practice_id": "practice-456",
  "appointment_datetime": "2024-01-15T10:30:00Z",
  "appointment_type": "routine",
  "duration_minutes": 30,
  "reason": "Annual check-up"
}
```

#### Get Appointments
```http
GET /appointments?patient_id=patient-123&start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer <token>
```

#### Update Appointment
```http
PUT /appointments/{appointment_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "appointment_datetime": "2024-01-15T11:00:00Z",
  "notes": "Updated appointment time"
}
```

#### Cancel Appointment
```http
DELETE /appointments/{appointment_id}
Authorization: Bearer <token>
```

### Patient Endpoints

#### Create Patient
```http
POST /patients
Authorization: Bearer <token>
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Smith",
  "date_of_birth": "1990-01-15",
  "email": "john.smith@email.com",
  "nhs_number": "1234567890"
}
```

#### Get Patient
```http
GET /patients/{patient_id}?include_medical=true&include_appointments=true
Authorization: Bearer <token>
```

## 🔐 Security Features

### Authentication & Authorization
- **JWT Tokens**: Secure token-based authentication
- **Role-Based Access**: Patient, Staff, and Admin roles
- **NHS Number Validation**: Proper NHS number format checking
- **Data Isolation**: Users can only access their authorised data

### Data Protection
- **Encryption**: Data encrypted at rest and in transit
- **Input Validation**: Comprehensive data validation
- **Audit Logging**: All operations logged for compliance
- **GDPR Compliance**: Privacy controls and data retention

## 🧪 Testing

### Manual Testing

1. **Register a test user**:
```bash
curl -X POST https://your-api-url/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "role": "patient"
  }'
```

2. **Login and get token**:
```bash
curl -X POST https://your-api-url/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

3. **Create an appointment**:
```bash
curl -X POST https://your-api-url/appointments \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "your-user-id",
    "practice_id": "practice-123",
    "appointment_datetime": "2024-12-15T10:30:00Z",
    "appointment_type": "routine"
  }'
```

### Load Testing

Use tools like Artillery or Apache Bench for load testing:

```bash
# Install Artillery
npm install -g artillery

# Run load test
artillery quick --count 10 --num 5 https://your-api-url/appointments
```

## 🚀 Deployment Options

### Development Environment
```bash
./deploy.sh --environment dev --region eu-west-2
```

### Production Environment
```bash
./deploy.sh --environment prod --region eu-west-2 --guided
```

### Cleanup
```bash
./deploy.sh --cleanup
```

### Manual Deployment
```bash
sam build
sam deploy --guided
```

## 🔍 Monitoring & Logging

### CloudWatch Logs
- Lambda function logs automatically sent to CloudWatch
- Log groups: `/aws/lambda/nhs-appointment-*`

### Metrics
- API Gateway metrics (requests, latency, errors)
- Lambda metrics (invocations, duration, errors)
- DynamoDB metrics (read/write capacity, throttles)

### Alarms
Set up CloudWatch alarms for:
- High error rates
- Increased latency
- DynamoDB throttling

## 🔧 Troubleshooting

### Common Issues

1. **Deployment Fails**
   - Check AWS credentials: `aws sts get-caller-identity`
   - Verify SAM CLI: `sam --version`
   - Check S3 bucket permissions

2. **Authentication Errors**
   - Verify Cognito User Pool configuration
   - Check JWT token expiration
   - Validate user permissions

3. **Database Errors**
   - Check DynamoDB table names in environment variables
   - Verify IAM permissions for Lambda functions
   - Monitor DynamoDB capacity and throttling

4. **API Gateway Issues**
   - Check CORS configuration
   - Verify API Gateway authorisers
   - Test endpoints individually

### Debug Mode
Enable debug logging by setting `LOG_LEVEL=DEBUG` in environment variables.

## 🔄 Future NHS Integration

This backend is designed for future integration with NHS systems:

### NHS Login Integration
- OpenID Connect compatibility
- NHS number verification
- Single sign-on capability

### GP Connect API
- FHIR-compliant data models
- Appointment synchronisation
- Practice system integration

### NHS App Integration
- Web integration standards
- NHS design system compliance
- Accessibility requirements

## 📝 Contributing

1. Follow NHS Digital Service Manual guidelines
2. Ensure GDPR compliance
3. Add comprehensive tests
4. Update documentation
5. Follow security best practices

## 📄 License

This project is intended for NHS use and follows NHS Digital standards and guidelines.

## 📚 API Reference

### Base URL
```
https://{api-id}.execute-api.{region}.amazonaws.com/{stage}/
```

### Authentication
All endpoints require JWT token: `Authorization: Bearer {token}`

### Key Endpoints

#### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh JWT token

#### Appointments
- `GET /appointments` - List appointments (with filters)
- `POST /appointments` - Create appointment
- `PUT /appointments/{id}` - Update appointment
- `DELETE /appointments/{id}` - Cancel appointment

#### Patients
- `GET /patients/{id}` - Get patient details
- `GET /patients/{id}?include_medical=true` - Get patient with medical info
- `POST /patients` - Create patient record
- `PUT /patients/{id}` - Update patient record

#### Practices (Healthcare Access Points)
- `GET /practices` - List all healthcare access points
- `GET /practices/{id}` - Get practice details
- `GET /practices/{id}/availability` - Check appointment availability

### Request/Response Format
All requests use JSON. Responses include:
```json
{
  "data": {...},
  "message": "Success message",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Medical Data Format
Patient medical information supports dual storage for data integrity:

```json
{
  "medical_info": {
    "allergies_legacy": ["Penicillin", "Nuts"],
    "allergies": [
      {
        "display_text": "Penicillin allergy",
        "code": "294505008",
        "system": "http://snomed.info/sct",
        "severity": "moderate",
        "reaction": ["rash", "swelling"],
        "onset_date": "2018-03-10"
      }
    ],
    "conditions": [...],
    "medications": [...],
    "notes": "Free-text clinical notes preserved",
    "data_source": "gp_records"
  }
}
```

For detailed API documentation with examples, see: [Full API Documentation](./DEPLOYMENT_GUIDE.md#post-deployment-testing)

## 🏗️ Technical Architecture

### Healthcare Access Point Model
```python
class Practice:
    access_point_type: HealthcareAccessPointType  # GP_SURGERY, WALK_IN_CENTRE, etc.
    accepts_walk_ins: bool
    requires_registration: bool  # For legacy practices
    ods_code: str  # NHS organisation code
```

### Medical Data Dual Storage
```python
class MedicalInfo:
    # Legacy string-based fields (backward compatibility)
    allergies_legacy: List[str]
    conditions_legacy: List[str]
    medications_legacy: List[str]
    
    # NHS-ready coded fields
    allergies: List[MedicalAllergy]
    conditions: List[MedicalCondition]
    medications: List[Medication]
    
    notes: str  # Free-text clinical notes
    data_source: str  # Source tracking for audit

class MedicalAllergy:
    display_text: str  # Human-readable description
    code: Optional[str]  # SNOMED CT code (future)
    system: Optional[str]  # Coding system URI
    severity: str  # mild, moderate, severe, life-threatening
    reaction: List[str]  # Allergic reactions
    onset_date: Optional[str]  # When identified
```

### Cross-Practice Usage Tracking
```python
class PatientPracticeUsage:
    patient_id: str
    nhs_number: str
    practice_id: str
    total_appointments: int
    is_primary_practice: bool  # Patient's "home" practice
```

### FHIR Integration Ready
- Appointment objects align with FHIR R4 standards
- NHS Spine integration prepared
- Summary Care Record access capability

## 🔄 Development Workflow

### Local Development
```bash
# Start local development environment
python app.py  # Runs on localhost:3001

# Run tests
python -m pytest tests/

# Seed test data
python scripts/seed_data.py --local
```

### Deployment
```bash
# Development deployment
./deploy.sh --guided

# Production deployment
./deploy.sh --environment prod
```

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for complete deployment instructions.

## 🔐 Security & Compliance

### NHS Standards
- NHS number validation with check digit algorithm
- FHIR-compliant data models
- NHS Login integration ready (OpenID Connect)
- Data retention and GDPR compliance

### Security Features
- JWT-based authentication with role-based access
- Input validation and sanitization
- Encryption at rest (DynamoDB) and in transit (HTTPS)
- Comprehensive audit logging

## 🚀 Future NHS Integration

### NHS Login Integration
Ready for NHS Digital ID integration using OpenID Connect standards.

### GP Connect API
FHIR-aligned appointment objects enable future GP Connect integration for real-time practice system updates.

### NHS App Integration
Web-based architecture supports embedding in NHS App via web integration standards.

## 🔐 Validation Algorithms

### NHS Number Validation (Modulus 11)

The system validates NHS numbers using the official NHS Modulus 11 algorithm:

**Algorithm:**
1. NHS number format: 10 digits (e.g., `943 476 5919`)
2. First 9 digits are the identifier
3. 10th digit is the check digit
4. Calculation:
   - Multiply each of the first 9 digits by (10 - position)
   - Sum all products
   - Calculate remainder when divided by 11
   - If remainder is 0, check digit is 0
   - If remainder is 1, NHS number is invalid
   - Otherwise, check digit = 11 - remainder

**Example:**
```
NHS Number: 943 476 5919
Calculation: (9×10 + 4×9 + 3×8 + 4×7 + 7×6 + 6×5 + 5×4 + 9×3 + 1×2)
           = 90 + 36 + 24 + 28 + 42 + 30 + 20 + 27 + 2 = 299
Remainder:   299 % 11 = 2
Check digit: 11 - 2 = 9 ✓
```

**Implementation:** `src/utils/validators.py::validate_nhs_number()`

**Valid Test NHS Numbers:**
- `943 476 5919`
- `401 023 2137`
- `599 012 8088`
- `630 469 5787`

### UK Phone Number Validation

Validates UK phone numbers in multiple formats:

**Accepted Formats:**
- Landline: `020 7123 4567`, `01234 567890`
- Mobile: `07123 456789`, `+44 7123 456789`
- International: `+44 20 7123 4567`

**Rules:**
- Must start with 0 or +44
- 10-11 digits total (excluding +44 prefix)
- Supports spaces, hyphens, parentheses

**Implementation:** `src/utils/validators.py::validate_phone_number()`

### UK Postcode Validation

Validates UK postcodes using official format rules:

**Format:** `AA9A 9AA` (various patterns supported)

**Examples:**
- `SW1A 1AA` (London)
- `M1 1AE` (Manchester)
- `B33 8TH` (Birmingham)

**Rules:**
- 1-2 letter area code
- 1-2 digit district
- Optional letter
- Space
- Single digit
- Two letters (not CIKMOV)

**Implementation:** `src/utils/validators.py::validate_postcode()`

### Email Validation

Uses RFC 5322 compliant email validation via the `validators` library.

**Implementation:** `src/utils/validators.py::validate_email()`

### Appointment Time Validation

Validates appointment times against practice operating hours and booking rules:

**Rules:**
- Must be within practice opening hours
- Must be in the future
- Must be on a valid booking increment (e.g., 15-minute slots)
- Cannot be on bank holidays or practice closure days
- Minimum advance booking period (e.g., 2 hours)
- Maximum advance booking period (e.g., 6 weeks)

**Implementation:** `src/utils/validators.py::validate_appointment_time()`

## 🆘 Support & Contributing

### Getting Help
1. Check [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for deployment issues
2. Review CloudWatch logs for runtime errors
3. Validate API requests against schemas in `src/utils/models.py`

### Contributing
1. Follow NHS Digital Service Manual guidelines
2. Ensure FHIR compliance for data models
3. Add comprehensive tests for new features
4. Update documentation

---

**Note**: This system demonstrates open-access healthcare booking. For NHS production deployment, additional security reviews, compliance audits, and NHS Digital approval are required.

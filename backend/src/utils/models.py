"""
Data models and schemas for the NHS appointment booking system.
Defines the structure of data entities and their relationships.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class AppointmentType(str, Enum):
    ROUTINE = "routine"
    URGENT = "urgent"
    FOLLOW_UP = "follow_up"
    CONSULTATION = "consultation"
    VACCINATION = "vaccination"

class UserRole(str, Enum):
    PATIENT = "patient"
    STAFF = "staff"
    ADMIN = "admin"

class PatientStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DECEASED = "deceased"

class PracticeStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class HealthcareAccessPointType(str, Enum):
    """Classification of healthcare access points for unified booking"""
    GP_SURGERY = "gp_surgery"
    WALK_IN_CENTRE = "walk_in_centre"
    URGENT_CARE_CENTRE = "urgent_care_centre"
    COMMUNITY_CLINIC = "community_clinic"
    SPECIALIST_CLINIC = "specialist_clinic"
    HOSPITAL_OUTPATIENT = "hospital_outpatient"

# Address Model
class Address(BaseModel):
    line1: str = Field(..., min_length=1, max_length=100)
    line2: Optional[str] = Field(None, max_length=100)
    city: str = Field(..., min_length=1, max_length=50)
    postcode: str = Field(..., min_length=5, max_length=10)
    country: str = Field(default="UK", max_length=50)

# Emergency Contact Model
class EmergencyContact(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    relationship: str = Field(..., min_length=1, max_length=50)
    phone: str = Field(..., min_length=10, max_length=20)
    email: Optional[str] = Field(None, max_length=100)

# Medical Coding Models (NHS-ready dual storage)
class CodedMedicalItem(BaseModel):
    """
    Dual storage model for medical data - supports both human-readable text
    and NHS coding standards (SNOMED CT, dm+d) for future integration.
    """
    display_text: str = Field(..., min_length=1, max_length=200, description="Human-readable description")
    code: Optional[str] = Field(None, max_length=50, description="NHS standard code (SNOMED CT/dm+d)")
    system: Optional[str] = Field(None, max_length=100, description="Coding system URI")
    verified: bool = Field(default=False, description="Whether code has been NHS-validated")
    
class MedicalAllergy(CodedMedicalItem):
    """Allergy information with severity and reaction details"""
    severity: Optional[str] = Field(None, description="mild, moderate, severe, life-threatening")
    reaction: Optional[List[str]] = Field(default_factory=list, description="Allergic reactions")
    onset_date: Optional[str] = Field(None, description="When allergy was first identified")

class MedicalCondition(CodedMedicalItem):
    """Medical condition with clinical status and dates"""
    clinical_status: Optional[str] = Field(default="active", description="active, resolved, inactive")
    onset_date: Optional[str] = Field(None, description="When condition was diagnosed")
    resolved_date: Optional[str] = Field(None, description="When condition was resolved")

class Medication(CodedMedicalItem):
    """Medication with dosage and administration details"""
    dosage: Optional[str] = Field(None, max_length=100, description="Dosage instructions")
    frequency: Optional[str] = Field(None, max_length=50, description="How often to take")
    route: Optional[str] = Field(None, max_length=50, description="oral, injection, topical, etc.")
    start_date: Optional[str] = Field(None, description="When medication started")
    end_date: Optional[str] = Field(None, description="When medication stopped")
    prescriber: Optional[str] = Field(None, max_length=100, description="Prescribing clinician")

# Enhanced Medical Information Model
class MedicalInfo(BaseModel):
    """
    Comprehensive medical information supporting both current string-based
    storage and future NHS-coded data for seamless migration.
    """
    # Legacy string-based fields (maintained for backward compatibility)
    allergies_legacy: List[str] = Field(default_factory=list, description="Legacy string allergies")
    conditions_legacy: List[str] = Field(default_factory=list, description="Legacy string conditions")
    medications_legacy: List[str] = Field(default_factory=list, description="Legacy string medications")
    
    # NHS-ready coded fields
    allergies: List[MedicalAllergy] = Field(default_factory=list, description="Coded allergy information")
    conditions: List[MedicalCondition] = Field(default_factory=list, description="Coded medical conditions")
    medications: List[Medication] = Field(default_factory=list, description="Coded medication information")
    
    # Clinical notes (preserved as free text)
    notes: Optional[str] = Field(None, max_length=2000, description="Free-text clinical notes")
    last_updated: Optional[str] = Field(None, description="When medical info was last updated")
    data_source: Optional[str] = Field(default="user_entered", description="Source of medical data")

# Patient Model
class Patient(BaseModel):
    patient_id: str = Field(..., min_length=1)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    date_of_birth: str = Field(..., regex=r'^\d{4}-\d{2}-\d{2}$')
    email: str = Field(..., min_length=5, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    nhs_number: Optional[str] = Field(None, min_length=10, max_length=10)
    address: Optional[Address] = None
    emergency_contact: Optional[EmergencyContact] = None
    medical_info: Optional[MedicalInfo] = None
    practice_id: Optional[str] = None
    preferred_gp_id: Optional[str] = None
    registration_date: str
    status: PatientStatus = PatientStatus.ACTIVE
    created_by: str
    created_at: str
    updated_at: str

    @validator('email')
    def validate_email(cls, v):
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email format')
        return v.lower()

# Opening Hours Model
class OpeningHours(BaseModel):
    monday: Optional[str] = Field(None, regex=r'^\d{2}:\d{2}-\d{2}:\d{2}$|^Closed$')
    tuesday: Optional[str] = Field(None, regex=r'^\d{2}:\d{2}-\d{2}:\d{2}$|^Closed$')
    wednesday: Optional[str] = Field(None, regex=r'^\d{2}:\d{2}-\d{2}:\d{2}$|^Closed$')
    thursday: Optional[str] = Field(None, regex=r'^\d{2}:\d{2}-\d{2}:\d{2}$|^Closed$')
    friday: Optional[str] = Field(None, regex=r'^\d{2}:\d{2}-\d{2}:\d{2}$|^Closed$')
    saturday: Optional[str] = Field(None, regex=r'^\d{2}:\d{2}-\d{2}:\d{2}$|^Closed$')
    sunday: Optional[str] = Field(None, regex=r'^\d{2}:\d{2}-\d{2}:\d{2}$|^Closed$')

# Practice Model (Healthcare Access Point)
class Practice(BaseModel):
    practice_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=100)
    address: Address
    phone: str = Field(..., min_length=10, max_length=20)
    email: str = Field(..., min_length=5, max_length=100)
    website: Optional[str] = Field(None, max_length=200)
    registration_number: Optional[str] = Field(None, max_length=20)
    ccg_code: Optional[str] = Field(None, max_length=10)
    ods_code: Optional[str] = Field(None, max_length=10)
    access_point_type: HealthcareAccessPointType = HealthcareAccessPointType.GP_SURGERY
    services: List[str] = Field(default_factory=list)
    opening_hours: Optional[OpeningHours] = None
    accepts_walk_ins: bool = Field(default=False)
    requires_registration: bool = Field(default=False)  # For legacy practices that still require registration
    status: PracticeStatus = PracticeStatus.ACTIVE
    created_at: str
    updated_at: str

# Practitioner Model
class Practitioner(BaseModel):
    practitioner_id: str = Field(..., min_length=1)
    practice_id: str = Field(..., min_length=1)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., max_length=20)  # Dr, Nurse, etc.
    role: str = Field(..., max_length=50)   # GP, Practice Nurse, etc.
    specialties: List[str] = Field(default_factory=list)
    gmc_number: Optional[str] = Field(None, max_length=20)
    available_days: List[str] = Field(default_factory=list)
    status: str = Field(default="active")
    created_at: str
    updated_at: str

# Appointment Model
class Appointment(BaseModel):
    appointment_id: str = Field(..., min_length=1)
    patient_id: str = Field(..., min_length=1)
    practice_id: str = Field(..., min_length=1)
    practitioner_id: Optional[str] = None
    appointment_datetime: str = Field(..., regex=r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$')
    appointment_type: AppointmentType
    duration_minutes: int = Field(default=30, ge=5, le=120)
    reason: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    created_by: str
    created_at: str
    updated_at: str
    cancelled_at: Optional[str] = None
    cancelled_by: Optional[str] = None

    @validator('appointment_datetime')
    def validate_appointment_datetime(cls, v):
        try:
            # Parse and validate the datetime
            dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
            # Ensure it's in the future (basic check)
            if dt <= datetime.now(dt.tzinfo):
                raise ValueError('Appointment must be in the future')
            return v
        except ValueError as e:
            raise ValueError(f'Invalid datetime format: {e}')

# API Request/Response Models
class CreateAppointmentRequest(BaseModel):
    patient_id: str
    practice_id: str
    practitioner_id: Optional[str] = None
    appointment_datetime: str
    appointment_type: AppointmentType
    duration_minutes: int = 30
    reason: Optional[str] = None
    notes: Optional[str] = None

class UpdateAppointmentRequest(BaseModel):
    appointment_datetime: Optional[str] = None
    appointment_type: Optional[AppointmentType] = None
    duration_minutes: Optional[int] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[AppointmentStatus] = None
    practitioner_id: Optional[str] = None

class CreatePatientRequest(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: str
    email: str
    phone: Optional[str] = None
    nhs_number: Optional[str] = None
    address: Optional[Address] = None
    emergency_contact: Optional[EmergencyContact] = None
    medical_info: Optional[MedicalInfo] = None
    practice_id: Optional[str] = None
    preferred_gp_id: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    nhs_number: Optional[str] = None
    role: UserRole = UserRole.PATIENT
    practice_id: Optional[str] = None

# Response Models
class APIResponse(BaseModel):
    data: Optional[Any] = None
    message: Optional[str] = None
    timestamp: str
    errors: Optional[Dict[str, Any]] = None

class AuthResponse(BaseModel):
    access_token: str
    id_token: str
    refresh_token: str
    expires_in: int
    user: Dict[str, Any]

# FHIR-aligned models for future NHS integration
class FHIRAppointment(BaseModel):
    """
    FHIR-compliant appointment model for NHS integration.
    Based on FHIR R4 Appointment resource.
    """
    resourceType: str = "Appointment"
    id: str
    status: str  # proposed | pending | booked | arrived | fulfilled | cancelled | noshow
    serviceCategory: Optional[List[Dict[str, str]]] = None
    serviceType: Optional[List[Dict[str, str]]] = None
    specialty: Optional[List[Dict[str, str]]] = None
    appointmentType: Optional[Dict[str, str]] = None
    reasonCode: Optional[List[Dict[str, str]]] = None
    description: Optional[str] = None
    start: str  # ISO datetime
    end: str    # ISO datetime
    minutesDuration: Optional[int] = None
    participant: List[Dict[str, Any]]
    created: Optional[str] = None

    def to_internal_appointment(self) -> Appointment:
        """Convert FHIR appointment to internal model."""
        # Implementation would map FHIR fields to internal model
        pass

    @classmethod
    def from_internal_appointment(cls, appointment: Appointment) -> 'FHIRAppointment':
        """Convert internal appointment to FHIR format."""
        # Implementation would map internal model to FHIR fields
        pass

# Cross-Practice Usage Tracking Model
class PatientPracticeUsage(BaseModel):
    """
    Track patient usage across different healthcare access points.
    Replaces traditional GP registration for funding and continuity tracking.
    """
    usage_id: str = Field(..., min_length=1)
    patient_id: str = Field(..., min_length=1)
    nhs_number: str = Field(..., min_length=10, max_length=10)
    practice_id: str = Field(..., min_length=1)
    access_point_type: HealthcareAccessPointType
    first_visit_date: str
    last_visit_date: str
    total_appointments: int = Field(default=1, ge=1)
    is_primary_practice: bool = Field(default=False)  # Patient's designated "home" practice
    created_at: str
    updated_at: str

# NHS Spine Integration Models
class SpinePatientSummary(BaseModel):
    """
    Summary of patient data from NHS Spine for cross-practice access.
    Based on Summary Care Record structure.
    """
    nhs_number: str = Field(..., min_length=10, max_length=10)
    family_name: str
    given_names: List[str]
    date_of_birth: str
    gender: str
    address: Address
    gp_practice_code: Optional[str] = None  # Current registered GP (if any)
    allergies: List[str] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    significant_medical_history: List[str] = Field(default_factory=list)
    last_updated: str

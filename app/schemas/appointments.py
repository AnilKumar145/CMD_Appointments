from pydantic import BaseModel, Field, validator
from datetime import date, time
from typing import Optional
from app.models.appointments import AppointmentStatus

class TimeSlot(BaseModel):
    start_time: time = Field(..., description="Start time of the appointment slot")
    end_time: time = Field(..., description="End time of the appointment slot")

    class Config:
        json_schema_extra = {
            "example": {
                "start_time": "09:00:00",
                "end_time": "10:00:00"
            }
        }

class AppointmentRequest(BaseModel):
    doctor_id: str = Field(
        ..., 
        description="Doctor ID cannot be null",
        example="DOC0001"
    )
    patient_id: str = Field(
        ..., 
        description="Patient ID cannot be null",
        example="PAT0001"
    )
    facility_id: str = Field(
        ..., 
        description="Facility ID cannot be null",
        example="FAC0001"
    )
    doctor_name: str = Field(
        ..., 
        min_length=2, 
        max_length=100, 
        description="Doctor name must be between 2 and 100 characters",
        example="Dr. John Smith"
    )
    patient_name: str = Field(
        ..., 
        min_length=2, 
        max_length=100, 
        description="Patient name must be between 2 and 100 characters",
        example="Jane Doe"
    )
    appointment_date: date = Field(
        ..., 
        description="Appointment date cannot be null",
        example="2023-12-25"
    )
    appointment_start_time: time = Field(
        ..., 
        description="Appointment start time cannot be null",
        example="09:00:00"
    )
    appointment_end_time: time = Field(
        ..., 
        description="Appointment end time cannot be null",
        example="10:00:00"
    )
    purpose_of_visit: str = Field(
        ..., 
        min_length=2, 
        max_length=255, 
        description="Purpose of visit must be between 2 and 255 characters",
        example="Regular checkup"
    )
    description: Optional[str] = Field(
        None, 
        max_length=500, 
        description="Description cannot exceed 500 characters",
        example="Patient has reported mild fever and headache"
    )

    @validator('appointment_date')
    def validate_appointment_date(cls, v):
        today = date.today()
        if v < today:
            raise ValueError("Appointment date must be in the future or present")
        return v


    @validator('appointment_end_time')
    def validate_appointment_time(cls, v, values):
        if 'appointment_start_time' in values and v <= values['appointment_start_time']:
            raise ValueError("End time must be after start time")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "doctor_id": "DOC0001",
                "patient_id": "PAT0001",
                "facility_id": "FAC0001",
                "doctor_name": "Dr. John Smith",
                "patient_name": "Jane Doe",
                "appointment_date": "2023-12-25",
                "appointment_start_time": "09:00:00",
                "appointment_end_time": "10:00:00",
                "purpose_of_visit": "Regular checkup",
                "description": "Patient has reported mild fever and headache"
            }
        }

class AppointmentResponse(AppointmentRequest):
    appointment_id: str  # Changed from int to str to match APT0001 format
    doctor_id: str
    patient_id: str
    facility_id: str
    doctor_name: str
    patient_name: str
    appointment_date: date
    appointment_start_time: time
    appointment_end_time: time
    purpose_of_visit: str
    description: Optional[str]
    status: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "appointment_id": 1,
                "doctor_id": "DOC0001",
                "patient_id": "PAT0001",
                "facility_id": "FAC0001",
                "doctor_name": "Dr. John Smith",
                "patient_name": "Jane Doe",
                "appointment_date": "2023-12-25",
                "appointment_start_time": "09:00:00",
                "appointment_end_time": "10:00:00",
                "purpose_of_visit": "Regular checkup",
                "description": "Patient has reported mild fever and headache",
                "status": "SCHEDULED"
            }
        }

class AppointmentStatusUpdateRequest(BaseModel):
    status: AppointmentStatus = Field(
        ..., 
        description="New status for the appointment",
        example=AppointmentStatus.COMPLETED
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "COMPLETED"
            }
        }

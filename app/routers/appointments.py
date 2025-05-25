from fastapi import APIRouter, Depends, HTTPException, Query, status, Security
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import date
from app.database import get_db
from app.models.appointments import AppointmentStatus
from app.schemas.appointments import (
    AppointmentRequest,
    AppointmentResponse,
    AppointmentStatusUpdateRequest,
    TimeSlot
)
from app.crud import (
    get_all_appointments,
    get_appointment_by_id,
    create_appointment,
    update_appointment_status,
    get_appointments_by_patient_id,
    get_appointments_by_doctor_id,
    get_appointments_by_facility_id,
    get_appointments_count_by_status,
    get_appointment_count_by_doctor_and_status,
    get_appointment_count_by_patient_and_status,
    get_available_time_slots
)
from app.auth_utils import get_current_user, get_admin_user, get_doctor_user, get_patient_user, get_staff_user, User

router = APIRouter(prefix="/api/appointments", tags=["Appointments"])

# Basic CRUD operations
@router.get("/", operation_id="get_all_appointments")
def get_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all appointments"""
    return get_all_appointments(db)

@router.post(
    "/", 
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_appointment",
    summary="Create a new appointment",
    description="Create a new appointment with the provided details"
)
async def create_new_appointment(
    appointment: AppointmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=["ADMIN", "DOCTOR", "STAFF"])
):
    """
    Create a new appointment with the following information:
    - **doctor_id**: ID of the doctor
    - **patient_id**: ID of the patient
    - **facility_id**: ID of the facility
    - **doctor_name**: Name of the doctor
    - **patient_name**: Name of the patient
    - **appointment_date**: Date of the appointment
    - **appointment_start_time**: Start time of the appointment
    - **appointment_end_time**: End time of the appointment
    - **purpose_of_visit**: Purpose of the visit
    - **description**: Additional description (optional)
    """
    return create_appointment(db, appointment)

@router.get("/id/{appointment_id}", operation_id="get_appointment_by_id")
def get_appointment(
    appointment_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get appointment by ID"""
    return get_appointment_by_id(db, appointment_id)

@router.put("/id/{appointment_id}/status", response_model=AppointmentResponse, operation_id="update_appointment_status")
def update_status(
    appointment_id: str, 
    status_update: AppointmentStatusUpdateRequest, 
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=["ADMIN", "DOCTOR", "STAFF"])
):
    """
    Update appointment status
    - **status**: New status for the appointment (SCHEDULED, COMPLETED, CANCELLED, or PENDING)
    """
    return update_appointment_status(db, appointment_id, status_update.status)

# Patient and doctor endpoints
@router.get("/patient/{patient_id}", operation_id="get_patient_appointments")
def get_patient_appointments(
    patient_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=["ADMIN", "DOCTOR", "STAFF", "PATIENT"])
):
    """Get all appointments for a specific patient"""
    # If user is a patient, they should only see their own appointments
    if current_user.role == "PATIENT" and current_user.username != patient_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patients can only view their own appointments"
        )
    return get_appointments_by_patient_id(db, patient_id)

@router.get("/doctor/{doctor_id}", operation_id="get_doctor_appointments")
def get_doctor_appointments(
    doctor_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=["ADMIN", "DOCTOR", "STAFF"])
):
    """Get all appointments for a specific doctor"""
    # If user is a doctor, they should only see their own appointments
    if current_user.role == "DOCTOR" and current_user.username != doctor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctors can only view their own appointments"
        )
    return get_appointments_by_doctor_id(db, doctor_id)

# Status count endpoints
@router.get("/count/scheduled", operation_id="get_scheduled_appointments_count")
def get_scheduled_appointments_count(
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=["ADMIN", "STAFF"])
):
    """Get count of scheduled appointments"""
    return get_appointments_count_by_status(db, AppointmentStatus.SCHEDULED)

@router.get("/count/pending", operation_id="get_pending_appointments_count")
def get_pending_appointments_count(
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=["ADMIN", "STAFF"])
):
    """Get count of pending appointments"""
    return get_appointments_count_by_status(db, AppointmentStatus.PENDING)

@router.get("/count/cancelled", operation_id="get_cancelled_appointments_count")
def get_cancelled_appointments_count(
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=["ADMIN", "STAFF"])
):
    """Get count of cancelled appointments"""
    return get_appointments_count_by_status(db, AppointmentStatus.CANCELLED)

@router.get("/count/completed", operation_id="get_completed_appointments_count")
def get_completed_appointments_count(
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=["ADMIN", "STAFF"])
):
    """Get count of completed appointments"""
    return get_appointments_count_by_status(db, AppointmentStatus.COMPLETED)

# Facility endpoint
@router.get("/facility/{facility_id}", operation_id="get_facility_appointments")
def get_facility_appointments(
    facility_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=["ADMIN", "STAFF"])
):
    """Get all appointments for a specific facility"""
    return get_appointments_by_facility_id(db, facility_id)

# Doctor status endpoint
@router.get("/doctor/{doctor_id}/status/{status}", operation_id="get_doctor_appointments_by_status")
def get_appointment_count_for_doctor(
    doctor_id: str,
    status: AppointmentStatus,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=["ADMIN", "DOCTOR", "STAFF"])
):
    """Get count of appointments for a doctor by status"""
    # If user is a doctor, they should only see their own appointments
    if current_user.role == "DOCTOR" and current_user.username != doctor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctors can only view their own appointment counts"
        )
    return get_appointment_count_by_doctor_and_status(db, doctor_id, status)

# Patient status endpoint
@router.get("/patient/{patient_id}/status/{status}", operation_id="get_patient_appointments_by_status")
def get_appointment_count_for_patient(
    patient_id: str,
    status: AppointmentStatus,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=["ADMIN", "DOCTOR", "STAFF", "PATIENT"])
):
    """Get count of appointments for a patient by status"""
    # If user is a patient, they should only see their own appointments
    if current_user.role == "PATIENT" and current_user.username != patient_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patients can only view their own appointment counts"
        )
    return get_appointment_count_by_patient_and_status(db, patient_id, status)

# Time slots endpoint
@router.get("/slots/available", operation_id="get_available_time_slots")
def get_available_slots(
    doctor_id: str,
    appointment_date: date = Query(..., alias="date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get available time slots for a doctor on a specific date"""
    return get_available_time_slots(db, doctor_id, appointment_date)

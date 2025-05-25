from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import date, time
from typing import List
from fastapi import HTTPException
from app.models.appointments import Appointment, AppointmentStatus
from app.schemas.appointments import TimeSlot, AppointmentRequest
import logging

logger = logging.getLogger(__name__)

def get_all_appointments(db: Session) -> List[Appointment]:
    """Get all appointments"""
    try:
        return db.query(Appointment).all()
    except Exception as e:
        logger.error(f"Error fetching all appointments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def get_appointment_by_id(db: Session, appointment_id: str) -> Appointment:
    """Get appointment by ID"""
    appointment = db.query(Appointment).filter(Appointment.appointment_id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

def create_appointment(db: Session, appointment: AppointmentRequest) -> Appointment:
    """Create a new appointment"""
    try:
        # Get the last appointment and extract the numeric part of the ID
        last_appointment = db.query(Appointment).order_by(Appointment.appointment_id.desc()).first()
        if last_appointment:
            last_id = int(last_appointment.appointment_id[3:])  # Extract number after 'APT'
            next_id = last_id + 1
        else:
            next_id = 1
            
        appointment_id = f"APT{str(next_id).zfill(4)}"  # Format: APT0001, APT0002, etc.

        # Check for conflicting appointments
        existing_appointment = db.query(Appointment).filter(
            and_(
                Appointment.doctor_id == appointment.doctor_id,
                Appointment.appointment_date == appointment.appointment_date,
                Appointment.status != AppointmentStatus.CANCELLED,
                and_(
                    Appointment.appointment_start_time < appointment.appointment_end_time,
                    Appointment.appointment_end_time > appointment.appointment_start_time
                )
            )
        ).first()

        if existing_appointment:
            raise HTTPException(
                status_code=400,
                detail="Doctor already has an appointment scheduled during this time"
            )

        db_appointment = Appointment(
            appointment_id=appointment_id,
            doctor_id=appointment.doctor_id,
            patient_id=appointment.patient_id,
            facility_id=appointment.facility_id,
            doctor_name=appointment.doctor_name,
            patient_name=appointment.patient_name,
            appointment_date=appointment.appointment_date,
            appointment_start_time=appointment.appointment_start_time,
            appointment_end_time=appointment.appointment_end_time,
            purpose_of_visit=appointment.purpose_of_visit,
            description=appointment.description,
            status=AppointmentStatus.SCHEDULED
        )
        
        db.add(db_appointment)
        db.commit()
        db.refresh(db_appointment)
        return db_appointment

    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating appointment: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

def update_appointment_status(db: Session, appointment_id: str, new_status: AppointmentStatus) -> Appointment:
    """Update appointment status"""
    try:
        appointment = get_appointment_by_id(db, appointment_id)
        appointment.status = new_status
        db.commit()
        db.refresh(appointment)
        return appointment
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating appointment status: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating appointment status")

def get_appointments_by_patient_id(db: Session, patient_id: str) -> List[Appointment]:
    """Get all appointments for a specific patient"""
    try:
        return db.query(Appointment).filter(Appointment.patient_id == patient_id).all()
    except Exception as e:
        logger.error(f"Error fetching patient appointments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def get_appointments_by_doctor_id(db: Session, doctor_id: str) -> List[Appointment]:
    """Get all appointments for a specific doctor"""
    try:
        return db.query(Appointment).filter(Appointment.doctor_id == doctor_id).all()
    except Exception as e:
        logger.error(f"Error fetching doctor appointments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def get_appointments_by_facility_id(db: Session, facility_id: str) -> List[Appointment]:
    return db.query(Appointment).filter(Appointment.facility_id == facility_id).all()

def get_appointment_count_by_doctor_and_status(
    db: Session,
    doctor_id: str,
    status: AppointmentStatus
) -> int:
    return db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.status == status
    ).count()

def get_appointment_count_by_patient_and_status(
    db: Session,
    patient_id: str,
    status: AppointmentStatus
) -> int:
    return db.query(Appointment).filter(
        Appointment.patient_id == patient_id,
        Appointment.status == status
    ).count()

def get_available_time_slots(
    db: Session,
    doctor_id: str,
    date: date
) -> List[TimeSlot]:
    # Get all appointments for the doctor on the given date
    booked_slots = db.query(
        Appointment.appointment_start_time,
        Appointment.appointment_end_time
    ).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == date,
        Appointment.status != AppointmentStatus.CANCELLED
    ).all()
    
    # Define working hours (e.g., 9 AM to 5 PM)
    working_hours = [
        TimeSlot(
            start_time=time(hour=i),
            end_time=time(hour=i+1)
        ) for i in range(9, 17)
    ]
    
    # Remove booked slots
    available_slots = []
    for slot in working_hours:
        is_available = True
        for booked in booked_slots:
            if (slot.start_time >= booked.appointment_start_time and 
                slot.start_time < booked.appointment_end_time):
                is_available = False
                break
        if is_available:
            available_slots.append(slot)
    
    return available_slots

def get_appointments_count_by_status(db: Session, status: AppointmentStatus) -> int:
    return db.query(Appointment).filter(Appointment.status == status).count()

from sqlalchemy import Column, Integer, String, Date, Time, DateTime, Text
from sqlalchemy.sql import func
from app.models.base import Base
from enum import Enum as PyEnum

class AppointmentStatus(str, PyEnum):
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    PENDING = "PENDING"

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True)
    appointment_id = Column(String(50), unique=True, nullable=False)
    doctor_id = Column(String(50),  nullable=False)
    patient_id = Column(String(50), nullable=False)
    facility_id = Column(String(50), nullable=False)
    doctor_name = Column(String(100), nullable=False)
    patient_name = Column(String(100), nullable=False)
    appointment_date = Column(Date, nullable=False)
    appointment_start_time = Column(Time, nullable=False)
    appointment_end_time = Column(Time, nullable=False)
    purpose_of_visit = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default=AppointmentStatus.PENDING)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://cmd_user:GIxYa0Fx753DAD47VNY9pH8Dpuq3Le7l@dpg-d0p91j8dl3ps73aipd3g-a/cmd")
    
    # Service URLs for inter-service communication
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "https://healthcare-auth-service.onrender.com")
    DOCTOR_SERVICE_URL: str = os.getenv("DOCTOR_SERVICE_URL", "https://healthcare-doctor-service.onrender.com")
    PATIENT_SERVICE_URL: str = os.getenv("PATIENT_SERVICE_URL", "https://healthcare-patient-service.onrender.com")
    APPOINTMENT_SERVICE_URL: str = os.getenv("APPOINTMENT_SERVICE_URL", "https://healthcare-appointment-service.onrender.com")
    FACILITY_SERVICE_URL: str = os.getenv("FACILITY_SERVICE_URL", "https://healthcare-facility-service.onrender.com")
    ASSETS_SERVICE_URL: str = os.getenv("ASSETS_SERVICE_URL", "https://healthcare-assets-service.onrender.com")
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "YOUR_SECRET_KEY_HERE")

    class Config:
        env_file = ".env"

# Create a settings instance
settings = Settings()





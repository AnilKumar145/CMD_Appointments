import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:Anil@localhost:5432/healthcare_db"
    
    # Service URLs for inter-service communication
    DOCTOR_SERVICE_URL: str = "http://localhost:8001"
    PATIENT_SERVICE_URL: str = "http://localhost:8002"

    class Config:
        env_file = ".env"

# Create a settings instance
settings = Settings()

# Export DATABASE_URL as a separate variable for convenience
DATABASE_URL = settings.DATABASE_URL





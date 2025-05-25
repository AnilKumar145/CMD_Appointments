
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from app.database import engine, Base
from app.routers import appointments
from app.auth_utils import get_current_user, User

# Create FastAPI app
app = FastAPI(
    title="Appointment Microservice",
    description="Handles appointment management in the healthcare system",
    version="1.0.0",
    swagger_ui_parameters={
        "deepLinking": True,
        "displayOperationId": True,
        "defaultModelsExpandDepth": 3,
        "defaultModelExpandDepth": 3,
        "docExpansion": "list",
        "filter": True,
        "showExtensions": True,
        "showCommonExtensions": True,
        "persistAuthorization": True  # This will keep the authorization token in the UI
    }
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(appointments.router)

@app.get("/")
def read_root():
    return {"message": "Appointment Microservice Running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    return {
        "message": "This is a protected route",
        "user": current_user.username,
        "role": current_user.role
    }

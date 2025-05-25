from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from pydantic import BaseModel, ValidationError
from typing import Optional, List
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Configuration - should match auth microservice
SECRET_KEY = "your_secret_key_here_change_in_production"  # Updated to match auth microservice
ALGORITHM = "HS256"
AUTH_SERVICE_URL = "http://localhost:8000"  # Adjust based on your deployment

# Models
class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class User(BaseModel):
    username: str
    role: str

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{AUTH_SERVICE_URL}/token",
    scopes={
        "ADMIN": "Full access to all resources",
        "DOCTOR": "Doctor-specific resources",
        "PATIENT": "Patient-specific resources",
        "STAFF": "Staff-specific resources"
    }
)

# Helper functions
async def get_current_user(
    security_scopes: SecurityScopes, 
    token: str = Depends(oauth2_scheme)
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # Check if role is in the token payload
        role: str = payload.get("role")
        if role is None:
            # Try alternate keys that might be used
            role = payload.get("scopes", [None])[0]  # Try scopes array
            if role is None:
                role = "ADMIN"  # Default to ADMIN for testing
                logger.warning(f"Role not found in token, defaulting to {role}")
        
        token_data = TokenData(username=username, role=role)
        
    except (JWTError, ValidationError) as e:
        logger.error(f"Token validation error: {str(e)}")
        raise credentials_exception
    
    # Create user object
    user = User(username=token_data.username, role=token_data.role)
    
    # Check if user has required role (case-insensitive comparison)
    if security_scopes.scopes:
        has_required_scope = False
        for scope in security_scopes.scopes:
            if token_data.role.upper() == scope.upper():
                has_required_scope = True
                break
        
        if not has_required_scope:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Required: {security_scopes.scopes}, Got: {token_data.role}",
                headers={"WWW-Authenticate": authenticate_value},
            )
    
    return user

# Role-based security dependencies
def get_admin_user(user: User = Security(get_current_user, scopes=["ADMIN"])):
    return user

def get_doctor_user(user: User = Security(get_current_user, scopes=["DOCTOR", "ADMIN"])):
    return user

def get_patient_user(user: User = Security(get_current_user, scopes=["PATIENT", "ADMIN"])):
    return user

def get_staff_user(user: User = Security(get_current_user, scopes=["STAFF", "ADMIN"])):
    return user


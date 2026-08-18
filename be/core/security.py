from typing import Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import decode, ExpiredSignatureError, InvalidTokenError
import os

security = HTTPBearer()

# Must match the Auth Service JWT_SECRET
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    if IS_PRODUCTION:
        raise RuntimeError("CRITICAL SECURITY ERROR: JWT_SECRET environment variable is mandatory in production mode.")
    JWT_SECRET = "super-secret-key-for-dev-only"

ALGORITHM = "HS256"


def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    token = credentials.credentials
    try:
        payload = decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

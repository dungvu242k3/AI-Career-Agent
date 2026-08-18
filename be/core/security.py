from typing import Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import decode, ExpiredSignatureError, InvalidTokenError
import os

from be.config import get_settings

security = HTTPBearer()


def get_jwt_secret() -> str:
    """Retrieve JWT secret from settings/env. Raises error if not configured."""
    secret = get_settings().get_jwt_secret_value()
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Hệ thống xác thực chưa được cấu hình khóa bảo mật (JWT_SECRET).",
        )
    return secret


def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    token = credentials.credentials
    jwt_secret = get_jwt_secret()
    algorithm = get_settings().jwt_algorithm

    try:
        payload = decode(token, jwt_secret, algorithms=[algorithm])

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

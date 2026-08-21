from dataclasses import dataclass
from typing import Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import decode, ExpiredSignatureError, InvalidTokenError

from be.config import get_settings

security = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    """Identity asserted by the Auth service access token."""

    id: int
    email: str
    tier: str


def get_jwt_secret() -> str:
    """Retrieve JWT secret from settings/env. Raises error if not configured."""
    secret = get_settings().get_jwt_secret_value()
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Hệ thống xác thực chưa được cấu hình khóa bảo mật (JWT_SECRET).",
        )
    return secret


def verify_jwt_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict[str, Any]:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    jwt_secret = get_jwt_secret()
    algorithm = get_settings().jwt_algorithm

    try:
        payload = decode(
            token,
            jwt_secret,
            algorithms=[algorithm],
            issuer=get_settings().jwt_issuer,
            audience=get_settings().jwt_audience,
        )

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


def require_current_user(payload: dict[str, Any] = Depends(verify_jwt_token)) -> CurrentUser:
    """Validate the minimum claims needed to authorize data access.

    The Node.js auth service is the token issuer.  FastAPI deliberately trusts
    only a numeric subject and a bounded subscription tier; route handlers must
    use this dependency before reading user-owned data.
    """
    try:
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token subject is invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user_id <= 0:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token subject is invalid")

    tier = payload.get("tier", "free")
    if tier not in {"free", "pro"}:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token tier is invalid")

    email = payload.get("email")
    if not isinstance(email, str) or not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token email is invalid")

    return CurrentUser(id=user_id, email=email, tier=tier)

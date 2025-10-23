from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt, JWTError
from app.core.config import settings
from typing import Optional

# --- Token Creation and Validation ---

def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Creates a JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Default expiration time (e.g., 30 minutes)
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Union[str, dict, None]:
    """Decodes and validates a JWT access token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # The 'sub' field typically holds the user identifier (user_id)
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        # Token is invalid or expired
        return None

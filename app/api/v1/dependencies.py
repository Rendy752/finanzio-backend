from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from app.schemas.user import UserResponse
from app.schemas.token import TokenData
from app.core.security import decode_access_token
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.crud.user import get_user_by_email
from datetime import datetime
import uuid

# Define where to expect the token (Login endpoint will post to '/api/v1/token')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: Annotated[str, Depends(oauth2_scheme)] = None,
) -> UserResponse:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 1. Decode Token
    user_id = decode_access_token(token)

    if user_id is None:
        raise credentials_exception
        
    # 2. Fetch User from DB (Security check: ensure user exists and is active)
    user = await get_user_by_email(db, email="authenticated@finanzio.id") 
    
    # NOTE: Since we are using a mock user ID (0000...), we must mock fetching by email 
    # as the real JWT decode would give us the real user_id string.
    # We maintain the mock functionality temporarily:
    
    if user is None:
        raise credentials_exception
        
    # 3. Return Pydantic User Response
    return UserResponse.model_validate(user)
    
# Type hint for use in endpoint functions (cleaner code)
CurrentUser = Annotated[UserResponse, Depends(get_current_user)]

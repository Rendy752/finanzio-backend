from fastapi import Depends, HTTPException, status
from typing import Annotated
from app.schemas.user import UserResponse
from datetime import datetime
import uuid

# NOTE: This is a PLACEHOLDER dependency.
# In a real application, this function would:
# 1. Extract the JWT token from the Authorization header.
# 2. Decode and validate the token.
# 3. Fetch the User object from the database using the user_id in the token.

async def get_current_user() -> UserResponse:
    """
    Placeholder dependency to simulate fetching the authenticated user.
    """
    # *** Replace this with actual JWT authentication logic ***
    
    # Dummy UUID for CRUD testing and user context.
    DUMMY_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
    
    return UserResponse(
        user_id=DUMMY_USER_ID, 
        email="authenticated@finanzio.id",
        first_name="Auth",
        last_name="User",
        is_active=True,
        created_at=datetime.utcnow()
    )
    
# Type hint for use in endpoint functions (cleaner code)
CurrentUser = Annotated[UserResponse, Depends(get_current_user)]
# app/api/v1/endpoints.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.user import UserCreate, UserResponse
from app.schemas.common import APIResponse
from app.crud.users import create_user  # CRUD function to save user to DB

router = APIRouter()

@router.post(
    "/users/", 
    response_model=APIResponse[UserResponse], 
    status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_in: UserCreate, 
    db: AsyncSession = Depends(get_db)
):
    """Handles new user registration."""
    # 1. Validation is automatically handled by Pydantic (UserCreate)
    
    # 2. Database interaction (using CRUD)
    db_user = await create_user(db, user_in=user_in)
    
    # 3. Security Check (Example: If email already exists)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )

    # 4. Standardized Response (wrapped by APIResponse)
    return APIResponse(
        message="User successfully registered.",
        data=UserResponse.model_validate(db_user)
    )
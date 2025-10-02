from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.user import UserCreate, UserResponse
from app.schemas.common import APIResponse
from app.crud.user import create_user 
from app.api.v1 import wallet

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
    db_user = await create_user(db, user_in=user_in)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )

    return APIResponse(
        message="User successfully registered.",
        data=UserResponse.model_validate(db_user)
    )

router.include_router(wallet.router)
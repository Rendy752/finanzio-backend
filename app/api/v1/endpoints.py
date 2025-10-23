from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token
from app.schemas.common import APIResponse
from app.crud import user as crud_user
from app.core.security import create_access_token
from app.api.v1 import wallet 
from app.api.v1 import category
from app.api.v1 import transaction
from app.api.v1 import debt
from app.api.v1 import budget

router = APIRouter()

# ----------------------------------------------------------------------
# 1. AUTHENTICATION ENDPOINTS (LOGIN)
# ----------------------------------------------------------------------

@router.post("/token", response_model=Token, summary="Authenticate and get JWT Access Token.")
async def login_for_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(), # Standard form login
):
    # 1. Cari user berdasarkan username (email)
    user = await crud_user.get_user_by_email(db, email=form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )
    
    # 2. Verifikasi Password
    if not crud_user.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )
        
    # 3. Buat Access Token (subject = user_id)
    access_token = create_access_token(
        subject=user.user_id # Menggunakan UUID sebagai subject
    )
    
    return Token(access_token=access_token)

# ----------------------------------------------------------------------
# 2. USER REGISTRATION (TETAP SAMA)
# ----------------------------------------------------------------------

@router.post(
    "/users/", 
    response_model=APIResponse[UserResponse], 
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account."
)
async def register_user(
    user_in: UserCreate, 
    db: AsyncSession = Depends(get_db)
):
    db_user = await crud_user.create_user(db, user_in=user_in)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )

    return APIResponse(
        message="User successfully registered.",
        data=UserResponse.model_validate(db_user)
    )

# ----------------------------------------------------------------------
# 3. RESOURCE ROUTERS
# ----------------------------------------------------------------------

router.include_router(wallet.router) 
router.include_router(category.router)
router.include_router(transaction.router)
router.include_router(debt.router)
router.include_router(budget.router)
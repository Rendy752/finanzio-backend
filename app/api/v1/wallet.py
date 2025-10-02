from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.core.db import get_db
from app.crud import wallet as crud_wallet
from app.schemas.wallet import WalletCreate, WalletResponse, WalletBase
from app.schemas.common import APIResponse, APIListResponse
from app.api.v1.dependencies import CurrentUser # Import dependency

router = APIRouter(prefix="/wallets", tags=["Wallets"])

DB_SESSION = Depends(get_db)

@router.post(
    "/",
    response_model=APIResponse[WalletResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new financial wallet/account."
)
async def create_wallet(
    wallet_in: WalletCreate,
    current_user: CurrentUser, # Requires authentication
    db: AsyncSession = DB_SESSION
):
    """Creates a new wallet (e.g., Cash, Bank Account) for the authenticated user."""
    db_wallet = await crud_wallet.create_wallet(
        db, 
        wallet_in=wallet_in, 
        user_id=current_user.user_id
    )
    
    return APIResponse(
        message="Wallet created successfully.",
        data=WalletResponse.model_validate(db_wallet)
    )

@router.get(
    "/",
    response_model=APIListResponse[WalletResponse],
    summary="Get all financial wallets for the authenticated user."
)
async def read_wallets(
    current_user: CurrentUser,
    db: AsyncSession = DB_SESSION
):
    """Retrieves a list of all wallets owned by the current user."""
    db_wallets = await crud_wallet.get_all_wallets_for_user(
        db, 
        user_id=current_user.user_id
    )
    
    # Using APIListResponse, aligned with the request structure.
    return APIListResponse(
        message="Wallets retrieved successfully.",
        data=[WalletResponse.model_validate(w) for w in db_wallets],
        total_count=len(db_wallets)
    )
    
@router.get(
    "/{wallet_id}",
    response_model=APIResponse[WalletResponse],
    summary="Get a specific wallet by ID."
)
async def read_wallet(
    wallet_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = DB_SESSION
):
    """Retrieves details for a specific wallet, ensuring ownership by the current user."""
    
    db_wallet = await crud_wallet.get_wallet_by_id(
        db, 
        wallet_id=wallet_id, 
        user_id=current_user.user_id
    )
    
    if not db_wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found or not accessible."
        )

    return APIResponse(
        message="Wallet retrieved successfully.",
        data=WalletResponse.model_validate(db_wallet)
    )

@router.put(
    "/{wallet_id}",
    response_model=APIResponse[WalletResponse],
    summary="Update wallet name and/or currency."
)
async def update_wallet(
    wallet_id: uuid.UUID,
    wallet_in: WalletBase, 
    current_user: CurrentUser,
    db: AsyncSession = DB_SESSION
):
    """Updates the name and currency of an existing wallet."""
    
    db_wallet = await crud_wallet.update_wallet(
        db,
        wallet_id=wallet_id,
        user_id=current_user.user_id,
        wallet_in=wallet_in
    )
    
    if not db_wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found or not accessible for update."
        )
        
    return APIResponse(
        message="Wallet updated successfully.",
        data=WalletResponse.model_validate(db_wallet)
    )

@router.delete(
    "/{wallet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response, 
    summary="Delete a specific wallet."
)
async def delete_wallet(
    wallet_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = DB_SESSION
):
    """Deletes a wallet owned by the current user."""
    
    deleted = await crud_wallet.delete_wallet(
        db,
        wallet_id=wallet_id,
        user_id=current_user.user_id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found or not accessible for deletion."
        )
        
    # Standard response for successful deletion (No Content)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
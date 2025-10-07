from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from app.core.db import get_db
from app.crud import transaction as crud_transaction
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.schemas.common import APIResponse, APIListResponse
from app.api.v1.dependencies import CurrentUser 

router = APIRouter(prefix="/transactions", tags=["Transactions"])

DB_SESSION = Depends(get_db)

@router.post(
    "/",
    response_model=APIResponse[TransactionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Record a new financial transaction."
)
async def create_transaction(
    transaction_in: TransactionCreate,
    current_user: CurrentUser,
    db: AsyncSession = DB_SESSION
):
    """Records a new transaction and automatically updates the associated wallet's balance."""
    
    db_transaction = await crud_transaction.create_transaction(
        db, 
        transaction_in=transaction_in, 
        user_id=current_user.user_id
    )
    
    if not db_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet or Category not found, or Wallet is not owned by the user."
        )
    
    return APIResponse(
        message="Transaction recorded and wallet balance updated successfully.",
        data=TransactionResponse.model_validate(db_transaction)
    )

@router.get(
    "/",
    response_model=APIListResponse[TransactionResponse],
    summary="Get all transactions for the authenticated user."
)
async def read_transactions(
    current_user: CurrentUser,
    db: AsyncSession = DB_SESSION,
    q: Optional[str] = Query(None, description="Search by transaction description."),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Retrieves a list of all user's transactions with search and pagination."""
    
    db_transactions, total_count = await crud_transaction.get_all_transactions_for_user(
        db, 
        user_id=current_user.user_id,
        q=q,
        limit=limit,
        offset=offset
    )
    
    return APIListResponse(
        message="Transactions retrieved successfully.",
        data=[TransactionResponse.model_validate(t) for t in db_transactions],
        total_count=total_count
    )
    
@router.get(
    "/{transaction_id}",
    response_model=APIResponse[TransactionResponse],
    summary="Get a specific transaction by ID."
)
async def read_transaction(
    transaction_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = DB_SESSION
):
    """Retrieves details for a specific transaction."""
    
    db_transaction = await crud_transaction.get_transaction_by_id(
        db, 
        transaction_id=transaction_id, 
        user_id=current_user.user_id
    )
    
    if not db_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found or not accessible."
        )

    return APIResponse(
        message="Transaction retrieved successfully.",
        data=TransactionResponse.model_validate(db_transaction)
    )

@router.put(
    "/{transaction_id}",
    response_model=APIResponse[TransactionResponse],
    summary="Update transaction details (reverts old balance change and applies new one)."
)
async def update_transaction(
    transaction_id: uuid.UUID,
    transaction_in: TransactionCreate, 
    current_user: CurrentUser,
    db: AsyncSession = DB_SESSION
):
    """Updates the transaction entry, ensuring wallet balance is recalculated based on changes."""
    
    db_transaction = await crud_transaction.update_transaction(
        db,
        transaction_id=transaction_id,
        user_id=current_user.user_id,
        transaction_in=transaction_in
    )
    
    if not db_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found or not accessible for update."
        )
        
    return APIResponse(
        message="Transaction updated and wallet balance re-calculated successfully.",
        data=TransactionResponse.model_validate(db_transaction)
    )

@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response, 
    summary="Delete a specific transaction."
)
async def delete_transaction(
    transaction_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = DB_SESSION
):
    """Deletes a transaction and reverts the change to the associated wallet balance."""
    
    deleted = await crud_transaction.delete_transaction(
        db,
        transaction_id=transaction_id,
        user_id=current_user.user_id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found or not accessible for deletion."
        )
        
    return Response(status_code=status.HTTP_204_NO_CONTENT)
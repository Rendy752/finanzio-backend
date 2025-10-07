from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from app.core.db import get_db
from app.crud import debt as crud_debt
from app.schemas.debt import DebtLedgerCreate, DebtLedgerUpdate, DebtLedgerResponse
from app.schemas.common import APIResponse, APIListResponse
from app.api.v1.dependencies import CurrentUser 

router = APIRouter(prefix="/debts", tags=["Debt Ledger"])

DB_SESSION = Depends(get_db)

@router.post(
    "/",
    response_model=APIResponse[DebtLedgerResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Record a new debt or receivable."
)
async def create_debt(
    debt_in: DebtLedgerCreate,
    current_user: CurrentUser,
    db: AsyncSession = DB_SESSION
):
    """Creates a new debt ledger entry (money owed to user or user owes money)."""
    db_debt = await crud_debt.create_debt(
        db, 
        debt_in=debt_in, 
        user_id=current_user.user_id
    )
    
    return APIResponse(
        message="Debt entry created successfully.",
        data=DebtLedgerResponse.model_validate(db_debt)
    )

@router.get(
    "/",
    response_model=APIListResponse[DebtLedgerResponse],
    summary="Get all debt ledger entries for the authenticated user."
)
async def read_debts(
    current_user: CurrentUser,
    db: AsyncSession = DB_SESSION,
    q: Optional[str] = Query(None, description="Search by contact name or phone number."),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Retrieves a list of all user's debt and receivable entries with search and pagination."""
    
    db_debts, total_count = await crud_debt.get_all_debts_for_user(
        db, 
        user_id=current_user.user_id,
        q=q,
        limit=limit,
        offset=offset
    )
    
    return APIListResponse(
        message="Debt entries retrieved successfully.",
        data=[DebtLedgerResponse.model_validate(d) for d in db_debts],
        total_count=total_count
    )
    
@router.get(
    "/{ledger_id}",
    response_model=APIResponse[DebtLedgerResponse],
    summary="Get a specific debt entry by ID."
)
async def read_debt(
    ledger_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = DB_SESSION
):
    """Retrieves details for a specific debt entry."""
    
    db_debt = await crud_debt.get_debt_by_id(
        db, 
        ledger_id=ledger_id, 
        user_id=current_user.user_id
    )
    
    if not db_debt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Debt entry not found or not accessible."
        )

    return APIResponse(
        message="Debt entry retrieved successfully.",
        data=DebtLedgerResponse.model_validate(db_debt)
    )

@router.put(
    "/{ledger_id}",
    response_model=APIResponse[DebtLedgerResponse],
    summary="Update debt, record payment, or mark as settled."
)
async def update_debt(
    ledger_id: uuid.UUID,
    debt_in: DebtLedgerUpdate, 
    current_user: CurrentUser,
    db: AsyncSession = DB_SESSION
):
    """Updates the debt entry (e.g., adding a partial payment)."""
    
    db_debt = await crud_debt.update_debt(
        db,
        ledger_id=ledger_id,
        user_id=current_user.user_id,
        debt_in=debt_in
    )
    
    if not db_debt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Debt entry not found or not accessible for update."
        )
        
    return APIResponse(
        message="Debt entry updated successfully.",
        data=DebtLedgerResponse.model_validate(db_debt)
    )

@router.delete(
    "/{ledger_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response, 
    summary="Delete a specific debt entry."
)
async def delete_debt(
    ledger_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = DB_SESSION
):
    """Deletes a debt ledger entry."""
    
    deleted = await crud_debt.delete_debt(
        db,
        ledger_id=ledger_id,
        user_id=current_user.user_id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Debt entry not found or not accessible for deletion."
        )
        
    return Response(status_code=status.HTTP_204_NO_CONTENT)
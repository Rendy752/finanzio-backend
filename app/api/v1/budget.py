from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.core.db import get_db
from app.crud import budget as crud_budget
from app.schemas.budget import BudgetCreate, BudgetResponse
from app.schemas.common import APIResponse, APIListResponse
from app.api.v1.dependencies import CurrentUser 

router = APIRouter(prefix="/budgets", tags=["Budgets"])

DB_SESSION = Depends(get_db)

@router.post(
    "/",
    response_model=APIResponse[BudgetResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new spending budget."
)
async def create_budget(
    budget_in: BudgetCreate,
    current_user: CurrentUser,
    db: AsyncSession = DB_SESSION
):
    """Creates a new budget for a specific category (Spendee style)."""
    db_budget = await crud_budget.create_budget(
        db, 
        budget_in=budget_in, 
        user_id=current_user.user_id
    )
    
    return APIResponse(
        message="Budget created successfully.",
        data=BudgetResponse.model_validate(db_budget)
    )

@router.get(
    "/",
    response_model=APIListResponse[BudgetResponse],
    summary="Get all budgets for the authenticated user."
)
async def read_budgets(
    current_user: CurrentUser,
    db: AsyncSession = DB_SESSION,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Retrieves a list of all user's budgets with pagination."""
    
    db_budgets, total_count = await crud_budget.get_all_budgets_for_user(
        db, 
        user_id=current_user.user_id,
        limit=limit,
        offset=offset
    )
    
    return APIListResponse(
        message="Budgets retrieved successfully.",
        data=[BudgetResponse.model_validate(b) for b in db_budgets],
        total_count=total_count
    )
    
@router.get(
    "/{budget_id}",
    response_model=APIResponse[BudgetResponse],
    summary="Get a specific budget by ID."
)
async def read_budget(
    budget_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = DB_SESSION
):
    """Retrieves details for a specific budget."""
    
    db_budget = await crud_budget.get_budget_by_id(
        db, 
        budget_id=budget_id, 
        user_id=current_user.user_id
    )
    
    if not db_budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found or not accessible."
        )

    return APIResponse(
        message="Budget retrieved successfully.",
        data=BudgetResponse.model_validate(db_budget)
    )

@router.put(
    "/{budget_id}",
    response_model=APIResponse[BudgetResponse],
    summary="Update budget details."
)
async def update_budget(
    budget_id: uuid.UUID,
    budget_in: BudgetCreate, 
    current_user: CurrentUser,
    db: AsyncSession = DB_SESSION
):
    """Updates the budget entry details (e.g., amount, dates)."""
    
    db_budget = await crud_budget.update_budget(
        db,
        budget_id=budget_id,
        user_id=current_user.user_id,
        budget_in=budget_in
    )
    
    if not db_budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found or not accessible for update."
        )
        
    return APIResponse(
        message="Budget updated successfully.",
        data=BudgetResponse.model_validate(db_budget)
    )

@router.delete(
    "/{budget_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response, 
    summary="Delete a specific budget."
)
async def delete_budget(
    budget_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = DB_SESSION
):
    """Deletes a budget entry."""
    
    deleted = await crud_budget.delete_budget(
        db,
        budget_id=budget_id,
        user_id=current_user.user_id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found or not accessible for deletion."
        )
        
    return Response(status_code=status.HTTP_204_NO_CONTENT)
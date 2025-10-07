from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update, func, or_
from typing import List, Optional, Tuple
from uuid import UUID
from datetime import date

from app.models.transaction import Budget
from app.schemas.budget import BudgetCreate

# --- Read Operations ---

async def get_budget_by_id(db: AsyncSession, budget_id: UUID, user_id: UUID) -> Optional[Budget]:
    """Retrieves a single budget by ID, owned by the specified user."""
    result = await db.execute(
        select(Budget)
        .where(Budget.budget_id == budget_id)
        .where(Budget.user_id == user_id)
    )
    return result.scalars().first()

async def get_all_budgets_for_user(
    db: AsyncSession, 
    user_id: UUID, 
    limit: int = 10, 
    offset: int = 0
) -> Tuple[List[Budget], int]:
    """Retrieves all budgets for a specific user with pagination."""
    
    base_query = select(Budget).where(Budget.user_id == user_id)
    
    # 1. Get Total Count
    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total_count = total_result.scalar_one()

    # 2. Apply Ordering and Pagination
    final_query = base_query.order_by(Budget.start_date.desc()).limit(limit).offset(offset)
    
    result = await db.execute(final_query)
    budgets = result.scalars().all()
    
    return budgets, total_count

# --- Write Operations ---

async def create_budget(db: AsyncSession, budget_in: BudgetCreate, user_id: UUID) -> Budget:
    """Creates a new budget entry."""
    db_budget = Budget(
        user_id=user_id,
        category_id=budget_in.category_id,
        amount_limit=budget_in.amount_limit,
        start_date=budget_in.start_date,
        end_date=budget_in.end_date
    )
    
    db.add(db_budget)
    await db.commit()
    await db.refresh(db_budget)
    
    return db_budget

async def update_budget(db: AsyncSession, budget_id: UUID, user_id: UUID, budget_in: BudgetCreate) -> Optional[Budget]:
    """Updates an existing budget entry."""
    
    # Use model_dump to exclude None values if using partial update (PUT)
    update_values = budget_in.model_dump(exclude_unset=True)

    stmt = (
        update(Budget)
        .where(Budget.budget_id == budget_id)
        .where(Budget.user_id == user_id)
        .values(**update_values)
        .returning(Budget)
    )
    
    result = await db.execute(stmt)
    await db.commit()
    
    return result.scalars().first()

async def delete_budget(db: AsyncSession, budget_id: UUID, user_id: UUID) -> bool:
    """Deletes a budget entry."""
    stmt = (
        delete(Budget)
        .where(Budget.budget_id == budget_id)
        .where(Budget.user_id == user_id)
    )
    
    result = await db.execute(stmt)
    await db.commit()
    
    return result.rowcount > 0
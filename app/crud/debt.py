from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update, func, or_
from typing import List, Optional, Tuple
from uuid import UUID

from app.models.debt import DebtLedger
from app.schemas.debt import DebtLedgerCreate, DebtLedgerUpdate

# --- Read Operations ---

async def get_debt_by_id(db: AsyncSession, ledger_id: UUID, user_id: UUID) -> Optional[DebtLedger]:
    """Retrieves a single debt ledger entry by ID, owned by the specified user."""
    result = await db.execute(
        select(DebtLedger)
        .where(DebtLedger.ledger_id == ledger_id)
        .where(DebtLedger.user_id == user_id)
    )
    return result.scalars().first()

async def get_all_debts_for_user(
    db: AsyncSession, 
    user_id: UUID, 
    q: Optional[str] = None, 
    limit: int = 10, 
    offset: int = 0
) -> Tuple[List[DebtLedger], int]:
    """Retrieves all debt ledger entries for a specific user with search and pagination."""
    
    base_query = select(DebtLedger).where(DebtLedger.user_id == user_id)
    
    # 1. Apply Search Filter
    if q:
        search_term = f"%{q}%"
        base_query = base_query.where(
            or_(
                DebtLedger.contact_name.ilike(search_term),
                DebtLedger.phone_number.ilike(search_term),
            )
        )
        
    # 2. Get Total Count
    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total_count = total_result.scalar_one()

    # 3. Apply Ordering and Pagination
    final_query = base_query.order_by(DebtLedger.due_date).limit(limit).offset(offset)
    
    result = await db.execute(final_query)
    debts = result.scalars().all()
    
    return debts, total_count

# --- Write Operations ---

async def create_debt(db: AsyncSession, debt_in: DebtLedgerCreate, user_id: UUID) -> DebtLedger:
    """Creates a new debt ledger entry."""
    db_debt = DebtLedger(
        user_id=user_id,
        contact_name=debt_in.contact_name,
        total_amount=debt_in.total_amount,
        is_debt_to_user=debt_in.is_debt_to_user,
        phone_number=debt_in.phone_number,
        due_date=debt_in.due_date,
        amount_paid=0.00, 
        is_settled=False
    )
    
    db.add(db_debt)
    await db.commit()
    await db.refresh(db_debt)
    
    return db_debt

async def update_debt(db: AsyncSession, ledger_id: UUID, user_id: UUID, debt_in: DebtLedgerUpdate) -> Optional[DebtLedger]:
    """Updates a debt ledger entry, typically for recording a payment or settling the debt."""
    
    existing_debt = await get_debt_by_id(db, ledger_id, user_id)
    if not existing_debt:
        return None
        
    update_values = {}
    
    if debt_in.amount_paid is not None:
        new_amount_paid = existing_debt.amount_paid + debt_in.amount_paid
        
        if new_amount_paid >= existing_debt.total_amount:
            new_amount_paid = existing_debt.total_amount
            update_values['is_settled'] = True
        
        update_values['amount_paid'] = new_amount_paid
        
    if debt_in.is_settled is not None:
        update_values['is_settled'] = debt_in.is_settled
        if debt_in.is_settled and 'amount_paid' not in update_values:
            update_values['amount_paid'] = existing_debt.total_amount

    if not update_values:
        return existing_debt 

    stmt = (
        update(DebtLedger)
        .where(DebtLedger.ledger_id == ledger_id)
        .where(DebtLedger.user_id == user_id)
        .values(**update_values)
        .returning(DebtLedger)
    )
    
    result = await db.execute(stmt)
    await db.commit()
    
    return result.scalars().first()

async def delete_debt(db: AsyncSession, ledger_id: UUID, user_id: UUID) -> bool:
    """Deletes a debt ledger entry."""
    stmt = (
        delete(DebtLedger)
        .where(DebtLedger.ledger_id == ledger_id)
        .where(DebtLedger.user_id == user_id)
    )
    
    result = await db.execute(stmt)
    await db.commit()
    
    return result.rowcount > 0
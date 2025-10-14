from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update, func, or_
from typing import List, Optional, Tuple
from decimal import Decimal
from uuid import UUID

from app.models.transaction import Transaction
from app.models.wallet import Wallet
from app.models.category import TransactionType
from app.schemas.transaction import TransactionCreate

# --- Helper Function for Balance Update ---

async def _update_wallet_balance(db: AsyncSession, wallet_id: UUID, amount: Decimal, type: TransactionType, is_reversal: bool = False):
    """Adjusts the Wallet balance based on transaction amount and type."""
    
    sign = 1 if type == TransactionType.INCOME else -1
    
    if is_reversal:
        sign = -sign
    
    adjustment = sign * amount

    # 2. Construct the update statement (rest is correct)
    stmt = (
        update(Wallet)
        .where(Wallet.wallet_id == wallet_id)
        .values(
            current_balance=Wallet.current_balance + adjustment
        )
    )
    
    await db.execute(stmt)
    
# --- Read Operations ---

async def get_transaction_by_id(db: AsyncSession, transaction_id: UUID, user_id: UUID) -> Optional[Transaction]:
    """Retrieves a single transaction by ID, ensuring user owns the related wallet."""
    # Subquery to check for user ownership of the wallet
    wallet_check = select(Wallet.wallet_id).where(Wallet.user_id == user_id).scalar_subquery()
    
    result = await db.execute(
        select(Transaction)
        .where(Transaction.transaction_id == transaction_id)
        .where(Transaction.wallet_id.in_(wallet_check))
    )
    return result.scalars().first()

async def get_all_transactions_for_user(
    db: AsyncSession, 
    user_id: UUID, 
    q: Optional[str] = None, 
    limit: int = 10, 
    offset: int = 0
) -> Tuple[List[Transaction], int]:
    """Retrieves transactions for a specific user with search, pagination, and total count."""
    
    # 1. Base query: Filter by transactions whose wallet is owned by the user.
    wallet_check = select(Wallet.wallet_id).where(Wallet.user_id == user_id).scalar_subquery()
    base_query = select(Transaction).where(Transaction.wallet_id.in_(wallet_check))
    
    # 2. Apply Search Filter
    if q:
        search_term = f"%{q}%"
        base_query = base_query.where(Transaction.description.ilike(search_term))
        
    # 3. Get Total Count
    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total_count = total_result.scalar_one()

    # 4. Apply Ordering and Pagination
    final_query = base_query.order_by(Transaction.transaction_date.desc()).limit(limit).offset(offset)
    
    result = await db.execute(final_query)
    transactions = result.scalars().all()
    
    return transactions, total_count

# --- Write Operations ---

async def create_transaction(db: AsyncSession, transaction_in: TransactionCreate, user_id: UUID) -> Optional[Transaction]:
    """Creates a new transaction, validates user ownership of wallet, and updates the wallet balance."""
    
    # CRITICAL VALIDATION: Ensure user owns the wallet
    wallet_check = select(Wallet).where(Wallet.wallet_id == transaction_in.wallet_id).where(Wallet.user_id == user_id)
    if not (await db.execute(wallet_check)).scalar_one_or_none():
        return None # Wallet not found or not owned by user

    # 1. Create the database model instance
    db_transaction = Transaction(
        wallet_id=transaction_in.wallet_id,
        category_id=transaction_in.category_id,
        transaction_type=transaction_in.transaction_type,
        amount=transaction_in.amount,
        description=transaction_in.description,
        transaction_date=transaction_in.transaction_date or func.now()
    )
    
    db.add(db_transaction)
    
    # 2. Update the Wallet balance
    await _update_wallet_balance(
        db, 
        wallet_id=db_transaction.wallet_id, 
        amount=db_transaction.amount, 
        type=db_transaction.transaction_type,
        is_reversal=False
    )
    
    await db.commit()
    await db.refresh(db_transaction)
    
    return db_transaction

async def update_transaction(db: AsyncSession, transaction_id: UUID, user_id: UUID, transaction_in: TransactionCreate) -> Optional[Transaction]:
    """Updates an existing transaction, reverting the old balance change and applying the new one."""
    
    # 1. Retrieve old transaction and ensure ownership
    old_transaction = await get_transaction_by_id(db, transaction_id, user_id)
    if not old_transaction:
        return None

    # 2. Reverse the effect of the old transaction on its wallet
    await _update_wallet_balance(
        db, 
        wallet_id=old_transaction.wallet_id, 
        amount=old_transaction.amount, 
        type=old_transaction.transaction_type,
        is_reversal=True
    )
    
    # 3. Apply the new transaction details (only update fields allowed in TransactionCreate)
    update_values = transaction_in.model_dump(exclude_unset=True) 
    
    stmt = (
        update(Transaction)
        .where(Transaction.transaction_id == transaction_id)
        .values(**update_values)
        .returning(Transaction)
    )
    
    updated_transaction_result = await db.execute(stmt)
    updated_transaction = updated_transaction_result.scalars().first()
    
    # 4. Apply the effect of the new transaction on its (potentially new) wallet
    if updated_transaction:
        await _update_wallet_balance(
            db,
            wallet_id=updated_transaction.wallet_id,
            amount=updated_transaction.amount,
            type=updated_transaction.transaction_type,
            is_reversal=False
        )
    
    await db.commit()
    
    return updated_transaction

async def delete_transaction(db: AsyncSession, transaction_id: UUID, user_id: UUID) -> bool:
    """Deletes a transaction and reverts the change to the associated wallet balance."""
    
    # 1. Retrieve transaction and ensure ownership
    transaction_to_delete = await get_transaction_by_id(db, transaction_id, user_id)
    if not transaction_to_delete:
        return False
    
    # 2. Reverse the effect of the transaction on the wallet
    await _update_wallet_balance(
        db,
        wallet_id=transaction_to_delete.wallet_id,
        amount=transaction_to_delete.amount,
        type=transaction_to_delete.transaction_type,
        is_reversal=True
    )
    
    # 3. Delete the transaction itself
    stmt = (
        delete(Transaction)
        .where(Transaction.transaction_id == transaction_id)
    )
    
    result = await db.execute(stmt)
    await db.commit()
    
    return result.rowcount > 0
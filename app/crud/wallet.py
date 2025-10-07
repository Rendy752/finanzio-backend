from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update, func, or_
from typing import List, Optional, Tuple
from uuid import UUID

from app.models.wallet import Wallet
from app.schemas.wallet import WalletCreate, WalletBase

async def get_wallet_by_id(db: AsyncSession, wallet_id: UUID, user_id: UUID) -> Optional[Wallet]:
    """Retrieves a single wallet by ID, owned by the specified user."""
    result = await db.execute(
        select(Wallet)
        .where(Wallet.wallet_id == wallet_id)
        .where(Wallet.user_id == user_id)
    )
    return result.scalars().first()

async def get_all_wallets_for_user(
    db: AsyncSession, 
    user_id: UUID, 
    q: Optional[str] = None, 
    limit: int = 10, 
    offset: int = 0
) -> Tuple[List[Wallet], int]:
    """
    Retrieves all wallets for a specific user with search, pagination, 
    and returns the list and total count.
    """
    base_query = select(Wallet).where(Wallet.user_id == user_id)
    
    if q:
        search_term = f"%{q}%"
        base_query = base_query.where(
            or_(
                Wallet.wallet_name.ilike(search_term),
                Wallet.currency.ilike(search_term),
            )
        )
        
    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total_count = total_result.scalar_one()

    final_query = base_query.order_by(Wallet.wallet_name).limit(limit).offset(offset)
    
    result = await db.execute(final_query)
    wallets = result.scalars().all()
    
    return wallets, total_count

# --- Write Operations ---

async def create_wallet(db: AsyncSession, wallet_in: WalletCreate, user_id: UUID) -> Wallet:
    """Creates a new wallet for the specified user."""
    db_wallet = Wallet(
        user_id=user_id,
        wallet_name=wallet_in.wallet_name,
        currency=wallet_in.currency,
        current_balance=wallet_in.initial_balance
    )
    
    db.add(db_wallet)
    await db.commit()
    await db.refresh(db_wallet)
    
    return db_wallet

async def update_wallet(db: AsyncSession, wallet_id: UUID, user_id: UUID, wallet_in: WalletBase) -> Optional[Wallet]:
    """Updates the name and currency of an existing wallet."""
    stmt = (
        update(Wallet)
        .where(Wallet.wallet_id == wallet_id)
        .where(Wallet.user_id == user_id)
        .values(
            wallet_name=wallet_in.wallet_name,
            currency=wallet_in.currency
        )
        .returning(Wallet)
    )
    
    result = await db.execute(stmt)
    await db.commit()
    
    return result.scalars().first()

async def delete_wallet(db: AsyncSession, wallet_id: UUID, user_id: UUID) -> bool:
    """Deletes a wallet owned by the specified user."""
    stmt = (
        delete(Wallet)
        .where(Wallet.wallet_id == wallet_id)
        .where(Wallet.user_id == user_id)
    )
    
    result = await db.execute(stmt)
    await db.commit()
    
    return result.rowcount > 0
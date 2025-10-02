from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update
from typing import List, Optional
from uuid import UUID

from app.models.wallet import Wallet
from app.schemas.wallet import WalletCreate, WalletBase

# --- Read Operations ---

async def get_wallet_by_id(db: AsyncSession, wallet_id: UUID, user_id: UUID) -> Optional[Wallet]:
    """Retrieves a single wallet by ID, owned by the specified user."""
    result = await db.execute(
        select(Wallet)
        .where(Wallet.wallet_id == wallet_id)
        .where(Wallet.user_id == user_id) # Critical: Ensure ownership
    )
    return result.scalars().first()

async def get_all_wallets_for_user(db: AsyncSession, user_id: UUID) -> List[Wallet]:
    """Retrieves all wallets for a specific user."""
    result = await db.execute(
        select(Wallet)
        .where(Wallet.user_id == user_id)
        .order_by(Wallet.wallet_name)
    )
    return result.scalars().all()

# --- Write Operations ---

async def create_wallet(db: AsyncSession, wallet_in: WalletCreate, user_id: UUID) -> Wallet:
    """
    Creates a new wallet for the specified user. 
    Uses initial_balance from schema to set current_balance.
    """
    db_wallet = Wallet(
        user_id=user_id,
        wallet_name=wallet_in.wallet_name,
        currency=wallet_in.currency,
        current_balance=wallet_in.initial_balance # Set initial balance from input
    )
    
    db.add(db_wallet)
    await db.commit()
    await db.refresh(db_wallet)
    
    return db_wallet

async def update_wallet(db: AsyncSession, wallet_id: UUID, user_id: UUID, wallet_in: WalletBase) -> Optional[Wallet]:
    """Updates the name and currency of an existing wallet."""
    # Note: current_balance is NOT updated here; it's managed via transactions.
    
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
    # Best Practice Note: Before deployment, ensure transactions linked to this wallet
    # are handled (e.g., deleted or marked as unassigned) to prevent integrity errors.
    
    stmt = (
        delete(Wallet)
        .where(Wallet.wallet_id == wallet_id)
        .where(Wallet.user_id == user_id)
    )
    
    result = await db.execute(stmt)
    await db.commit()
    
    # Returns True if at least one row was affected (deleted)
    return result.rowcount > 0
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, case, and_
from typing import Dict, Any, List
from uuid import UUID
from datetime import date, datetime, timedelta
from decimal import Decimal

from app.models.transaction import Transaction, Budget
from app.models.wallet import Wallet
from app.models.category import TransactionType
from app.schemas.transaction import TransactionResponse

# --- 1. Transaction Logic (for Atomic Transfer) ---

async def perform_atomic_transfer(
    db: AsyncSession,
    user_id: UUID,
    source_wallet_id: UUID,
    target_wallet_id: UUID,
    amount: Decimal,
    description: str
) -> List[Transaction]:
    """
    Performs an atomic money transfer (Expense from Source, Income to Target) 
    within a single database session and transaction.
    """
    
    # CRITICAL: Pastikan kedua wallet dimiliki oleh user yang sama
    wallet_check = select(Wallet.wallet_id).where(Wallet.user_id == user_id, 
                                                 Wallet.wallet_id.in_([source_wallet_id, target_wallet_id]))
    
    owned_wallets = (await db.execute(wallet_check)).scalars().all()
    if len(owned_wallets) != 2:
        # Mengembalikan list kosong atau raise exception jika validasi gagal
        return []

    # Asumsi: Category "Transfer" sudah ada atau kita menggunakan category umum.
    # Untuk kesederhanaan, kita bisa menggunakan category Expense & Income dummy.
    # Dalam implementasi nyata, transfer harus memiliki kategori khusus.
    
    # 1. Transaction OUT (Expense from Source)
    txn_out = Transaction(
        wallet_id=source_wallet_id,
        # Menggunakan ID Category Expense dummy. Idealnya, ini adalah 'Transfer Out'
        category_id=UUID('ffffffff-0000-0000-0000-000000000002'), 
        transaction_type=TransactionType.EXPENSE,
        amount=amount,
        description=f"Transfer OUT: {description}",
        transaction_date=datetime.now()
    )

    # 2. Transaction IN (Income to Target)
    txn_in = Transaction(
        wallet_id=target_wallet_id,
        # Menggunakan ID Category Income dummy. Idealnya, ini adalah 'Transfer In'
        category_id=UUID('ffffffff-0000-0000-0000-000000000001'), 
        transaction_type=TransactionType.INCOME,
        amount=amount,
        description=f"Transfer IN: {description}",
        transaction_date=datetime.now()
    )

    db.add_all([txn_out, txn_in])
    
    # 3. Update Wallet Balances (menggunakan logic dari crud/transaction.py)
    # Reverse EXPENSE logic (Subtract from source)
    await db.execute(
        update(Wallet)
        .where(Wallet.wallet_id == source_wallet_id)
        .values(current_balance=Wallet.current_balance - amount)
    )

    # Apply INCOME logic (Add to target)
    await db.execute(
        update(Wallet)
        .where(Wallet.wallet_id == target_wallet_id)
        .values(current_balance=Wallet.current_balance + amount)
    )

    # Commit both transactions and balance updates atomically
    await db.commit()
    await db.refresh(txn_out)
    await db.refresh(txn_in)
    
    return [txn_out, txn_in]

# --- 2. Report Logic ---

async def get_financial_summary(db: AsyncSession, user_id: UUID) -> Dict[str, Any]:
    """
    Generates a high-level financial summary (Total Income, Total Expense, Net Balance)
    for the user across all transactions.
    """
    
    # 1. Filter transaksi hanya untuk wallet yang dimiliki user
    wallet_check = select(Wallet.wallet_id).where(Wallet.user_id == user_id).scalar_subquery()
    
    # 2. Hitung total Income dan Expense
    income_case = case((Transaction.transaction_type == TransactionType.INCOME, Transaction.amount), else_=0)
    expense_case = case((Transaction.transaction_type == TransactionType.EXPENSE, Transaction.amount), else_=0)
    
    query = select(
        func.sum(income_case).label('total_income'),
        func.sum(expense_case).label('total_expense')
    ).where(Transaction.wallet_id.in_(wallet_check))
    
    result = await db.execute(query)
    summary = result.one_or_none()
    
    total_income = summary.total_income or Decimal(0)
    total_expense = summary.total_expense or Decimal(0)
    
    net_balance = total_income - total_expense
    
    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "net_balance": net_balance,
        "date_generated": datetime.now()
    }

from sqlalchemy import Column, UUID, String, Numeric, ForeignKey, DateTime, Date, Enum as SQLEnum, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.base import Base
import uuid
from app.models.category import TransactionType # Import Enum

# Core Transaction Ledger
class Transaction(Base):
    __tablename__ = "transactions"
    
    transaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wallet_id = Column(UUID(as_uuid=True), ForeignKey("wallets.wallet_id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.category_id"), nullable=False)
    
    # Use the Enum defined in category.py
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    
    # Store amount as positive; type indicates debit/credit
    amount = Column(Numeric(18, 2), nullable=False)
    description = Column(String(255), nullable=True)
    transaction_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relationships
    wallet = relationship("Wallet", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    
# Budget Limits (Spendee style)
class Budget(Base):
    __tablename__ = "budgets"

    budget_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.category_id"), nullable=False)
    
    amount_limit = Column(Numeric(18, 2), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    # Relationships
    user = relationship("User", back_populates="budgets")
    category = relationship("Category")

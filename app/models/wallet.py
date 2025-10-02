from sqlalchemy import Column, UUID, String, Numeric, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.base import Base
import uuid

# Wallets represent cash, bank accounts, or credit cards
class Wallet(Base):
    __tablename__ = "wallets"
    
    wallet_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    wallet_name = Column(String(100), nullable=False)
    currency = Column(String(10), nullable=False, default="IDR")
    
    # Store the calculated current balance (Numeric(18, 2) is standard for finance)
    current_balance = Column(Numeric(18, 2), nullable=False, default=0.00)
    
    # Relationships
    user = relationship("User", back_populates="wallets")
    transactions = relationship("Transaction", back_populates="wallet")

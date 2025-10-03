# app/models/user.py
from sqlalchemy import Column, UUID, String, Boolean, DateTime
from sqlalchemy.orm import relationship 
from sqlalchemy.sql import func
from app.core.base import Base
import uuid

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships (defining links to the new tables)
    wallets = relationship("Wallet", back_populates="user")
    categories = relationship("Category", back_populates="user")
    budgets = relationship("Budget", back_populates="user")
    debts = relationship("DebtLedger", back_populates="user")

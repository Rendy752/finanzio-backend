from sqlalchemy import Column, UUID, String, Numeric, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship
from app.core.base import Base
import uuid

class DebtLedger(Base):
    __tablename__ = "debt_ledgers"
    
    ledger_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    
    contact_name = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True) # For SMS reminders
    
    # TRUE = Receivable (user is owed money); FALSE = Payable (user owes money)
    is_debt_to_user = Column(Boolean, nullable=False) 
    
    total_amount = Column(Numeric(18, 2), nullable=False)
    amount_paid = Column(Numeric(18, 2), nullable=False, default=0.00)
    due_date = Column(Date, nullable=True)
    is_settled = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="debts")

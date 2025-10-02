from sqlalchemy import Column, UUID, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.base import Base
import enum
import uuid

class TransactionType(enum.Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"

# Categories for grouping transactions (Food, Transport, Salary)
class Category(Base):
    __tablename__ = "categories"
    
    category_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True) # Nullable for default system categories
    category_name = Column(String(50), nullable=False)
    type = Column(SQLEnum(TransactionType), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")

from pydantic import BaseModel, Field, constr
from typing import Optional
import uuid
import enum

class TransactionType(str, enum.Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"

class CategoryBase(BaseModel):
    category_name: constr(max_length=50)
    type: TransactionType = Field(..., description="Whether the category is for 'INCOME' or 'EXPENSE'.")

class CategoryCreate(CategoryBase):
    pass 

class CategoryResponse(CategoryBase):
    category_id: uuid.UUID
    
    class Config:
        from_attributes = True

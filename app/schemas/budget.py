from pydantic import BaseModel, Field, condecimal
from datetime import date
from typing import Optional
import uuid

class BudgetBase(BaseModel):
    category_id: uuid.UUID = Field(..., description="ID of the category this budget applies to.")
    amount_limit: condecimal(max_digits=18, decimal_places=2) = Field(gt=0, description="The maximum amount allowed for this budget period.")
    start_date: date
    end_date: date

class BudgetCreate(BudgetBase):
    pass 

class BudgetResponse(BudgetBase):
    budget_id: uuid.UUID
    user_id: uuid.UUID
    
    class Config:
        from_attributes = True
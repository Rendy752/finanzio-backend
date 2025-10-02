from pydantic import BaseModel, Field, constr, condecimal
from datetime import datetime
from typing import Optional
import uuid

# Note: Assumes TransactionType Enum is available, either by importing or defining here.
# For simplicity, we define it here, but in a real app, it should come from a common utility file.
import enum
class TransactionType(str, enum.Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"

class TransactionCreate(BaseModel):
    wallet_id: uuid.UUID
    category_id: uuid.UUID
    transaction_type: TransactionType = Field(..., description="Must match the category type (INCOME or EXPENSE).")
    amount: condecimal(max_digits=18, decimal_places=2) = Field(gt=0, description="The magnitude of the transaction amount (always positive).")
    description: Optional[constr(max_length=255)] = Field(None, description="Optional note or description for the transaction.")
    transaction_date: Optional[datetime] = Field(None, description="The date/time the transaction occurred. Defaults to now().")

class TransactionResponse(TransactionCreate):
    transaction_id: uuid.UUID

    class Config:
        from_attributes = True

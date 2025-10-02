from pydantic import BaseModel, Field, constr, condecimal
from datetime import date
from typing import Optional
import uuid

class DebtLedgerCreate(BaseModel):
    contact_name: constr(max_length=255)
    total_amount: condecimal(max_digits=18, decimal_places=2) = Field(gt=0)
    is_debt_to_user: bool = Field(..., description="True if the user is owed money (Receivable); False if the user owes money (Payable).")
    phone_number: Optional[constr(max_length=20)] = Field(None, description="Contact phone for sending reminders.")
    due_date: Optional[date] = None

class DebtLedgerUpdate(BaseModel):
    # Used when partially paying off a debt
    amount_paid: Optional[condecimal(max_digits=18, decimal_places=2)] = None
    is_settled: Optional[bool] = None

class DebtLedgerResponse(DebtLedgerCreate):
    ledger_id: uuid.UUID
    amount_paid: condecimal(max_digits=18, decimal_places=2)
    is_settled: bool
    user_id: uuid.UUID

    class Config:
        from_attributes = True

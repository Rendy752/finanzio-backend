from pydantic import BaseModel, Field, constr, condecimal
from typing import Optional
import uuid
from datetime import datetime

class WalletBase(BaseModel):
    wallet_name: constr(max_length=100) = Field(..., description="Name of the financial account (e.g., 'Cash', 'Bank Mandiri').")
    currency: constr(max_length=10) = Field("IDR", description="Currency code (e.g., IDR, USD).")

class WalletCreate(WalletBase):
    initial_balance: condecimal(max_digits=18, decimal_places=2) = Field(0.00, gt=-1, description="Initial starting balance of the wallet.")

class WalletResponse(WalletBase):
    wallet_id: uuid.UUID
    current_balance: condecimal(max_digits=18, decimal_places=2)
    user_id: uuid.UUID
    
    class Config:
        from_attributes = True

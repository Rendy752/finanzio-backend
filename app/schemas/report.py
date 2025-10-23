from pydantic import BaseModel, Field, condecimal
from datetime import datetime
from decimal import Decimal

class FinancialSummaryResponse(BaseModel):
    total_income: condecimal(max_digits=18, decimal_places=2)
    total_expense: condecimal(max_digits=18, decimal_places=2)
    net_balance: condecimal(max_digits=18, decimal_places=2)
    date_generated: datetime

    class Config:
        from_attributes = True

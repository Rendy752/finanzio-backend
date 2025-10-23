from pydantic import BaseModel, Field, constr, condecimal
import uuid
from decimal import Decimal

class TransferCreate(BaseModel):
    source_wallet_id: uuid.UUID
    target_wallet_id: uuid.UUID
    amount: condecimal(max_digits=18, decimal_places=2) = Field(gt=0, description="Amount to transfer.")
    description: constr(max_length=255) = Field(..., description="Description for the transfer transaction.")

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        super().__pydantic_init_subclass__(**kwargs)
        if not cls.__config__.validate_assignment:
            cls.__config__.validate_assignment = True

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_wallets

    @classmethod
    def validate_wallets(cls, values):
        if 'source_wallet_id' in values and 'target_wallet_id' in values:
            if values['source_wallet_id'] == values['target_wallet_id']:
                raise ValueError("Source and target wallets must be different.")
        return values

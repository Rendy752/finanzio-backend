# app/schemas/user.py
from pydantic import BaseModel, EmailStr, constr, Field
from typing import Optional
import uuid
from datetime import datetime

# 1. Base (Shared properties)
class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[constr(max_length=100)] = None
    last_name: Optional[constr(max_length=100)] = None

# 2. Input/Creation Schema (For POST requests)
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=72)
    
# 3. Response Schema (For data returned by API)
class UserResponse(UserBase):
    user_id: uuid.UUID
    is_active: bool
    created_at: datetime
    
    # Required for ORM mode (allows direct conversion from SQLAlchemy model)
    class Config:
        from_attributes = True
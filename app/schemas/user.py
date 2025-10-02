# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
from datetime import datetime

# 1. Base (Shared properties)
class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

# 2. Input/Creation Schema (For POST requests)
class UserCreate(UserBase):
    password: str
    
# 3. Response Schema (For data returned by API)
class UserResponse(UserBase):
    user_id: uuid.UUID
    is_active: bool
    created_at: datetime
    
    # Required for ORM mode (allows direct conversion from SQLAlchemy model)
    class Config:
        from_attributes = True
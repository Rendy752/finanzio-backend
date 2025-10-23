from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    """Token returned upon successful login."""
    access_token: str
    token_type: str = "bearer"
    
class TokenData(BaseModel):
    """Payload data embedded in the token."""
    user_id: Optional[str] = None

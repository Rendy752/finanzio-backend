# app/schemas/common.py
from pydantic import BaseModel
from typing import TypeVar, Generic, Any

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    """Standardized successful API response structure."""
    success: bool = True
    message: str = "Request successful"
    data: T
    
class ErrorResponse(BaseModel):
    """Standardized error response structure."""
    success: bool = False
    error_code: int
    message: str
    details: Any = None
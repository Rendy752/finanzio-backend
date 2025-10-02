# app/schemas/common.py
from pydantic import BaseModel, Field
from typing import TypeVar, Generic, Any, List

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    """Standardized successful API response structure for a single item."""
    success: bool = True
    message: str = "Request successful"
    data: T
    
class APIListResponse(BaseModel, Generic[T]):
    """Standardized successful API response structure for lists/collections."""
    success: bool = True
    message: str = "Request successful"
    data: List[T]
    total_count: int = Field(0, description="Total number of items in the list (before pagination, if applied).")

class ErrorResponse(BaseModel):
    """Standardized error response structure."""
    success: bool = False
    error_code: int = Field(..., description="HTTP status code for the error.")
    message: str = Field(..., description="User-friendly description of the error.")
    details: Any = Field(None, description="Optional field for detailed error information (e.g., validation errors).")

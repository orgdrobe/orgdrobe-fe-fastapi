from typing import Optional, Any
from pydantic import BaseModel, Field

class ValidationErrorDetail(BaseModel):
    field: str
    issue: str
    message: str

class ErrorContent(BaseModel):
    code: str = Field(..., description="Stable error code for the client (snake_case)")
    message: str = Field(...,  description="Human-readable message")
    details: Optional[Any] = Field(default=None,  description="Additional details (e.g. field validation errors)")
    trace_id: Optional[str] = Field(default=None,  description="Request ID for debugging")

class ErrorResponse(BaseModel):
    error: ErrorContent
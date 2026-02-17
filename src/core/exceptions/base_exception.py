from typing import Optional, Any
from core.enums.error_codes import ErrorCode

class BaseAPIException(Exception):
    status_code: int = 500
    code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR
    message: str = "An unexpected error occurred."
    # TODO: add module= auth, 

    def __init__(self, message: Optional[str] = None, details: Optional[Any] = None) -> None:
        if message:
            self.message = message
        self.details = details
        super().__init__(self.message)
